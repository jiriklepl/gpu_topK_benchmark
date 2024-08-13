#!/usr/bin/env python3

import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import utils
import os

def plot(file, hostname, jobid):
    if hostname.startswith("volta05"): # V100 32GB PCIe: https://images.nvidia.com/content/technologies/volta/pdf/tesla-volta-v100-datasheet-letter-fnl-web.pdf
        THEORETICAL_FLOAT_THROUGHPUT = 900.0 * 1024 * 1024 * 1024 / 4
    elif hostname.startswith("ampere02"): # A100 80GB PCIe: https://www.nvidia.com/content/dam/en-zz/Solutions/Data-Center/a100/pdf/nvidia-a100-datasheet-nvidia-us-2188504-web.pdf
        THEORETICAL_FLOAT_THROUGHPUT = 1935.0 * 1024 * 1024 * 1024 / 4
    elif hostname.startswith("ampere01"): # L40: https://www.nvidia.com/content/dam/en-zz/Solutions/design-visualization/support-guide/NVIDIA-L40-Datasheet-January-2023.pdf
        THEORETICAL_FLOAT_THROUGHPUT = 864.0 * 1024 * 1024 * 1024 / 4
    else:
        raise ValueError(f"unknown hostname: {hostname}")

    fig, ax = plt.subplots(nrows=3, ncols=2, sharey=True)
    fig.subplots_adjust(bottom=0.18, top=0.95, hspace=0.4, wspace=0.1)

    data : pd.DataFrame = pd.read_csv(file, sep=',')
    
    # # strip whitespaces from all values
    data = data.map(lambda x: x.strip() if isinstance(x, str) else x)

    data.drop(columns=["n_power", "k_power"], inplace=True)
    
    data = data.loc[(data["dist"].isin(["Uniform"])) & True]
    
    # rename columns
    data.rename(columns={
        "N": "point_count",
        "k": "k",
        "batch": "query_count",
    }, inplace=True)

    # merge columns with different algorithm times into two columns: algorithm and time
    algorithms = []
    times = []
    for c in data.columns:
        # ignore columns containing experiment parameters
        if c in ["point_count", "k", "dist", "query_count"]:
            continue
        
        algorithms.append([c] * len(data))
        times.append(data[c].map(float) / 1000) # convert to seconds
        
        data.drop(columns=[c], inplace=True)
        
    old_data = data
    data = None

    for a, t in zip(algorithms, times):
        new_data = pd.concat([old_data, pd.DataFrame({
            "algorithm": a,
            "time": t
        })], axis=1)
        
        data = pd.concat([data, new_data], ignore_index=True) if data is not None else new_data
        

    # compute throughput
    data["throughput"] = data["point_count"] * data["query_count"] / data["time"]

    best = max(data["throughput"])
    print(f"peak throughput: {best / THEORETICAL_FLOAT_THROUGHPUT}")

    # transform labels to human readable strings
    # data = data.replace({"algorithm": {
    #     "bits": "bits (our implementation)",
    #     "warp-select": "WarpSelect",
    #     "warp-select-tuned": "WarpSelect with tuned parameters",
    #     "block-select": "BlockSelect",
    #     "block-select-tuned": "BlockSelect with tuned parameters",
    #     "fgknn-buffered": "Merge queue"
    # }})

    # compute the maximum throughput that is shown in the plot
    max_throughput = (math.ceil(THEORETICAL_FLOAT_THROUGHPUT / 1e11) - 0.3) * 1e11

    # plot the speed-up
    i = 1
    for n, group in data.groupby("point_count"):
        scaled_n = n // 1024
        group = group.filter(items=["algorithm", "k", "throughput"])
        ax = plt.subplot(3, 2, i)
        ax.set_title(f"n = {scaled_n}k, q = {1024 // scaled_n}k")
        ax.set_ylim([0, max_throughput])
        ax.set_yticks(ax.get_yticks().tolist()) # shut up the warning (other than that, does nothing)
        ax.set_yticklabels([int(val / 1e10) for val in ax.get_yticks().tolist()])
        ax.grid(alpha=0.4, linestyle="--")
        i += 1

        # setup the secondary axis
        ax2 = ax.twinx()
        ax2.set_ylim([0.0, max_throughput / THEORETICAL_FLOAT_THROUGHPUT * 100])
        ax2.plot([], [])

        # set label for the secondary axis
        if scaled_n in [64, 256, 1024]:
            ax2.set_yticks([0, 25, 50, 75, 100])
        else:
            ax2.set_yticks([])

        ax.axhline(
            y=THEORETICAL_FLOAT_THROUGHPUT, 
            color="black", 
            linestyle=":",
            label="Theoretical peak throughput")
        
        ax.set_xlim([8, 2048])
        ax.set_xscale("log", base=2)
        ax.set_xticks([2 ** i for i in range(3, 12)])

        for group, algorithm in group.groupby("algorithm"):
            ax.plot(
                algorithm["k"], 
                algorithm["throughput"],
                label=algorithm["algorithm"].iloc[0],
                linewidth=1.5, 
                marker='.')

    handles, labels = ax.get_legend_handles_labels()
    fig.legend(handles, labels, loc='lower center', bbox_to_anchor=(0.5, 0), frameon=False, ncol=2)

    fig.supylabel("Throughput [distances/s] ×$10^{10}$", x=0.05)
    fig.text(0.97, 0.5, 'Throughput [\\% of peak]', va='center', rotation='vertical', fontsize='large')
    fig.supxlabel("Nearest neighbors --- k", y=0.115)
    fig.set_size_inches(6.3, 7)

    # create directory if it does not exist
    os.makedirs("figures", exist_ok=True)

    fig.savefig(f"figures/hanak.pgf", bbox_inches='tight')
    fig.savefig(f"figures/hanak.pdf", bbox_inches='tight')

plot("hanak.out.a100", "ampere02", 42)
