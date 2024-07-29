import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
in_dir = "/Users/smgroves/Box/CPC_Model_Project/vcell_plots"
import matplotlib as m
import os

name_folder = "RefModel_base_sim_relaxed_v_tensed"
in_dir = f"/Users/smgroves/Box/CPC_Model_Project/vcell_plots"
plot_list = ["04_02_24_tensed_RefModel","03_21_24_relaxed_RefModel_64rxns"]
species = "CPC"
name_list = ['Proper attachments','Improper attachments']
location='ic'
name_plot="relaxed_v_tensed_all"
active= 'all'
column = "Sum_Active"
name = None


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
#################
# Add stretched sim
#################
pre_stretch_dir = "10_16_23_relaxed_RefModel_Mps1_phos_Plk1a_transactiv"
post_stretch_dir = f"10_25_23_400s_post_transition_base_20Pac"
stretch_plot_data = pd.DataFrame()
n = "Attachment Transition"
# pre_stretch = pd.read_csv(f"{in_dir}/{pre_stretch_dir}/data/data_{location}_{species}.csv", header = 0, index_col = None)
# pre_stretch['Time'] = 10*pre_stretch['Time']
# pre_stretch['parameter'] = n
# pre_stretch['all'] = pre_stretch[list(set(pre_stretch.columns).difference({"Time",'parameter'}))].sum(axis = 1)
# pre_stretch = pre_stretch.loc[pre_stretch['Time'] <= 100]

post_stretch = pd.read_csv(f"{in_dir}/{post_stretch_dir}/data/data_{location}_{species}.csv", header = 0, index_col = None)
post_stretch['Time'] = 10*post_stretch['Time'] + 101
post_stretch['parameter'] = n
post_stretch['all'] = post_stretch[list(set(post_stretch.columns).difference({"Time",'parameter'}))].sum(axis = 1)

# stretch = pd.concat([pre_stretch[['parameter',"all", 'Time']],post_stretch[['parameter',"all", 'Time']]], ignore_index=True)
# print(stretch.head())

plot_data = pd.concat([plot_data,post_stretch[['parameter',"all", 'Time']]], ignore_index=True)



# fig = plt.figure(figsize = (5,6))
# print(plot_data.loc[plot_data["Time"]==500][column])
# print(plot_data.head())
# ax = sns.lineplot(x = plot_data['Time'].to_numpy(), y= plot_data[column].to_numpy(), hue = plot_data['parameter'].to_numpy(), estimator = None)
# ax.set_xlim(0,500)
# ax.set_ylim(0,6)

# plt.xlabel("Time (s)")
# if name is not None:
#     plt.ylabel(f"{name} Concentration (uM)")
#     plt.title(f"{name} Concentration in {location.upper()} over {plot_data['Time'].max()} seconds")
# else:
#     if column.startswith('Sum'):
#         plt.ylabel(f"Sum of {active} {species} Concentration (uM)")
#         plt.title(f"Sum of {active} {species} Concentration in {location.upper()} over {plot_data['Time'].max()} seconds")
#     else:
#         plt.ylabel(f"{species} Concentration (uM)")
#         plt.title(f"{species} Concentration in {location.upper()} over {plot_data['Time'].max()} seconds")

# # ax.legend(loc='center left', bbox_to_anchor=(1.25, 0.5), ncol=1)
# plt.tight_layout()
# # print("saving fig")
# plt.savefig(f"/Users/smgroves/Documents/GitHub/VCell_Analysis/plotting_functions/figures/lineplot_across_sims/{name_folder}/{name_plot}-{species}_loc-{location}_with_stretch.pdf")
# # plt.show()
# plt.close()


f, (ax1, ax2) = plt.subplots(ncols=2, nrows=1,
                             sharey=True,
                             gridspec_kw={'width_ratios': [1, 4]},
                             figsize = (3,4))

# we want the "Test" to appear on the x axis as individual parameters
# "Latency in ms" should be what is shown on the y axis as a value
# hue should be the "Experiment Setup"
# this will result three ticks on the x axis with X1...X3 and each with three bars for T1...T3
# (you could turn this around if you need to, depending on what kind of data you want to show)
ax1 = sns.lineplot(x = plot_data['Time'].to_numpy(), y= plot_data[column].to_numpy(), hue = plot_data['parameter'].to_numpy(), estimator = None, ax=ax1)

ax2 = sns.lineplot(x = plot_data['Time'].to_numpy(), y= plot_data[column].to_numpy(), hue = plot_data['parameter'].to_numpy(), estimator = None, ax=ax2)


# here is the fun part: setting the limits for the individual y axis
# the upper part (ax1) should show only values from 250 to 400
# the lower part (ax2) should only show 0 to 150
# you can define your own limits, but the range (150) should be the same so scale is the same across both plots
# it could be possible to use a different range and then adjust plot height but who knows how that works
ax1.set_xlim(0, 100)
ax2.set_xlim(101, 500)

# the upper part does not need its own x axis as it shares one with the lower part
ax2.get_yaxis().set_visible(False)
ax1.set_ylim(0,6)
ax2.set_ylim(0,6)
ax1.set_ylabel(f"CPC Concentration (uM)")

# by default, each part will get its own "Latency in ms" label, but we want to set a common for the whole figure
# first, remove the y label for both subplots
ax1.set_xlabel("")
ax2.set_xlabel("")
# then, set a new label on the plot (basically just a piece of text) and move it to where it makes sense (requires trial and error)
f.text(0.40, 0.02, "Time (s)", va="center")
f.text(0.10, 0.94, "Total CPC Concentration in IC over 501s", va="center", fontsize = 14)

# by default, seaborn also gives each subplot its own legend, which makes no sense at all
# soe remove both default legends first
ax1.get_legend().remove()
ax2.get_legend().remove()
# then create a new legend and put it to the side of the figure (also requires trial and error)
ax2.legend(loc = "lower right")

# # let's put some ticks on the top of the upper part and bottom of the lower part for style
# ax1.yaxis.tick_top()
# ax2.yaxis.tick_bottom()

# finally, adjust everything a bit to make it prettier (this just moves everything, best to try and iterate)
f.subplots_adjust(left=0.1, right=0.9, bottom=0.1, top=0.9)
plt.savefig(f"/Users/smgroves/Documents/GitHub/VCell_Analysis/plotting_functions/figures/lineplot_across_sims/{name_folder}/{name_plot}-{species}_loc-{location}_with_stretch_split_small.pdf")

# f.tight_layout()
plt.show()