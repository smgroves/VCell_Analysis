# %%
import pandas as pd
import h5py
import os
import sys
import time
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from hdf5_converter_Rivanna import convert_h5_to_csvs_Logan_results

# %%
model_name = "_09_16_25_CPC_metacentric_relaxed_model"
dir_path = f"./vcell_out/{model_name}"
sedml_name = model_name
file_name = "reports.h5"
species_list = []
sim_key_name = "0"
overwrite = True
convert_h5_to_csvs_Logan_results(
    dir_path, model_name, sedml_name, file_name, species_list, sim_key_name, overwrite)

# %%
