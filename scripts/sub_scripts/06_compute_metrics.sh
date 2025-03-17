#!/bin/bash
source ../vars.sh

mkdir -p "$DS5/geod"
# Convert to 2D
for mapping in "${MAPPINGS[@]}"; do
    mkdir -p "$DS5/geod/$mapping"

    # do SEA-ATM mapping
    for varA in "${SEA_VARS[@]}"; do
        for varB in "${ATM_VARS[@]}"; do
            for fun in "${FUNCTIONS[@]}"; do
                echo "    [06] Converting $varA to $varB with $fun to 2D and mapping $mapping"
                input_file="$DS5/cart/$mapping/${varA}_to_${varB}_masked_by_${varA}_${fun}.vtk"
                output_file="$DS5/geod/$mapping/${varA}_to_${varB}_masked_by_${varA}_${fun}.vtk"
                envt vtkc "$input_file" --output "$output_file" -cv32 --attach
            done
        done
    done

    # do ATM-SEA mapping
    for varA in "${SEA_VARS[@]}"; do
        for varB in "${ATM_VARS[@]}"; do
            for fun in "${FUNCTIONS[@]}"; do
                echo "    [06] Converting $varB to $varA with $fun to 2D and mapping $mapping"
                input_file="$DS5/cart/$mapping/${varB}_masked_by_${varA}_to_${varA}_${fun}.vtk"
                output_file="$DS5/geod/$mapping/${varB}_masked_by_${varA}_to_${varA}_${fun}.vtk"
                envt vtkc "$input_file" --output "$output_file" -cv32 --attach
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
                echo "    [06] Converting $varA to $varB with $fun to 2D and mapping $mapping"
                input_file="$DS5/cart/$mapping/${varA}_to_${varB}_${fun}.vtk"
                output_file="$DS5/geod/$mapping/${varA}_to_${varB}_${fun}.vtk"
                envt vtkc "$input_file" --output "$output_file" -cv32 --attach
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
                echo "    [06] Converting $varA to $varB with $fun to 2D and mapping $mapping"
                input_file="$DS5/cart/$mapping/${varA}_masked_by_nogt_to_${varB}_masked_by_nogt_${fun}.vtk"
                output_file="$DS5/geod/$mapping/${varA}_masked_by_nogt_to_${varB}_masked_by_nogt_${fun}.vtk"
                envt vtkc "$input_file" --output "$output_file" -cv32 --attach
            done
        done
    done
done

mkdir -p "$DS6"
# Compute metrics on 2D meshes
for mapping in "${MAPPINGS[@]}"; do
    mkdir -p "$DS6/$mapping"
    mkdir -p "$DS6/$mapping/geod"

    # do SEA-ATM mapping
    for varA in "${SEA_VARS[@]}"; do
        for varB in "${ATM_VARS[@]}"; do
            for fun in "${FUNCTIONS[@]}"; do
                echo "    [06] Computing metrics for $varA to $varB with $fun and mapping $mapping"
                mapped_file="$DS5/geod/$mapping/${varA}_to_${varB}_masked_by_${varA}_${fun}.vtk"
                src_file="$DS3/geod/${varA}.vtk"
                output_file="$DS6/$mapping/${varA}_to_${varB}_masked_by_${varA}_${fun}.txt"
                output_vtk="$DS6/$mapping/geod/${varA}_to_${varB}_masked_by_${varA}_${fun}.vtk"
                envt vtke "$mapped_file" --output "$output_file" --source "$src_file" -f "$fun" --diff -ov "$output_vtk"
            done
        done
    done

    # do ATM-SEA mapping
    for varA in "${SEA_VARS[@]}"; do
        for varB in "${ATM_VARS[@]}"; do
            for fun in "${FUNCTIONS[@]}"; do
                echo "    [06] Computing metrics for $varB to $varA with $fun and mapping $mapping"
                mapped_file="$DS5/geod/$mapping/${varB}_masked_by_${varA}_to_${varA}_${fun}.vtk"
                src_file="$DS3/geod/${varB}_masked_by_${varA}.vtk"
                output_file="$DS6/$mapping/${varB}_masked_by_${varA}_to_${varA}_${fun}.txt"
                output_vtk="$DS6/$mapping/geod/${varB}_masked_by_${varA}_to_${varA}_${fun}.vtk"
                envt vtke "$mapped_file" --output "$output_file" --source "$src_file" -f "$fun" --diff -ov "$output_vtk"
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
                echo "    [06] Computing metrics for $varA to $varB with $fun and mapping $mapping"
                mapped_file="$DS5/geod/$mapping/${varA}_to_${varB}_${fun}.vtk"
                src_file="$DS3/geod/${varA}.vtk"
                output_file="$DS6/$mapping/${varA}_to_${varB}_${fun}.txt"
                output_vtk="$DS6/$mapping/geod/${varA}_to_${varB}_${fun}.vtk"
                envt vtke "$mapped_file" --output "$output_file" --source "$src_file" -f "$fun" --diff -ov "$output_vtk"
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
                echo "    [06] Computing metrics for $varA to $varB with $fun and mapping $mapping"
                mapped_file="$DS5/geod/$mapping/${varA}_masked_by_nogt_to_${varB}_masked_by_nogt_${fun}.vtk"
                src_file="$DS3/geod/${varA}_masked_by_nogt.vtk"
                output_file="$DS6/$mapping/${varA}_masked_by_nogt_to_${varB}_masked_by_nogt_${fun}.txt"
                output_vtk="$DS6/$mapping/geod/${varA}_masked_by_nogt_to_${varB}_masked_by_nogt_${fun}.vtk"
                envt vtke "$mapped_file" --output "$output_file" --source "$src_file" -f "$fun" --diff -ov "$output_vtk"
            done
        done
    done
done

# Convert to 3D
for mapping in "${MAPPINGS[@]}"; do
    mkdir -p "$DS6/$mapping/cart"

    # do SEA-ATM mapping
    for varA in "${SEA_VARS[@]}"; do
        for varB in "${ATM_VARS[@]}"; do
            for fun in "${FUNCTIONS[@]}"; do
                echo "    [06] Converting $varA to $varB with $fun to 3D and mapping $mapping"
                input_file="$DS6/$mapping/geod/${varA}_to_${varB}_masked_by_${varA}_${fun}.vtk"
                output_file="$DS6/$mapping/cart/${varA}_to_${varB}_masked_by_${varA}_${fun}.vtk"
                envt vtkc "$input_file" --output "$output_file" -cv23 --attach
            done
        done
    done

    # do ATM-SEA mapping
    for varA in "${SEA_VARS[@]}"; do
        for varB in "${ATM_VARS[@]}"; do
            for fun in "${FUNCTIONS[@]}"; do
                echo "    [06] Converting $varB to $varA with $fun to 3D and mapping $mapping"
                input_file="$DS6/$mapping/geod/${varB}_masked_by_${varA}_to_${varA}_${fun}.vtk"
                output_file="$DS6/$mapping/cart/${varB}_masked_by_${varA}_to_${varA}_${fun}.vtk"
                envt vtkc "$input_file" --output "$output_file" -cv23 --attach
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
                echo "    [06] Converting $varA to $varB with $fun to 3D and mapping $mapping"
                input_file="$DS6/$mapping/geod/${varA}_to_${varB}_${fun}.vtk"
                output_file="$DS6/$mapping/cart/${varA}_to_${varB}_${fun}.vtk"
                envt vtkc "$input_file" --output "$output_file" -cv23 --attach
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
                echo "    [06] Converting $varA to $varB with $fun to 3D and mapping $mapping"
                input_file="$DS6/$mapping/geod/${varA}_masked_by_nogt_to_${varB}_masked_by_nogt_${fun}.vtk"
                output_file="$DS6/$mapping/cart/${varA}_masked_by_nogt_to_${varB}_masked_by_nogt_${fun}.vtk"
                envt vtkc "$input_file" --output "$output_file" -cv23 --attach
            done
        done
    done
done