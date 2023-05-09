#!/usr/bin/env python

import os
import argparse
import math
import numpy as np
import subprocess
import pandas as pd
from matplotlib import pyplot as plt

####

clock_speed = 850.E6 # Hz
peta = 1.E15
num_pes = 750*994


####

parser = argparse.ArgumentParser()
parser.add_argument('--test', help='the test type (copy, scale, add, triad)', default='copy')
parser.add_argument('--data-width', help='the data type size (16, 32)', type=int)
parser.add_argument('--cs2', help='run on CS-2', default=False, action='store_true')
args = parser.parse_args()

test = args.test
data_width = args.data_width
cs2 = args.cs2

result_dir = 'results'

test_name = test + '_f' + str(data_width)

if   test=='copy'  and data_width==16:
  simd = 4
  access_per_op = 2
  flop_per_op = 1
elif test=='copy'  and data_width==32:
  simd = 2
  access_per_op = 2
  flop_per_op = 1
elif test=='scale' and data_width==16:
  simd = 4
  access_per_op = 2
  flop_per_op = 1
elif test=='scale' and data_width==32:
  simd = 1
  access_per_op = 2
  flop_per_op = 1
elif test=='add'   and data_width==16:
  simd = 4
  access_per_op = 3
  flop_per_op = 1
elif test=='add'   and data_width==32:
  simd = 2
  access_per_op = 3
  flop_per_op = 1
elif test=='triad' and data_width==16:
  simd = 4
  access_per_op = 3
  flop_per_op = 2
elif test=='triad' and data_width==32:
  simd = 1
  access_per_op = 3
  flop_per_op = 2

theoretical_bw  = simd * access_per_op * data_width/8 * num_pes * clock_speed / peta
theoretical_ops = simd * flop_per_op * num_pes * clock_speed / peta

####

if cs2:
  csv_name = test_name + '_cs2.csv'
else:
  csv_name = test_name + '_sim.csv'

df = pd.read_csv(result_dir + '/' + csv_name)

size_max = max(df['size']) # Sets x-axis max
bw_max = math.ceil(theoretical_bw) # Sets y-axis max
ops_max = theoretical_ops + 0.1    # sets y-axis max

# Create unique ordered list of all strides
strides = list(dict.fromkeys(df['stride'].to_list()))

# Plot bandwidth
for stride in strides:
  size = df.loc[df['stride'] == stride, 'size']
  bandwidth = df.loc[df['stride'] == stride, 'scale_bw']
  plt.plot(size, bandwidth, label='Measured')

plt.plot([0, size_max], [theoretical_bw, theoretical_bw], \
         'k--', label='Theoretical')

#plt.legend(bbox_to_anchor=(1.05, 1.05), title='Stride')
plt.legend(bbox_to_anchor=(1.05, 1.05))
plt.grid()
plt.xlabel('Array Size')
plt.ylabel('Memory Bandwidth (PB/s)')
plt.xlim([0, size_max])
plt.ylim([0, bw_max])

if not cs2:
  plt.title(test_name + " Simulation")
  plt.savefig(test_name + '_bw_sim.png', bbox_inches='tight')
else:
  plt.title(test_name + " CS2")
  plt.savefig(test_name + '_bw_cs2.png', bbox_inches='tight')

# Plot ops
plt.clf()
for stride in strides:
  size = df.loc[df['stride'] == stride, 'size']
  ops = df.loc[df['stride'] == stride, 'scale_flops_sec']
  plt.plot(size, ops, label='Measured')

plt.plot([0, size_max], [theoretical_ops, theoretical_ops], \
         'k--', label='Theoretical')

#plt.legend(bbox_to_anchor=(1.05, 1.05), title='Stride')
plt.legend(bbox_to_anchor=(1.05, 1.05))
plt.grid()
plt.xlabel('Array Size')
plt.ylabel('PetaFLOPS')
plt.xlim([0, size_max])
plt.ylim([0, ops_max])

if not cs2:
  plt.title(test_name + " Simulation")
  plt.savefig(test_name + '_ops_sim.png', bbox_inches='tight')
else:
  plt.title(test_name + " CS2")
  plt.savefig(test_name + '_ops_cs2.png', bbox_inches='tight')
