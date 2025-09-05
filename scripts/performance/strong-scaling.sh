#!/bin/bash
source ../vars.sh

mkdir -p "$DS4/cart"

# partition meshes
for varA in "${SEA_VARS[@]}"; do
    for fun in "${FUNCTIONS[@]}"; do
        for p in "${PARTITIONS[@]}"; do
            echo "    [Partition] Splitting $varA with $fun into $p partitions"
            input_file="$DS4/cart/${varA}_${fun}.vtk"
            output_filename="${varA}_${fun}"
            output_path="$DS4/cart/${varA}_${fun}_${p}"
            precice-aste-partition --mesh "$input_file" --algorithm topology -o "$output_filename" --directory "$output_path" -n "$p"
        done
    done
done
for varA in "${SEA_VARS[@]}"; do
    for varB in "${ATM_VARS[@]}"; do
        for fun in "${FUNCTIONS[@]}"; do
            for p in "${PARTITIONS[@]}"; do
                echo "    [Partition] Splitting ${varB}_masked_by_${varA} with $fun into $p partitions"
                input_file="$DS4/cart/${varB}_masked_by_${varA}_${fun}.vtk"
                output_filename="${varB}_masked_by_${varA}_${fun}"
                output_path="$DS4/cart/${varB}_masked_by_${varA}_${fun}_${p}"
                precice-aste-partition --mesh "$input_file" --algorithm topology -o "$output_filename" --directory "$output_path" -n "$p"
            done
        done
    done
done

# set up mapping tmp work dir
rm -rf "./tmp"
mkdir -p "./tmp"
cd "./tmp"

# perform mappings
for (( i=1; i<=$ITERATIONS; i++ )); do
    for pA in "${PARTITIONS[@]}"; do
        for pB in "${PARTITIONS[@]}"; do
            for mapping in "${MAPPINGS[@]}"; do
                cp "../../precice-configs/precice-config-mesh-perf-$mapping.xml" ./precice-config.xml

                # do SEA-ATM mapping
                for varA in "${SEA_VARS[@]}"; do
                    for varB in "${ATM_VARS[@]}"; do
                        for fun in "${FUNCTIONS[@]}"; do
                            input_fileA="$DS4/cart/${varA}_${fun}_${pA}/${varA}_${fun}"
                            input_fileB="$DS4/cart/${varB}_masked_by_${varA}_${fun}_${pB}/${varB}_masked_by_${varA}_${fun}"
                            output_file="tmp-out"

                            mpirun -n "$pA" "$MPI_ARGS_A" precice-aste-run -v -a -p A --mesh "$input_fileA" --data "eval" || kill 0 &
                            mpirun -n "$pB" "$MPI_ARGS_B" precice-aste-run -v -a -p B --mesh "$input_fileB" --output "$output_file" --data "eval-mapped" || kill 0 & wait

                            outdir="$DPERF/$mapping/${varA}_to_${varB}_masked_by_${varA}/${fun}/p${pA}_to_p${pB}/it${i}"
                            mkdir -p "$outdir"
                            mv "./precice-profiling" "$outdir"
                            mv "./precice-run" "$outdir"
                            rm -rf "$output_file"
                        done
                    done
                done

                # do ATM-SEA mapping
                for varA in "${SEA_VARS[@]}"; do
                    for varB in "${ATM_VARS[@]}"; do
                        for fun in "${FUNCTIONS[@]}"; do
                            input_fileA="$DS4/cart/${varB}_masked_by_${varA}_${fun}_${pA}/${varB}_masked_by_${varA}_${fun}"
                            input_fileB="$DS4/cart/${varA}_${fun}_${pB}/${varA}_${fun}"
                            output_file="tmp-out"

                            mpirun -n "$pA" "$MPI_ARGS_A" precice-aste-run -v -a -p A --mesh "$input_fileA" --data "eval" || kill 0 &
                            mpirun -n "$pB" "$MPI_ARGS_B" precice-aste-run -v -a -p B --mesh "$input_fileB" --output "$output_file" --data "eval-mapped" || kill 0 & wait

                            outdir="$DPERF/$mapping/${varB}_masked_by_${varA}_to_${varA}/${fun}/p${pA}_to_p${pB}/it${i}"
                            mkdir -p "$outdir"
                            mv "./precice-profiling" "$outdir"
                            mv "./precice-run" "$outdir"
                            rm -rf "$output_file"
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
                            input_fileA="$DS4/cart/${varA}_${fun}_${pA}/${varA}_${fun}"
                            input_fileB="$DS4/cart/${varB}_${fun}_${pB}/${varB}_${fun}"
                            output_file="tmp-out"

                            mpirun -n "$pA" "$MPI_ARGS_A" precice-aste-run -v -a -p A --mesh "$input_fileA" --data "eval" || kill 0 &
                            mpirun -n "$pB" "$MPI_ARGS_B" precice-aste-run -v -a -p B --mesh "$input_fileB" --output "$output_file" --data "eval-mapped" || kill 0 & wait

                            outdir="$DPERF/$mapping/${varA}_to_${varB}/${fun}/p${pA}_to_p${pB}/it${i}"
                            mkdir -p "$outdir"
                            mv "./precice-profiling" "$outdir"
                            mv "./precice-run" "$outdir"
                            rm -rf "$output_file"
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
                            input_fileA="$DS4/cart/${varA}_masked_by_nogt_${fun}_${pA}/${varA}_masked_by_nogt_${fun}"
                            input_fileB="$DS4/cart/${varB}_masked_by_nogt_${fun}_${pB}/${varB}_masked_by_nogt_${fun}"
                            output_file="tmp-out"

                            mpirun -n "$pA" "$MPI_ARGS_A" precice-aste-run -v -a -p A --mesh "$input_fileA" --data "eval" || kill 0 &
                            mpirun -n "$pB" "$MPI_ARGS_B" precice-aste-run -v -a -p B --mesh "$input_fileB" --output "$output_file" --data "eval-mapped" || kill 0 & wait

                            outdir="$DPERF/$mapping/${varA}_masked_by_nogt_to_${varB}_masked_by_nogt/${fun}/p${pA}_to_p${pB}/it${i}"
                            mkdir -p "$outdir"
                            mv "./precice-profiling" "$outdir"
                            mv "./precice-run" "$outdir"
                            rm -rf "$output_file"
                        done
                    done
                done
            done
        done
    done
done

# Exiting tmp work dir
cd ..
rm -rf "./tmp"
