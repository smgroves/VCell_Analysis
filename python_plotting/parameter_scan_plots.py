import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
in_dir = "/Users/smgroves/Box/CPC_Model_Project/vcell_plots"

def lineplot(species, in_dir, sim_prefix, name_scan, num_scans, xmax = None, xmin = 0, log = False,
             location = 'ic',column = "Sum_Active", active = 'active', name = None):
    plot_data = pd.DataFrame()
    if xmax is not None:
        step = (xmax - xmin) / (num_scans - 1)
        param_range = np.arange(start=xmin, stop=xmax+step, step=step)
    else:
        param_range = np.arange(num_scans)
    for i in range(num_scans):
        # if i == 5: continue
        param = param_range[i]
        tmp = pd.read_csv(f"{in_dir}/{sim_prefix}{i}/data/data_{active}_{location}_{species}.csv", header = 0, index_col = None)
        tmp['Time'] = 10*tmp['Time']
        tmp['parameter'] = param
        plot_data = pd.concat([plot_data,tmp[['parameter',column, 'Time']]], ignore_index=True)
    ax = sns.lineplot(x = plot_data['Time'].to_numpy(), y= plot_data[column].to_numpy(), hue = plot_data['parameter'].to_numpy())
    plt.xlabel("Time (s)")
    if name is not None:
        plt.ylabel(f"{name} Concentration (uM)")
        plt.title(f"{name} Concentration over {plot_data['Time'].max()} seconds")

    else:
        if column.startswith('Sum'):
            plt.ylabel(f"Sum of {active} {species} Concentration (uM)")
            plt.title(f"Sum of {active} {species} Concentration over {plot_data['Time'].max()} seconds \n"
                      f"Parameter scan over {name_scan}")
        else:
            plt.ylabel(f"{species} Concentration (uM)")
            plt.title(f"{species} Concentration over {plot_data['Time'].max()} seconds")

    if xmax is not None:
        norm = plt.Normalize(xmin, xmax)
    else:
        norm = plt.Normalize(0, 100)
    sm = plt.cm.ScalarMappable(cmap=sns.cubehelix_palette(as_cmap=True), norm=norm)
    sm.set_array([])
    # Remove the legend and add a colorbar (optional)
    ax.get_legend().remove()
    if xmax is not None:
        ax.figure.colorbar(sm, label = f"{name_scan} (uM)", ticks=param_range)
    else:
        ax.figure.colorbar(sm, label = f"{name_scan} (%)")
    plt.tight_layout()
    plt.show()
#
# sim_prefix = "03_08_24_relaxed_RefModel_Bub1_scan"
# name_scan = 'Bub1 IC'
# num_scans = 11
# log = False
# xmin = 0
# xmax = 0.03*13.587
# lineplot('CPC', in_dir, sim_prefix, name_scan, num_scans, xmax)

# sim_prefix = "03_08_24_relaxed_RefModel_Knl1_scan"
# name_scan = 'Knl1 IC'
# num_scans = 10
# log = False
# xmin = 0
# xmax = 12*15
# lineplot('CPC', in_dir, sim_prefix, name_scan, num_scans, xmax)

sim_prefix = "02_19_24_relaxed_RefModel_Mps1_phos_Plk1a_20Pac_transactiv_CPCi_scan_FIXED_not20Pac "
name_scan = 'CPCi IC'
num_scans = 11
log = False
xmin = 0
xmax = 1.065
lineplot('CPC', in_dir, sim_prefix, name_scan, num_scans, xmax)
