#!/bin/bash
source ../vars.sh

mkdir -p "$DS5/geod"
# Convert to 2D
for varA in "${SEA_VARS[@]}"; do
    for varB in "${ATM_VARS[@]}"; do
        for fun in "${FUNCTIONS[@]}"; do
            echo "    [06] Converting $varA on $varB with $fun to 2D"
            input_file="$DS5/cart/${varB}_masked_by_${varA}_${fun}.vtk"
            output_file="$DS5/geod/${varB}_masked_by_${varA}_${fun}.vtk"
            #envt vtkc "$input_file" --output "$output_file" -cv32
        done
    done
done

mkdir -p "$DS6"
# Compute metrics on 2D meshes
for varA in "${SEA_VARS[@]}"; do
    for varB in "${ATM_VARS[@]}"; do
        for fun in "${FUNCTIONS[@]}"; do
            echo "    [06] Computing metrics for $varA on $varB with $fun"
            mapped_file="$DS5/geod/${varB}_masked_by_${varA}_${fun}.vtk"
            src_file="$DS3/geod/${varA}.vtk"
            output_file="$DS6/${varB}_masked_by_${varA}_${fun}.txt"
            envt vtke "$mapped_file" --output "$output_file" --source "$src_file" -f "$fun" --diff
        done
    done
done