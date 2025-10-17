# %%
import time
import numpy as np
import patches
import pyvcell.vcml as vc

# Record the start time
start_time = time.perf_counter()

# %% load model from vcml file
########################################

vcml_file = "/Users/smgroves/Documents/GitHub/VCell_Analysis/vcell_models/vcml/_09_16_25_CPC_metacentric_tensed_model.vcml"
bio_model = vc.load_vcml_file(vcml_file)


model = bio_model.model
print(bio_model)
print(model.parameter_values)

# %% run a single simulation
########################################
# sim = bio_model.applications[0].simulations[0]
# print(sim.mesh_size)


# sims = [sim for app in bio_model.applications for sim in app.simulations]

# result = vc.simulate(biomodel=bio_model, simulation=sims[0].name)

# print(result.solver_output_dir)
# print([c.label for c in result.channel_data])

# result.plotter.plot_slice_3d(time_index=3, channel_id="s1")
# result.plotter.plot_concentrations()
# result.cleanup()

# # %% run a loop of simulations
# ########################################

# # take N samples from normal distribution for CPC_ic
# N = 1
# CPCi_ic_values = np.random.normal(loc=4.52, scale=1.0, size=N)

# # run N simulations and store results
# all_results = []
# for val in CPCi_ic_values:
#     model.set_parameter_value("CPCi_ic", val)
#     print(f"running sim with CPCi_ic={val}")
#     all_results.append(vc.simulate(bio_model, sim.name))

# # Record the end time
# end_time = time.perf_counter()

# # Calculate the elapsed time
# elapsed_time = end_time - start_time

# print(f"{N} simulation[s] executed in {elapsed_time:.6f} seconds")
