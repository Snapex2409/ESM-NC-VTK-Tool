import numpy as np
import vtkmodules.util.numpy_support as vtk_np
from pyproj import Proj, transform
import envt.vtk_util.vtk_wrapper as vtkw
from typing import Type, Union
import warnings

class Converter(vtkw.VTKInputFile):
    """Provides coordinate conversion functionality for VTK files"""

    class Mode:
        """Conversion mode interface, check_data will be called prior to conversion"""
        def __init__(self):
            self.src_proj = None
            """Source Proj data representation"""
            self.dst_proj = None
            """Destination Proj data representation"""

        def src_crs(self) -> Proj: return self.src_proj

        def dst_crs(self) -> Proj: return self.dst_proj

        def check_data(self, d0, d1, d2): pass

    class Mode2DTO3D(Mode):
        """Converter from 2D geodesic to 3D cartesian"""
        def __init__(self):
            super().__init__()
            self.src_proj = Proj(proj="latlong", datum="WGS84")
            self.dst_proj = Proj(proj="geocent", datum="WGS84")

        def check_data(self, lon, lat, _):
            lon[lon > 180] -= 360
            lon[lon < -180] += 360

    class Mode3DTO2D(Mode):
        """Converter from 3D cartesian to 2D geodesic"""
        def __init__(self):
            super().__init__()
            self.src_proj = Proj(proj="geocent", datum="WGS84")
            self.dst_proj = Proj(proj="latlong", datum="WGS84")

    class ModeManual(Mode):
        """Converter for manual targets"""
        def __init__(self, src_proj, dst_proj):
            super().__init__()
            self.src_proj = src_proj
            self.dst_proj = dst_proj

    def __init__(self, infile, outfile):
        super().__init__(infile)
        self.outfile = outfile
        """Output file name"""

    @staticmethod
    def convert_data_arrays(mode:Union[Mode2DTO3D, Mode3DTO2D, ModeManual], in_arr_d0, in_arr_d1, in_arr_d2):
        """
        Applies provided transformation on specified data arrays
        :param mode: transformation mode
        :param in_arr_d0: data array dimension 0
        :param in_arr_d1: data array dimension 1
        :param in_arr_d2: data array dimension 2
        :return: converted data arrays (stacked)
        """
        mode.check_data(in_arr_d0, in_arr_d1, in_arr_d2)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=FutureWarning)
            out_arr_d0, out_arr_d1, out_arr_d2 = transform(mode.src_crs(), mode.dst_crs(), in_arr_d0, in_arr_d1, in_arr_d2)
        np_out_array = np.column_stack((out_arr_d0, out_arr_d1, out_arr_d2))
        return np_out_array

    @staticmethod
    def convert_data(mode:Union[Mode2DTO3D, Mode3DTO2D, ModeManual], input_array, num_points):
        """
        Applies provided transformation on specified stacked data array. Will extend input data to 3 dimensions with zeros.
        Will always return 3-dimensional output.
        :param mode: transformation mode
        :param input_array: stacked data array
        :param num_points: number of points in input_array
        :return: converted data arrays (stacked)
        """
        zeros = np.zeros((num_points, 1))
        in_arr_d0, in_arr_d1, in_arr_d2 = zeros, zeros, zeros
        if input_array.shape[1] >= 1: in_arr_d0 = input_array[:, 0]
        if input_array.shape[1] >= 2: in_arr_d1 = input_array[:, 1]
        if input_array.shape[1] >= 3: in_arr_d2 = input_array[:, 2]

        return Converter.convert_data_arrays(mode, in_arr_d0, in_arr_d1, in_arr_d2)

    def convert(self, mode:Union[Mode2DTO3D, Mode3DTO2D, ModeManual], attach:bool):
        """
        Applies target conversion on the loaded VTK file.
        :param mode: transformation mode
        :param attach: should connectivity be attached?
        :return:
        """
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

        if attach:
            output_unstructured_grid.SetCells(vtkw.VTK_TRIANGLE, self.input_grid.GetCells())

        # Write the new 3D VTK unstructured grid to a file
        vtkw.VTKOutputFile(self.outfile, output_unstructured_grid).write()
