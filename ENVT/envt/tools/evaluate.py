import numpy as np

import envt.vtk_util.vtk_wrapper as vtkw
from envt.vtk_util.eval_functions import *
import envt.tools.convert as conv
import vtkmodules.util.numpy_support as vtk_np
import json

class Evaluator(vtkw.VTKInputFile):
    """Evaluates points of this VTK file for a given test function"""

    FUNCTIONS = {"sinusoid" : fun_sinusoid, "harmonic" : fun_harmonic, "vortex" : fun_vortex, "gulfstream" : fun_gulfstream}

    def __init__(self, infile, outfile):
        super().__init__(infile)
        self.outfile = outfile
        """Output file path"""

    @staticmethod
    def integrate_2d(points, evals, areas):
        """
        Computes integral for provided points. Assumes that around point i is a cell of size areas[i] and has
        a function value of evals[i]
        :param points: cell centers
        :param evals: function evaluations
        :param areas: cell areas
        :return: surface integral
        """
        integral = np.sum(evals * areas)
        return integral

    def evaluate(self, fun_name):
        """
        Evaluates this VTK file for the given test function and writes result to file
        :param fun_name: test function name
        :return:
        """
        np_points = vtk_np.vtk_to_numpy(self.input_points.GetData())
        np_points_eval = Evaluator.FUNCTIONS[fun_name](np_points)
        output_point_data = vtk_np.numpy_to_vtk(np_points_eval, deep=True)
        output_point_data.SetName("eval")
        self.input_point_data.AddArray(output_point_data)

        vtkw.VTKOutputFile(self.outfile, self.input_grid).write()

    def evaluate_diff(self, source_mesh_file, fun_name, out_vtk, use_gulfstream_filter=False):
        """
        Evaluates the error of this VTK file with respect to another source mesh file after mapping.
        Results and errors are written to files.
        :param source_mesh_file: Respective source mesh file
        :param fun_name: Used function name
        :param out_vtk: output VTK file path
        :param use_gulfstream_filter: should we apply special filtering for the gulfstream case?
        :return:
        """
        np_points = vtk_np.vtk_to_numpy(self.input_points.GetData())
        mesh_points_tgt = np_points
        ana_point_data_tgt = Evaluator.FUNCTIONS[fun_name](np_points)

        map_point_data = None
        map_point_data_cell = None
        if self.input_point_data:
            for i in range(self.input_point_data.GetNumberOfArrays()):
                array = self.input_point_data.GetArray(i)
                if array.GetName() == "eval":
                    map_point_data = vtk_np.vtk_to_numpy(array)
                if array.GetName() == "area":
                    map_point_data_cell = vtk_np.vtk_to_numpy(array)

        if map_point_data is None or map_point_data_cell is None:
            print("No eval/area data in mapped VTK file")
            return

        source_mesh = vtkw.VTKInputFile(source_mesh_file)
        source_point_data_cell = None
        for i in range(source_mesh.input_point_data.GetNumberOfArrays()):
            array = source_mesh.input_point_data.GetArray(i)
            if array.GetName() == "area":
                source_point_data_cell = vtk_np.vtk_to_numpy(array)
                break
        if source_point_data_cell is None:
            print("No area data in source VTK file")

        np_points = vtk_np.vtk_to_numpy(source_mesh.input_points.GetData())
        ana_points_data_src = Evaluator.FUNCTIONS[fun_name](np_points)
        mesh_points_src = np_points

        offset = 1e-20
        misfit = np.zeros_like(map_point_data)
        non_zero_mask = np.logical_not(np.isclose(ana_point_data_tgt, 0, atol=1e-3))
        #misfit = (np.abs((map_point_data + offset) - (ana_point_data_tgt + offset)) / np.abs(ana_point_data_tgt + offset)) - offset
        misfit[non_zero_mask] = np.abs(map_point_data[non_zero_mask] - ana_point_data_tgt[non_zero_mask]) / np.abs(ana_point_data_tgt[non_zero_mask])

        if use_gulfstream_filter:
            gulfstream_weight = np.ones_like(misfit)
            points_3d = conv.Converter.convert_data(conv.Converter.Mode2DTO3D(), mesh_points_tgt[:, 0:2], mesh_points_tgt.shape[0])
            last_pos = points_3d[-1]
            dist_to_center = np.linalg.norm(points_3d - last_pos, axis=1) # dist to filter center
            max_dist = 2.5e+6
            patch_mask = dist_to_center <= max_dist
            gulfstream_weight[patch_mask] = np.power(dist_to_center[patch_mask] / max_dist, 3.0)
            misfit = misfit * gulfstream_weight

        mean_misfit = np.mean(misfit)
        max_misfit = np.max(misfit)
        rms_misfit = np.sqrt(np.mean(misfit * misfit))
        l_min = (np.min(ana_point_data_tgt) - np.min(map_point_data)) / np.max(np.abs(ana_point_data_tgt))
        l_max = (np.max(map_point_data) - np.max(ana_point_data_tgt)) / np.max(np.abs(ana_point_data_tgt))

        int_map = Evaluator.integrate_2d(mesh_points_tgt, map_point_data, map_point_data_cell)
        int_ana_src = Evaluator.integrate_2d(mesh_points_src, ana_points_data_src, source_point_data_cell)
        int_ana_tgt = Evaluator.integrate_2d(mesh_points_tgt, ana_point_data_tgt, map_point_data_cell)
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

        misfit_point_data = vtk_np.numpy_to_vtk(misfit, deep=True)
        misfit_point_data.SetName("error")
        self.input_point_data.AddArray(misfit_point_data)
        vtkw.VTKOutputFile(out_vtk, self.input_grid).write()
