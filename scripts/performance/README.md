## How to run performance scripts
In the following we assume the root directory of this repository is: `<root>=ESM-NC-VTK-Tool`. 
The main benchmark output directory is: `<bench>=<root>/benchmark`

1. Edit `<root>/scripts/vars.sh` to only contain the desired meshes and the appropriate MPI flags. If no MPI flags are set, then all subsequent preCICE mappings will be executed on the host-machine. The fields `PARTITIONS` and `ITERATIONS` determine in how many partitions meshes should be subdivided und thus also subsequently how many target ranks should be launched and also how often the benchmark should be repeated.
2. Next, execute steps 1 to 4 from `<root>/scripts/sub_scripts/` such that the required base meshes are generated withing the `<bench>` directory.
3. Once this has completed, `<root>/scripts/performance/strong-scaling.sh` can be run. It will perform the performance benchmark using the previously defined configuration
    * preCICE will use the configuration files `<root>/scripts/precice-configs/*-perf-*.xml`. By default, these are setup to use the network interface "eno1". Check with `ip link` if your device has such an interface or rename it to desired one.
    * The file `<root>/scripts/performance/mpi-cmd.sh` is called from `strong-scaling.sh` and contains the actual `mpirun` commands.
4. Afterwards, there should be `profiling.json` and `trace.json` files, located in all `<bench>/strong_scaling/.../it<N>` directories containing the timing information.
5. Extracting and plotting result data can be done with `perf-ana.py`, however, it is currently hard-coded to only consider the bilinear nogt to icos_masked_by_nogt mapping using the vortex test function. As it is fairly short and simple to understand, this should be used as a basis for own data extraction and plotting mechanisms. The functions "load_oasis_result" and "load_result" extract the appropriate fields from the performance files.
    * In order to load oasis results with this script, oasis results should be placed in the following format: `<bench>/strong_scaling_oasis/RUNDIR_YAC_A/regrid_environment_nogt_icos_bili_vortex_1_<n>_1_YAC_A/it<i>/model1.timers_0000`
    * For instructions on how to run OASIS-YAC, refer to their documentation.