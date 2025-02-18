#!/bin/bash

OPWD=`pwd`
cd ../..
NPWD=`pwd`

# Output directory
OUT="$NPWD/benchmark"
# Data directory
NC_DIR="$NPWD/data"
# NC Mesh File
NC_MESH="${NC_DIR}/bench_grids.nc"
# NC Mask File
NC_MASK="${NC_DIR}/bench_masks_ocea_not_atm.nc"

# directories for data of each step
DS1="${OUT}/01_corner_meshes"
DS2="${OUT}/02_masks"
DS3="${OUT}/03_center_meshes"
DS4="${OUT}/04_evaluated_meshes"
DS5="${OUT}/05_mapped_meshes"
DS6="${OUT}/06_metrics"


SEA_VARS=("nogt" "torc")
ATM_VARS=("bggd" "icoh" "icos" "sse7" "ssea")
FUNCTIONS=("sinusoid" "harmonic" "vortex" "gulfstream")

cd $OPWD