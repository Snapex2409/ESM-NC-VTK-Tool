import envt.vtk_util.vtk_wrapper as vtkw
import numpy as np
import vtkmodules.util.numpy_support as vtk_np

class Filter:
    def __init__(self, input_file):
        self.vtk_file = vtkw.VTKInputFile(input_file)

    def apply(self, output_file, threshold=0.001, denotes_water=False):
        np_points = vtk_np.vtk_to_numpy(self.vtk_file.input_points.GetData())

        np_mask_data = None
        for i in range(self.vtk_file.input_point_data.GetNumberOfArrays()):
            array = self.vtk_file.input_point_data.GetArray(i)
            if array.GetName() == "mask":
                np_mask_data = vtk_np.vtk_to_numpy(array)
                break

        if np_mask_data is None:
            print("WARNING: No mask data available")
            return

        valid_points = None
        if denotes_water:
            valid_points = np_mask_data > threshold
        else:
            ones = np.ones_like(np_mask_data)
            land_amount = np.minimum(ones, np_mask_data)
            water_amount = ones - land_amount
            valid_points = water_amount > threshold

        out_grid = vtkw.vtkUnstructuredGrid()
        np_points = np_points[valid_points]
        out_points = vtkw.vtkPoints()
        out_points.SetData(vtk_np.numpy_to_vtk(np_points))
        out_grid.SetPoints(out_points)

        out_point_data = out_grid.GetPointData()
        for i in range(self.vtk_file.input_point_data.GetNumberOfArrays()):
            array = self.vtk_file.input_point_data.GetArray(i)
            np_array = vtk_np.vtk_to_numpy(array)
            np_array = np_array[valid_points]
            out_array = vtk_np.numpy_to_vtk(np_array)
            out_array.SetName(array.GetName())
            out_point_data.AddArray(out_array)

        vtkw.VTKOutputFile(output_file, out_grid).write()
