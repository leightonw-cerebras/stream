#!/usr/bin/env python

import os
import argparse
import numpy as np
import re
import subprocess
import csv

####

clock_speed = 850E6 # Hz
bits_to_kB = 1 / 8E3
bits_to_GB = 1 / 8E9

####

parser = argparse.ArgumentParser()
parser.add_argument('--test', help='the test type (copy, scale, add, triad)', default='copy')
parser.add_argument('--width', help='the data type size (16, 32)', type=int)
parser.add_argument('--cs2', help='run on CS-2', default=False, action='store_true')
parser.add_argument('--stride', help='run across strides 1, 2, 4, 8, 16', default=False, action='store_true')
parser.add_argument('--tile', help='side length of fab square on which problem is tiled', type=int, default=1)
args = parser.parse_args()

test = args.test
width = args.width
cs2 = args.cs2
stride = args.stride
tile = args.tile

test_name = test + '_f' + str(width)

size_min = 4096 // width # 0.512 kB (256 elems f16, 128 elems f32)

if test is 'add' or test is 'triad':
  size_max = size_min * 30 # 15.36 kB per array
else:
  size_max = size_min * 40 # 20.48 kB per array

sizes = range(size_min, size_max+1, size_min*4)

if stride:
  strides = {1, 2, 4, 8, 16}
else:
  strides = {1}

if cs2:
  csv_name = test_name + '_cs2.csv'
  compile_cmd = "cslc code_tiled.csl --arch=wse2 --fabric-dims=757,996 --fabric-offsets=1,1 --verbose -o out_cs2 "
  run_cmd = "cs_python run_tiled.py --name out_cs2 --cmaddr ${CS_IP_ADDR}:9000"
else:
  csv_name = test_name + '_sim.csv'
  fabdims = str(tile+2) + "," + str(tile+2)
  compile_cmd = "cslc code_tiled.csl --fabric-dims=" + fabdims + " --fabric-offsets=1,1 --verbose -o out_sim "
  run_cmd = "cs_python run_tiled.py --name out_sim"

os.chdir(test_name)

with open(csv_name, mode='w') as csv_file:
  csv_writer = csv.writer(csv_file)
  csv_writer.writerow(['PE x', 'PE y', 'Stride', 'Size (elems)', 'Size (kB)',
                       'Processed Size (elems)', 'Processed Size (kB)',
                       'Stop Cycle', 'Start Cycle', 'Num Cycles', 'GB/s', 'Elems/Cycle'])

  for stride_size in strides:
    for size in sizes:

      # Compile
      size_prms = "--params=stride_size:" + str(stride_size) + ",size:" + str(size) + ",tile:" + str(tile)
      output = subprocess.check_output(compile_cmd + size_prms, shell=True)

      # Run and grab stdout
      output = subprocess.check_output(run_cmd, shell=True)

      # Parse cycle counts
      pe_ids = [[int(line.split()[2]), int(line.split()[3])] for line in output.decode("utf-8").split('\n') \
                   if "PE ID:" in line]
      cycle_starts = [int(line.split()[2]) for line in output.decode("utf-8").split('\n') \
                   if "Cycle Start:" in line]

      cycle_stops = [int(line.split()[2]) for line in output.decode("utf-8").split('\n') \
                   if "Cycle Stop:" in line]

      size_bits = size * width
      size_kb = size_bits * bits_to_kB

      processed_size = size // stride_size
      processed_size_bits = processed_size * width
      processed_size_kb = processed_size_bits * bits_to_kB

      for (pe_id, cycle_start, cycle_stop) in zip(pe_ids, cycle_starts, cycle_stops):

        num_cycles = cycle_stop - cycle_start

        bandwidth = clock_speed / num_cycles * processed_size_bits * bits_to_GB
        elems_cycle = float(processed_size) / float(num_cycles)

        csv_writer.writerow([pe_id[0], pe_id[1], stride_size, size, size_kb, processed_size, processed_size_kb,
                             cycle_start, cycle_stop, num_cycles, bandwidth, elems_cycle])

        print(pe_id[0], pe_id[1], stride_size, size, size_kb, processed_size, processed_size_kb,
              cycle_start, cycle_stop, num_cycles, bandwidth, elems_cycle)
