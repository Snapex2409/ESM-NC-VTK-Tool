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
RES="TH0_2"
DS1="${OUT}/01_corner_meshes"
DS2="${OUT}/02_masks/${RES}"
DS3="${OUT}/03_center_meshes/${RES}"
DS4="${OUT}/04_evaluated_meshes/${RES}"
DS5="${OUT}/05_mapped_meshes/${RES}"
DS6="${OUT}/06_metrics/${RES}"
DPERF="${OUT}/strong_scaling"


SEA_VARS=("nogt" "torc")
ATM_VARS=("bggd" "icos" "sse7") # excluding icoh for faster computation
FUNCTIONS=("sinusoid" "harmonic" "vortex" "gulfstream")
MAPPINGS=("nn" "np" "rbf")
PARTITIONS=(1 2 4 8)
ITERATIONS=10
MPI_ARGS_A="" # set this up for your local environment
MPI_ARGS_B="" # set this up for your local environment

THRESHOLD=0.2
BAD_TORC=0

cd $OPWD