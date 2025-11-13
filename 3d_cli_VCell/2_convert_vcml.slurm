#!/bin/bash
#SBATCH -N 1
#SBATCH --ntasks-per-node=16
#SBATCH --account=janeslab
#SBATCH --time=10
#SBATCH --mem=20G
#SBATCH --partition=standard

module load singularity

# SCRATCH_DIRECTORY=/scratch/${USER}
# ${SCRATCH_DIRECTORY}
SIF=/home/${USER}/vcell_misc/vcell_sif.sif
# ${SIF}, /path/to/save/singularity-image.sif
INPUT=/scratch/${USER}/vcell_in/vcml_files
# ${INPUT}, /path/to/input/omex/file.omex
OUTPUT=/scratch/${USER}/vcell_out
# ${OUTPUT}, /path/to/output/folder

singularity run ${SIF} convert -i ${INPUT}  -o ${OUTPUT} -vcml