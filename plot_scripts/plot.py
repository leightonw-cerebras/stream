#!/usr/bin/env python

import os
import argparse
import math
import numpy as np
import subprocess
import pandas as pd
from matplotlib import pyplot as plt

####

clock_speed = 850E6 # Hz
bits_to_kB = 1 / 8E3
bits_to_GB = 1 / 8E9

####

parser = argparse.ArgumentParser()
parser.add_argument('--test', help='the test type (copy, scale, add, triad)', default='copy')
parser.add_argument('--width', help='the data type size (16, 32)', type=int)
parser.add_argument('--cs2', help='run on CS-2', default=False, action='store_true')
parser.add_argument('--bw', help='plot BW instead of ops', default=False, action='store_true')
args = parser.parse_args()

test = args.test
width = args.width
cs2 = args.cs2
bw = args.bw

test_name = test + '_f' + str(width)

if   test=='copy'  and width==16:
  theoretical_bw  = 6.8
  theoretical_ops = 4
elif test=='copy'  and width==32:
  theoretical_bw  = 6.8
  theoretical_ops = 2
elif test=='scale' and width==16:
  theoretical_bw  = 6.8
  theoretical_ops = 4
elif test=='scale' and width==32:
  theoretical_bw  = 3.4
  theoretical_ops = 1
elif test=='add'   and width==16:
  theoretical_bw  = 6.8
  theoretical_ops = 4
elif test=='add'   and width==32:
  theoretical_bw  = 6.8
  theoretical_ops = 2
elif test=='triad' and width==16:
  theoretical_bw  = 6.8
  theoretical_ops = 4
elif test=='triad' and width==32:
  theoretical_bw  = 3.4
  theoretical_ops = 1

####

if cs2:
  csv_name = test_name + '_cs2.csv'
else:
  csv_name = test_name + '_sim.csv'

os.chdir(test_name)

df = pd.read_csv(csv_name)

size_kb_max = max(df['Size (kB)']) # Sets x-axis max
bw_max = math.ceil(theoretical_bw) # Sets y-axis max
ops_max = theoretical_ops + 0.1    # sets y-axis max

# Create unique ordered list of all strides
strides = list(dict.fromkeys(df['Stride'].to_list()))

# Plot bandwidth
if bw:
  for stride in strides:
    size = df.loc[df['Stride'] == stride, 'Size (kB)']
    bandwidth = df.loc[df['Stride'] == stride, 'GB/s']
    plt.plot(size, bandwidth, label=stride)
  
  plt.plot([0, size_kb_max], [theoretical_bw, theoretical_bw], \
           'k--', label='Theoretical')

  plt.legend(bbox_to_anchor=(1.05, 1.05), title="Stride")
  plt.grid()
  plt.xlabel('Size of Array (kB)')
  plt.ylabel('Memory Bandwidth (GB/s)')
  plt.xlim([0, size_kb_max])
  plt.ylim([0, bw_max])

  if not cs2:
    plt.title(test_name + " Simulation")
    plt.savefig(test_name + '_bw_sim.png', bbox_inches='tight')
  else:
    plt.title(test_name + " CS2")
    plt.savefig(test_name + '_bw_cs2.png', bbox_inches='tight')

# Plot ops
elif not bw:
  for stride in strides:
    size = df.loc[df['Stride'] == stride, 'Size (kB)']
    ops = df.loc[df['Stride'] == stride, 'Elems/Cycle']
    plt.plot(size, ops, label=stride)

  plt.plot([0, size_kb_max], [theoretical_ops, theoretical_ops], \
           'k--', label='Theoretical')

  plt.legend(bbox_to_anchor=(1.05, 1.05), title="Stride")
  plt.grid()
  plt.xlabel('Size of Array (kB)')
  plt.ylabel('Elems / Cycle')
  plt.xlim([0, size_kb_max])
  plt.ylim([0, ops_max])

  if not cs2:
    plt.title(test_name + " Simulation")
    plt.savefig(test_name + '_ops_sim.png', bbox_inches='tight')
  else:
    plt.title(test_name + " CS2")
    plt.savefig(test_name + '_ops_cs2.png', bbox_inches='tight')
