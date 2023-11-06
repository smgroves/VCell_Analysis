#!/bin/bash
#SBATCH -N 1
#SBATCH --ntasks-per-node=16
#SBATCH --account=janeslab
#SBATCH --time=10
#SBATCH --mem=20G
#SBATCH --partition=standard

module load singularity

singularity pull /home/${USER}/vcell_misc/vcell_sif.sif docker://ghcr.io/virtualcell/biosimulators_vcell:latest