#!/usr/bin/env cs_python

import argparse
import csv
import json
import math
import struct
import time
import numpy as np

from cerebras.sdk.runtime import runtime_utils # pylint: disable=no-name-in-module
from cerebras.sdk.runtime.sdkruntimepybind import SdkRuntime # pylint: disable=no-name-in-module
from cerebras.sdk.runtime.sdkruntimepybind import MemcpyDataType, MemcpyOrder

import cycle_utils

def parse_args():
  """ parse the command line """

  parser = argparse.ArgumentParser(description='STREAM benchmark test')
  parser.add_argument('--test', help='the test type (copy, scale, add, triad)', default='copy')
  parser.add_argument('--data-width', help='the data type size (16, 32)', type=int)
  parser.add_argument('--name', required=False, default='out', help='prefix of ELF files')
  parser.add_argument('--cmaddr', required=False, default='', help='IP:port for CS system')
  

  args = parser.parse_args()
  return args


def main():

  """Main method to run the example code."""

  args = parse_args()

  name = args.name
  cmaddr = args.cmaddr
  data_width = args.data_width
  test = args.test 

  test_name = test + '_f' + str(data_width)

  bytes_per_elem = data_width / 8

  if test == 'add' or test == 'triad':
    elem_per_op = 3
  else: # copy, scale
    elem_per_op = 2

  if test == 'triad':
    flop_per_op = 2
  else: # add, copy, scale
    flop_per_op = 1

  # Parse the compile metadata
  with open(f"{name}/out.json", encoding="utf-8") as json_file:
    compile_data = json.load(json_file)

  width = int(compile_data["params"]["width"])
  height = int(compile_data["params"]["height"])
  size = int(compile_data["params"]["size"])
  stride = int(compile_data["params"]["stride"])


  #############
  # Run
  #############
  print()
  print(f"Benchmarking {test}_f{data_width}, size={size}, stride={stride}")
  print()

  start = time.time()

  # Instantiate runner
  runner = SdkRuntime(name, cmaddr=cmaddr)

  # Device symbols for memcpy
  symbol_maxmin_time = runner.get_id("maxmin_time")

  # Load and begin run
  runner.load()
  runner.run()

  # Launch the compute kernel
  print("Launch kernel...")
  runner.call("compute", [], nonblock=False)

  # Copy back timestamps from device
  data = np.zeros((width*height*3, 1), dtype=np.float32)
  runner.memcpy_d2h(data, symbol_maxmin_time, 0, 0, width, height, 3,
    streaming=False, data_type=MemcpyDataType.MEMCPY_32BIT, order=MemcpyOrder.ROW_MAJOR, nonblock=False)
  maxmin_time_hwl = data.view(np.float32).reshape((height, width, 3))
  print("Copied back timestamps.")
  print("Done.")

  # End walltime timer
  runner.stop()
  end = time.time()
  walltime = end-start

  #################################
  # Calculate mem accesses and FLOP
  #################################

  elems_accessed = int(size / stride)
  mem_access_per_pe = elem_per_op * elems_accessed * bytes_per_elem
  mem_access_total = mem_access_per_pe * width * height

  flop_per_pe = flop_per_op * elems_accessed
  flop_total = flop_per_pe * width * height

  #######################
  # Calculate cycle count
  #######################

  tsc_tensor_d2h = np.zeros(6).astype(np.uint16)
  min_cycles = math.inf
  max_cycles = 0

  for w in range(width):
    for h in range(height):
      cycles = cycle_utils.calculate_cycles(maxmin_time_hwl[h, w])

      if cycles < min_cycles:
        min_cycles = cycles
        min_w = w
        min_h = h
      if cycles > max_cycles:
        max_cycles = cycles
        max_w = w
        max_h = h

  #####################
  # Calculate bandwidth
  #####################

  # Calculate in bytes/sec and FLOP/sec for program rectangle
  secs = max_cycles / 850000000.
  bw = mem_access_total / secs
  flops_sec = flop_total / secs

  # Convert to Petabytes/sec and PetaFLOPS
  bw /= 1.E15
  flops_sec /= 1.E15

  # Scale to program rectangle
  scale_factor = (994.*750.) / (width*height)
  scale_bw = bw * scale_factor
  scale_flops_sec = flops_sec * scale_factor


  #################
  # Generate output
  #################

  print()
  print(f"Real walltime: {walltime}s")
  print()
  print("Fabric size (number of PEs): ", width, " x ", height)
  print()
  print("Cycle Counts:")
  print("Min cycles (", min_w, ", ", min_h, "): ", min_cycles)
  print("Max cycles (", max_w, ", ", max_h, "): ", max_cycles)
  print()
  print("Accesses and FLOP Information:")
  print("Accesses (bytes): ", mem_access_total)
  print("FP operations:    ", flop_total)
  print()
  print("Bandwidth and FLOPS Information:")
  print("BW (PB/s): ", bw)
  print("PetaFLOPS: ", flops_sec)
  print()
  print("Scaled (", width, ",", height, ") to (750,994)...")
  print("Scaled BW (PB/s): ", scale_bw)
  print("Scaled PetaFLOPS: ", scale_flops_sec)

  # Write a CSV
  if cmaddr:
    csv_name = test_name + "_cs2.csv"
  else:
    csv_name = test_name + "_sim.csv"

  with open(csv_name, mode='a') as csv_file:
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow([cmaddr, width, height, size, stride, min_cycles, max_cycles,
      mem_access_total, bw, scale_bw, flop_total, flops_sec, scale_flops_sec, walltime])



if __name__ == "__main__":
  main()
