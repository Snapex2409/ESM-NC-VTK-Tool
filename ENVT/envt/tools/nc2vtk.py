from collections import defaultdict

import envt.nc_util.nc_wrapper as ncw
import envt.vtk_util.vtk_wrapper as vtkw
from envt.tools.convert import Converter as cv
from envt.tools.triangulation import triangulate_polygon as triangulate, compute_plane_basis, compute_normal, sort_counterclockwise
import numpy as np
import vtkmodules.util.numpy_support as vtk_np

class NC2VTK:
    """Converts NC file data into VTK file format using unstructured arrays"""
    def __init__(self, nc_file_path, msk_file_path):
        self.nc_input = ncw.NCFile(nc_file_path)
        """NC input data"""
        self.msk_input = ncw.NCFile(msk_file_path) if msk_file_path is not None else None
        """Mask input data"""

    def nc2vtk(self, var:ncw.NCVars, output_path, use_filter:bool, use_corner:bool, use_torc_fix:bool=True, use_triangulate:bool=True):
        """
        Converts NC data into VTK format, selects implementation based on params
        :param var: active variable
        :param output_path: output VTK file path
        :param use_filter: should we already filter out points? (only possible for SEA meshes)
        :param use_corner: should the target mesh use corner data? (alternative is center)
        :param use_torc_fix: do we want to apply the empirical torc mesh fix
        :param use_triangulate: enables mesh triangulation
        :return:
        """
        grid = self._nc2vtk_corner(var, use_filter, use_torc_fix, use_triangulate) if use_corner else self._nc2vtk_center(var, use_filter)
        vtkw.VTKOutputFile(output_path, grid).write()

    def _nc2vtk_center(self, var:ncw.NCVars, use_filter:bool):
        """
        Extracts center based mesh
        :param var: active variable
        :param use_filter: should we already filter out points? (only possible for SEA meshes)
        :return:
        """
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
        """
        Determines unique points of corner data and filters out numerically spurious different points
        :param clo: clo data array
        :param cla: cla data array
        :param msk: mask data array
        :param use_filter: should we apply the mask?
        :return: tuple of (lon, lat, num_entries, corner_indices)
        """
        dims = clo.shape[0]
        clo = np.array([clo[i, :, :].flatten() for i in range(dims)])
        cla = np.array([cla[i, :, :].flatten() for i in range(dims)])
        clo_cla_points = np.array([np.column_stack((clo[i, :], cla[i, :])) for i in range(dims)])
        if use_filter and msk is not None: clo_cla_points = clo_cla_points[:, msk == 0, :]
        clo_cla_points[np.isclose(clo_cla_points, 0)] = 0.0
        clo_cla_points = np.round(clo_cla_points, decimals=8)
        unique_points = np.unique(clo_cla_points.reshape((-1, 2)), axis=0)

        lon = unique_points[:, 0]
        lat = unique_points[:, 1]
        num_entries = clo_cla_points.shape[1]
        coord_2_unique_idx = {tuple(point): idx for idx, point in enumerate(unique_points)}

        corner_coords = clo_cla_points
        corner_indices = np.array([[coord_2_unique_idx[tuple(point)] for point in corner_coords[i, :, :]] for i in range(dims)])
        return lon, lat, num_entries, corner_indices

    @staticmethod
    def generate_corner_u_grid(lon, lat, num_entries, corner_indices, var, msk, use_filter, create_conn, use_torc_fix:bool=True, use_triangulation:bool=True):
        cart_points = cv.convert_data_arrays(cv.Mode2DTO3D(), lon, lat, np.zeros((len(lon),)))

        if var == ncw.NCVars.TORC and use_torc_fix:
            # we want to add one point at the South Pole here
            tmp = np.zeros((len(cart_points) + 1, 3))
            tmp[0:-1, :] = cart_points
            tmp[-1, :] = np.average(cart_points[cart_points[:, 2] <= -6215000], axis=0)
            cart_points = tmp

        cart_points_data_array = vtk_np.numpy_to_vtk(cart_points, deep=True)
        vtk_points = vtkw.vtkPoints()
        vtk_points.SetData(cart_points_data_array)

        if create_conn: vtk_cells = vtkw.vtkCellArray()
        if msk is not None:
            nfilter_msk = np.zeros((len(lon),))
            override_zero = list()

            point_to_cells = defaultdict(set)
            for cell_idx in range(num_entries):
                for point_idx in corner_indices[:, cell_idx]:
                    point_to_cells[point_idx].add(cell_idx)

        for i in range(num_entries):
            # first filter out duplicates, some cells are malformed
            indices = corner_indices[:, i]
            indices = np.unique(indices)
            if len(indices) < 3: continue

            # mark cell vertices as valid
            if msk is not None and msk[i] == 0:
                for point_idx in indices:
                    other_cells = point_to_cells[point_idx]
                    mean_msk = np.mean(msk[np.array(list(other_cells))])
                    nfilter_msk[point_idx] = 1.0 - mean_msk # we flip the meaning of 0 and 1
                #nfilter_msk[indices] = 1.0

            # create mesh connectivity
            if create_conn:
                points = cart_points[indices]

                if use_triangulation:
                    _, tri_indices = triangulate(points, indices) # first triangulate
                    for idx_tri in range(tri_indices.shape[0]): # now handle each tri
                        # filter out bad cells from torc mesh
                        if var == ncw.NCVars.TORC and use_torc_fix:
                            TORC_THRESHOLD = 1e+6
                            p1 = cart_points[tri_indices[idx_tri][0]]
                            p2 = cart_points[tri_indices[idx_tri][1]]
                            p3 = cart_points[tri_indices[idx_tri][2]]
                            l1 = np.linalg.norm(p1 - p2)
                            l2 = np.linalg.norm(p2 - p3)
                            l3 = np.linalg.norm(p3 - p1)
                            if l1 > TORC_THRESHOLD or l2 > TORC_THRESHOLD or l3 > TORC_THRESHOLD:
                                if msk is not None:
                                    override_zero.append(tri_indices[idx_tri][0])
                                    override_zero.append(tri_indices[idx_tri][1])
                                    override_zero.append(tri_indices[idx_tri][2])
                                continue

                        tri = vtkw.vtkTriangle()
                        tri.GetPointIds().SetId(0, tri_indices[idx_tri][0])
                        tri.GetPointIds().SetId(1, tri_indices[idx_tri][1])
                        tri.GetPointIds().SetId(2, tri_indices[idx_tri][2])
                        vtk_cells.InsertNextCell(tri)
                else:
                    # first sort points based on rotation around normal, then setup polygon
                    e1, e2 = compute_plane_basis(points)
                    normal = compute_normal(points, e1, e2)
                    _, sorted_indices = sort_counterclockwise(points, indices, normal)

                    poly = vtkw.vtkPolygon()
                    poly.GetPointIds().SetNumberOfIds(len(sorted_indices))
                    for i, idx in enumerate(sorted_indices):
                        poly.GetPointIds().SetId(i, idx)
                    vtk_cells.InsertNextCell(poly)

        # general torc fix that fills in the hole in the south-pole
        if var == ncw.NCVars.TORC and use_torc_fix and create_conn and use_triangulation:
            total_indices = np.arange(len(cart_points))
            low_indices = total_indices[cart_points[:, 2] <= -6215000]
            _, tris = triangulate(cart_points[low_indices], low_indices)
            for idx_tri in range(tris.shape[0]):
                tri = vtkw.vtkTriangle()
                tri.GetPointIds().SetId(0, tris[idx_tri][0])
                tri.GetPointIds().SetId(1, tris[idx_tri][1])
                tri.GetPointIds().SetId(2, tris[idx_tri][2])
                vtk_cells.InsertNextCell(tri)

            if msk is not None:
                tmp = np.zeros((len(cart_points),))
                tmp[0:-1] = nfilter_msk
                nfilter_msk = tmp
                nfilter_msk[low_indices] = 0.0

                nfilter_msk[np.array(list(set(override_zero)))] = 0.0

        unstructured_grid = vtkw.vtkUnstructuredGrid()
        unstructured_grid.SetPoints(vtk_points)
        if create_conn: unstructured_grid.SetCells(vtkw.VTK_TRIANGLE if use_triangulation else vtkw.VTK_POLYGON, vtk_cells)

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

    def _nc2vtk_corner(self, var:ncw.NCVars, use_filter:bool, use_torc_fix:bool=True, use_triangulation:bool=True):
        """
        Extracts coner based mesh
        :param var: active variable
        :param use_filter: should we already filter out points? (only possible for SEA meshes)
        :return:
        """
        clo = self.nc_input.var_clo_data(var)
        cla = self.nc_input.var_cla_data(var)
        msk = self.msk_input.var_msk_data(var).flatten() if self.msk_input is not None else None
        lon, lat, num_entries, corner_indices = NC2VTK.process_corner_data(clo, cla, msk, use_filter)
        return NC2VTK.generate_corner_u_grid(lon, lat, num_entries, corner_indices, var, msk, use_filter, True, use_torc_fix, use_triangulation)
