#%%
import os
import numpy as np
import subprocess

VCEll_EXPORTS="/Users/smgroves/Box/Research/CPC_Model_Project/VCell_Exports"
# VCEll_EXPORTS="/Users/smgroves/Library/CloudStorage/Box-Box/Research/JanesLab/CPC_Model_Project/VCell_Exports"
#Update the simulation data
models = np.array([
    # "006_13_26 CPC_metacentric_transition_tensed_MCF10A_chr19_PMP1",
	# "006_13_26 CPC_metacentric_transition_tensed_MCF10A_chr19_PMP1",
    # "006_13_26 CPC_metacentric_transition_tensed_MCF10A_chr19_PMP1"
    "006_13_26 CPC_metacentric_MCF10A_chr19_PMP1_double_tensed_relaxed_v2"

	])


simulations = np.array([
	# "06_13_26_metacentric_transition_tensed_MCF10A_chr19_PMP1_t_5min",
	# "06_13_26_metacentric_transition_tensed_MCF10A_chr19_PMP1_t_0_high_t_res",
	# "06_13_26_metacentric_transition_tensed_MCF10A_chr19_PMP1_t_0"
	"06_19_26_metacentric_MCF10A_double_tensed_relaxed_chr19_PMP1_seconds"

        ])
 
simID = np.array([ 
	# "SimID_316523023_0__exported",
	# "SimID_316523021_0__exported",
	# "SimID_316523018_0__exported"
	# "SimID_316534873_0__exported"
	# "SimID_316812427_0__exported"
	"SimID_317322923_0__exported"
        ])

for i in range(len(models)):
	subprocess.run([
		"python",
		"/Users/smgroves/Documents/GitHub/VCell_Analysis/4_post_VCell_processing/hdf5_converter_Cata.py",
        	f"{simID[i]}.hdf5",
        	VCEll_EXPORTS,
        	models[i],
        	simulations[i]
	])  

