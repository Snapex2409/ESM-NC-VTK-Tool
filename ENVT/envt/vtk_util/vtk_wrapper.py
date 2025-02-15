import vtk
import vtkmodules.util.numpy_support as vtk_np

VTK_QUAD = vtk.VTK_QUAD
VTK_POLYGON = vtk.VTK_POLYGON
VTK_TRIANGLE = vtk.VTK_TRIANGLE

def vtkUnstructuredGridReader(): return vtk.vtkUnstructuredGridReader()
def vtkUnstructuredGridWriter(): return vtk.vtkUnstructuredGridWriter()
def vtkPoints(): return vtk.vtkPoints()
def vtkUnstructuredGrid(): return vtk.vtkUnstructuredGrid()
def vtkCellArray(): return vtk.vtkCellArray()
def vtkFloatArray(): return vtk.vtkFloatArray()
def vtkQuad(): return vtk.vtkQuad()
def vtkPolygon(): return vtk.vtkPolygon()
def vtkTriangle():return vtk.vtkTriangle()

class VTKInputFile:
    def __init__(self, filename):
        self.infile = filename
        reader = vtkUnstructuredGridReader()
        reader.SetFileName(filename)
        reader.Update()
        self.input_grid = reader.GetOutput()

        # Extract points from the grid
        self.input_points = self.input_grid.GetPoints()
        self.input_point_data = self.input_grid.GetPointData()
        self.input_num_points = self.input_points.GetNumberOfPoints()

class VTKOutputFile:
    def __init__(self, filename, grid):
        self.outfile = filename
        self.grid = grid

    def write(self):
        writer = vtkUnstructuredGridWriter()
        writer.SetFileName(self.outfile)
        writer.SetInputData(self.grid)
        writer.SetFileTypeToASCII()
        writer.Write()