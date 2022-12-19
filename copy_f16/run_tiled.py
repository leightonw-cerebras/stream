#!/usr/bin/env cs_python

import argparse
from glob import glob
import numpy as np
from cerebras.elf.cs_elf_runner import CSELFRunner
import cerebras.elf.cs_elf_runner.lib.csl_utils as csl_utils

parser = argparse.ArgumentParser()
parser.add_argument('--name', help='the test name')
parser.add_argument("--cmaddr", help="IP:port for CS system")
args = parser.parse_args()
name = args.name

# Path to ELF and simulation output files
elf_list = glob(f"{name}/bin/out_[0-9]*.elf")

# Simulate ELF file and produce the simulation output
runner = CSELFRunner(elf_list, cmaddr=args.cmaddr)

done_color = 1
ready = np.zeros(1).astype(np.float32)
runner.add_output_array("ready", done_color, "E", ready, 0)

# Proceed with simulation
runner.connect_and_run()

for x in range(300,451,10):
  for y in range(300,451,10):
    trace_output = csl_utils.read_trace(runner, x, y, 'trace')
    print("PE ID: ", x, " ", y)
    print("Cycle Start: ", trace_output[0])
    print("Cycle Stop: ", trace_output[1])
