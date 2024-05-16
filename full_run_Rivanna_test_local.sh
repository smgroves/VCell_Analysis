echo $(date)

conda activate VCell_Analysis

MODEL_NAME=MaybeFixedResults

SEDML_NAME=TEST_10_16_23_CPC_tensed_RefModel_128x64_to_omex_SBML_units

OUTPUT=/Users/smgroves/Documents/GitHub/VCell_Analysis/vcell_out/${MODEL_NAME}

echo $OUTPUT

#Convert reports.h5 (in OUTPUT folder) to csvs in OUTPUT/simulation_name/data folder
echo "Convert reports.h5 to csvs"
# python hdf5_converter_Rivanna.py ${OUTPUT} ${MODEL_NAME} "reports.h5" ${SEDML_NAME} TRUE

for SIM_NAME in ${OUTPUT}/simulations/*/ ; do
    echo "$SIM_NAME"
    DATA=${SIM_NAME}
    PLOTS=${SIM_NAME}plots
    Rscript vcell_run_v3_CL.R $SIM_NAME $DATA $PLOTS -k "Tensed" -t 100 -I 10
done