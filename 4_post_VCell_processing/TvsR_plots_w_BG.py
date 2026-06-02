#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov  4 21:40:23 2025
"""
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os

os.chdir('/Users/catalinaalvarez/Documents/CPC_plots_2026/figures/lineplot_across_sims/')

#CODE 2: SIMULATIONS COMPARISON - Simultaneous plotting of IC and BG
### Comparing extra reactions
def plot_across_models(species, plot_list, in_dir, location, name_list = [], column = "Sum_Active", active = 'active',
                        name = None, name_plot="", name_folder =""):
    print("Plotting across models")
    if os.path.isdir(f"/Users/catalinaalvarez/Documents/CPC_plots_2026/figures/lineplot_across_sims/{name_folder}"):
        pass
    else:
        os.makedirs(f"/Users/catalinaalvarez/Documents/CPC_plots_2026/figures/lineplot_across_sims/{name_folder}")
        print(f"Made folder {name_folder}")
    # plot_list = sorted(plot_list)
    plot_data = pd.DataFrame()
    if len(name_list) == 0:
        name_list = plot_list 
    if active == 'all':
        tag = 0
        for i in range(0, len(plot_list), 2):            
            current_plots = plot_list[i:i+2]
            current_names = name_list[i:i+2]
            plot_data = pd.DataFrame()
            df = pd.DataFrame(columns=["Region", "Value"])
            for n, p in zip(current_names,current_plots):
                for z in location:
                    tmp = pd.read_csv(f"{in_dir}/{p}/data/data_{z}_{species}.csv", header = 0, index_col = None)
                    tmp['Time'] = 10*tmp['Time']
                    tmp['parameter'] = n + z
                    tmp['all'] = tmp[list(set(tmp.columns).difference({"Time",'parameter'}))].sum(axis = 1)
                    print(tmp)
                    result = tmp.loc[tmp['Time'] == 200, 'all'].values[0]
                    print(result)
                    df.loc[len(df)] = [z, result]
                    plot_data = pd.concat([plot_data,tmp[['parameter','all', 'Time']]], ignore_index=True)
                    column = 'all'
                    plot_data = pd.concat([plot_data,tmp[['parameter',column, 'Time']]], ignore_index=True) 
            print(df)
            ratio = round(df.iloc[0, 1] / df.iloc[2, 1],3)
            print(ratio)
            fig = plt.figure(figsize = (4,3))
            ax = sns.lineplot(x = plot_data['Time'], y= plot_data[column], hue = plot_data['parameter'], palette="magma")
            # hue = plot_data['parameter'].to_numpy()  --> palette = "crest"
            ax.set_xlim(0,500)
            ax.set_ylim(1,22)

            plt.xlabel("Time (s)")
            if name is not None:
                plt.ylabel(f"{name} (uM)")
                plt.title(f"{name} at {location.upper()}")
            else:
                if column.startswith('Sum'):
                    plt.ylabel(f"Total {active} {species} (uM)")
                    plt.title(f"Total {active} {species}")
                else:
                    plt.ylabel(f"{species} (uM)")
                    plt.title(f"{tag}% acH2A at the arms")
                    plt.text(150, 10, f"Ratio at 200s = {ratio}", fontsize=8)

            #Change legend labels here following simulation order:
                L=ax.legend()
                L.get_texts()[0].set_text('Relaxed KT')
                L.get_texts()[1].set_text('Relaxed BG')
                L.get_texts()[2].set_text('Tensed KT')
                L.get_texts()[3].set_text('Tensed BG')
                
                sns.move_legend(ax, "best", labelspacing = 0.01, fontsize='7')
                plt.setp(plt.gca().get_legend().get_texts())
                # plt.legend(labelspacing=0.01, fontsize='7')
                plt.tight_layout()
                print("saving fig")
                print(tag)
                plt.savefig(f"/Users/catalinaalvarez/Documents/CPC_plots_2026/figures/lineplot_across_sims/{name_plot}_{tag}%_kt_bg_500s.pdf")
            tag = tag + 5
            plt.show()
            plt.close()

    else:
        if active == 'inactive' and column == 'Sum_Active':
            column = 'Sum_Inactive'
        if active == 'active' and column == 'Sum_Inactive':
            column = 'Sum_Active'  
            for p, z in zip(plot_list, location):
                tmp = pd.read_csv(f"{in_dir}/{p}/data/data_{active}_{z}_{species}.csv", header = 0, index_col = None)
                tmp['Time'] = 10*tmp['Time']
                tmp['parameter'] = p + z
                plot_data = pd.concat([plot_data,tmp[['parameter',column, 'Time']]], ignore_index=True)

    
name_folder = "cata"
in_dir_ = "/Users/catalinaalvarez/Documents/CPC_plots_2026"
plot_list = [
            "05_08_26_metacentric_relaxed_MCF10A_chr19_PMP1_acH2A_arms_0P",
            "05_08_26_metacentric_tensed_MCF10A_chr19_PMP1_acH2A_arms_0P",
            "05_08_26_metacentric_relaxed_MCF10A_chr19_PMP1_acH2A_arms_5P",
            "05_08_26_metacentric_tensed_MCF10A_chr19_PMP1_acH2A_arms_5P",
            "05_08_26_metacentric_relaxed_MCF10A_chr19_PMP1_acH2A_arms_10P",
            "05_08_26_metacentric_tensed_MCF10A_chr19_PMP1_acH2A_arms_10P",
            "05_08_26_metacentric_relaxed_MCF10A_chr19_PMP1_acH2A_arms_15P",
            "05_08_26_metacentric_tensed_MCF10A_chr19_PMP1_acH2A_arms_15P",
            "05_08_26_metacentric_relaxed_MCF10A_chr19_PMP1_acH2A_arms_20P",
            "05_08_26_metacentric_tensed_MCF10A_chr19_PMP1_acH2A_arms_20P",
            "05_08_26_metacentric_relaxed_MCF10A_chr19_PMP1_acH2A_arms_25P",
            "05_08_26_metacentric_tensed_MCF10A_chr19_PMP1_acH2A_arms_25P",
            "05_08_26_metacentric_relaxed_MCF10A_chr19_PMP1_acH2A_arms_30P",
            "05_08_26_metacentric_tensed_MCF10A_chr19_PMP1_acH2A_arms_30P",
            "05_08_26_metacentric_relaxed_MCF10A_chr19_PMP1_acH2A_arms_35P",
            "05_08_26_metacentric_tensed_MCF10A_chr19_PMP1_acH2A_arms_35P",
            "05_08_26_metacentric_relaxed_MCF10A_chr19_PMP1_acH2A_arms_40P",
            "05_08_26_metacentric_tensed_MCF10A_chr19_PMP1_acH2A_arms_40P",
            "05_08_26_metacentric_relaxed_MCF10A_chr19_PMP1_acH2A_arms_45P",
            "05_08_26_metacentric_tensed_MCF10A_chr19_PMP1_acH2A_arms_45P",
            "05_08_26_metacentric_relaxed_MCF10A_chr19_PMP1_acH2A_arms_50P",
            "05_08_26_metacentric_tensed_MCF10A_chr19_PMP1_acH2A_arms_50P",
            "05_08_26_metacentric_relaxed_MCF10A_chr19_PMP1_acH2A_arms_55P",
            "05_08_26_metacentric_tensed_MCF10A_chr19_PMP1_acH2A_arms_55P",
            "05_08_26_metacentric_relaxed_MCF10A_chr19_PMP1_acH2A_arms_60P",
            "05_08_26_metacentric_tensed_MCF10A_chr19_PMP1_acH2A_arms_60P",
            "05_08_26_metacentric_relaxed_MCF10A_chr19_PMP1_acH2A_arms_65P",
            "05_08_26_metacentric_tensed_MCF10A_chr19_PMP1_acH2A_arms_65P",
            "05_08_26_metacentric_relaxed_MCF10A_chr19_PMP1_acH2A_arms_70P",
            "05_08_26_metacentric_tensed_MCF10A_chr19_PMP1_acH2A_arms_70P",
            "05_08_26_metacentric_relaxed_MCF10A_chr19_PMP1_acH2A_arms_75P",
            "05_08_26_metacentric_tensed_MCF10A_chr19_PMP1_acH2A_arms_75P",
            "05_08_26_metacentric_relaxed_MCF10A_chr19_PMP1_acH2A_arms_80P",
            "05_08_26_metacentric_tensed_MCF10A_chr19_PMP1_acH2A_arms_80P",
            "05_08_26_metacentric_relaxed_MCF10A_chr19_PMP1_acH2A_arms_85P",
            "05_08_26_metacentric_tensed_MCF10A_chr19_PMP1_acH2A_arms_85P",
            "05_08_26_metacentric_relaxed_MCF10A_chr19_PMP1_acH2A_arms_90P",
            "05_08_26_metacentric_tensed_MCF10A_chr19_PMP1_acH2A_arms_90P",
            "05_08_26_metacentric_relaxed_MCF10A_chr19_PMP1_acH2A_arms_95P",
            "05_08_26_metacentric_tensed_MCF10A_chr19_PMP1_acH2A_arms_95P",
            "05_08_26_metacentric_relaxed_MCF10A_chr19_PMP1_acH2A_arms_100P",
            "05_08_26_metacentric_tensed_MCF10A_chr19_PMP1_acH2A_arms_100P"
                                            ]

location = ["kt", 
            "bg"
                ]

plot_across_models('CPC', plot_list, in_dir_, location, name_plot="Comparison arms ",active= 'all')

