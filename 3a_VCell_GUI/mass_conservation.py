# checking if mass is conserved over transition model, even though species are building up at KTs
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


def compute_total_mass(data_dir, species, timepoint, timestep=10):
    timeslice_id = ""
    if timepoint / timestep >= 10:
        timeslice_id = "00" + str(int(timepoint / timestep))
    else:
        timeslice_id = "000" + str(int(timepoint / timestep))

    total_mass = 0.0
    for file in os.listdir(data_dir):
        if species in file and timeslice_id in file:
            data = pd.read_csv(os.path.join(data_dir, file),
                               sep=",", skiprows=10, header=None)
            data_array = np.array(data)

            # Sum all values to compute total mass
            total_mass += np.sum(data_array)

    print(
        f"Total mass at timepoint {timepoint} seconds for {species}: {total_mass}")
    return total_mass


# Example usage

data_directory_transition = "/Users/smgroves/Documents/GitHub/VCell_Analysis/vcell_out/10_30_25_CPC_metacentric_transition_model/SimID_298553153_0__exported/"
data_directory_relaxed = "/Users/smgroves/Documents/GitHub/VCell_Analysis/vcell_out/_09_16_25_CPC_metacentric_relaxed_model/SimID_296945372_0__exported"
data_directory_tensed = "/Users/smgroves/Documents/GitHub/VCell_Analysis/vcell_out/09_16_25_CPC_metacentric_tensed_model_v2/SimID_296945950_0__exported"

species = "H3"

mass_relaxed = []
mass_tensed = []
mass_transition = []

timepoints = range(0, 500, 10)
for time_point in timepoints:  # seconds
    mass_relaxed.append(compute_total_mass(data_directory_relaxed,
                                           species, time_point, timestep=10))
    mass_tensed.append(compute_total_mass(data_directory_tensed,
                                          species, time_point, timestep=10))
init_relaxed = mass_relaxed[0]
mass_relaxed = mass_relaxed/init_relaxed
mass_tensed = mass_tensed/mass_tensed[0]
plt.plot(timepoints, mass_relaxed, marker='o', label='Relaxed Model')
plt.plot(timepoints, mass_tensed, marker='o', label='Tensed Model')

timepoints = range(21)
for time_point in timepoints:
    mass_transition.append(compute_total_mass(data_directory_transition,
                                              species, time_point, timestep=1))
mass_transition = mass_transition/init_relaxed
plt.plot([i + 100 for i in timepoints], mass_transition,
         marker='o', label='Transition Model')
plt.xlabel('Time (s)')
plt.ylabel(f'Scaled Total Mass of {species}')
plt.legend()
plt.title(f'Mass Conservation of {species} in Different Models')
plt.savefig(f"mass_conservation_{species}_models.png")
