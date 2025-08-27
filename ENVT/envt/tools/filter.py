import envt.vtk_util.vtk_wrapper as vtkw
import envt.nc_util.nc_wrapper as ncw
from envt.tools.nc2vtk import NC2VTK
from envt.tools.convert import Converter as cv
from envt.tools.triangulation import triangulate_polygon as triangulate, triangulate_convex_shape, check_order, check_distances
import numpy as np
import vtkmodules.util.numpy_support as vtk_np
from collections import defaultdict

class Filter:
    """
    Applies mapped mask meshes (corner based) to target meshes (center based)
    and attaches connectivity information for center based mesh if needed.
    """

    def __init__(self, input_file, var:ncw.NCVars, nc_file_path):
        self.vtk_file = vtkw.VTKInputFile(input_file)
        """Mask VTK file"""
        self.nc_input = ncw.NCFile(nc_file_path)
        """NC File Original Data"""
        self.clo = self.nc_input.var_clo_data(var)
        """ Corner data mask full longitude"""
        self.cla = self.nc_input.var_cla_data(var)
        """ Corner data mask full latitude"""
        msk_lon, msk_lat, msk_entries, msk_corner_indices = NC2VTK.process_corner_data(self.clo, self.cla)
        self.msk_lon = msk_lon
        """ Unique corner data longitude"""
        self.msk_lat = msk_lat
        """ Unique corner data latitude"""
        self.msk_num_entries = msk_entries
        """ Number of unique corner points"""
        self.msk_corner_indices = msk_corner_indices
        """ Mapping of cells to unique corner points based on indices"""

        self.lon = self.nc_input.var_lon_data(var).flatten()
        """ Center data longitude"""
        self.lat = self.nc_input.var_lat_data(var).flatten()
        """ Center data latitude"""
        self.var = var
        """ Active variable"""

    def check_center(self, cell_neighbours, cell_idx_i, points):
        """
        Heuristically determines valid triangles around cell_idx_i that do not overlap
        :param cell_neighbours: information about which cells neighbour each other
        :param cell_idx_i: considered cell
        :param points: cell center positions
        :return: list of non interfering triangles, or None if no conflict detected
        """
        neighbours_i = cell_neighbours[cell_idx_i]
        exclusive_tris = []
        optional_tris = []
        for cell_idx_j in neighbours_i:
            neighbours_j = cell_neighbours[cell_idx_j]
            shared_ij = neighbours_i & neighbours_j
            for cell_idx_k in shared_ij:
                neighbours_k = cell_neighbours[cell_idx_k]
                shared_ijk = shared_ij & neighbours_k
                for cell_idx_l in shared_ijk:
                    # this is a quad with mutually exclusive triangles
                    sorting = sorted((cell_idx_i, cell_idx_j, cell_idx_k, cell_idx_l))
                    if np.isclose(self.lon[sorting[0]], self.lon[sorting[3]], rtol=1e-4) or np.isclose(self.lat[sorting[0]], self.lat[sorting[3]], rtol=1e-4) or \
                        (self.lon[sorting[0]] < self.lon[sorting[1]] and self.lon[sorting[0]] < self.lon[sorting[2]] and
                         self.lon[sorting[3]] < self.lon[sorting[1]] and self.lon[sorting[3]] < self.lon[sorting[2]]) or \
                        (self.lon[sorting[0]] > self.lon[sorting[1]] and self.lon[sorting[0]] > self.lon[sorting[2]] and
                         self.lon[sorting[3]] > self.lon[sorting[1]] and self.lon[sorting[3]] > self.lon[sorting[2]]) or \
                        (self.lat[sorting[0]] < self.lat[sorting[1]] and self.lat[sorting[0]] < self.lat[sorting[2]] and
                         self.lat[sorting[3]] < self.lat[sorting[1]] and self.lat[sorting[3]] < self.lat[sorting[2]]) or \
                        (self.lat[sorting[0]] > self.lat[sorting[1]] and self.lat[sorting[0]] > self.lat[sorting[2]] and
                         self.lat[sorting[3]] > self.lat[sorting[1]] and self.lat[sorting[3]] > self.lat[sorting[2]]) or \
                         check_distances(points[np.array(sorting)]):
                        exclusive_tris.append((sorting[0], sorting[1], sorting[2]))
                        exclusive_tris.append((sorting[0], sorting[2], sorting[3]))
                    else:
                        exclusive_tris.append((sorting[0], sorting[1], sorting[2]))
                        exclusive_tris.append((sorting[1], sorting[2], sorting[3]))

                # we detected a non-conflicting triangle ijk
                # need to store it and return it as well, if we detect interfering quads
                if len(shared_ijk) == 0:
                    opt_tri = tuple(sorted((cell_idx_i, cell_idx_j, cell_idx_k)))
                    optional_tris.append(opt_tri)

        if len(exclusive_tris)>0:
            exclusive_tris.extend(optional_tris)
            return exclusive_tris
        else: return None

    def compute_cell_center_tris_alt2(self, cell_neighbours, points):
        """
        Computes all valid triangles for the center based mesh
        :param cell_neighbours: information about which cells neighbour each other
        :param points: cell center positions
        :return: set of all valid triangles
        """
        known_tris = set()
        edge_counts = defaultdict(int)

        for cell_idx_i in cell_neighbours.keys():
            neighbours_i = cell_neighbours[cell_idx_i]

            tris = self.check_center(cell_neighbours, cell_idx_i, points)
            if tris is not None: # has mutually exclusive tris
                for tri in tris:
                    e0 = tuple((tri[0], tri[1]))
                    e1 = tuple((tri[0], tri[2]))
                    e2 = tuple((tri[1], tri[2]))
                    if tri in known_tris: continue
                    if edge_counts[e0] >= 2 or edge_counts[e1] >= 2 or edge_counts[e2] >= 2: continue
                    known_tris.add(tri)
                    edge_counts[e0] += 1
                    edge_counts[e1] += 1
                    edge_counts[e2] += 1
            else: # can handle regularly
                pass
                for cell_idx_j in neighbours_i:
                    edge = tuple(sorted((cell_idx_i, cell_idx_j)))
                    if edge_counts[edge] >= 2: continue
#
                    neighbours_j = cell_neighbours[cell_idx_j]
                    shared = neighbours_i & neighbours_j
                    for cell_idx_k in shared:
                        e0 = edge
                        e1 = tuple(sorted((cell_idx_i, cell_idx_k)))
                        e2 = tuple(sorted((cell_idx_j, cell_idx_k)))
                        tri = tuple(sorted((cell_idx_i, cell_idx_j, cell_idx_k)))
                        if tri in known_tris: continue
                        if edge_counts[e0] >= 2 or edge_counts[e1] >= 2 or edge_counts[e2] >= 2: continue
#
                        known_tris.add(tri)
                        edge_counts[e0] += 1
                        edge_counts[e1] += 1
                        edge_counts[e2] += 1

        return known_tris

    def compute_cell_connectivity(self, valid_cells, unique_cells):
        """
        Computes connectivity between cells
        :param valid_cells: filter for which cells are valid after water filtering
        :param unique_cells: filter for which cells are unique as some only differ spuriously
        :return: cell connectivity information
        """
        corner_indices = self.msk_corner_indices[:,valid_cells][:, unique_cells]
        N, M = corner_indices.shape  # N = corners per cell, M = number of cells

        # Step 1: Create a point-to-cells mapping
        point_to_cells = defaultdict(set)
        for cell_idx in range(M):
            # ignore cell if it has less than 3 corners
            #if len(np.unique(corner_indices[:, cell_idx])) < 3: continue

            for point_idx in corner_indices[:, cell_idx]:
                point_to_cells[point_idx].add(cell_idx)

        # Step 2: Compute connectivity by checking shared points
        cell_connections = defaultdict(set)
        for cell_idx in range(M):
            #if len(np.unique(corner_indices[:, cell_idx])) < 3: continue
            # Get all other cells that share at least one point with the current cell
            connected_cells = set()
            for point_idx in corner_indices[:, cell_idx]:
                connected_cells.update(point_to_cells[point_idx])

            # Remove self from connections
            connected_cells.discard(cell_idx)
            cell_connections[cell_idx] = connected_cells

        return cell_connections

    def gather_cell_mask(self):
        np_mask_data = None
        for i in range(self.vtk_file.input_point_data.GetNumberOfArrays()):
            array = self.vtk_file.input_point_data.GetArray(i)
            if array.GetName() == "mask":
                np_mask_data = vtk_np.vtk_to_numpy(array)
                break
        if np_mask_data is None:
            print("WARNING: No mask data available")
            return None
        np_cell_mask = np.average(np_mask_data[self.msk_corner_indices], axis=0)
        return np_cell_mask

    @staticmethod
    def get_valid_cells(denotes_water, threshold, mask):
        if denotes_water:
            valid_points = mask > threshold
        else:
            ones = np.ones_like(mask)
            land_amount = np.minimum(ones, mask)
            water_amount = ones - land_amount
            valid_points = water_amount > threshold
        return valid_points

    def apply(self, output_file, threshold=0.001, denotes_water=False, create_conn=False):
        """
        Applies mapped mask meshes (corner based) to target meshes (center based)
        and attaches connectivity information for center based mesh if needed.
        :param output_file: target VTK output file
        :param threshold: used to filter out masked cells after mask mapping
        :param denotes_water: does the mask value need to be inverted (1 - val)?
        :param create_conn: should we add connectivity information?
        :return:
        """
        # load mask data
        np_cell_mask = self.gather_cell_mask()
        if np_cell_mask is None: return

        # find valid cells
        valid_points = Filter.get_valid_cells(denotes_water, threshold, np_cell_mask)

        # load center points and apply filter
        np_points = cv.convert_data_arrays(cv.Mode2DTO3D(), self.lon, self.lat, np.zeros((len(self.lon),)))
        np_points = np_points[valid_points]
        np_points = np.round(np_points, decimals=5)
        np_points, unique_points = np.unique(np_points, return_index=True, axis=0)
        self.lon = self.lon[valid_points][unique_points]
        self.lat = self.lat[valid_points][unique_points]

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
        point_data_integral = vtk_np.numpy_to_vtk(np_cell_sizes[valid_points][unique_points], deep=True)
        point_data_integral.SetName("area")

        # compute new cells based on centers
        if create_conn:
            cell_connections = self.compute_cell_connectivity(valid_points, unique_points)
            tris = self.compute_cell_center_tris_alt2(cell_connections, np_points)

            vtk_cells = vtkw.vtkCellArray()
            for tri in tris:
                i, j, k = tri
                vtk_tri = vtkw.vtkTriangle()
                vtk_tri.GetPointIds().SetId(0, i)
                vtk_tri.GetPointIds().SetId(1, j)
                vtk_tri.GetPointIds().SetId(2, k)
                vtk_cells.InsertNextCell(vtk_tri)

        out_grid = vtkw.vtkUnstructuredGrid()
        out_points = vtkw.vtkPoints()
        out_points.SetData(vtk_np.numpy_to_vtk(np_points))
        out_grid.SetPoints(out_points)
        if create_conn: out_grid.SetCells(vtkw.VTK_TRIANGLE, vtk_cells)
        out_grid.GetPointData().AddArray(point_data_integral)
        vtkw.VTKOutputFile(output_file, out_grid).write()

    def apply_corner(self, output_file, threshold=0.001, denotes_water=False, create_conn=False):
        # load mask data
        np_cell_mask = self.gather_cell_mask()
        if np_cell_mask is None: return

        # need to invert mask for valid cells
        valid_cells = Filter.get_valid_cells(denotes_water, threshold, np_cell_mask)
        mask = np.ones_like(valid_cells)
        mask[valid_cells] = 0

        lon, lat, num_entries, corner_indices = NC2VTK.process_corner_data(self.clo, self.cla, mask, True)
        grid = NC2VTK.generate_corner_u_grid(lon, lat, num_entries, corner_indices, self.var, mask, True, True)
        vtkw.VTKOutputFile(output_file, grid).write()
