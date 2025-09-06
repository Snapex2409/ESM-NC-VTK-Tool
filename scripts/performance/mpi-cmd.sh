#!/bin/bash

pA="$1"
MPI_ARGS_A="$2"
input_fileA="$3"

pB="$4"
MPI_ARGS_B="$5"
input_fileB="$6"
output_file="$7"

# launch task
#export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH
mpirun -n "$pA" $MPI_ARGS_A precice-aste-run -v -a -p A --mesh "$input_fileA" --data "eval" &
pidA=$!
mpirun -n "$pB" $MPI_ARGS_B precice-aste-run -v -a -p B --mesh "$input_fileB" --output "$output_file" --data "eval-mapped" &
pidB=$!

# wait for any of the background tasks to finish
wait -n
status=$?

# if anything failed, exit
if [ $status -ne 0 ]; then
    echo "One MPI job failed, killing both jobs."
    kill $pidA $pidB 2>/dev/null
    exit 0
fi

wait
