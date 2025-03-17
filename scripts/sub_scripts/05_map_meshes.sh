#!/bin/bash
source ../vars.sh

# Setting up tmp work dir

rm -rf "./tmp"
mkdir -p "./tmp"
cd "./tmp"

# cp ../../precice-configs/precice-config-mesh.xml ./precice-config.xml

mkdir -p "$DS5/cart"
for mapping in "${MAPPINGS[@]}"; do
    mkdir -p "$DS5/cart/$mapping"
    cp "../../precice-configs/precice-config-mesh-$mapping.xml" ./precice-config.xml

    # do SEA-ATM mapping
    for varA in "${SEA_VARS[@]}"; do
        for varB in "${ATM_VARS[@]}"; do
            for fun in "${FUNCTIONS[@]}"; do
                input_fileA="$DS4/cart/${varA}_${fun}"
                input_fileB="$DS3/cart/${varB}_masked_by_${varA}"
                output_file="$DS5/cart/$mapping/${varA}_to_${varB}_masked_by_${varA}_${fun}"

                precice-aste-run -p A --mesh "$input_fileA" --data "eval"&
                precice-aste-run -p B --mesh "$input_fileB" --output "$output_file" --data "eval"

                rm -rf precice-profiling
                rm -rf precice-run
            done
        done
    done

    # do ATM-SEA mapping
    for varA in "${SEA_VARS[@]}"; do
        for varB in "${ATM_VARS[@]}"; do
            for fun in "${FUNCTIONS[@]}"; do
                input_fileA="$DS4/cart/${varB}_masked_by_${varA}_${fun}"
                input_fileB="$DS3/cart/${varA}"
                output_file="$DS5/cart/$mapping/${varB}_masked_by_${varA}_to_${varA}_${fun}"

                precice-aste-run -p A --mesh "$input_fileA" --data "eval"&
                precice-aste-run -p B --mesh "$input_fileB" --output "$output_file" --data "eval"

                rm -rf precice-profiling
                rm -rf precice-run
            done
        done
    done

    # do SEA-SEA mapping
    for varA in "${SEA_VARS[@]}"; do
        for varB in "${SEA_VARS[@]}"; do
            if [[ "$varA" == "$varB" ]]; then
                continue
            fi

            for fun in "${FUNCTIONS[@]}"; do
                input_fileA="$DS4/cart/${varA}_${fun}"
                input_fileB="$DS3/cart/${varB}"
                output_file="$DS5/cart/$mapping/${varA}_to_${varB}_${fun}"

                precice-aste-run -p A --mesh "$input_fileA" --data "eval"&
                precice-aste-run -p B --mesh "$input_fileB" --output "$output_file" --data "eval"

                rm -rf precice-profiling
                rm -rf precice-run
            done
        done
    done

    # do ATM-ATM mapping
    for varA in "${ATM_VARS[@]}"; do
        for varB in "${ATM_VARS[@]}"; do
            if [[ "$varA" == "$varB" ]]; then
                continue
            fi

            for fun in "${FUNCTIONS[@]}"; do
                input_fileA="$DS4/cart/${varA}_masked_by_nogt_${fun}"
                input_fileB="$DS3/cart/${varB}_masked_by_nogt"
                output_file="$DS5/cart/$mapping/${varA}_masked_by_nogt_to_${varB}_masked_by_nogt_${fun}"

                precice-aste-run -p A --mesh "$input_fileA" --data "eval"&
                precice-aste-run -p B --mesh "$input_fileB" --output "$output_file" --data "eval"

                rm -rf precice-profiling
                rm -rf precice-run
            done
        done
    done
done

# Exiting tmp work dir
cd ..
rm -rf "./tmp"