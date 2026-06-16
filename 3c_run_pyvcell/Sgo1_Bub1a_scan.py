# %%
import warnings
warnings.filterwarnings("ignore")
import sim_scripts as ss
import pyvcell.vcml as vc
import numpy as np
import pandas as pd
from colorama import Fore, Style, init
init(autoreset=True) # Automatically resets color after every print

chr = "chr19"
phase = "PMP1"
KT_loc = "metacentric"
run_tensed = True
run_transition = False


########################################
# load model from vcml file
########################################
vcml_file_relaxed = "/Users/smgroves/Documents/GitHub/VCell_Analysis/vcell_models/vcml/_005_20_26_CPC_metacentric_relaxed_MCF10A_chr19_PMP1.vcml"
bio_model = ss.load_model(vcml_file_relaxed)

########################################
# run each simulation of relaxed and tensed
########################################
# output a csv file for each simulation with the gridpoints, chr#, phase, length, scaling factor
# save vcml files in output_dir for each simulation for reproducibility

state ="relaxed"
relaxed_model = ss.build_chromosome(relaxed_model=bio_model, chr=chr, phase=phase, KT_loc=KT_loc)
sim = relaxed_model.applications[0].simulations[0]
print(f"{Fore.GREEN}Running relaxed model simulation with sim.duration={sim.duration} and sim.output_time_step={sim.output_time_step}...{Style.RESET_ALL}")
result_relaxed = ss.run_simulation(biomodel=relaxed_model, simulation=sim.name,
                                   run_name=f"_005_20_26_CPC_metacentric_relaxed_MCF10A_{chr}_{phase}_{state}", fields=None, local=True, overwrite=True)
print(result_relaxed.solver_output_dir)
result_relaxed.plotter.plot_slice_2d(10, "CPCa", 0)

# Export spatial CSVs (one per species per timepoint) to workspace/run_name/exported/
ss.export_result_to_csv(result_relaxed)

if run_tensed:
    state="tensed"
    print(f"{Fore.GREEN}Building tensed model from relaxed model...{Style.RESET_ALL}")
    tensed_model = ss.build_tensed_model(relaxed_model, application="Spatial")
    sim = tensed_model.applications[0].simulations[0]
    print(f"{Fore.GREEN}Running tensed model simulation with sim.duration={sim.duration} and sim.output_time_step={sim.output_time_step}...{Style.RESET_ALL}")
    result_tensed = ss.run_simulation(biomodel=tensed_model, simulation=sim.name,
                                  run_name=f"_005_20_26_CPC_metacentric_tensed_MCF10A_{chr}_{phase}_{state}", fields=None, local=True, overwrite=True)
    print(result_tensed.solver_output_dir)
    result_tensed.plotter.plot_slice_2d(10, "CPCa", 0)

    # Export spatial CSVs to workspace/run_name/exported/
    ss.export_result_to_csv(result_tensed)


# print(f"{Fore.GREEN}Building transition model from relaxed model...{Style.RESET_ALL}")
# transition_model = ss.build_transition_model(
#     relaxed_model=relaxed_model, field_data_dir="_005_20_26_CPC_metacentric_relaxed_MCF10A_chr19_PMP1_test_run", application="Spatial", t_transition=30)
# print(f"{Fore.GREEN}Running transition model simulation...{Style.RESET_ALL}")
# result_transition = ss.run_simulation(biomodel=transition_model, simulation=sim.name,
#                                       run_name="_005_20_26_CPC_metacentric_transition_MCF10A_chr19_PMP1__from_pyvcell_test_run", fields=None, local=True, overwrite=True)
# print(result_transition.solver_output_dir)
# result_transition.plotter.plot_slice_2d(10, "CPCa", 0)
# ss.export_result_to_csv(result_transition)


# %%
