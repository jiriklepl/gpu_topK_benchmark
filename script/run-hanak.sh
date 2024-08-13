#!/bin/bash

out_file="hanak.out.a100"
err_file="hanak.err.a100"
bench="../benchmark/benchmark"

niter=10

StrNames="faiss_warp,faiss_block,raft_radix_11bits_extra_pass,grid_select,n_power,k_power,batch,N,k,dist"
AlgoNames=( faiss_warp faiss_block raft_radix_11bits_extra_pass grid_select)

ARG=('-w 10 -c ' '-w 10 -c -g ' '-w 10 -c -r 12')
DIST=('Uniform' 'Normal' 'Unfriendly')

echo ${StrNames} > ${out_file}
echo echo "Errorlog" > ${err_file}


for i in "${!ARG[@]}"; do
	arg=${ARG[i]}
	dist=${DIST[i]}

	for n_power in 15 16 17 18 19 20; do
		bs=$(((2 ** 30) / (2 ** n_power)))

		for k_power in {3..11}; do
			N=$((2 ** n_power))
			k=$((2 ** k_power))

			for algo in "${AlgoNames[@]}"; do
				cm="${bench} $arg -n $niter $algo $bs $N $k"
				# echo "${cm}"
				${cm} 2>>${err_file} 1>>${out_file} || echo -n "0.0, " 1>>${out_file}
			done

			echo "${n_power}, ${k_power}, $bs, $N, $k, $dist" 1>>${out_file}
			echo "${n_power}, ${k_power}, $bs, $N, $k, $dist"
		done
	done
done
