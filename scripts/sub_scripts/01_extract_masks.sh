#!/bin/bash
source ../vars.sh

mkdir -p "$DS1/cart"

for var in "${SEA_VARS[@]}"; do
    echo "    [01] Extracting ${var}"
    extra_args=""
    [ "$BAD_TORC" -eq 1 ] && extra_args="--notorcfix"
    envt vtk "$NC_MESH" --var "$var" --mask "$NC_MASK" -o "$DS1/cart/${var}.vtk" -c $extra_args
done

for var in "${ATM_VARS[@]}"; do
    echo "    [01] Extracting ${var}"
    envt vtk "$NC_MESH" --var "$var" -o "$DS1/cart/${var}.vtk" -c
done