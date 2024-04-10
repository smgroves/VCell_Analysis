import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import os
import pathlib
import re
from sklearn.metrics import auc

#for some species, make a line plot of the horizontal and vertical axes of the heatmap
# so that we can directly compare across simulations without having to define an IC region
# This should allow us to see if any perturbations make the CPC accumulation wider or longer, for example

in_dir = "/Users/smgroves/Box/CPC_Model_Project/VCell_Exports"

def line_scan_plot(species, sim, in_dir, out_dir, name, tSpan = 500, desired_interval = 100,
                   tInterval = 10,x_dim = 64, y_dim = 128,x_um = 1.6, y_um = 3.2,
                   ymax = 10, save = True, savetype = 'png', show_auc = False):
    #Set up timepoints
    timepoints = np.linspace(0,tSpan, int(tSpan/desired_interval)+1, endpoint = True)
    t_list = []
    for t in timepoints:
        t_list.append("{:04d}".format(int(t/tInterval)))

    # Iterate over timepoints for each plot
    horiz_dic = {sim[i]:[0]*x_dim for i in sim.keys()}
    vert_dic = {sim[i]:[0]*y_dim for i in sim.keys()}
    if show_auc:
        all_aucs = {sim[i]:[] for i in sim.keys()}
    for i,timepoint in enumerate(t_list):
        # for each simulation
        for s in sim.keys():
            horiz_line = [0]*x_dim
            vert_line = [0]*y_dim
            for f in os.listdir(f"{in_dir}/{s}"):
                if species in f and timepoint in f:
                    tmp = pd.read_csv(f"{in_dir}/{s}/{f}",skiprows=10, header = None, index_col=None)
                    horiz_line += tmp.iloc[int(y_dim/2)]
                    vert_line += tmp[int(x_dim/2)]
            horiz_dic[sim[s]] = horiz_line
            vert_dic[sim[s]] = vert_line


        horiz_df = pd.DataFrame(horiz_dic)
        horiz_df['x'] = np.linspace(start = 0, stop = x_um, num = x_dim)
        long_horiz_df = pd.melt(horiz_df, id_vars='x', var_name = "Simulation")
        # #horizontal axis
        ax = sns.lineplot(data = long_horiz_df, x = 'x', y = "value", hue = "Simulation")
        plt.ylabel(f"Total {species} across horizontal axis \n at {timepoints[i]} (uM)")
        plt.xlabel("X dimension (um)")
        plt.title(f"Line Scan across Horizontal Midpoint Axis at {timepoints[i]}")
        plt.ylim(0,ymax)
        # box = ax.get_position()
        # ax.set_position([box.x0, box.y0 + box.height * 0.4,
        #                  box.width, box.height * 0.6])
        #
        # # Put a legend below current axis
        # ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.18))
        if show_auc:
            aucs = {}
            # Area under curve
            for hue in sorted(list(set(long_horiz_df['Simulation']))):
                tmp = long_horiz_df.loc[long_horiz_df['Simulation'] == hue]
                tmp = tmp.sort_values("x", ascending=True)
                # aucs[hue] = auc(tmp['x'], tmp["value"])
                tmp = tmp.loc[(tmp['x']>.425) & (tmp['x']<1.175)]
                aucs[f"{hue}"] = auc(tmp['x'], tmp["value"])
                all_aucs[f"{hue}"].append(auc(tmp['x'], tmp["value"]))

            # create tuples of positions
            positions = [(.94-.05*x) for x in range(2)]
            # add text
            plt.text(.01, .99, "Area under curve between relaxed KT",ha='left', va='top', transform=ax.transAxes)
            for (y), (k, v) in zip(positions, aucs.items()):
                plt.text(.01, y, f'{k}: {round(v,3)}', ha='left', va='top', transform=ax.transAxes)
            plt.axvline(.425, linestyle = "--", c = "gray", alpha = .5)
            plt.axvline(1.175, linestyle = "--", c = "gray", alpha = .5)

            l1 = ax.lines[0]
            y1 = l1.get_xydata()[:, 1]
            plt.fill_between(
                x= horiz_df['x'],
                y1=y1,
                where=(.425 <  horiz_df['x']) & ( horiz_df['x'] < 1.175),
                color="lightgrey",
                alpha=0.2)
        plt.tight_layout()

        if save:
            if os.path.isdir(f"{out_dir}/line_scans/{name}/horiz"): pass
            else:
                os.makedirs(f"{out_dir}/line_scans/{name}/horiz")
            plt.savefig(f"{out_dir}/line_scans/{name}/horiz/{species}_t{timepoints[i]}_horiz.{savetype}")
            plt.close()
        else:
            plt.show()



        fig_width, fig_height = plt.gcf().get_size_inches()

        vert_df = pd.DataFrame(vert_dic)
        vert_df['y'] = np.linspace(start = 0, stop = y_um, num = y_dim)
        long_vert_df = pd.melt(vert_df, id_vars='y', var_name = "Simulation")
        #vertical axis
        plt.figure(figsize = (fig_width-2,fig_width+4))
        sns.lineplot(data = long_vert_df, y = 'y', x = "value", hue = "Simulation", orient = 'y')
        plt.xlabel(f"Total {species} across vertical axis \n at Time {timepoints[i]}s (uM)")
        plt.ylabel("Y dimension (um)")
        plt.title(f"Line Scan across Vertical Midpoint Axis \n at Time {timepoints[i]}s")
        plt.xlim(0,ymax)
        plt.tight_layout()
        if save:
            if os.path.isdir(f"{out_dir}/line_scans/{name}/vert"): pass
            else:
                os.mkdir(f"{out_dir}/line_scans/{name}/vert")
            plt.savefig(f"{out_dir}/line_scans/{name}/vert/{species}_t{timepoints[i]}_vert.{savetype}")
            plt.close()
        else:
            plt.show()

    if show_auc:
        all_aucs_df = pd.DataFrame(all_aucs, index = timepoints)
        all_aucs_df['Timepoint'] = all_aucs_df.index
        long_auc_df = pd.melt(all_aucs_df, id_vars = 'Timepoint', var_name="Simulation")
        sns.lineplot(data = long_auc_df, x = "Timepoint", y ='value', hue = "Simulation")
        plt.ylabel("AUC")
        plt.title("Area under curve of horizontal line scan \n between relaxed KTs across simulations")
        if save:
            plt.savefig(f"{out_dir}/line_scans/{name}/horiz/AUC_{species}_horiz.{savetype}")
            plt.close()
        else:
            plt.show()

outdir = "/Users/smgroves/Documents/GitHub/VCell_Analysis/plotting_functions/figures"
# sim = {"SimID_270423544_0__exported":"04_01_24_relaxed_RefModel_Bub1_his_kd_0.001_Knl1_scan0",
#        "SimID_270423544_1__exported":"04_01_24_relaxed_RefModel_Bub1_his_kd_0.001_Knl1_scan1",
#        "SimID_270423544_2__exported":"04_01_24_relaxed_RefModel_Bub1_his_kd_0.001_Knl1_scan2"}
# species = 'CPC'
# line_scan_plot(species, sim, in_dir, out_dir=outdir, name = "Bub1a-his-kd-0.001_Knl1_scan")

sim = {"SimID_270510934_0__exported":"04_02_24_tensed_RefModel",
       "SimID_270418727_0__exported":"03_25_24_relaxed_RefModel"}
species = 'CPC'
line_scan_plot(species, sim, in_dir, out_dir=outdir, name = "RefModel_base_sim_relaxed_v_tensed_AUC",ymax = 6, save = False,
               show_auc=True)

# indir = "/Volumes/GoogleDrive/My Drive/UVA Postdoc/Simulations_for_line_scan_plots/Simulations csv"
# sim = {"SimID_270207522_0__exported":"03_21_24_relaxed_RefModel_DependentParameters",
#        "SimID_270238898_0__exported":"03_21_24_relaxed_RefModel_Sgo1_50P",
#     # "SimID_270413068_0__exported":"03_21_24_relaxed_RefModel_Haspin50_inh",
# # "SimID_270413071_0__exported":"03_21_24_relaxed_RefModel_Plk150_inh",
# "SimID_270413074_0__exported":"03_21_24_relaxed_RefModel_CPC50_inh",
# # "SimID_270413077_0__exported":"03_21_24_relaxed_RefModel_Sgo1_50P_Haspin50_inh"
# # "SimID_270413080_0__exported":"03_21_24_relaxed_RefModel_Sgo1_50P_Plk150_inh",
# "SimID_270413083_0__exported":"03_21_24_relaxed_RefModel_Sgo1_50P_CPC50_inh",
#
#        }
# species = 'CPC'
# line_scan_plot(species, sim, indir, out_dir=outdir, name = "Sgo1_CPC_synergy", save=True, ymax = 6)