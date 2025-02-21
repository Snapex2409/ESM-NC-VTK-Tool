import envt.vtk_util.vtk_wrapper as vtkw
import envt.nc_util.nc_wrapper as ncw
from envt.tools.nc2vtk import NC2VTK
from envt.tools.convert import Converter as cv
from envt.tools.triangulation import triangulate_polygon as triangulate, triangulate_convex_shape, check_order, check_distances
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

    def check_edge_nb(self, cell_neighbours, edge_to_tris, idx, edge):
        tris_with_same_edge = edge_to_tris[edge]
        third_point_of_tris_with_same_edge = {el for tup in tris_with_same_edge for el in tup}
        third_point_of_tris_with_same_edge.discard(edge[0])
        third_point_of_tris_with_same_edge.discard(edge[1])
        return any(idx in cell_neighbours[p] for p in third_point_of_tris_with_same_edge)

    def check_center(self, cell_neighbours, cell_idx_i, points):
        neighbours_i = cell_neighbours[cell_idx_i]
        exclusive_tris = []
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

        if len(exclusive_tris)>0: return exclusive_tris
        else: return None

    def compute_cell_center_tris_alt2(self, cell_neighbours, points):
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

    def compute_cell_center_tris_alt(self, cell_neighbours):
        known_tris = set()
        edge_counts = defaultdict(int)
        edge_to_tris = defaultdict(set)

        def rec_tri(e, new_idx, limit=10):
            if limit <= 0: return
            e0 = e
            e1 = tuple(sorted((e[0], new_idx)))
            e2 = tuple(sorted((e[1], new_idx)))
            tri = tuple(sorted((e[0], e[1], new_idx)))
            if tri in known_tris: return
            if edge_counts[e0] >= 2 or edge_counts[e1] >= 2 or edge_counts[e2] >= 2: return

            known_tris.add(tri)
            edge_counts[e0] += 1
            edge_counts[e1] += 1
            edge_counts[e2] += 1

            shared_nb_e0 = cell_neighbours[e0[0]] & cell_neighbours[e0[1]]
            shared_nb_e0.discard(new_idx)
            shared_nb_e1 = cell_neighbours[e1[0]] & cell_neighbours[e1[1]]
            shared_nb_e1.discard(e[1])
            shared_nb_e2 = cell_neighbours[e2[0]] & cell_neighbours[e2[1]]
            shared_nb_e2.discard(e[0])
            lengths = [len(shared_nb_e0), len(shared_nb_e1), len(shared_nb_e2)]
            smallest = min(lengths)
            smallest_items = [l for l in lengths if l == smallest]
            if len(set(smallest_items)) != len(smallest_items): return

            for nb_idx in shared_nb_e0:
                if lengths[0] == smallest:
                    rec_tri(e0, nb_idx, limit-1)
                    break
            for nb_idx in shared_nb_e1:
                if lengths[1] == smallest:
                    rec_tri(e1, nb_idx, limit-1)
                    break
            for nb_idx in shared_nb_e2:
                if lengths[2] == smallest:
                    rec_tri(e2, nb_idx, limit-1)
                    break

            for nb_idx in shared_nb_e0:
                if lengths[0] != smallest:
                    rec_tri(e0, nb_idx, limit-1)
                    break
            for nb_idx in shared_nb_e1:
                if lengths[1] != smallest:
                    rec_tri(e1, nb_idx, limit-1)
                    break
            for nb_idx in shared_nb_e2:
                if lengths[2] != smallest:
                    rec_tri(e2, nb_idx, limit-1)
                    break

        for cell_idx_i in cell_neighbours.keys():
            neighbours_i = cell_neighbours[cell_idx_i]
            for cell_idx_j in neighbours_i:
                edge = tuple(sorted((cell_idx_i, cell_idx_j)))
                if edge_counts[edge] >= 2: continue

                neighbours_j = cell_neighbours[cell_idx_j]
                shared = neighbours_i & neighbours_j
                for cell_idx_k in shared:
                    rec_tri(edge, cell_idx_k, 100)


        return known_tris

    def compute_cell_center_tris(self, cell_neighbours):
        known_tris = set()
        edge_counts = defaultdict(int)
        edge_to_tris = defaultdict(set)

        for cell_idx_i in cell_neighbours.keys():
            neighbours_i = cell_neighbours[cell_idx_i]
            for cell_idx_j in neighbours_i:
                edge = tuple(sorted((cell_idx_i, cell_idx_j)))
                if edge_counts[edge] >= 2: continue

                neighbours_j = cell_neighbours[cell_idx_j]
                shared = neighbours_i & neighbours_j
                for cell_idx_k in shared:
                    e0 = edge
                    e1 = tuple(sorted((cell_idx_i, cell_idx_k)))
                    e2 = tuple(sorted((cell_idx_j, cell_idx_k)))
                    if self.check_edge_nb(cell_neighbours, edge_to_tris, cell_idx_k, e0): continue
                    if self.check_edge_nb(cell_neighbours, edge_to_tris, cell_idx_j, e1): continue
                    if self.check_edge_nb(cell_neighbours, edge_to_tris, cell_idx_i, e2): continue

                    tri = tuple(sorted((cell_idx_i, cell_idx_j, cell_idx_k)))
                    if tri in known_tris: continue

                    if edge_counts[e0] >= 2 or edge_counts[e1] >= 2 or edge_counts[e2] >= 2: continue

                    known_tris.add(tri)
                    edge_counts[e0] += 1
                    edge_counts[e1] += 1
                    edge_counts[e2] += 1
                    edge_to_tris[e0].add(tri)
                    edge_to_tris[e1].add(tri)
                    edge_to_tris[e2].add(tri)

        return known_tris

    def compute_cell_connectivity(self, valid_cells, unique_cells):
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
        out_grid.SetCells(vtkw.VTK_TRIANGLE, vtk_cells)
        out_grid.GetPointData().AddArray(point_data_integral)
        vtkw.VTKOutputFile(output_file, out_grid).write()
