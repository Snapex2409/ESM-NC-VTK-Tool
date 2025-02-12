import envt.vtk_util.vtk_wrapper as vtkw
from envt.vtk_util.eval_functions import *
import vtkmodules.util.numpy_support as vtk_np
import json

class Evaluator(vtkw.VTKInputFile):
    FUNCTIONS = {"sinusoid" : fun_sinusoid, "harmonic" : fun_harmonic, "vortex" : fun_vortex, "gulfstream" : fun_gulfstream}

    def __init__(self, infile, outfile):
        super().__init__(infile)
        self.outfile = outfile

    @staticmethod
    def integrate_2d(points, evals):
        return 1

    def evaluate(self, fun_name):
        np_points = vtk_np.vtk_to_numpy(self.input_points.GetData())
        np_points_eval = Evaluator.FUNCTIONS[fun_name](np_points)
        output_point_data = vtk_np.numpy_to_vtk(np_points_eval, deep=True)
        output_point_data.SetName("eval")
        self.input_point_data.AddArray(output_point_data)

        vtkw.VTKOutputFile(self.outfile, self.input_grid).write()

    def evaluate_diff(self, source_mesh_file, fun_name):
        np_points = vtk_np.vtk_to_numpy(self.input_points.GetData())
        mesh_points_tgt = np_points
        ana_point_data_tgt = Evaluator.FUNCTIONS[fun_name](np_points)

        map_point_data = None
        if self.input_point_data:
            for i in range(self.input_point_data.GetNumberOfArrays()):
                array = self.input_point_data.GetArray(i)
                if array.GetName() == "eval":
                    map_point_data = vtk_np.vtk_to_numpy(array)
                    break

        if map_point_data is None:
            print("No eval data in VTK file")
            return

        source_mesh = vtkw.VTKInputFile(source_mesh_file)
        np_points = vtk_np.vtk_to_numpy(source_mesh.input_points.GetData())
        ana_points_data_src = Evaluator.FUNCTIONS[fun_name](np_points)
        mesh_points_src = np_points

        offset = 1e-20
        misfit = (np.abs((map_point_data + offset) - (ana_point_data_tgt + offset)) / np.abs(
            ana_point_data_tgt + offset)) - offset
        mean_misfit = np.mean(misfit)
        max_misfit = np.max(misfit)
        rms_misfit = np.sqrt(np.mean(misfit * misfit))
        l_min = (np.min(ana_point_data_tgt) - np.min(map_point_data)) / np.max(np.abs(ana_point_data_tgt))
        l_max = (np.max(map_point_data) - np.max(ana_point_data_tgt)) / np.max(np.abs(ana_point_data_tgt))

        int_map = Evaluator.integrate_2d(mesh_points_tgt, map_point_data)
        int_ana_src = Evaluator.integrate_2d(mesh_points_src, ana_points_data_src)
        int_ana_tgt = Evaluator.integrate_2d(mesh_points_tgt, ana_point_data_tgt)
        glob_cons_src = np.abs(int_map - int_ana_src) / np.abs(int_ana_src)
        glob_cons_tgt = np.abs(int_map - int_ana_tgt) / np.abs(int_ana_tgt)

        metrics = {
            "mean_misfit": mean_misfit,
            "max_misfit": max_misfit,
            "rms_misfit": rms_misfit,
            "l_min": l_min,
            "l_max": l_max,
            "glob_cons_src": glob_cons_src,
            "glob_cons_tgt": glob_cons_tgt
        }

        with open(self.outfile, 'w') as file:
            json.dump(metrics, file, indent=4)