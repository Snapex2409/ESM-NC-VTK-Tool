import envt.nc_util.nc_wrapper as ncw
import envt.vtk_util.vtk_wrapper as vtkw
from envt.tools.convert import Converter as cv
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

    def _nc2vtk_corner(self, var:ncw.NCVars, use_filter:bool):
        clo = self.nc_input.var_clo_data(var)
        cla = self.nc_input.var_cla_data(var)
        msk = self.msk_input.var_msk_data(var).flatten() if self.msk_input is not None else None

        dims = clo.shape[0]
        clo = np.array([clo[i, :, :].flatten() for i in range(dims)])
        cla = np.array([cla[i, :, :].flatten() for i in range(dims)])
        clo_cla_points = np.array([np.column_stack((clo[i, :], cla[i, :])) for i in range(dims)])
        if use_filter and msk is not None: clo_cla_points = clo_cla_points[:, msk == 0, :]
        unique_points = np.unique(clo_cla_points.reshape((-1, 2)), axis=0)

        lon = unique_points[:, 0]
        lat = unique_points[:, 1]
        num_entries = clo_cla_points.shape[1]
        coord_2_unique_idx = {tuple(point): idx for idx, point in enumerate(unique_points)}

        corner_coords = clo_cla_points
        corner_indices = np.array([[coord_2_unique_idx[tuple(point)] for point in corner_coords[i, :, :]] for i in range(dims)])

        cart_points = cv.convert_data_arrays(cv.Mode2DTO3D(), lon, lat, np.zeros((len(lon),)))
        cart_points_data_array = vtk_np.numpy_to_vtk(cart_points, deep=True)

        vtk_points = vtkw.vtkPoints()
        vtk_points.SetData(cart_points_data_array)

        vtk_cells = vtkw.vtkCellArray()
        for i in range(num_entries):
            if dims == 4:
                idx0, idx1, idx2, idx3 = corner_indices[0, i], corner_indices[1, i], corner_indices[2, i], \
                corner_indices[3, i]
                quad = vtkw.vtkQuad()
                quad.GetPointIds().SetId(0, idx0)
                quad.GetPointIds().SetId(1, idx1)
                quad.GetPointIds().SetId(2, idx2)
                quad.GetPointIds().SetId(3, idx3)

                vtk_cells.InsertNextCell(quad)
            else:
                # triangulate points
                # first filter out duplicates
                indices = corner_indices[:, i]
                indices = np.unique(indices)
                poly = vtkw.vtkPolygon()
                poly.GetPointIds().SetNumberOfIds(len(indices))
                for pos, idx in enumerate(indices):
                    poly.GetPointIds().SetId(pos, idx)
                vtk_cells.InsertNextCell(poly)

        unstructured_grid = vtkw.vtkUnstructuredGrid()
        unstructured_grid.SetPoints(vtk_points)
        unstructured_grid.SetCells(vtkw.VTK_QUAD if dims == 4 else vtkw.VTK_POLYGON, vtk_cells)

        if msk is not None:
            if use_filter:
                vtk_point_data = vtk_np.numpy_to_vtk(np.ones((cart_points.shape[0],)).astype(np.float32), deep=True)
                vtk_point_data.SetName("mask")  # Set the name of the point data
                unstructured_grid.GetPointData().AddArray(vtk_point_data)
            else:
                cell_data = vtkw.vtkFloatArray()
                cell_data.SetName("mask")
                cell_data.SetNumberOfValues(1)
                mask_data_data_array = vtk_np.numpy_to_vtk(msk.astype(np.float32), deep=True)
                cell_data.DeepCopy(mask_data_data_array)
                unstructured_grid.GetCellData().SetScalars(cell_data)

        return unstructured_grid
