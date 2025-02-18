#!/bin/bash
source ../vars.sh

mkdir -p "$DS1/cart"

for var in "${SEA_VARS[@]}"; do
    echo "    [01] Extracting ${var}"
    envt vtk "$NC_MESH" --var "$var" --mask "$NC_MASK" -o "$DS1/cart/${var}.vtk" -c
done

for var in "${ATM_VARS[@]}"; do
    echo "    [01] Extracting ${var}"
    envt vtk "$NC_MESH" --var "$var" -o "$DS1/cart/${var}.vtk" -c
done