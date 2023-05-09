#!/bin/bash

#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
#-#-#-# SLURM Commands #-#-#-#-#

#SBATCH --job-name=csSTREAM                        # Job name
#SBATCH --mail-type=END,FAIL                       # Mail events (NONE, BEGIN, END, FAIL, ALL)
#SBATCH --mail-user=leighton.wilson@cerebras.net   # Where to send mail

#SBATCH --gres=cs:cerebras:1
#SBATCH --nodelist=sdf-1
#SBATCH --cpus-per-task=28
#SBATCH --time=12:00:00

#SBATCH --output=sweep_%j.log   # Standard output and error log
#SBATCH --error=sweep_%j.log   # Standard output and error log

#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
#-#-#-#-# Environment Set-up #-#-#-#-#

export SDK_INSTALL_PATH=/ocean/neocortex/cerebras/sdk_archive/Cerebras-SDK-0.7.0-202304042343-14-30f7fcfe
export PATH=$SDK_INSTALL_PATH:$PATH

#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
#-#-#-#-# Compile and Run #-#-#-#-#

#python3 sweep.py --test copy --data-width 16 --dims 750,994 --cmaddr $CS_IP_ADDR:9000
python3 sweep.py --test copy --data-width 32 --dims 750,994 --cmaddr $CS_IP_ADDR:9000

python3 sweep.py --test scale --data-width 16 --dims 750,994 --cmaddr $CS_IP_ADDR:9000
python3 sweep.py --test scale --data-width 32 --dims 750,994 --cmaddr $CS_IP_ADDR:9000

python3 sweep.py --test add --data-width 16 --dims 750,994 --cmaddr $CS_IP_ADDR:9000
#python3 sweep.py --test add --data-width 32 --dims 750,994 --cmaddr $CS_IP_ADDR:9000

python3 sweep.py --test triad --data-width 16 --dims 750,994 --cmaddr $CS_IP_ADDR:9000
python3 sweep.py --test triad --data-width 32 --dims 750,994 --cmaddr $CS_IP_ADDR:9000

#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
