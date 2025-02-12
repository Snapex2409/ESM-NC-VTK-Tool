import numpy as np
import vtkmodules.util.numpy_support as vtk_np
from pyproj import Proj, transform
import envt.vtk_util.vtk_wrapper as vtkw
from typing import Type

class Converter(vtkw.VTKInputFile):
    class Mode:
        def __init__(self):
            self.src_crs = None
            self.dst_crs = None

    class Mode2DTO3D(Mode):
        def __init__(self):
            super().__init__()
            self.src_crs = Proj(proj="latlong", datum="WGS84")
            self.dst_crs = Proj(proj="geocent", datum="WGS84")

    class Mode3DTO2D(Mode):
        def __init__(self):
            super().__init__()
            self.src_crs = Proj(proj="geocent", datum="WGS84")
            self.dst_crs = Proj(proj="latlong", datum="WGS84")

    class ModeManual(Mode):
        def __init__(self, src_proj, dst_proj):
            super().__init__()
            self.src_crs = src_proj
            self.dst_crs = dst_proj

    def __init__(self, infile, outfile):
        super().__init__(infile)
        self.outfile = outfile

    @staticmethod
    def convert_data_arrays(mode:Type[Mode], in_arr_d0, in_arr_d1, in_arr_d2, num_points):
        out_arr_d0, out_arr_d1, out_arr_d2 = transform(mode.src_crs, mode.dst_crs, in_arr_d0, in_arr_d1, in_arr_d2)
        np_out_array = np.column_stack((out_arr_d0, out_arr_d1, out_arr_d2))
        return np_out_array

    @staticmethod
    def convert_data(mode:Type[Mode], input_array, num_points):
        zeros = np.zeros((num_points, 1))
        in_arr_d0, in_arr_d1, in_arr_d2 = zeros, zeros, zeros
        if input_array.shape[1] >= 1: in_arr_d0 = input_array[:, 0]
        if input_array.shape[1] >= 2: in_arr_d1 = input_array[:, 1]
        if input_array.shape[1] >= 3: in_arr_d2 = input_array[:, 2]

        return Converter.convert_data_arrays(mode, in_arr_d0, in_arr_d1, in_arr_d2, num_points)

    def convert(self, mode:Type[Mode]):
        np_point_array = np.array([self.input_points.GetPoint(i) for i in range(self.input_num_points)])
        np_out_array = Converter.convert_data(mode, np_point_array, self.input_num_points)
        out_points_data_array = vtk_np.numpy_to_vtk(np_out_array, deep=True)

        output_points = vtkw.vtkPoints()
        output_points.SetData(out_points_data_array)

        # Assign the transformed points to a new unstructured grid
        output_unstructured_grid = vtkw.vtkUnstructuredGrid()
        output_unstructured_grid.SetPoints(output_points)

        # Copy the cells (topology) from the original grid to the new one
        if self.input_point_data:
            output_point_data = output_unstructured_grid.GetPointData()
            for i in range(self.input_point_data.GetNumberOfArrays()):
                array = self.input_point_data.GetArray(i)
                output_point_data.AddArray(array)

        # Write the new 3D VTK unstructured grid to a file
        vtkw.VTKOutputFile(self.outfile, output_unstructured_grid).write()
