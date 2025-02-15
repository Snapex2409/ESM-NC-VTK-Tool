# ESM-NC-VTK-Tool (ENVT)
Tool for ESM benchmark providing utility functions for NC and VTK operations.

Original benchmark: https://www.mdpi.com/2297-8747/27/2/31

This tool is used to process data for the steps described in the paper, to run the benchmark using preCICE.
https://precice.org/, https://github.com/precice/precice/tree/develop

Data is provided in the /data folder. As the files are large, they can be accessed using git-lfs.

## Installation

### Requirements

* Python Version >= 3.9
* Modules: TODO

### Steps

* clone repository
* `cd ENVT && pip install .`
* run with `envt <mode> <args>`

### Data

Provided NC files contain meshes and masks. There are the following meshes:
* bggd
* icoh
* icos
* nogt
* sse7
* ssea
* torc

The mesh NC file has fields `<var_name>.lon` `<var_name>.lat` `<var_name>.clo` `<var_name>.cla`.
All fields describe coordinates in geodesic coordinate system. Meshes are discretized by many cells.
lon/lat fields contain center points of cells, while clo/cla fields contain corner points of cells.

## Program Modes

#### View

Provides an overview of provided NC files.

`envt view <file.nc> [--data var]`, var can be bggd.lon

#### Plot

Plot provided data into a png file.

`envt plot <file.nc> --var <var> [--mask <mask.nc>] [--output <output.png>]`

#### VTK

Creates a VTK file from NC data. Output will be in 3D cartesian coordinate system.

`envt vtk <file.nc> --var <var> [--corner] [--mask <mask.nc>] [--output <output.vtk>] [--filter]`
* specifying --corner creates a mesh based on cell corners containing connectivity information
* specifying --mask attaches mask data to output
* specifying --filter filters out all cells containing 0 as mask data, mask must be provided

#### VTKC

Converts VTK data between cartesian and geodesic coordinate systems.

`envt vtkc <file.vtk> (--conv23|--conv32) [--output <output.vtk>]`

#### VTKE

Evaluates the given mesh using the selected predefined test function. Test function as described in original benchmarking paper.

`envt vtke <file.vtk> --function <fun> [--output <output.vtk>] [--diff --source <original_mesh.vtk>]`

* Options for `<fun>` are: sinusoid, harmonic, vortex, golfstream
* specifying diff creates statistics and compares the mesh after mapping to the original mesh

#### VTKF

Filters the mesh defined by center points based on the mapped mask defined by its corner points. Also attaches cell sizes to each point.

`envt vtkf <file.vtk> <file.nc> <var> [--output <output.vtk>] --water`

* specifying --water inverts the treatment of the mask values

