#!/usr/bin/env python

import numpy as np
import re
import subprocess
import csv

test_type = 'dot'
data_size = 16 # bits

stride_size_max = 16
size_min = 4096 // data_size # 0.512 kB (256 elems f16, 128 elems f32)
size_max = size_min * 40 # 20.48 kB

####

clock_speed = 850E6 # Hz
bits_to_kB = 1 / 8E3
bits_to_GB = 1 / 8E9

compile_cmd = "cslc code.csl --fabric-dims=3,3 --fabric-offsets=1,1 --verbose -o out "
run_cmd = "cs_python run.py --name out"

with open(test_type + '_f' + str(data_size) + '.csv', mode='w') as csv_file:
  csv_writer = csv.writer(csv_file)
  csv_writer.writerow(['Stride', 'Size (elems)', 'Size (kB)',
                        'Processed Size (elems)', 'Processed Size (kB)',
                        'Stop Cycle', 'Start Cycle', 'Num Cycles', 'GB/s'])

  #for stride_size in range(1, stride_size_max+1, 1):
  for stride_size in {1, 2, 4, 8, 16}:
    for size in range(size_min, size_max+1, size_min):

      # Compile
      size_prms = "--params=stride_size:" + str(stride_size) + ",size:" + str(size)
      output = subprocess.check_output(compile_cmd + size_prms, shell=True)

      # Run and grab stdout
      output = subprocess.check_output(run_cmd, shell=True)

      # Parse cycle counts
      cycle_str = [line for line in output.decode("utf-8").split('\n') \
                   if "Cycle Start:" in line]
      cycle_start = cycle_str[0].split()[2]

      cycle_str = [line for line in output.decode("utf-8").split('\n') \
                   if "Cycle Stop:" in line]
      cycle_stop = cycle_str[0].split()[2]

      num_cycles = int(cycle_stop) - int(cycle_start)

      size_bits = size * data_size
      size_kb = size_bits * bits_to_kB

      processed_size = size // stride_size
      processed_size_bits = processed_size * data_size
      processed_size_kb = processed_size_bits * bits_to_kB

      bandwidth = clock_speed / num_cycles * processed_size_bits * bits_to_GB

      csv_writer.writerow([stride_size, size, size_kb, processed_size, processed_size_kb, cycle_start, cycle_stop, num_cycles, bandwidth])

      print(stride_size, size, size_kb, processed_size, processed_size_kb, cycle_start, cycle_stop, num_cycles, bandwidth)
