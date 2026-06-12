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
vcml_file_relaxed = "/Users/smgroves/Documents/GitHub/VCell_Analysis/vcell_models/vcml/_006_10_26_CPC_metacentric_relaxed_MCF10A_chr19_PMP1.vcml"
relaxed_model = ss.load_model(vcml_file_relaxed)
transition_model = ss.build_transition_model(relaxed_model=relaxed_model, field_data_dir="_006_10_26_CPC_metacentric_relaxed_MCF10A_chr19_PMP1", application="Spatial", t_transition=100)
#save transition_model to vcml file
vc.write_vcml_file(transition_model, "_006_10_26_CPC_metacentric_transition_MCF10A_chr19_PMP1.vcml")
