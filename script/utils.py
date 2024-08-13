import math
import numpy as np
import matplotlib.pyplot as plt

WARMUP = 10

plt.rcParams['axes.autolimit_mode'] = 'round_numbers'
plt.rcParams['pgf.texsystem'] = 'pdflatex'
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.size'] = 11
plt.rcParams['pgf.rcfonts'] = False
plt.rcParams['text.usetex'] = True

def restricted_size(data, axis):
    if type(axis) is int:
        return data.shape[axis]
    if axis is None:
        axis = range(len(data.shape))
    n = 1
    for a in axis:
        n *= data.shape[a]
    return n

# compute harmonic mean
def harm_mean(data, axis=None):
    n = restricted_size(data, axis)
    return n / np.sum(1.0 / data, axis=axis)

# compute standard deviation of harmonic mean
def harm_std(data, axis=None):
    inv_data = 1.0 / data
    n = restricted_size(data, axis)
    return np.sqrt(
        np.var(inv_data, axis=axis) / (np.mean(inv_data, axis=axis) ** 4) / n
    )