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
    """
    Represents an input VTK file, automatically loads file and extracts relevant aspects
    """
    def __init__(self, filename):
        self.infile = filename
        """Path to VTK file"""
        reader = vtkUnstructuredGridReader()
        reader.SetFileName(filename)
        reader.Update()
        self.input_grid = reader.GetOutput()
        """VTK Grid"""
        # Extract points from the grid
        self.input_points = self.input_grid.GetPoints()
        """Grid Points"""
        self.input_point_data = self.input_grid.GetPointData()
        """Point Data Arrays"""
        self.input_num_points = self.input_points.GetNumberOfPoints()
        """Number of Points"""

class VTKOutputFile:
    """
    Represents an output VTK file, writes file on calling write
    """
    def __init__(self, filename, grid):
        self.outfile = filename
        """Path to VTK file"""
        self.grid = grid
        """VTK Grid"""

    def write(self):
        writer = vtkUnstructuredGridWriter()
        writer.SetFileName(self.outfile)
        writer.SetInputData(self.grid)
        writer.SetFileTypeToASCII()
        writer.Write()