import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
in_dir = "/Users/smgroves/Box/CPC_Model_Project/vcell_plots"
import matplotlib as m
import os
def lineplot(species, in_dir, sim_prefix, name_scan, num_scans, xmax = None, xmin = 0, log = False,
             location = 'ic',column = "Sum_Active", active = 'active', name = None, suffix = "",
             highlight = None, name_folder = "", palette = sns.color_palette("Spectral", as_cmap=True)):

    if os.path.isdir(f"./figures/lineplot_param_scans/{name_folder}"):
        pass
    else:
        os.makedirs(f"./figures/lineplot_param_scans/{name_folder}")
    plot_data = pd.DataFrame()

    if log:
        param_range = np.logspace(start = np.log10(xmin), stop = np.log10(xmax), num = num_scans, endpoint = True)
    else:
        if xmax is not None:
            step = (xmax - xmin) / (num_scans - 1)
            param_range = np.arange(start=xmin, stop=xmax+step, step=step)
        else:
            param_range = np.arange(num_scans)

    if active == 'all':
        for i in range(num_scans):
            # if i == 5: continue
            param = param_range[i]
            tmp = pd.read_csv(f"{in_dir}/{sim_prefix}{i}/data/data_{location}_{species}.csv", header=0,
                              index_col=None)
            tmp['Time'] = 10 * tmp['Time']
            tmp['parameter'] = param
            tmp['all'] = tmp[list(set(tmp.columns).difference({"Time",'parameter'}))].sum(axis = 1)
            plot_data = pd.concat([plot_data, tmp[['parameter', 'all', 'Time']]], ignore_index=True)
            column = 'all'
    else:
        if active == 'inactive' and column == 'Sum_Active':
            column = 'Sum_Inactive'
        if active == 'active' and column == 'Sum_Inactive':
            column = 'Sum_Active'
        for i in range(num_scans):
            # if i == 5: continue
            param = param_range[i]
            tmp = pd.read_csv(f"{in_dir}/{sim_prefix}{i}/data/data_{active}_{location}_{species}.csv", header=0,
                              index_col=None)
            tmp['Time'] = 10 * tmp['Time']
            tmp['parameter'] = param
            plot_data = pd.concat([plot_data, tmp[['parameter', column, 'Time']]], ignore_index=True)


    if log:
        ax = sns.lineplot(x = plot_data['Time'].to_numpy(), y= plot_data[column].to_numpy(), hue = plot_data['parameter'].to_numpy(),
                      hue_norm=m.colors.LogNorm(), palette = palette)
    else:
        ax = sns.lineplot(x=plot_data['Time'].to_numpy(), y=plot_data[column].to_numpy(),
                          hue=plot_data['parameter'].to_numpy(),palette = palette)
    plt.xlabel("Time (s)")
    if name is not None:
        plt.ylabel(f"{name} Concentration (uM)")
        plt.title(f"{name} Concentration in {location.upper()} over {plot_data['Time'].max()} seconds")

    else:
        if column.startswith('Sum'):
            plt.ylabel(f"Sum of {active} {species} Concentration (uM)")
            plt.title(f"Sum of {active} {species} Concentration in {location.upper()} over {plot_data['Time'].max()} seconds \n"
                      f"Parameter scan over {name_scan}")
        else:
            plt.ylabel(f"{species} Concentration (uM)")
            plt.title(f"{species} Concentration in {location.upper()} over {plot_data['Time'].max()} seconds")

    if highlight is not None:
        if active == 'all':
            tmp = pd.read_csv(f"{in_dir}/{highlight}/data/data_{location}_{species}.csv", header=0,
                              index_col=None)
            tmp['all'] = tmp[list(set(tmp.columns).difference({"Time",'parameter'}))].sum(axis = 1)

        else:
            tmp = pd.read_csv(f"{in_dir}/{highlight}/data/data_{active}_{location}_{species}.csv", header=0, index_col=None)
        tmp['Time'] = 10 * tmp['Time']

        sns.lineplot(x = tmp['Time'].to_numpy(), y= tmp[column].to_numpy(), color = 'black',linestyle = "dotted", ax = ax, legend=False)


    if log:
        norm = m.colors.LogNorm(xmin, xmax)
    else:
        if xmax is not None:
            norm = plt.Normalize(xmin, xmax)
        else:
            norm = plt.Normalize(0, 100)
    # old color palette: sns.cubehelix_palette(as_cmap=True)
    sm = plt.cm.ScalarMappable(cmap=palette, norm=norm)
    sm.set_array([])
    # Remove the legend and add a colorbar (optional)
    ax.get_legend().remove()
    if xmax is not None:
        ax.figure.colorbar(sm, label = f"{name_scan} (uM)", ticks=param_range)
    else:
        ax.figure.colorbar(sm, label = f"{name_scan} (%)")
    plt.tight_layout()
    plt.savefig(f"./figures/lineplot_param_scans/{name_folder}/scan-{name_scan}_species-{species}_loc-{location}{suffix}.png")
    # plt.show()
    plt.close()
#
# in_dir_ = "/Users/smgroves/Box/CPC_Model_Project/VCell_Exports/From_Catalina/Bub1_plots"
# sim_prefix = "03_21_24_relaxed_RefModel_Bub1_scan_"
# name_scan = 'Bub1 IC'
# num_scans = 11
# xmax = 0.03*13.587
# lineplot('CPC', in_dir_, sim_prefix, name_scan, num_scans, xmax, location='ic')
# lineplot('CPC', in_dir_, sim_prefix, name_scan, num_scans, xmax, location='kt')

# in_dir_ = "/Users/smgroves/Box/CPC_Model_Project/VCell_Exports/From_Catalina/Knl1_plots/Bub1_0.006"
# sim_prefix = "03_21_24_relaxed_RefModel_Bub10.006_Knl1_"
# name_scan = 'Knl1 IC'
# num_scans = 10
# xmax = 12*15
# lineplot('CPC', in_dir_, sim_prefix, name_scan, num_scans, xmax, location = 'kt', suffix = '_Bub1_0.006')
# lineplot('CPC', in_dir_, sim_prefix, name_scan, num_scans, xmax, location = 'ic', suffix = '_Bub1_0.006')

# sim_prefix = "02_19_24_relaxed_RefModel_Mps1_phos_Plk1a_20Pac_transactiv_CPCi_scan_FIXED_not20Pac "
# name_scan = 'CPCi IC'
# num_scans = 11
# log = False
# xmin = 0
# xmax = 1.065
# lineplot('CPC', in_dir, sim_prefix, name_scan, num_scans, xmax, location='ic')

# sim_prefix = "04_01_24_relaxed_RefModel_Bub1_his_scan"
# name_scan = 'Bub1a_his_KD'
# num_scans = 6
# xmin = 0.001
# xmax = 100
# lineplot('CPC', in_dir, sim_prefix, name_scan, num_scans, xmax = xmax, xmin = xmin,
#          location='ic', log = True, active = 'all',
#          suffix = '_all',
#          highlight = "04_01_24_relaxed_RefModel_Bub1_his_scan3",
#          name_folder="Bub1-his-scan-relaxed_rainbow")

# sim_prefix = "04_01_24_relaxed_RefModel_Bub1_his_kd_0.001_Knl1_scan"
# in_dir_ = "/Users/smgroves/Box/CPC_Model_Project/vcell_plots/"
# name_scan = 'Knl1 IC'
# num_scans = 10
# xmax = 12*15
# lineplot('CPC', in_dir_, sim_prefix, name_scan, num_scans, xmax, location = 'kt', suffix = '_Bub1_his_kd_0.001')
# lineplot('CPC', in_dir_, sim_prefix, name_scan, num_scans, xmax, location = 'ic', suffix = '_Bub1_his_kd_0.001')
#
# sim_prefix = "04_01_24_tensed_RefModel_Bub1_his_scan"
# name_scan = 'Bub1a_his_KD'
# num_scans = 6
# xmin = 0.001
# xmax = 100
# lineplot('CPC', in_dir, sim_prefix, name_scan, num_scans, xmax = xmax, xmin = xmin,
#          location='kt', log = True, active = 'all',
#          suffix = '_all',
#          highlight = "04_01_24_tensed_RefModel_Bub1_his_scan3",
#          name_folder="Bub1-his-scan-tensed_rainbow")

##### Comparing old and new geometry
##### Comparing extra reactions
def plot_across_models(species, plot_list, in_dir,  name_list = [], location = 'ic',column = "Sum_Active", active = 'active',
                       name = None, name_plot="", name_folder =""):
    print("Plotting across models")
    if os.path.isdir(f"/Users/smgroves/Documents/GitHub/VCell_Analysis/plotting_functions/figures/lineplot_across_sims/{name_folder}"):
        pass
    else:
        os.makedirs(f"/Users/smgroves/Documents/GitHub/VCell_Analysis/plotting_functions/figures/lineplot_across_sims/{name_folder}")
        print(f"Made folder {name_folder}")
    # plot_list = sorted(plot_list)
    plot_data = pd.DataFrame()
    if len(name_list) == 0:
        name_list = plot_list
    if active == 'all':
        for n, p in zip(name_list,plot_list):
            tmp = pd.read_csv(f"{in_dir}/{p}/data/data_{location}_{species}.csv", header = 0, index_col = None)
            tmp['Time'] = 10*tmp['Time']
            tmp['parameter'] = n
            tmp['all'] = tmp[list(set(tmp.columns).difference({"Time",'parameter'}))].sum(axis = 1)
            plot_data = pd.concat([plot_data,tmp[['parameter','all', 'Time']]], ignore_index=True)
            column = 'all'
    else:
        if active == 'inactive' and column == 'Sum_Active':
            column = 'Sum_Inactive'
        if active == 'active' and column == 'Sum_Inactive':
            column = 'Sum_Active'
        for p in plot_list:
            tmp = pd.read_csv(f"{in_dir}/{p}/data/data_{active}_{location}_{species}.csv", header = 0, index_col = None)
            tmp['Time'] = 10*tmp['Time']
            tmp['parameter'] = p
            plot_data = pd.concat([plot_data,tmp[['parameter',column, 'Time']]], ignore_index=True)
    fig = plt.figure(figsize = (4,3))
    print(plot_data.loc[plot_data["Time"]==500][column])
    ax = sns.lineplot(x = plot_data['Time'].to_numpy(), y= plot_data[column].to_numpy(), hue = plot_data['parameter'].to_numpy())
    ax.set_xlim(0,500)
    ax.set_ylim(0,6)

    plt.xlabel("Time (s)")
    if name is not None:
        plt.ylabel(f"{name} Concentration (uM)")
        plt.title(f"{name} Concentration in {location.upper()} over {plot_data['Time'].max()} seconds")
    else:
        if column.startswith('Sum'):
            plt.ylabel(f"Sum of {active} {species} Concentration (uM)")
            plt.title(f"Sum of {active} {species} Concentration in {location.upper()} over {plot_data['Time'].max()} seconds")
        else:
            plt.ylabel(f"{species} Concentration (uM)")
            plt.title(f"{species} Concentration in {location.upper()} over {plot_data['Time'].max()} seconds")

    # ax.legend(loc='center left', bbox_to_anchor=(1.25, 0.5), ncol=1)
    plt.tight_layout()
    print("saving fig")
    # plt.savefig(f"/Users/smgroves/Documents/GitHub/VCell_Analysis/plotting_functions/figures/lineplot_across_sims/{name_folder}/{name_plot}-{species}_loc-{location}.pdf")
    plt.show()
    plt.close()

# in_dir_ = "/Users/smgroves/Box/CPC_Model_Project/VCell_Exports/From_Catalina/CPC_plots"
# plot_list = ['03_21_24_relaxed_RefModel_128x64_ref_grid_sarah', '03_21_24_relaxed_RefModel_DependentParameters']
# plot_across_models('CPC', plot_list, in_dir_, location='ic',name_plot="dependent_params_inactive",active= 'inactive')
# plot_across_models('CPC', plot_list, in_dir_, location='kt',name_plot="dependent_params_inactive",active= 'inactive')

# plot_list = ['03_21_24_relaxed_RefModel_DependentParameters','03_21_24_relaxed_RefModel_HaspinRxn2',
#              '03_21_24_relaxed_RefModel_Knl1Haspin_Rnx2','03_21_24_relaxed_RefModel_Knl1Rnx2']
# plot_across_models('CPC', plot_list, in_dir_, location='ic',name_plot="extra_rxns_inactive",active= 'inactive')
# plot_across_models('CPC', plot_list, in_dir_, location='kt', name_plot="extra_rxns_inactive",active= 'inactive')
#
# in_dir_ = "/Users/smgroves/Box/CPC_Model_Project/VCell_Exports/From_Catalina/Sgo1_plots"
# plot_list = ["CPC 50%",'03_21_24_relaxed_RefModel_Knl1Haspin_Rnx2','03_21_24_relaxed_RefModel_Sgo1_50P', '03_21_24_relaxed_RefModel_Sgo1_50P_CPC50P',
#              '03_21_24_relaxed_RefModel_Sgo1_50P_Haspin50P','03_21_24_relaxed_RefModel_Sgo1_50P_Plk150P']
# plot_across_models('CPC', plot_list, in_dir_, location='ic',name_plot="Sgo1_plots_all_active",active= 'active')
# plot_across_models('CPC', plot_list, in_dir_, location='kt',name_plot="Sgo1_plots_all_active",active= 'active')
#
# in_dir_ = "/Users/smgroves/Box/CPC_Model_Project/VCell_Exports/From_Catalina/Sgo1_plots/Sgo1_CPC"
# plot_list = ["03_21_24_relaxed_RefModel_64rxns", '03_21_24_relaxed_RefModel_Sgo1_50P']
#             #  "03_21_24_relaxed_RefModel_CPC50_inh","03_21_24_relaxed_RefModel_Sgo1_50P_CPC50_inh"]
# # name_list = ["Base Model",  "Sgo1+/-", "50% CPC Inh","50% CPC Inh + Sgo1+/-"]
# name_list = ["Base Model",  "Sgo1+/-"]

# print(plot_list)
# plot_across_models('CPC', plot_list, in_dir_, name_list= name_list, location='ic',name_plot="Sgo1_plots",active= 'all', name_folder="Sgo1_CPC_05_20_24")
# plot_across_models('CPC', plot_list, in_dir_, location='kt',name_plot="3Sgo1_CPC_plots_all",active= 'all')

# in_dir_ = "/Users/smgroves/Box/CPC_Model_Project/VCell_Exports/From_Catalina/Sgo1_plots/Sgo1_haspin"
# plot_list = ["03_21_24_relaxed_RefModel_64rxns",'03_21_24_relaxed_RefModel_Haspin50_inh',
#              '03_21_24_relaxed_RefModel_Sgo1_50P', '03_21_24_relaxed_RefModel_Sgo1_50P_Haspin50_inh']
# plot_across_models('CPC', plot_list, in_dir_, location='ic',name_plot="2Sgo1_haspin_plots_all",active= 'all')
# plot_across_models('CPC', plot_list, in_dir_, location='kt',name_plot="2Sgo1_haspin_plots_all",active= 'all')

# in_dir_ = "/Users/smgroves/Box/CPC_Model_Project/VCell_Exports/From_Catalina/Sgo1_plots/Sgo1_Plk1"
# plot_list = ["03_21_24_relaxed_RefModel_64rxns",'03_21_24_relaxed_RefModel_Plk150_inh',
#              '03_21_24_relaxed_RefModel_Sgo1_50P', '03_21_24_relaxed_RefModel_Sgo1_50P_Plk150_inh']
# plot_across_models('CPC', plot_list, in_dir_, location='ic',name_plot="Sgo1_Plk1_plots_active",active= 'active')
# plot_across_models('CPC', plot_list, in_dir_, location='kt',name_plot="Sgo1_Plk1_plots_active",active= 'active')
#
# plot_across_models('CPC', plot_list, in_dir_, location='ic',name_plot="2Sgo1_Plk1_plots_all",active= 'all')
# plot_across_models('CPC', plot_list, in_dir_, location='kt',name_plot="2Sgo1_Plk1_plots_all",active= 'all')

# name_folder = "Haspin_width"
# in_dir = f"/Users/smgroves/Box/CPC_Model_Project/VCell_Exports/From_Catalina/{name_folder}"
# plot_list = ["03_21_24_relaxed_RefModel_64rxns",'03_25_24_relaxed_RefModel_haswidth_0.1',
#              '03_25_24_relaxed_RefModel_haswidth_0.3', '03_25_24_relaxed_RefModel_haswidth_0.4',
#              '03_25_24_relaxed_RefModel_haswidth_0.5','03_25_24_relaxed_RefModel_haswidth_0.05',
#              "03_25_24_relaxed_RefModel_haswidth_0.6"]
# plot_across_models('CPC', plot_list, in_dir, location='ic',name_plot="Haspin_width",active= 'all',name_folder=name_folder)
# plot_across_models('CPC', plot_list, in_dir, location='kt',name_plot="Haspin_width",active= 'all', name_folder=name_folder
#                    )

# in_dir = "/Users/smgroves/Box/CPC_Model_Project/VCell_Exports/From_Catalina/Precursors"
# plot_list = ["03_21_24_relaxed_RefModel_64rxns",'03_25_24_relaxed_RefModel_CPC_inh',
#              '03_25_24_relaxed_RefModel_Mps1_CPC_inh', '03_25_24_relaxed_RefModel_Mps1_inh',
#              '03_25_24_relaxed_RefModel_Plk1_CPC_inh','03_25_24_relaxed_RefModel_Plk1_inh']
# plot_across_models('CPC', plot_list, in_dir, location='ic',name_plot="Precursors",active= 'all')
# plot_across_models('CPC', plot_list, in_dir, location='kt',name_plot="Precursors",active= 'all')
#

## TO DO
name_folder = "RefModel_base_sim_relaxed_v_tensed"
in_dir = f"/Users/smgroves/Box/CPC_Model_Project/vcell_plots"
plot_list = ["04_02_24_tensed_RefModel","03_21_24_relaxed_RefModel_64rxns"]
plot_across_models('CPC', plot_list, in_dir,name_list = ['Proper attachments','Improper attachments'], location='ic',name_plot="relaxed_v_tensed_all",active= 'all',name_folder=name_folder)
# plot_across_models('CPC', plot_list, in_dir, location='kt',name_plot="relaxed_v_tensed_all",active= 'all', name_folder=name_folder )

