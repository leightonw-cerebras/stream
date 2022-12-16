#!/usr/bin/env python

import math
import numpy as np
import subprocess
import pandas as pd
from matplotlib import pyplot as plt

test_type = 'scale'
data_size = 32 # bits
theoretical_bw = 6.8 # GB/s

####

clock_speed = 850E6 # Hz
bits_to_kB = 1 / 8E3
bits_to_GB = 1 / 8E9

name_str = test_type + '_f' + str(data_size)
df = pd.read_csv(name_str + '.csv')

size_kb_max = max(df['Size (kB)']) # Sets x-axis max
bw_max = max(df['GB/s']) # Find max measured bandwidth
y_ax_max = math.ceil(max(bw_max, theoretical_bw)) # Sets y-axis max

# Create unique ordered list of all strides
strides = list(dict.fromkeys(df['Stride'].to_list()))

for stride in strides:
  # Only plot the first one and the even ones
  if stride == 1 or stride % 2 == 0:
    size = df.loc[df['Stride'] == stride, 'Size (kB)']
    bandwidth = df.loc[df['Stride'] == stride, 'GB/s']
    plt.plot(size, bandwidth, label=stride)

# Only plot this if I've figured out the bandwidth
if theoretical_bw != 0.0:
  plt.plot([0, size_kb_max], [theoretical_bw, theoretical_bw], \
           'k--', label='Theoretical')

plt.legend(bbox_to_anchor=(1.05, 1.05), title="Stride")
plt.grid()
plt.xlabel('Size of Array (kB)')
plt.ylabel('Throughput (GB/s)')
plt.xlim([0, size_kb_max])
plt.ylim([0, y_ax_max])
plt.title(test_type + ' f' + str(data_size))

plt.savefig(name_str + '.png', bbox_inches='tight')
