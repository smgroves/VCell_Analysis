import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
in_dir = "/Users/smgroves/Box/CPC_Model_Project/vcell_plots"
import matplotlib as m
import os


def relaxed_tensed_plots(species, relaxed_model, tensed_model, in_dir, location = 'ic',column = "Sum_Active", active = 'active',
                       name = None, name_folder ="", suffix=''):
    if os.path.isdir(f"./figures/relaxed_tensed_ratio/{name_folder}"):
        pass
    else:
        os.makedirs(f"./figures/relaxed_tensed_ratio/{name_folder}")
    if active == 'all':
            relaxed = pd.read_csv(f"{in_dir}/{relaxed_model}/data/data_{location}_{species}.csv", header=0, index_col=None)
            relaxed['Time'] = 10 * relaxed['Time']
            relaxed['all'] = relaxed[list(set(relaxed.columns).difference({"Time"}))].sum(axis=1)

            tensed = pd.read_csv(f"{in_dir}/{tensed_model}/data/data_{location}_{species}.csv", header=0, index_col=None)
            tensed['Time'] = 10 * tensed['Time']
            tensed['all'] = tensed[list(set(tensed.columns).difference({"Time"}))].sum(axis=1)
            column = 'all'
            relaxed = relaxed[[column, 'Time']]
            tensed = tensed[[column, 'Time']]
    else:
        if active == 'inactive' and column == 'Sum_Active':
            column = 'Sum_Inactive'
        if active == 'active' and column == 'Sum_Inactive':
            column = 'Sum_Active'
        relaxed = pd.read_csv(f"{in_dir}/{relaxed_model}/data/data_{active}_{location}_{species}.csv", header=0, index_col=None)
        relaxed['Time'] = 10 * relaxed['Time']
        tensed = pd.read_csv(f"{in_dir}/{tensed_model}/data/data_{active}_{location}_{species}.csv", header=0, index_col=None)
        tensed['Time'] = 10 * tensed['Time']
        relaxed = relaxed[[column, 'Time']]
        tensed = tensed[[column, 'Time']]


    plot_data = pd.merge(relaxed, tensed,  how = 'inner', on = "Time", suffixes = ('_relaxed','_tensed'))
    plot_data['ratio'] = plot_data[f'{column}_relaxed']/plot_data[f'{column}_tensed']
    plot_data['absolute_diff'] = plot_data[f'{column}_relaxed'] - plot_data[f'{column}_tensed']

    ax = sns.lineplot(x=plot_data['Time'].to_numpy(), y=plot_data['ratio'].to_numpy())
    plt.xlabel("Time (s)")
    if name is not None:
        plt.ylabel(f"Ratio of relaxed:tensed for {name}")
        plt.title(f"Ratio of relaxed:tensed for \n {name} in {location.upper()} over {plot_data['Time'].max()} seconds")
    else:
        if column.startswith('Sum'):
            plt.ylabel(f"Ratio of relaxed:tensed for sum of {active} {species}")
            plt.title(
                f"Ratio of relaxed:tensed for \n Sum of {active} {species} Concentration in {location.upper()} over {plot_data['Time'].max()} seconds")
        else:
            plt.ylabel(f"Ratio of relaxed:tensed for {species}")
            plt.title(f"Ratio of relaxed:tensed for \n {species} in {location.upper()} over {plot_data['Time'].max()} seconds")

    plt.axhline(y = 1, linestyle = '--', color = 'gray')
    plt.text(.99, .99, f"mean = {round(plot_data['ratio'].mean(),3)}", ha='right', va='top', transform=ax.transAxes)

    # ax.legend(loc='center left', bbox_to_anchor=(1.25, 0.5), ncol=1)
    plt.tight_layout()
    plt.savefig(f"./figures/relaxed_tensed_ratio/{name_folder}/ratio_{species}_{active}_loc-{location}{suffix}.png")

    # plt.show()
    plt.close()
    #
    # ax = sns.lineplot(x=plot_data['Time'].to_numpy(), y=plot_data['absolute_diff'].to_numpy())
    # plt.xlabel("Time (s)")
    # if name is not None:
    #     plt.ylabel(f"Difference (relaxed - tensed) for {name}")
    #     plt.title(f"Difference (relaxed - tensed) for \n {name} in {location.upper()} over {plot_data['Time'].max()} seconds")
    # else:
    #     if column.startswith('Sum'):
    #         plt.ylabel(f"Difference (relaxed - tensed) for sum of {active} {species}")
    #         plt.title(
    #             f"Difference (relaxed - tensed)for \n Sum of {active} {species} Concentration in {location.upper()} over {plot_data['Time'].max()} seconds")
    #     else:
    #         plt.ylabel(f"Difference (relaxed - tensed) for {species}")
    #         plt.title(f"Difference (relaxed - tensed) for \n {species} in {location.upper()} over {plot_data['Time'].max()} seconds")
    # # ax.legend(loc='center left', bbox_to_anchor=(1.25, 0.5), ncol=1)
    # plt.text(.99, .99, f"mean = {round(plot_data['absolute_diff'].mean(),3)}", ha='right', va='top', transform=ax.transAxes)
    # plt.tight_layout()
    # plt.savefig(f"./figures/relaxed_tensed_ratio/{name_folder}/difference_{species}_{active}_loc-{location}{suffix}.png")
    # # plt.show()
    # plt.close()

species = "CPC"
relaxed_model = "03_21_24_relaxed_RefModel_64rxns"
tensed_model = "04_02_24_tensed_RefModel"
relaxed_tensed_plots(species, relaxed_model, tensed_model, in_dir, location = 'ic',
                     column = "Sum_Active", active = 'active',
                     name_folder ="Base_model")

# species = "CPC"
# relaxed_model = "04_01_24_relaxed_RefModel_Bub1_his_scan0"
# tensed_model = "04_01_24_tensed_RefModel_Bub1_his_scan0"
# relaxed_tensed_plots(species, relaxed_model, tensed_model, in_dir, location = 'ic',
#                     active = 'all',
#                      name_folder ="Bub1-his-KD_scan", suffix = "_100")

def param_scan_relaxed_tensed_plots(species, relaxed_models, tensed_models, in_dir, name_scan, location = 'ic',column = "Sum_Active", active = 'active',
                       name = None, name_folder ="", suffix='',xmax=None, xmin=0, log=False, palette = sns.color_palette("Spectral", as_cmap=True) ):

    num_scans = len(relaxed_models)
    if log:
        param_range = np.logspace(start = np.log10(xmin), stop = np.log10(xmax), num = num_scans, endpoint = True)
    else:
        if xmax is not None:
            step = (xmax - xmin) / (num_scans - 1)
            param_range = np.arange(start=xmin, stop=xmax+step, step=step)
        else:
            param_range = np.arange(num_scans)
    if os.path.isdir(f"./figures/relaxed_tensed_ratio/{name_folder}"):
        pass
    else:
        os.makedirs(f"./figures/relaxed_tensed_ratio/{name_folder}")
    all_plot_data = pd.DataFrame()
    for x, (relaxed_model, tensed_model) in enumerate(zip(relaxed_models,tensed_models)):
        if active == 'all':
                relaxed = pd.read_csv(f"{in_dir}/{relaxed_model}/data/data_{location}_{species}.csv", header=0, index_col=None)
                relaxed['Time'] = 10 * relaxed['Time']
                relaxed['all'] = relaxed[list(set(relaxed.columns).difference({"Time"}))].sum(axis=1)

                tensed = pd.read_csv(f"{in_dir}/{tensed_model}/data/data_{location}_{species}.csv", header=0, index_col=None)
                tensed['Time'] = 10 * tensed['Time']
                tensed['all'] = tensed[list(set(tensed.columns).difference({"Time"}))].sum(axis=1)
                column = 'all'
                relaxed = relaxed[[column, 'Time']]
                tensed = tensed[[column, 'Time']]
        else:
            if active == 'inactive' and column == 'Sum_Active':
                column = 'Sum_Inactive'
            if active == 'active' and column == 'Sum_Inactive':
                column = 'Sum_Active'
            relaxed = pd.read_csv(f"{in_dir}/{relaxed_model}/data/data_{active}_{location}_{species}.csv", header=0, index_col=None)
            relaxed['Time'] = 10 * relaxed['Time']
            tensed = pd.read_csv(f"{in_dir}/{tensed_model}/data/data_{active}_{location}_{species}.csv", header=0, index_col=None)
            tensed['Time'] = 10 * tensed['Time']
            relaxed = relaxed[[column, 'Time']]
            tensed = tensed[[column, 'Time']]

        plot_data = pd.merge(relaxed, tensed,  how = 'inner', on = "Time", suffixes = ('_relaxed','_tensed'))
        plot_data['ratio'] = plot_data[f'{column}_relaxed']/plot_data[f'{column}_tensed']
        plot_data['absolute_diff'] = plot_data[f'{column}_relaxed'] - plot_data[f'{column}_tensed']
        plot_data['parameter'] = x
        all_plot_data = pd.concat([all_plot_data, plot_data], ignore_index=True)

    ######## RATIO PLOT #########
    if log:
        ax = sns.lineplot(x = all_plot_data['Time'].to_numpy(), y= all_plot_data['ratio'].to_numpy(), hue = all_plot_data['parameter'].to_numpy(),
                      hue_norm=m.colors.LogNorm(), palette = palette)
    else:
        ax = sns.lineplot(x=all_plot_data['Time'].to_numpy(), y=all_plot_data['ratio'].to_numpy(),
                          hue=all_plot_data['parameter'].to_numpy(), palette = palette)

    plt.xlabel("Time (s)")
    if name is not None:
        plt.ylabel(f"Ratio of relaxed:tensed for {name}")
        plt.title(f"Ratio of relaxed:tensed for \n {name} in {location.upper()} over {plot_data['Time'].max()} seconds")
    else:
        if column.startswith('Sum'):
            plt.ylabel(f"Ratio of relaxed:tensed for sum of {active} {species}")
            plt.title(
                f"Ratio of relaxed:tensed for \n Sum of {active} {species} Concentration in {location.upper()} over {plot_data['Time'].max()} seconds")
        else:
            plt.ylabel(f"Ratio of relaxed:tensed for {species}")
            plt.title(f"Ratio of relaxed:tensed for \n {species} in {location.upper()} over {plot_data['Time'].max()} seconds")

    plt.axhline(y = 1, linestyle = '--', color = 'gray')
    plt.text(.99, .99, f"mean = {round(plot_data['ratio'].mean(),3)}", ha='right', va='top', transform=ax.transAxes)

    if log:
        norm = m.colors.LogNorm(xmin, xmax)
    else:
        if xmax is not None:
            norm = plt.Normalize(xmin, xmax)
        else:
            norm = plt.Normalize(0, 100)
    sm = plt.cm.ScalarMappable(cmap=palette, norm=norm)
    sm.set_array([])
    # Remove the legend and add a colorbar (optional)
    ax.get_legend().remove()
    if xmax is not None:
        ax.figure.colorbar(sm, label = f"{name_scan} (uM)", ticks=param_range)
    else:
        ax.figure.colorbar(sm, label = f"{name_scan} (%)")
    plt.tight_layout()
    plt.savefig(f"./figures/relaxed_tensed_ratio/{name_folder}/scan_ratio_{species}_{active}_loc-{location}{suffix}.png")

    plt.show()
    plt.close()

    ###### ABSOLUTE DIFF PLOT #######
    # if log:
    #     ax = sns.lineplot(x = all_plot_data['Time'].to_numpy(), y= all_plot_data['absolute_diff'].to_numpy(), hue = all_plot_data['parameter'].to_numpy(),
    #                   hue_norm=m.colors.LogNorm(), palette = palette)
    # else:
    #     ax = sns.lineplot(x=all_plot_data['Time'].to_numpy(), y=all_plot_data['absolute_diff'].to_numpy(),
    #                       hue=all_plot_data['parameter'].to_numpy(), palette = palette)
    # plt.xlabel("Time (s)")
    # if name is not None:
    #     plt.ylabel(f"Difference (relaxed - tensed) for {name}")
    #     plt.title(f"Difference (relaxed - tensed) for \n {name} in {location.upper()} over {plot_data['Time'].max()} seconds")
    # else:
    #     if column.startswith('Sum'):
    #         plt.ylabel(f"Difference (relaxed - tensed) for sum of {active} {species}")
    #         plt.title(
    #             f"Difference (relaxed - tensed)for \n Sum of {active} {species} Concentration in {location.upper()} over {plot_data['Time'].max()} seconds")
    #     else:
    #         plt.ylabel(f"Difference (relaxed - tensed) for {species}")
    #         plt.title(f"Difference (relaxed - tensed) for \n {species} in {location.upper()} over {plot_data['Time'].max()} seconds")
    # # ax.legend(loc='center left', bbox_to_anchor=(1.25, 0.5), ncol=1)
    # plt.text(.99, .99, f"mean = {round(plot_data['absolute_diff'].mean(),3)}", ha='right', va='top', transform=ax.transAxes)
    # if log:
    #     norm = m.colors.LogNorm(xmin, xmax)
    # else:
    #     if xmax is not None:
    #         norm = plt.Normalize(xmin, xmax)
    #     else:
    #         norm = plt.Normalize(0, 100)
    # sm = plt.cm.ScalarMappable(cmap=palette, norm=norm)
    # sm.set_array([])
    # # Remove the legend and add a colorbar (optional)
    # ax.get_legend().remove()
    # if xmax is not None:
    #     ax.figure.colorbar(sm, label = f"{name_scan} (uM)", ticks=param_range)
    # else:
    #     ax.figure.colorbar(sm, label = f"{name_scan} (%)")
    # plt.tight_layout()
    # plt.savefig(f"./figures/relaxed_tensed_ratio/{name_folder}/scan_difference_{species}_{active}_loc-{location}{suffix}.png")
    # # plt.show()
    # plt.close()

# relaxed_models = []
# tensed_models = []
# for n in range(6):
#     relaxed_models.append(f"04_01_24_relaxed_RefModel_Bub1_his_scan{n}")
#     tensed_models.append(f"04_01_24_tensed_RefModel_Bub1_his_scan{n}")
# xmin = 0.001
# xmax = 100
# param_scan_relaxed_tensed_plots("CPC", relaxed_models, tensed_models, in_dir,
#                                 name_scan="Bub1-his_KD",location = 'ic',
#                                 active = 'all', log = True, xmin = xmin, xmax = xmax,
#                                 name_folder ="Bub1-his-KD_scan", suffix = "_100")

