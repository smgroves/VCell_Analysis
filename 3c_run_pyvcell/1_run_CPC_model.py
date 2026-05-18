import sys
import importlib
import time
import numpy as np
import pyvcell.vcml as vc


# Record the start time
start_time = time.perf_counter()

# load model from vcml file
########################################
vcml_file = "/Users/smgroves/Documents/GitHub/VCell_Analysis/vcell_models/vcml/_09_16_25_CPC_metacentric_relaxed_model_v2.vcml"
bio_model = vc.load_vcml_file(vcml_file)
# print(patches.verify_patch())

model = bio_model.model
# print(bio_model)
# run a single simulation
########################################
sim = bio_model.applications[0].simulations[0]
print(sim.mesh_size)
bio_model.applications[0].simulations[0].duration = 20.0
bio_model.applications[0].simulations[0].output_time_step = 10.0


# sims = [sim for app in bio_model.applications for sim in app.simulations]

result = vc.simulate(biomodel=bio_model, simulation=sim.name)

print(result.solver_output_dir)
print([c.label for c in result.channel_data])

result.plotter.plot_slice_2d(time_index=3, channel_id="CPCa")
result.plotter.plot_concentrations()
result.cleanup()

# Record the end time
end_time = time.perf_counter()

# Calculate the elapsed time
elapsed_time = end_time - start_time

print(f"Simulations executed in {elapsed_time:.6f} seconds")

