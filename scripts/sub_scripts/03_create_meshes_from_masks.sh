#!/bin/bash
source ../vars.sh

mkdir -p "$DS3/cart"

for varA in "${SEA_VARS[@]}"; do
    for varB in "${ATM_VARS[@]}"; do
        echo "    [03] Filtering $varB on $varA"
        input_file="$DS2/cart/${varB}_masked_by_${varA}.vtk"
        output_file="$DS3/cart/${varB}_masked_by_${varA}.vtk"
        msk_file="$DS2/cart/${varA}.vtk"
        envt vtkf "$input_file" $NC_MESH $varB --output "$output_file" --water --connect --threshold $THRESHOLD --fraction "$msk_file" --fvar $varA
    done
done


# extract center point sea meshes
for var in "${SEA_VARS[@]}"; do
    echo "    [03] Filtering $var"
    input_file="$DS2/cart/${var}.vtk"
    output_file="$DS3/cart/${var}.vtk"
    envt vtkf "$input_file" $NC_MESH $var --output "$output_file" --water --connect --threshold $THRESHOLD --fraction "$input_file" --fvar $var
done