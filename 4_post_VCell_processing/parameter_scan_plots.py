import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
#import numpy as np
in_dir = "/Users/catalinaalvarez/Documents/cpc_plots_2023"
#import matplotlib as m
import os

# CODE 1: PARAMETER SCAN
# def lineplot(species, in_dir, sim_prefix, name_scan, num_scans, xmax = None, xmin = 0, log = False,
#               location = 'ic',column = "Sum_Active", active = 'active', name = None, suffix = "",
#               highlight = None, name_folder = "", palette = sns.color_palette("crest", as_cmap=True)):

#     if os.path.isdir(f"/Users/catalinaalvarez/Documents/cpc_plots_2023/figures/lineplot_param_scans/{name_folder}"):
#         pass
#     else:
#         os.makedirs(f"/Users/catalinaalvarez/Documents/cpc_plots_2023/figures/lineplot_param_scans/{name_folder}")
#     plot_data = pd.DataFrame()

#     if log:
#         param_range = np.logspace(start = np.log10(xmin), stop = np.log10(xmax), num = num_scans, endpoint = True)
#     else:
#         if xmax is not None:
#             step = (xmax - xmin) / (num_scans - 1)
#             param_range = np.arange(start=xmin, stop=xmax+step, step=step)
#         else:
#             param_range = np.arange(num_scans)

#     if active == 'all':
#         for i in range(num_scans):
#             # if i == 5: continue
#             param = param_range[i]
#             tmp = pd.read_csv(f"{in_dir}/{sim_prefix}{i}/data/data_{location}_{species}.csv", header=0,
#                               index_col=None)
#             tmp['Time'] = 10 * tmp['Time']
#             tmp['parameter'] = param
#             tmp['all'] = tmp[list(set(tmp.columns).difference({"Time",'parameter'}))].sum(axis = 1)
#             plot_data = pd.concat([plot_data, tmp[['parameter', 'all', 'Time']]], ignore_index=True)
#             column = 'all'
#     else:
#         if active == 'inactive' and column == 'Sum_Active':
#             column = 'Sum_Inactive'
#         if active == 'active' and column == 'Sum_Inactive':
#             column = 'Sum_Active'
#         for i in range(num_scans):
#             # if i == 5: continue
#             param = param_range[i]
#             tmp = pd.read_csv(f"{in_dir}/{sim_prefix}{i}/data/data_{active}_{location}_{species}.csv", header=0,
#                               index_col=None)
#             tmp['Time'] = 10 * tmp['Time']
#             tmp['parameter'] = param
#             plot_data = pd.concat([plot_data, tmp[['parameter', column, 'Time']]], ignore_index=True)


#     if log:
#         ax = sns.lineplot(x = plot_data['Time'].to_numpy(), y= plot_data[column].to_numpy(), hue = plot_data['parameter'].to_numpy(),
#                       hue_norm=m.colors.LogNorm(), palette = palette)
#     else:
#         ax = sns.lineplot(x=plot_data['Time'].to_numpy(), y=plot_data[column].to_numpy(),
#                           hue=plot_data['parameter'].to_numpy(),palette = palette)
#     plt.xlabel("Time (s)")
#     if name is not None:
#         plt.ylabel(f"{name} (uM)")
#         plt.title(f"{name} at {location.upper()}")

#     else:
#         if column.startswith('Sum'):
#             plt.ylabel(f"Total {active} {species} (uM)")
#             plt.title(f"Total {active} {species} at {location.upper()}")
#                       # f"Parameter scan over {name_scan}")
#         else:
#             plt.ylabel(f"{species} (uM)")
#             plt.title(f"{species} at {location.upper()}")

#     if highlight is not None:
#         if active == 'all':
#             tmp = pd.read_csv(f"{in_dir}/{highlight}/data/data_{location}_{species}.csv", header=0,
#                               index_col=None)
#             tmp['all'] = tmp[list(set(tmp.columns).difference({"Time",'parameter'}))].sum(axis = 1)

#         else:
#             tmp = pd.read_csv(f"{in_dir}/{highlight}/data/data_{active}_{location}_{species}.csv", header=0, index_col=None)
#         tmp['Time'] = 10 * tmp['Time']

#         sns.lineplot(x = tmp['Time'].to_numpy(), y= tmp[column].to_numpy(), color = 'black',linestyle = "dotted", ax = ax, legend=False)


#     if log:
#         norm = m.colors.LogNorm(xmin, xmax)
#     else:
#         if xmax is not None:
#             norm = plt.Normalize(xmin, xmax)
#         else:
#             norm = plt.Normalize(0, 100)
#     # old color palette: sns.cubehelix_palette(as_cmap=True)
#     sm = plt.cm.ScalarMappable(cmap=palette, norm=norm)
#     sm.set_array([])
#     # Remove the legend and add a colorbar (optional)
#     ax.get_legend().remove()
#     if xmax is not None:
#         ax.figure.colorbar(sm, label = f"{name_scan} (uM)", ticks=param_range, ax=ax)
#     else:
#         ax.figure.colorbar(sm, label = f"{name_scan} (%)")
        
#     plt.tight_layout()
#     print("saving fig")
#     plt.savefig(f"/Users/catalinaalvarez/Documents/cpc_plots_2023/figures/lineplot_param_scans/{name_folder}/scan-{name_scan}_species-{species}_loc-{location}{suffix}.pdf")
#     plt.show()
#     plt.close()

# name_folder = "Kon scan 12-27-24"
# in_dir_ = "/Users/catalinaalvarez/Documents/cpc_plots_2023"
# sim_prefix = "12_27_24_relaxed_RefModel_MonseData_Kon_"
# name_scan = 'Kon'
# num_scans = 5
# xmin = 0.1
# xmax = 0.5
# lineplot('CPC', in_dir_, sim_prefix, name_scan, num_scans, xmax, location='ic')
# lineplot('CPC', in_dir_, sim_prefix, name_scan, num_scans, xmax, location='kt')

# in_dir_ = "/Users/catalinaalvarez/Documents/cpc_plots_2023/Knl1_plots/Bub1_0.006"
# sim_prefix = "03_21_24_relaxed_RefModel_Bub10.006_Knl1_"
# name_scan = 'Knl1 IC'
# num_scans = 10
# xmax = 180
# lineplot('CPC', in_dir_, sim_prefix, name_scan, num_scans, xmax, location = 'kt', suffix = '_Bub1_0.006')
# lineplot('CPC', in_dir_, sim_prefix, name_scan, num_scans, xmax, location = 'ic', suffix = '_Bub1_0.006')

# Example with log:
# sim_prefix = "02_19_24_relaxed_RefModel_Mps1_phos_Plk1a_20Pac_transactiv_CPCi_scan_FIXED_not20Pac "
# name_scan = 'CPCi IC'
# num_scans = 11
# log = False
# xmin = 0
# xmax = 1.065
# lineplot('CPC', in_dir, sim_prefix, name_scan, num_scans, xmax, location='ic')

# Example with one highlight:
# sim_prefix = "04_01_24_tensed_RefModel_Bub1_his_scan"
# name_scan = 'Bub1a_his_KD'
# num_scans = 6
# xmin = 0.001
# xmax = 100
# lineplot('CPC', in_dir, sim_prefix, name_scan, num_scans, xmax = xmax, xmin = xmin,
#           location='kt', log = True, active = 'all',
#           suffix = '_all',
#           highlight = "04_01_24_tensed_RefModel_Bub1_his_scan3",
#           name_folder="Bub1-his-scan-tensed_rainbow")

#CODE 2: SIMULATIONS COMPARISON
### Comparing extra reactions
def plot_across_models(species, plot_list, in_dir,  name_list = [], location = 'ic',column = "Sum_Active", active = 'active',
                        name = None, name_plot="", name_folder =""):
    print("Plotting across models")
    if os.path.isdir(f"/Users/catalinaalvarez/Documents/cpc_plots_2023/figures/lineplot_across_sims/{name_folder}"):
        pass
    else:
        os.makedirs(f"/Users/catalinaalvarez/Documents/cpc_plots_2023/figures/lineplot_across_sims/{name_folder}")
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
    ax = sns.lineplot(x = plot_data['Time'], y= plot_data[column], hue = plot_data['parameter'])
    # hue = plot_data['parameter'].to_numpy()  --> palette = "crest"
    ax.set_xlim(0,200)
    ax.set_ylim(4,13)

    plt.xlabel("Time (s)")
    if name is not None:
        plt.ylabel(f"{name} (uM)")
        plt.title(f"{name} at {location.upper()}")
    else:
        if column.startswith('Sum'):
            plt.ylabel(f"Total {active} {species} (uM)")
            plt.title(f"Total {active} {species} at {location.upper()}")
        else:
            plt.ylabel(f"{species} (uM)")
            plt.title(f"{species} at {location.upper()}")

#Change legend labels here following simulation order:
    L=ax.legend()
    # L.get_texts()[0].set_text('KON = 0.05 µM-1.s-1')
    # L.get_texts()[1].set_text('Ref. KON = 0.1 µM-1.s-1')
    # L.get_texts()[2].set_text('KON = 0.15 µM-1.s-1')
    # L.get_texts()[3].set_text('KON = 0.2 µM-1.s-1')
    # L.get_texts()[4].set_text('KON = 0.25 µM-1.s-1')
    # L.get_texts()[0].set_text('Relaxed kppKT = 0.3 s-1')
    # L.get_texts()[1].set_text('Relaxed kppKT = 3 s-1')
    # L.get_texts()[2].set_text('Relaxed kppKT = 5 s-1')
    # L.get_texts()[3].set_text('Relaxed kppKT = 7s-1')
    # L.get_texts()[4].set_text('Relaxed kppKT = 10 s-1')
    # L.get_texts()[0].set_text('Ref. Haspin = 0.602 uM')
    # L.get_texts()[1].set_text('Haspin = 0.301 uM')
    # L.get_texts()[2].set_text('Haspin = 0.201 uM')
    # L.get_texts()[3].set_text('Haspin = 0.151 uM')
    # L.get_texts()[4].set_text('Haspin = 0.121 uM')
    # L.get_texts()[0].set_text('Ref. Plk1 = 5.44 uM')
    # L.get_texts()[1].set_text('Plk1 = 2.72 uM')
    # L.get_texts()[2].set_text('Plk1 = 1.81 uM')
    # L.get_texts()[3].set_text('Plk1 = 1.36 uM')
    # L.get_texts()[4].set_text('Plk1 = 1.09 uM')
    # L.get_texts()[5].set_text('Plk1 = 0.93 uM')
    # L.get_texts()[6].set_text('Plk1 = 0.70 uM')
    # L.get_texts()[7].set_text('Plk1 = 0.46 uM')  
    # L.get_texts()[8].set_text('Plk1 = 0.23 uM')   
    # L.get_texts()[9].set_text('Plk1 = 0.12 uM')
    # L.get_texts()[10].set_text('Plk1 = 0.023 uM')
    # L.get_texts()[11].set_text('Plk1 = 0 uM')
    
    # next
    L.get_texts()[0].set_text('kd = 150 nM') 
    L.get_texts()[1].set_text('kd = 100 nM')
    L.get_texts()[2].set_text('kd = 80 nM')
    L.get_texts()[3].set_text('kd = 52.8 nM')
    # L.get_texts()[5].set_text('kpp = 0.8 s-1')
    # L.get_texts()[6].set_text('kpp = 1 s-1')
    # L.get_texts()[0].set_text('Telocentric Ref. model') 
    # L.get_texts()[1].set_text('Telocentric 30 s')
    # L.get_texts()[2].set_text('Telocentric 50 s')
    # L.get_texts()[3].set_text('Telocentric 100 s')
    # L.get_texts()[4].set_text('Telocentric 200 s')
    # L.get_texts()[5].set_text('Telocentric 300 s')
   
    # L.get_texts()[0].set_text('Metacentric Ref. model') 
    # L.get_texts()[1].set_text('CPC 50%')
    # L.get_texts()[2].set_text('Sgo1 50%')
    # L.get_texts()[3].set_text('CPC & Sgo1 50%')
    # L.get_texts()[4].set_text('Old Bub1')
    # L.get_texts()[5].set_text('Bub1 50%')
    # L.get_texts()[6].set_text('Bub1 & CPC 50%')
    # L.get_texts()[7].set_text('Bub1 & Sgo1 50%')
    # L.get_texts()[8].set_text('CPC 90%')
    # L.get_texts()[9].set_text('Sgo1 50% & CPC 90%')
    # L.get_texts()[10].set_text('Bub1 90%')
    # L.get_texts()[11].set_text('Bub1 & CPC 90%')
    # L.get_texts()[12].set_text('Sgo1 50% & Bub1 90%')
    # L.get_texts()[13].set_text('Haspin 50%')
    # L.get_texts()[14].set_text('Haspin & CPC 50%')
    # L.get_texts()[15].set_text('Haspin 90%')
    # L.get_texts()[16].set_text('Haspin & CPC 90%')
                               
    # L.get_texts()[0].set_text('kppKT = 0.1 s-1')
    # L.get_texts()[1].set_text('Ref. kppKT = 0.3 s-1')
    # L.get_texts()[2].set_text('kppKT = 0.5 s-1')
    # L.get_texts()[3].set_text('kppKT = 0.7 s-1')
    # L.get_texts()[0].set_text('Relaxed Ref. model')
    # L.get_texts()[1].set_text('Relaxed 50% Sgo1') 
    # L.get_texts()[2].set_text('Relaxed 50% CPC')
    # L.get_texts()[3].set_text('Relaxed 50% CPC + 50% Sgo1')
    # L.get_texts()[4].set_text('Tensed Ref. model')
    # L.get_texts()[5].set_text('Tensed 50% Sgo1')
    # L.get_texts()[6].set_text('Tensed 50% CPC')
    # L.get_texts()[7].set_text('Tensed 50% CPC + 50% Sgo1')
    # L.get_texts()[2].set_text('Tensed model')
    # L.get_texts()[3].set_text('Relaxed model @ 50% CPC + 50% Sgo1')

    sns.move_legend(ax, "upper left", labelspacing = 0.01, fontsize='7')
    plt.setp(plt.gca().get_legend().get_texts())
    # plt.legend(labelspacing=0.01, fontsize='7')
    plt.tight_layout()
    print("saving fig")
    plt.savefig(f"/Users/catalinaalvarez/Documents/cpc_plots_2023/figures/lineplot_across_sims/{name_plot}-{species}_loc-{location}.pdf")
    plt.show()
    plt.close()

name_folder = "cata"
in_dir_ = "/Users/catalinaalvarez/Documents/cpc_plots_2023"
plot_list = [
                "02_22_25_metacentric_relaxed_model_kd test_0.15",
                "02_22_25_metacentric_relaxed_model_kd test_0.1",
                "02_22_25_metacentric_relaxed_model_kd test_0.08",
                "02_22_25_metacentric_relaxed_model_kd test_0.0528"
                
                
                      # 
            ]
plot_across_models('CPC', plot_list, in_dir_, location='ic',name_plot="meta_all_kd_02-22-25",active= 'all')
plot_across_models('CPC', plot_list, in_dir_, location='kt',name_plot="meta_all_ks_02-22-25",active= 'all')









