#%%
import sys
import importlib
import time
import numpy as np
import pyvcell.vcml as vc
import sim_scripts as ss


# load model from vcml file
########################################
vcml_file_relaxed = "/Users/smgroves/Documents/GitHub/VCell_Analysis/vcell_models/vcml/_005_20_26_CPC_metacentric_relaxed_MCF10A_chr19_PMP1.vcml"
bio_model_r = ss.load_model(vcml_file_relaxed)

#%% try building tensed model and compare
print("Building tensed model from relaxed model...")
tensed_model = ss.build_tensed_model(relaxed_vcml_file=vcml_file_relaxed, application="Spatial")

#%%
# run each simulation of relaxed and tensed 
########################################
sim = bio_model_r.applications[0].simulations[0]
#testing params
sim.duration = 100.0
sim.output_time_step = 10.0

print("Running relaxed model simulation...")
result_relaxed = ss.run_simulation(biomodel=bio_model_r, simulation=sim.name, run_name="_005_20_26_CPC_metacentric_relaxed_MCF10A_chr19_PMP1_test_run", fields=None, local=True)
print(result_relaxed.solver_output_dir)
result_relaxed.plotter.plot_slice_2d(time_index=3, channel_id="CPCa")


print("Running tensed model simulation...")
sim = tensed_model.applications[0].simulations[0]
sim.duration = 100.0
sim.output_time_step = 10.0
result_tensed = ss.run_simulation(biomodel=tensed_model, simulation=sim.name, run_name="_005_20_26_CPC_metacentric_tensed_MCF10A_chr19_PMP1__from_pyvcell_test_run", fields=None, local=True)
print(result_tensed.solver_output_dir)
result_tensed.plotter.plot_slice_2d(time_index=3, channel_id="CPCa")

print("Building transition model from relaxed model...")
transition_model = ss.build_transition_model(relaxed_vcml_file=vcml_file_relaxed, field_data_dir=result_relaxed.solver_output_dir, application="Spatial")
sim = transition_model.applications[0].simulations[0]
result_transition = ss.run_simulation(biomodel=transition_model, simulation=sim.name, run_name="_005_20_26_CPC_metacentric_transition_MCF10A_chr19_PMP1__from_pyvcell_test_run", fields=None, local=True)
print(result_transition.solver_output_dir)
result_transition.plotter.plot_slice_2d(time_index=3, channel_id="CPCa")
#%%
# compare old models

# bio_model_relaxed = ss.load_model("/Users/smgroves/Documents/GitHub/VCell_Analysis/vcell_models/vcml/_02_23_26_CPC_metacentric_relaxed_MCF10A_chr19_PMP1.vcml")

# bio_model_transition = ss.load_model("/Users/smgroves/Documents/GitHub/VCell_Analysis/vcell_models/vcml/_02_23_26_CPC_metacentric_transition_MCF10A_chr19_PMP1.vcml")
# ss.compare_models(bio_model_relaxed, bio_model_transition, name1="Relaxed", name2="Transition", verbose=1)
# %%
