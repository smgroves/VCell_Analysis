#!/bin/bash
#SBATCH -N 1
#SBATCH --ntasks-per-node=16
#SBATCH --account=janeslab
#SBATCH --time=10:00:00
#SBATCH --mem=50G
#SBATCH --partition=standard

module load singularity
module load anaconda
module load R/4.2.1

# activate conda environment
source activate vcell #needs pandas, h5py, python

# run simulation with VCell CLI on Rivanna
# SCRATCH_DIRECTORY=/scratch/${USER}
# ${SCRATCH_DIRECTORY}
MODEL=_10_16_23_CPC_relaxed_RefModel.omex

SIF=/home/${USER}/vcell_misc/vcell_sif.sif
# ${SIF}, /path/to/save/singularity-image.sif
INPUT=/scratch/${USER}/vcell_in/${MODEL}
# ${INPUT}, /path/to/input/omex/file.omex
OUTPUT=/scratch/${USER}/vcell_out/${MODEL}
mkdir ${OUTPUT}
# ${OUTPUT}, /path/to/output/folder

singularity run ${SIF} -i ${INPUT} -o ${OUTPUT}

SIMID=### #TODO add simulation id!
SIMNAME=### #TODO add simulation name!
#output into OUTPUT folder should generate an hdf5 
python hdf5_converter.py ${SIMID} ${OUTPUT} ${MODEL} ${SIM_NAME}

Rscript vcell_plotting.R #add arguments
