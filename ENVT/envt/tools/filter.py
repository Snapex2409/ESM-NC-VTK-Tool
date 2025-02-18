import envt.vtk_util.vtk_wrapper as vtkw
import envt.nc_util.nc_wrapper as ncw
from envt.tools.nc2vtk import NC2VTK
from envt.tools.convert import Converter as cv
from envt.tools.triangulation import triangulate_polygon as triangulate, triangulate_convex_shape
import numpy as np
import vtkmodules.util.numpy_support as vtk_np
from collections import defaultdict

class Filter:
    def __init__(self, input_file, var:ncw.NCVars, nc_file_path):
        self.vtk_file = vtkw.VTKInputFile(input_file)
        self.nc_input = ncw.NCFile(nc_file_path)
        self.clo = self.nc_input.var_clo_data(var)
        self.cla = self.nc_input.var_cla_data(var)
        msk_lon, msk_lat, msk_entries, msk_corner_indices = NC2VTK.process_corner_data(self.clo, self.cla)
        self.msk_lon = msk_lon
        self.msk_lat = msk_lat
        self.msk_num_entries = msk_entries
        self.msk_corner_indices = msk_corner_indices

        self.lon = self.nc_input.var_lon_data(var).flatten()
        self.lat = self.nc_input.var_lat_data(var).flatten()
        self.var = var

    def compute_cell_connectivity(self, valid_cells):
        corner_indices = self.msk_corner_indices[:,valid_cells]
        N, M = corner_indices.shape  # N = corners per cell, M = number of cells

        # Step 1: Create a point-to-cells mapping
        point_to_cells = defaultdict(set)
        for cell_idx in range(M):
            for point_idx in corner_indices[:, cell_idx]:
                point_to_cells[point_idx].add(cell_idx)

        # Step 2: Compute connectivity by checking shared points
        cell_connections = defaultdict(set)
        for cell_idx in range(M):
            # Get all other cells that share at least one point with the current cell
            connected_cells = set()
            for point_idx in corner_indices[:, cell_idx]:
                connected_cells.update(point_to_cells[point_idx])

            # Remove self from connections
            #connected_cells.discard(cell_idx)
            cell_connections[cell_idx] = connected_cells

        return cell_connections

    def apply(self, output_file, threshold=0.001, denotes_water=False, orig_mask=None):
        # load mask data
        np_mask_data = None
        if orig_mask is None:
            for i in range(self.vtk_file.input_point_data.GetNumberOfArrays()):
                array = self.vtk_file.input_point_data.GetArray(i)
                if array.GetName() == "mask":
                    np_mask_data = vtk_np.vtk_to_numpy(array)
                    break
            if np_mask_data is None:
                print("WARNING: No mask data available")
                return
            np_cell_mask = np.average(np_mask_data[self.msk_corner_indices], axis=0)
        else:
            msk_file = ncw.NCFile(orig_mask)
            np_cell_mask = msk_file.var_msk_data(self.var).flatten()

        # find valid cells
        valid_points = None
        if denotes_water:
            valid_points = np_cell_mask > threshold
        else:
            ones = np.ones_like(np_cell_mask)
            land_amount = np.minimum(ones, np_cell_mask)
            water_amount = ones - land_amount
            valid_points = water_amount > threshold

        # load center points and apply filter
        np_points = cv.convert_data_arrays(cv.Mode2DTO3D(), self.lon, self.lat, np.zeros((len(self.lon),)))
        np_points = np_points[valid_points]

        # compute cell sizes for integral quantities
        np_msk_points = cv.convert_data_arrays(cv.Mode2DTO3D(), self.msk_lon, self.msk_lat, np.zeros(len(self.msk_lon),))
        np_cell_sizes = np.zeros_like(np_cell_mask)
        for i in range(np_cell_mask.shape[0]):
            if not valid_points[i]: continue
            indices = self.msk_corner_indices[:, i]
            indices = np.unique(indices)
            if len(indices) < 3: continue

            points = np_msk_points[indices]
            tri_points, tri_indices = triangulate(points, indices)

            for idx_tri in range(tri_indices.shape[0]):
                p0 = tri_points[idx_tri][0]
                p1 = tri_points[idx_tri][1]
                p2 = tri_points[idx_tri][2]

                v = p1 - p0
                w = p2 - p0
                cross_product = np.cross(v, w)
                np_cell_sizes[i] += np.abs(0.5 * np.linalg.norm(cross_product))
        point_data_integral = vtk_np.numpy_to_vtk(np_cell_sizes[valid_points], deep=True)
        point_data_integral.SetName("area")

        # compute new cells based on centers
        cell_connections = self.compute_cell_connectivity(valid_points)
        vtk_cells = vtkw.vtkCellArray()
        for i in range(np_points.shape[0]):
            cell_ids = np.array(list(cell_connections[i]))
            points = np_points[cell_ids]
            if len(points) < 3: continue
            _, tri_indices = triangulate_convex_shape(points, cell_ids)

            for idx_tri in range(tri_indices.shape[0]):
                tri = vtkw.vtkTriangle()
                tri.GetPointIds().SetId(0, tri_indices[idx_tri][0])
                tri.GetPointIds().SetId(1, tri_indices[idx_tri][1])
                tri.GetPointIds().SetId(2, tri_indices[idx_tri][2])
                vtk_cells.InsertNextCell(tri)

        out_grid = vtkw.vtkUnstructuredGrid()
        out_points = vtkw.vtkPoints()
        out_points.SetData(vtk_np.numpy_to_vtk(np_points))
        out_grid.SetPoints(out_points)
        out_grid.SetCells(vtkw.VTK_TRIANGLE, vtk_cells)
        out_grid.GetPointData().AddArray(point_data_integral)
        vtkw.VTKOutputFile(output_file, out_grid).write()
