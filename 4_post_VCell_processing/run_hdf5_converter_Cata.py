#%%
import os
import numpy as np
import subprocess

VCEll_EXPORTS="/Users/smgroves/Box/Research/CPC_Model_Project/VCell_Exports"

#Update the simulation data
models = np.array([
    "006_13_26 CPC_metacentric_transition_tensed_MCF10A_chr19_PMP1"
	])


simulations = np.array([
	"06_13_26_metacentric_transition_tensed_MCF10A_chr19_PMP1_t_0"
        ])
 
simID = np.array([ 
	"SimID_316455468_0__exported"
        ])

for i in range(len(models)):
	subprocess.run([
		"python",
		"/Users/smgroves/Documents/GitHub/VCell_Analysis/4_post_VCell_processing/hdf5_converter.py",
        	f"{simID[i]}.hdf5",
        	VCEll_EXPORTS,
        	models[i],
        	simulations[i]
	])  

