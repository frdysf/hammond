#!/bin/bash
#PBS -l walltime=23:59:00
#PBS -l nodes=4:ppn=6
module load conda
source activate ~/.conda/envs/synthenv/
cd $PBS_O_WORKDIR
./programmer.py