#!/bin/bash

#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
#-#-#-# SLURM Commands #-#-#-#-#

#SBATCH --job-name=simSTREAM                       # Job name
#SBATCH --mail-type=END,FAIL                       # Mail events (NONE, BEGIN, END, FAIL, ALL)
#SBATCH --mail-user=leighton.wilson@cerebras.net   # Where to send mail

#SBATCH --cpus-per-task=28
#SBATCH --time=12:00:00

#SBATCH --output=sweep_%j.log   # Standard output and error log

#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
#-#-#-#-# Environment Set-up #-#-#-#-#

export SDK_INSTALL_LOCATION=/ocean/neocortex/cerebras
export SDK_INSTALL_PATH=$SDK_INSTALL_LOCATION/sdk
export PATH=$PATH:$SDK_INSTALL_PATH

#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


#export SINGULARITYENV_SIMFABRIC_DEBUG=hwtile

#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
#-#-#-#-# Compile and Run #-#-#-#-#

./sweep.py --test copy --width 16 --tile 1 --loop_iter 1

#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
