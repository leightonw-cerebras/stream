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
args = parser.parse_args()

test = args.test
data_width = args.data_width

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

cs2_csv_name = test_name + '_cs2.csv'
sim_csv_name = test_name + '_sim.csv'

df_cs2 = pd.read_csv(result_dir + '/' + cs2_csv_name)
df_sim = pd.read_csv(result_dir + '/' + sim_csv_name)

size_max = max(max(df_cs2['size']), max(df_sim['size'])) # Sets x-axis max
bw_max = math.ceil(theoretical_bw) # Sets y-axis max
ops_max = theoretical_ops + 0.1    # sets y-axis max

# Plot bandwidth
plt.plot(df_sim['size'], df_sim['scale_bw'], '-xb', label='Simulated', markersize=6)
plt.plot(df_cs2['size'], df_cs2['scale_bw'], '-og', label='Measured', markersize=6)

plt.plot([0, size_max], [theoretical_bw, theoretical_bw], \
         'k--', label='Theoretical')

plt.legend(bbox_to_anchor=(1.05, 1.05))
plt.grid()
plt.xlabel('Array Size')
plt.ylabel('Memory Bandwidth (PB/s)')
plt.xlim([0, size_max])
plt.ylim([0, bw_max])

plt.title(test_name)
plt.savefig(test_name + '_bw_sim_cs2.png', bbox_inches='tight')

# Plot ops
plt.clf()
plt.plot(df_sim['size'], df_sim['scale_flops_sec'], '-xb', label='Simulated', markersize=6)
plt.plot(df_cs2['size'], df_cs2['scale_flops_sec'], '-og', label='Measured', markersize=6)

plt.plot([0, size_max], [theoretical_ops, theoretical_ops], \
         'k--', label='Theoretical')

plt.legend(bbox_to_anchor=(1.05, 1.05))
plt.grid()
plt.xlabel('Array Size')
plt.ylabel('PetaFLOPS')
plt.xlim([0, size_max])
plt.ylim([0, ops_max])

plt.title(test_name)
plt.savefig(test_name + '_ops_sim_cs2.png', bbox_inches='tight')
