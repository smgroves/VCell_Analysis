# Comparing the outputs of TEST_10_16_23_CPC_tensed_RefModel_128x64_to_omex (which is just _10_16_23 on Rivanna due to naming constraints)
# They don't seem to be matching up at all so I want to compare each species initial conditions directly

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os
# for each simulation, for each species, plot the initial frame side by side
simID = "264596882"
param_scan = 0
gui_dir = f'/Users/smgroves/Box/CPC_Model_Project/VCell_Exports/SimID_{simID}_0__exported' #base
#SimID_264596885_0__exported CPCi IC scan
# cli_dir = '/Users/smgroves/Documents/GitHub/VCell_Analysis/vcell_out/_10_16_23/simulations/_10_16_23_tensed_RefModel_Mps1_phos_Plk1a_20Pac_transactiv/data'
cli_dir = "/Users/smgroves/Box/CPC_Model_Project/VCell_Rivanna_Exports/MaybeFixedResults_from_Logan_03_15_24_TEST_CPC_tensed/_10_16_23_tensed_RefModel_Mps1_phos_Plk1a_20Pac_transactiv/data"
default_species = ["Bub1a", "Bub1a_his","CPCa","CPCi", "H2A", "H3", "Haspina","Haspini","Knl1","Mps1a","Mps1i", "Ndc80",
            "Ndc80_Mps1a", "Ndc80_Mps1i", "Ndc80_pMps1a", "Ndc80_pMps1i", "pH2A","pH2A_Sgo1","pH2A_Sgo1_CPCa","pH2A_Sgo1_CPCi",
            "pH2A_Sgo1_pH3_CPCa", "pH2A_Sgo1_pH3_CPCi", "pH3","pH3_CPCa","pH3_CPCi","pKnl1","pKnl1_Bub1a","Plk1a","Plk1i",
            "pMps1a", "pMps1i", "pNdc80", "pNdc80_Mps1a", "pNdc80_Mps1i", "pNdc80_pMps1a", "pNdc80_pMps1i", "Sgo1"]
output = f"/Users/smgroves/Documents/GitHub/VCell_Analysis/vcell_out/cli_vs_gui_04_05_24/"
try:
    os.mkdir(output)
except FileExistsError: pass

for s in default_species:
    cli = pd.read_csv(f"{cli_dir}/SimID_{param_scan}__Slice_XY_0_{s}_0000.csv", skiprows=10)
    gui = pd.read_csv(f"{gui_dir}/SimID_{simID}_{param_scan}__Slice_XY_0_{s}_0000.csv", skiprows=10)
    fig, (ax1, ax2) = plt.subplots(1,2)
    plt.suptitle(s)
    vmax = (1 if np.max(cli)==0 and np.max(gui)==0 else np.max([np.max(cli),np.max(gui)]))
    sns.heatmap(gui, square = True, xticklabels = False, yticklabels = False, vmin = 0,
                vmax = vmax, cmap = 'rocket', ax = ax1)
    sns.heatmap(cli, square = True, xticklabels = False, yticklabels = False, vmin = 0,
                vmax = vmax, cmap = 'rocket', ax = ax2)
    ax1.set_title('VCell Interface')
    ax2.set_title('CLI on Rivanna')

    plt.savefig(f"{output}/{s}.png")
    plt.close()