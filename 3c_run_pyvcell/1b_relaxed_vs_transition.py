# %%
import warnings
warnings.filterwarnings("ignore")
import sim_scripts as ss
import pyvcell.vcml as vc
import numpy as np
import pandas as pd
from colorama import Fore, Style, init
init(autoreset=True) # Automatically resets color after every print

#TODO:
## make a telocentric version
# make a csv to read in parameter scans, etc.; add a suffix to the folder names that takes in param scan values, etc. for better organization and to avoid overwriting results
#read in IC csv
#make an option to not run tensed

#TODO: option to run plotting code
# TODO: run in a loop on rivanna: all chr and all phases 
#TODO: add R plotting code; use input variables from here to run the code
# TODO: organize plots with tensed/relaxed folder inside results dir, and with subfolders for each chromosome and phase.
#TODO: make a pdf of all heatmaps combined
#TODO: fix plot for troubleshooting regions in r code; calculations are correct but plot is not
# TODO: Sgo1 abundance and Bub1 catalytic activity perturbations 

# load model from vcml file
########################################
vcml_file_relaxed = "/Users/smgroves/Documents/GitHub/VCell_Analysis/vcell_models/vcml/_005_20_26_CPC_metacentric_relaxed_MCF10A_chr19_PMP1.vcml"
# this model should have rxns, parameters, compartments, and at least one application as defaults.

#output name convention:
# sim_name_{chr}_{phase}_{state}_{KT_loc}_{suffix}

#suffix should incluce parameter scan values, etc. for better organization and to avoid overwriting results

# - The geometry can be set with functions in sim_scripts
# - IC can be set from a CSV
# - kinetic parameters can be set from a CSV
# - relaxed vs. tensed. transition models can all be made for a specific chromosome (chr1-chr22, chrX, or chrY)
# - during a specific phase: PMP1, PMP2, PMP3, PMP4, or Metaphase

#%%
bio_model = ss.load_model(vcml_file_relaxed)
chr = "chr19"
phase = "PMP1"
KT_loc = "metacentric"
relaxed_model = ss.build_chromosome(relaxed_model=bio_model, chr=chr, phase=phase, KT_loc=KT_loc)

# relaxed_model = bio_model
# set testing params
# sim = relaxed_model.applications[0].simulations[0]
# sim.duration = 30.0 #this will be set for relaxed and tensed models
# sim.output_time_step = 10.0
#%%
# run each simulation of relaxed and tensed
########################################
# make a csv file for each simulation with the gridpoints, chr#, phase, length, scaling factor,
#
state ="relaxed"
sim = relaxed_model.applications[0].simulations[0]
print(f"{Fore.GREEN}Running relaxed model simulation with sim.duration={sim.duration} and sim.output_time_step={sim.output_time_step}...{Style.RESET_ALL}")
result_relaxed = ss.run_simulation(biomodel=relaxed_model, simulation=sim.name,
                                   run_name=f"_005_20_26_CPC_metacentric_relaxed_MCF10A_{chr}_{phase}_{state}", fields=None, local=True, overwrite=True)
print(result_relaxed.solver_output_dir)
result_relaxed.plotter.plot_slice_2d(10, "CPCa", 0)

state="tensed"
print(f"{Fore.GREEN}Building tensed model from relaxed model...{Style.RESET_ALL}")
tensed_model = ss.build_tensed_model(relaxed_model, application="Spatial")
sim = tensed_model.applications[0].simulations[0]
print(f"{Fore.GREEN}Running tensed model simulation with sim.duration={sim.duration} and sim.output_time_step={sim.output_time_step}...{Style.RESET_ALL}")
result_tensed = ss.run_simulation(biomodel=tensed_model, simulation=sim.name,
                                  run_name=f"_005_20_26_CPC_metacentric_tensed_MCF10A_{chr}_{phase}_{state}", fields=None, local=True, overwrite=True)
print(result_tensed.solver_output_dir)
result_tensed.plotter.plot_slice_2d(10, "CPCa", 0)

# print(f"{Fore.GREEN}Building transition model from relaxed model...{Style.RESET_ALL}")
# transition_model = ss.build_transition_model(
#     relaxed_model=relaxed_model, field_data_dir="_005_20_26_CPC_metacentric_relaxed_MCF10A_chr19_PMP1_test_run", application="Spatial", t_transition=30)
# print(f"{Fore.GREEN}Running transition model simulation...{Style.RESET_ALL}")
# result_transition = ss.run_simulation(biomodel=transition_model, simulation=sim.name,
#                                       run_name="_005_20_26_CPC_metacentric_transition_MCF10A_chr19_PMP1__from_pyvcell_test_run", fields=None, local=True, overwrite=True)
# print(result_transition.solver_output_dir)
# result_transition.plotter.plot_slice_2d(10, "CPCa", 0)

# %%
