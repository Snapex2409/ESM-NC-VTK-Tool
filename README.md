# ESM-NC-VTK-Tool (ENVT)
Tool for ESM benchmark providing utility functions for NC and VTK operations.

Original benchmark: https://www.mdpi.com/2297-8747/27/2/31

This tool is used to process data for the steps described in the paper, to run the benchmark using preCICE.
https://precice.org/, https://github.com/precice/precice/tree/develop

Data is provided in the /data folder. As the files are large, they can be accessed using git-lfs.

## Installation

### Requirements
* Due to module issues we only support the following anaconda environment.
* Python Version == 3.9.20
* Modules: see  [ENVT/requirements.yml](./ENVT/requirements.yml)
* Create env with: `conda env create -f ./ENVT/requirements.yml`

### Steps

* clone repository
* `cd ENVT && pip install .`
* run with `envt <mode> <args>`

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

## Data 

Provided NC files contain meshes and masks. There are the following meshes:
* bggd (cells: 20.592)
* icoh (cells: 2.016.012)
* icos (cells: 15.212)
* nogt (cells: 106.428)
* sse7 (cells: 24.572)
* ssea (cells: 24.572)
* torc (cells: 27.118)

The mesh NC file has fields `<var_name>.lon` `<var_name>.lat` `<var_name>.clo` `<var_name>.cla`.
All fields describe coordinates in geodesic coordinate system. Meshes are discretized by many cells.
lon/lat fields contain center points of cells, while clo/cla fields contain corner points of cells.

As a general categorization, the meshes are split into 2 groups. 

SEA-MESHES: torc, nogt

ATM-MESHES: bggd, icoh, icos, sse7, ssea

## Benchmark

The process used here to reproduce the papers benchmark results is split into 6 steps. 
1. Corner based meshes are extracted from the NC files. For SEA meshes land masks are available, thus they are attached to the VTK meshes. At this stage all meshes still contain all non duplicated points. No further filtering in terms of land masks was performed. Point data is currently 3D cartesian.
2. Mask information of SEA meshes is mapped in a preliminary step to the ATM meshes. This is performed using preCICE (`precice-aste-run`).
3. As mask information is now available for all meshes, center based meshes are extracted while filtering out non-unique points and points of masked out cells.
4. The resulting meshes only contain points in sea regions. At this point the test functions can be applied. However, as those require the points to be in 2D geodesic coordinate system, all VTK files are first converted from 3D to 2D. After the evaluation of the test function the resulting VTK meshes are converted back from 2D geodesic to 3D cartesian coordinate system.
5. All evaluated meshes are mapped to all other meshes (not containing evaluation data). This is performed using preCICE (`precice-aste-run`). Three different mapping methods are used: neaerest-neighbour, nearest-projection and Radial Basis Function
6. Finally, metrics in terms of mapping error are computed for all mapping pairs. Errors are also attached to meshes. Since the error computation requires the analytical solution, all meshes are converted to 2D geodesic and afterward back to 3D.

This process can be executed via the scripts located in /scripts. /scripts/run.sh will execute the entire process. Beware, this will generate > 100GB of files.

For finer control, each step can be executed individually in the /scripts/subscripts folder. As those scripts expect to be run from within the sub_scripts folder, one should cd into said location.

The behaviour of these scripts can be controlled via the /scripts/vars.sh file.

### Requirements

* working installation of preCICE and preCICE-ASTE
* locally installed version of ENVT (i.e. using pip install)