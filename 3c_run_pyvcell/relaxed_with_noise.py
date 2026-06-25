# %%
import random
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

########################################
# load model from vcml file
########################################
vcml_file_relaxed = "/Users/smgroves/Documents/GitHub/VCell_Analysis/vcell_models/vcml/_006_13_26_CPC_metacentric_relaxed_MCF10A_chr19_PMP1_fortransition.vcml"
bio_model = ss.load_model(vcml_file_relaxed)


########################################
# Make perturbations to the model
########################################

# Inspect what will be perturbed
params = ss.get_all_numeric_parameters(bio_model)
for name, val in params.items():
    print(f"{name}: {val}")
#%%
# Run an ensemble, recording all perturbed values
relaxed_model = ss.build_chromosome(relaxed_model=bio_model, chr=chr, phase=phase, KT_loc=KT_loc)
sim = relaxed_model.applications[0].simulations[0]

cv = 0.1
records = []
for i in range(20):
    brcd = random.randint(1, 1000)

    perturbed_model, values = ss.perturb_parameters(relaxed_model, cv=cv, seed=brcd)
    print({"run": i, **values})

    result = ss.run_simulation(perturbed_model, sim.name, run_name=f"ensemble_run{i}_brcd{brcd}")
    ss.export_result_to_csv(result)

    row = pd.DataFrame([{"run": i, "seed": brcd, "cv": cv, "result_dir": str(result.solver_output_dir), **values}])
    row.to_csv("ensemble_parameters.csv", mode='a', header=(i == 0), index=False)
