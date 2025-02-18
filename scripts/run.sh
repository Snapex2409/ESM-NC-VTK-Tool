#!/bin/bash

echo "[Main Script] Starting Mask extraction"
(cd ./sub_scripts && bash ./01_extract_masks.sh)
echo "[Main Script] Starting Mask mapping"
(cd ./sub_scripts && bash ./02_map_masks.sh)
echo "[Main Script] Starting Mask to Mesh conversion"
(cd ./sub_scripts && bash ./03_create_meshes_from_masks.sh)
echo "[Main Script] Starting Mesh evaluation"
(cd ./sub_scripts && bash ./04_eval_meshes.sh)
echo "[Main Script] Starting Mesh mapping"
(cd ./sub_scripts && bash ./05_map_meshes.sh)
echo "[Main Script] Starting Metric computation"
(cd ./sub_scripts && bash ./06_compute_metrics.sh)
echo "[Main Script] Done"
