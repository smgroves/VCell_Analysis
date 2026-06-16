#%%
from cmath import phase
import sys
import importlib
import time
from colorama import Fore
import numpy as np
import pyvcell.vcml as vc
import sim_scripts as ss
from colorama import Style, init
init(autoreset=True) # Automatically resets color after every print
# Record the start time

# load model from vcml file
########################################
model_name = "_006_02_26_CPC_metacentric_relaxed_MCF10A_chr19_PMP1"
vcml_file = f"/Users/smgroves/Documents/GitHub/VCell_Analysis/vcell_models/vcml/{model_name}.vcml"
bio_model = ss.load_model(vcml_file)

# print(patches.verify_patch())

#%%
# print(bio_model)
# run a single simulation
########################################
for i in [0,1]:
    sim = bio_model.applications[0].simulations[i]
    print(sim.mesh_size)

    sim = bio_model.applications[0].simulations[0]
    print(f"{Fore.GREEN}Running relaxed {sim.name} with sim.duration={sim.duration} and sim.output_time_step={sim.output_time_step}...{Style.RESET_ALL}")
    results  = ss.run_simulation(biomodel= bio_model, simulation=sim.name,
                                    run_name=f"{model_name}_{sim.name}", fields=None, local=True, overwrite=True)
    print(results.solver_output_dir)
    results.plotter.plot_slice_2d(10, "CPCa", 0)
    ss.export_result_to_csv(results)

