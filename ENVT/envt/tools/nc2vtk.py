import envt.nc_util.nc_wrapper as ncw
import envt.vtk_util.vtk_wrapper as vtkw
from envt.tools.convert import Converter as cv
from envt.tools.triangulation import triangulate_polygon as triangulate
import numpy as np
import vtkmodules.util.numpy_support as vtk_np

class NC2VTK:
    def __init__(self, nc_file_path, msk_file_path):
        self.nc_input = ncw.NCFile(nc_file_path)
        self.msk_input = ncw.NCFile(msk_file_path) if msk_file_path is not None else None

    def nc2vtk(self, var:ncw.NCVars, output_path, use_filter:bool, use_corner:bool):
        grid = self._nc2vtk_corner(var, use_filter) if use_corner else self._nc2vtk_center(var, use_filter)
        vtkw.VTKOutputFile(output_path, grid).write()

    def _nc2vtk_center(self, var:ncw.NCVars, use_filter:bool):
        lon = self.nc_input.var_lon_data(var).flatten()
        lat = self.nc_input.var_lat_data(var).flatten()
        msk = self.msk_input.var_msk_data(var).flatten() if self.msk_input is not None else None
        if use_filter and msk is not None:
            lon = lon[msk == 0]
            lat = lat[msk == 0]

        cart_points = cv.convert_data_arrays(cv.Mode2DTO3D(), lon, lat, np.zeros((len(lon),)))
        cart_points_data_array = vtk_np.numpy_to_vtk(cart_points, deep=True)

        vtk_points = vtkw.vtkPoints()
        vtk_points.SetData(cart_points_data_array)
        unstructured_grid = vtkw.vtkUnstructuredGrid()
        unstructured_grid.SetPoints(vtk_points)

        if msk is not None:
            vtk_point_data = vtk_np.numpy_to_vtk(np.ones_like(lon) if use_filter else msk, deep=True)
            vtk_point_data.SetName("mask")
            unstructured_grid.GetPointData().AddArray(vtk_point_data)

        return unstructured_grid

    @staticmethod
    def process_corner_data(clo, cla, msk=None, use_filter=False):
        dims = clo.shape[0]
        clo = np.array([clo[i, :, :].flatten() for i in range(dims)])
        cla = np.array([cla[i, :, :].flatten() for i in range(dims)])
        clo_cla_points = np.array([np.column_stack((clo[i, :], cla[i, :])) for i in range(dims)])
        if use_filter and msk is not None: clo_cla_points = clo_cla_points[:, msk == 0, :]
        clo_cla_points[np.isclose(clo_cla_points, 0)] = 0.0
        unique_points = np.unique(clo_cla_points.reshape((-1, 2)), axis=0)

        lon = unique_points[:, 0]
        lat = unique_points[:, 1]
        num_entries = clo_cla_points.shape[1]
        coord_2_unique_idx = {tuple(point): idx for idx, point in enumerate(unique_points)}

        corner_coords = clo_cla_points
        corner_indices = np.array([[coord_2_unique_idx[tuple(point)] for point in corner_coords[i, :, :]] for i in range(dims)])
        return lon, lat, num_entries, corner_indices

    def _nc2vtk_corner(self, var:ncw.NCVars, use_filter:bool):
        clo = self.nc_input.var_clo_data(var)
        cla = self.nc_input.var_cla_data(var)
        msk = self.msk_input.var_msk_data(var).flatten() if self.msk_input is not None else None
        lon, lat, num_entries, corner_indices = NC2VTK.process_corner_data(clo, cla, msk, use_filter)

        cart_points = cv.convert_data_arrays(cv.Mode2DTO3D(), lon, lat, np.zeros((len(lon),)))
        cart_points_data_array = vtk_np.numpy_to_vtk(cart_points, deep=True)

        vtk_points = vtkw.vtkPoints()
        vtk_points.SetData(cart_points_data_array)

        vtk_cells = vtkw.vtkCellArray()
        if msk is not None:
            nfilter_msk = np.zeros((len(lon),))
        for i in range(num_entries):
            # triangulate points
            # first filter out duplicates
            indices = corner_indices[:, i]
            indices = np.unique(indices)
            if len(indices) < 3: continue

            points = cart_points[indices]
            _, tri_indices = triangulate(points, indices)

            for idx_tri in range(tri_indices.shape[0]):
                tri = vtkw.vtkTriangle()
                tri.GetPointIds().SetId(0, tri_indices[idx_tri][0])
                tri.GetPointIds().SetId(1, tri_indices[idx_tri][1])
                tri.GetPointIds().SetId(2, tri_indices[idx_tri][2])
                vtk_cells.InsertNextCell(tri)

            if msk is not None and msk[i] == 0:
                nfilter_msk[indices] = 1.0

        unstructured_grid = vtkw.vtkUnstructuredGrid()
        unstructured_grid.SetPoints(vtk_points)
        unstructured_grid.SetCells(vtkw.VTK_TRIANGLE, vtk_cells)

        if msk is not None:
            if use_filter:
                vtk_point_data = vtk_np.numpy_to_vtk(np.ones((cart_points.shape[0],)).astype(np.float32), deep=True)
                vtk_point_data.SetName("mask")  # Set the name of the point data
                unstructured_grid.GetPointData().AddArray(vtk_point_data)
            else:
                vtk_point_data = vtk_np.numpy_to_vtk(nfilter_msk, deep=True)
                vtk_point_data.SetName("mask")  # Set the name of the point data
                unstructured_grid.GetPointData().AddArray(vtk_point_data)

        return unstructured_grid
