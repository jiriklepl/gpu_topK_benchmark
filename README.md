# Top-K benchmark on GPU

## Tested Environment

* Ubuntu 22.04
* CUDA 12.0
* NVIDIA A100 GPU


## Build

### Dependencies

* RAFT (https://github.com/rapidsai/raft)
* Faiss (https://github.com/facebookresearch/faiss)
* gpu_selection (https://github.com/upsj/gpu_selection)
* DrTopK (https://github.com/Anil-Gaihre/DrTopKSC)

A script is provided to get them:

```bash
cd third_party && ./download.sh
```

### build Faiss

```bash
cd third_party && make -f faiss/Makefile
```

### build gpu_selection

Cmake is required to build gpu_selection:

```bash
cd third_party
mkdir -p gpu_selection/build
cmake -S gpu_selection -B gpu_selection/build
cmake --build gpu_selection/build && \
mv gpu_selection/build/lib/libgpu_selection.so gpu_selection/libgpu_selection.so
```

### build benchmark

After building the dependencies, run `cd benchmark && make` to build the benchmark.


## Benchmark Usage
Run `./benchmark` without any argument to see the usage and available algorithms.

Use `-c` to check correctness. Use `-n` with a large number (e.g. `-n 100`) to get more stable benchmark results. Use `-w` to set the number of warmup runs.

For example, to run algorithm CUB for batch_size=1, len=1e6, k=20 (note that exponential form is acceptable for batch/len/k):

```bash
$ ./benchmark -c -w 20 -n 100 cub 1 1e6 20
```
