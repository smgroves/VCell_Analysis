import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import os
import pathlib
import re
#for some species, make a line plot of the horizontal and vertical axes of the heatmap
# so that we can directly compare across simulations without having to define an IC region

in_dir = "/Users/smgroves/Box/CPC_Model_Project/VCell_Exports"

def line_scan_plot(species, sim, in_dir, out_dir, name, tSpan = 500, desired_interval = 100,
                   tInterval = 10,x_dim = 64, y_dim = 128,x_um = 1.6, y_um = 3.2,
                   ymax = 10, save = True):
    #Set up timepoints
    timepoints = np.linspace(0,tSpan, int(tSpan/desired_interval)+1, endpoint = True)
    t_list = []
    for t in timepoints:
        t_list.append("{:04d}".format(int(t/tInterval)))

    # Iterate over timepoints for each plot
    horiz_dic = {sim[i]:[0]*x_dim for i in sim.keys()}
    vert_dic = {sim[i]:[0]*y_dim for i in sim.keys()}

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
        sns.lineplot(data = long_horiz_df, x = 'x', y = "value", hue = "Simulation")
        plt.ylabel(f"Total {species} across horizontal axis at {timepoints[i]} (uM)")
        plt.xlabel("X dimension (um)")
        plt.title(f"Line Scan across Horizontal Midpoint Axis at {timepoints[i]}")
        plt.ylim(0,ymax)
        plt.tight_layout()
        if save:
            if os.path.isdir(f"{out_dir}/line_scans/{name}/horiz"): pass
            else:
                os.makedirs(f"{out_dir}/line_scans/{name}/horiz")
            plt.savefig(f"{out_dir}/line_scans/{name}/horiz/{species}_t{timepoints[i]}_horiz.pdf")
            plt.close()
        else:
            plt.show()
        fig_width, fig_height = plt.gcf().get_size_inches()

        vert_df = pd.DataFrame(vert_dic)
        vert_df['y'] = np.linspace(start = 0, stop = y_um, num = y_dim)
        long_vert_df = pd.melt(vert_df, id_vars='y', var_name = "Simulation")
        #vertical axis
        plt.figure(figsize = (fig_width,fig_width+4))
        sns.lineplot(data = long_vert_df, y = 'y', x = "value", hue = "Simulation", orient = 'y')
        plt.xlabel(f"Total {species} across vertical axis at Time {timepoints[i]}s (uM)")
        plt.ylabel("Y dimension (um)")
        plt.title(f"Line Scan across Vertical Midpoint Axis at Time {timepoints[i]}s")
        plt.xlim(0,ymax)
        plt.tight_layout()
        if save:
            if os.path.isdir(f"{out_dir}/line_scans/{name}/vert"): pass
            else:
                os.mkdir(f"{out_dir}/line_scans/{name}/vert")
            plt.savefig(f"{out_dir}/line_scans/{name}/vert/{species}_t{timepoints[i]}_vert.pdf")
            plt.close()
        else:
            plt.show()



outdir = "/Users/smgroves/Documents/GitHub/VCell_Analysis/plotting_functions/figures"
sim = {"SimID_270423544_0__exported":"04_01_24_relaxed_RefModel_Bub1_his_kd_0.001_Knl1_scan0", "SimID_270423544_1__exported":"04_01_24_relaxed_RefModel_Bub1_his_kd_0.001_Knl1_scan1",
       "SimID_270423544_2__exported":"04_01_24_relaxed_RefModel_Bub1_his_kd_0.001_Knl1_scan2"}
species = 'CPC'
line_scan_plot(species, sim, in_dir, out_dir=outdir, name = "Bub1a-his-kd-0.001_Knl1_scan")