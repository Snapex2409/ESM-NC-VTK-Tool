#!/bin/bash
source ../vars.sh

mkdir -p "$DS3/geod"
mkdir -p "$DS4/geod"
mkdir -p "$DS4/cart"

# map to 2D
for varA in "${SEA_VARS[@]}"; do
    echo "    [04] Converting $varA to 2D"
    input_file="$DS3/cart/${varA}.vtk"
    output_file="$DS3/geod/${varA}.vtk"
    envt vtkc "$input_file" --output "$output_file" -cv32 --attach
done
for varA in "${SEA_VARS[@]}"; do
    for varB in "${ATM_VARS[@]}"; do
        echo "    [04] Converting ${varB}_masked_by_${varA} to 2D"
        input_file="$DS3/cart/${varB}_masked_by_${varA}.vtk"
        output_file="$DS3/geod/${varB}_masked_by_${varA}.vtk"
        envt vtkc "$input_file" --output "$output_file" -cv32 --attach
    done
done

# eval on 2D mesh
for varA in "${SEA_VARS[@]}"; do
    for fun in "${FUNCTIONS[@]}"; do
        echo "    [04] Evaluating $varA with $fun"
        input_file="$DS3/geod/${varA}.vtk"
        output_file="$DS4/geod/${varA}_${fun}.vtk"
        envt vtke "$input_file" --output "$output_file" -f "$fun"
    done
done
for varA in "${SEA_VARS[@]}"; do
    for varB in "${ATM_VARS[@]}"; do
        for fun in "${FUNCTIONS[@]}"; do
            echo "    [04] Evaluating ${varB}_masked_by_${varA} with $fun"
            input_file="$DS3/geod/${varB}_masked_by_${varA}.vtk"
            output_file="$DS4/geod/${varB}_masked_by_${varA}_${fun}.vtk"
            envt vtke "$input_file" --output "$output_file" -f "$fun"
        done
    done
done

# map back to 3D
for varA in "${SEA_VARS[@]}"; do
    for fun in "${FUNCTIONS[@]}"; do
        echo "    [04] Converting $varA with $fun to 3D"
        input_file="$DS4/geod/${varA}_${fun}.vtk"
        output_file="$DS4/cart/${varA}_${fun}.vtk"
        envt vtkc "$input_file" --output "$output_file" -cv23 --attach
    done
done
for varA in "${SEA_VARS[@]}"; do
    for varB in "${ATM_VARS[@]}"; do
        for fun in "${FUNCTIONS[@]}"; do
            echo "    [04] Converting ${varB}_masked_by_${varA} with $fun to 3D"
            input_file="$DS4/geod/${varB}_masked_by_${varA}_${fun}.vtk"
            output_file="$DS4/cart/${varB}_masked_by_${varA}_${fun}.vtk"
            envt vtkc "$input_file" --output "$output_file" -cv23 --attach
        done
    done
done