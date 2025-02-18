#!/bin/bash
source ../vars.sh

# Setting up tmp work dir

rm -rf "./tmp"
mkdir -p "./tmp"
cd "./tmp"

cp ../../precice-configs/precice-config-mesh.xml ./precice-config.xml

mkdir -p "$DS5/cart"
for varA in "${SEA_VARS[@]}"; do
    for varB in "${ATM_VARS[@]}"; do
        for fun in "${FUNCTIONS[@]}"; do
            input_fileA="$DS4/cart/${varA}_${fun}"
            input_fileB="$DS3/cart/${varB}_masked_by_${varA}"
            output_file="$DS5/cart/${varB}_masked_by_${varA}_${fun}"

            precice-aste-run -p A --mesh "$input_fileA" --data "eval"&
            precice-aste-run -p B --mesh "$input_fileB" --output "$output_file" --data "eval"

            rm -rf precice-profiling
            rm -rf precice-run
        done
    done
done


# Exiting tmp work dir
cd ..
rm -rf "./tmp"