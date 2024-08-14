#!/bin/bash
# sudo nvidia-smi -i 0 -ac 1215,1410

out_file=nvidia.out.a100
err_file=nvidia.err.a100
bench="../benchmark/benchmark"

niter=5

StrNames="faiss_warp,faiss_block,raft_radix_11bits_extra_pass,grid_select,n_power,k_power,batch,N,k,dist"
AlgoNames=( faiss_warp faiss_block raft_radix_11bits_extra_pass grid_select)

ARG=('-w 2 ')
DIST=('Uniform')

echo ${StrNames} > ${out_file}
echo echo "Errorlog" > ${err_file}


for i in "${!ARG[@]}"; do
	arg=${ARG[i]}
	dist=${DIST[i]}
	for bs in 200 400 600 800 1000; do
		for n_power in 20 21 22 23 24 25; do
			for k_power in {5..20}; do
				N=$((2 ** n_power))
				k=$((2 ** k_power))

				# not enough GPU memory on V100
				if [ $((bs * N)) -gt $(( 2 ** 32 )) ]; then
					continue
				fi

				if [ $k -gt $N ]; then
					continue
				fi

				for algo in "${AlgoNames[@]}"; do
					cm="${bench} $arg -n $niter $algo $bs $N $k"
					${cm} 2>>${err_file} 1>>${out_file} || echo -n "0.0, " 1>>${out_file}
				done

				echo "${n_power}, ${k_power}, $bs, $N, $k, $dist" 1>>${out_file}
				echo "${n_power}, ${k_power}, $bs, $N, $k, $dist"
			done
		done
	done
done
