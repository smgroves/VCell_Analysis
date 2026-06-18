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
relaxed_model = ss.load_model(vcml_file_relaxed)
double_chromosome = ss.build_double_chromosome(relaxed_model=relaxed_model, application="Spatial", left="relaxed", right="relaxed")
vc.write_vcml_file(double_chromosome, "/Users/smgroves/Documents/GitHub/VCell_Analysis/vcell_models/vcml/_006_13_26_CPC_metacentric_MCF10A_chr19_PMP1_double_relaxed.vcml")
