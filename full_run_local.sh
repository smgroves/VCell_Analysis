#!/bin/bash

# activate conda environment
# conda activate VCell_Analysis #needs pandas, h5py, python

# run simulation with VCell CLI on Rivanna
# SCRATCH_DIRECTORY=/scratch/${USER}
# ${SCRATCH_DIRECTORY}
MODEL_NAME=_06_23_23_model1
MODEL=${MODEL_NAME}.omex

# SIF=/home/${USER}/vcell_misc/vcell_sif.sif
# ${SIF}, /path/to/save/singularity-image.sif
# INPUT=/scratch/${USER}/vcell_in/${MODEL}
# ${INPUT}, /path/to/input/omex/file.omex
OUTPUT=/Users/smgroves/Documents/GitHub/VCell_Analysis/vcell_out/${MODEL_NAME}
mkdir ${OUTPUT}
# ${OUTPUT}, /path/to/output/folder

# singularity run ${SIF} -i ${INPUT} -o ${OUTPUT}

#Convert reports.h5 (in OUTPUT folder) to csvs in OUTPUT/simulation_name/data folder
python hdf5_converter_Rivanna.py ${OUTPUT} ${MODEL_NAME} "reports.h5"


# Uses csvs in OUTPUT/{sim_name}/data folder to create plots in OUTPUT/{sim_name}/plots folder
    # if there are parameter scans, they will be in subfolders numerically
for SIM_NAME in ${OUTPUT}/*/ ; do
    echo "$SIM_NAME"
    DATA=${SIM_NAME}
    PLOTS=${SIM_NAME}plots
    Rscript vcell_run_v3_CL.R $SIM_NAME $DATA $PLOTS

done
