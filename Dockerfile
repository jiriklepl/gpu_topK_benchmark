FROM nvidia/cuda:12.5.1-devel-ubuntu22.04

WORKDIR /gpu_topk_benchmark

# move ./benchmark, ./include, and ./third_party to the image
COPY benchmark benchmark
COPY include include
COPY third_party third_party

# update packages
RUN apt-get update && apt-get upgrade -y && apt-get install -y wget git cmake make g++ unzip

WORKDIR /gpu_topk_benchmark/third_party

# run ./third_party/download.sh
RUN ./download.sh

# build faiss
RUN make -f faiss/Makefile -j4

# build gpu_selection
RUN cmake -B gpu_selection/build -S gpu_selection && cmake --build gpu_selection/build -j4
# move gpu_selection/build/lib/libgpu_selection.so to gpu_selection
RUN cd gpu_selection && cp build/lib/libgpu_selection.so .

WORKDIR /gpu_topk_benchmark/benchmark

# build benchmark
RUN make -j4

ENTRYPOINT ["/bin/bash"]
