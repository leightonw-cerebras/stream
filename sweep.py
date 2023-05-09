#!/usr/bin/env python

import os
import argparse
import subprocess
import numpy as np

parser = argparse.ArgumentParser()
parser.add_argument('--test', help='the test type (copy, scale, add, triad)', default='copy')
parser.add_argument('--data-width', help='the data type size (16, 32)', type=int)
parser.add_argument('--cmaddr', help='CM address for CS-2', type=str, default='')
parser.add_argument('--stride', help='run across strides 1, 2, 4, 8, 16', default=False, action='store_true')
parser.add_argument('--dims', help='Fabric and program dimension, i.e. <W>,<H>')
args = parser.parse_args()

test = args.test
data_width = args.data_width
cmaddr = args.cmaddr
stride = args.stride

w, h = args.dims.split(",")
width = int(w)
height = int(h)

test_name = test + '_f' + str(data_width)

#min_size = 4096//data_width
#max_size = 65536//data_width
#sizes = range(min_size, max_size+1, min_size)

sizes = np.array([512, 1024, 2048, 4096, 8192, 16384, 32768, 65536], dtype=np.uint32)
sizes = sizes // data_width

if stride:
  strides = {1, 2, 4, 8, 16}
else:
  strides = {1}

if cmaddr:
  csv_name = test_name + '_cs2.csv'
  compile_cmd = f"cslc {test_name}/layout.csl --arch=wse2 --fabric-dims=757,996 --fabric-offsets=4,1 --verbose -o out_cs2 " \
              + f"--params=width:{width},height:{height} --memcpy --channels=1 "
  run_cmd = f"cs_python run.py --name out_cs2 --test {test} --data-width {data_width} --cmaddr {cmaddr} "
else:
  csv_name = test_name + '_sim.csv'
  compile_cmd = f"cslc {test_name}/layout.csl --fabric-dims={width+7},{height+2} --fabric-offsets=4,1 --verbose -o out_sim " \
              + f"--params=width:{width},height:{height} --memcpy --channels=1 "
  run_cmd = f"cs_python run.py --name out_sim --test {test} --data-width {data_width} "

for stride in strides:
  for size in sizes:

    # Compile
    size_prms = f"--params=stride:{stride},size:{size} "
    output = subprocess.check_output(compile_cmd + size_prms, shell=True)
    print(output)
    output = subprocess.check_output(run_cmd, shell=True)
