# Detailed instructions to reproduce results

### Important notes
The script computes natively all possible mapping pairs. However, in the discussion of the results only a subset of mappings are considered.
To reduce compute time one can remove the "icoh" mesh from the ATM meshes. This can be changed in [scripts/vars.sh](./scripts/vars.sh)
* Change: ATM_VARS=("bggd" "icoh" "icos" "sse7") To: ATM_VARS=("bggd" "icos" "sse7")

All test function were translated from Fortran from the reference paper to python code. Semantics were mostly not altered.
Only for the gulfstream test function an offset of 1 was added to avoid division by 0.

### Consistent Mapping Results
For consistent results no further changes to [scripts/vars.sh](./scripts/vars.sh) are necessary. The scripts in [scripts/sub_scripts](./scripts/sub_scripts) can be execute
in ascending order.

### Scaled-Consistent (approx. conservative) Results
In order to change to scaled-consistent mappings the "mapping" fields in the preCICE configs, must be replaced by the commented out version.
This must be done in the following files:

* [scripts/precice-configs/precice-config-mesh-nn.xml](./scripts/precice-configs/precice-config-mesh-nn.xml)
* [scripts/precice-configs/precice-config-mesh-np.xml](./scripts/precice-configs/precice-config-mesh-np.xml)
* [scripts/precice-configs/precice-config-mesh-rbf.xml](./scripts/precice-configs/precice-config-mesh-rbf.xml)

In order to avoid overriding any previous results, it is advisable to change the required output paths in [scripts/vars.sh](./scripts/vars.sh).

* Change: DS5="\${OUT}/05_mapped_meshes/\$RES" To: DS5="\${OUT}/05_mapped_meshes_cons/\$RES"
* Change: DS6="\${OUT}/06_metrics/\$RES" To: DS6="\${OUT}/06_metrics_cons/\$RES"

Afterwards, only the scripts 
[scripts/sub_scripts/05_map_meshes.sh](./scripts/sub_scripts/05_map_meshes.sh)
[scripts/sub_scripts/06_compute_metrics.sh](./scripts/sub_scripts/06_compute_metrics.sh)
need to be executed.

### Using malformed torc mesh
To disable the fixes applied to the torc mesh, only one variable in [scripts/vars.sh](./scripts/vars.sh) needs to be changed.
* Change: BAD_TORC=0 To: BAD_TORC=1 

Afterwards, the entire pipeline needs to be recomputed.