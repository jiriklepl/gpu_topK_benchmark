#!/bin/sh

set -e


remove() {
    echo "Removing $*" >&2 && rm -rf -- "$@"
}

trap "remove faiss-1.7.3 faiss-1.7.3.zip gpu_selection-master.zip spdlog-1.8.5.zip rmm-22.04.00.zip raft-23.04.00.zip" EXIT

wget https://github.com/facebookresearch/faiss/archive/refs/tags/v1.7.3.zip -O faiss-1.7.3.zip
unzip faiss-1.7.3.zip
mv -t faiss/ -- faiss-1.7.3/faiss/*

wget https://github.com/upsj/gpu_selection/archive/master.zip -O gpu_selection-master.zip
unzip gpu_selection-master.zip
mv gpu_selection-master gpu_selection
patch -p0 < gpu_selection.patch

wget https://github.com/gabime/spdlog/archive/refs/tags/v1.8.5.zip -O spdlog-1.8.5.zip
unzip spdlog-1.8.5.zip
mv spdlog-1.8.5 spdlog

wget https://github.com/rapidsai/rmm/archive/refs/tags/v22.04.00.zip -O rmm-22.04.00.zip
unzip rmm-22.04.00.zip
mv rmm-22.04.00 rmm

wget https://github.com/rapidsai/raft/archive/refs/tags/v23.04.00.zip -O raft-23.04.00.zip
unzip raft-23.04.00.zip
mv raft-23.04.00 raft
patch -p0 raft/cpp/include/raft/matrix/detail/select_radix.cuh raft.patch

# Dr.topk source code
git clone https://github.com/Anil-Gaihre/DrTopKSC.git
patch -p0 DrTopKSC/baseline+filter+beta+shuffle/radixselect.cuh radix.patch
cat DrTopKSC/bitonic/LargerKVersions/largerK/bitonic_com.cuh | sed -e '13d' -e '/printf/d' -e '/cout/d' -e '9a namespace drtopk_bitonic {' -e '696s/vec1/\&vec1/' > bitonic_com.cuh
sed -n '149,185p'  DrTopKSC/bitonic/LargerKVersions/largerK/sampleBitonic.cu >> bitonic_com.cuh
echo '}' >> bitonic_com.cuh
mv bitonic_com.cuh DrTopKSC/bitonic/LargerKVersions/largerK

# perform checks
md5sum -c checksums.md5
sha256sum -c checksums.sha256
sha512sum -c checksums.sha512

DrTopKSC_EXPECTED_COMMIT=2b8ed1e160448923834324ddb2ffc5f6222448b2
DrTopKSC_ACTUAL_COMMIT=$(git -C DrTopKSC rev-parse HEAD)
test "$DrTopKSC_EXPECTED_COMMIT" = "$DrTopKSC_ACTUAL_COMMIT" && echo "DrTopKSC commit is correct"
