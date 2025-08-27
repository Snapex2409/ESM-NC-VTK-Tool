#!/bin/bash
source ../vars.sh

# Setting up tmp work dir

rm -rf "./tmp"
mkdir -p "./tmp"
cd "./tmp"

cp ../../precice-configs/precice-config-mask.xml ./precice-config.xml

# Process each file with each function
mkdir -p "$DS2/cart"
for varA in "${SEA_VARS[@]}"; do
    for varB in "${ATM_VARS[@]}"; do
        input_fileA="$DS1/cart/${varA}"
        input_fileB="$DS1/cart/${varB}"
        output_file="$DS2/cart/${varB}_masked_by_${varA}"

        echo "    [02] Processing $input_fileA with mapping partner $input_fileB..."

        # Run the mapping
        precice-aste-run -p A --mesh "$input_fileA" --data "mask"&
        precice-aste-run -p B --mesh "$input_fileB" --output "$output_file" --data "mask"

        rm -rf precice-profiling
        rm -rf precice-run
    done
done

# copy over sea meshes
for var in "${SEA_VARS[@]}"; do
    cp "$DS1/cart/${var}.vtk" "$DS2/cart/${var}.vtk"
done

# Exiting tmp work dir
cd ..
rm -rf "./tmp"
