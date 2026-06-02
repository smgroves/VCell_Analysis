#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 20 2026
"""
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os
import re

def plot_across_models(species, plot_list, in_dir, location, timepoint, name_list = [], column = "Sum_Active", active = 'active',
                        name = None, name_plot="", name_folder =""):
    print("Plotting across models")
    
    #fcCPC
    if os.path.isdir(f"/Users/catalinaalvarez/Documents/CPC_plots_2026/CPC_readouts/fcCPC/{name_folder}"):
        pass
    else:
        os.makedirs(f"/Users/catalinaalvarez/Documents/CPC_plots_2026/CPC_readouts/fcCPC/{name_folder}")
        print(f"Made folder {name_folder}")
    if len(name_list) == 0:
        name_list = plot_list 
    if active == 'all':
        tag = 0
        df = pd.DataFrame(columns=["state", "percentage", "fcCPC"])
        for n, p in zip(name_list,plot_list):
            tmpc = pd.DataFrame()
            for z in location:
                    if z in ['kt', 'ic']:
                        tmp1 = pd.read_csv(f"{in_dir}/{p}/data/data_{z}_{species}.csv", header = 0, index_col = None)
                        tmp1['Time'] = 10*tmp1['Time']
                        tmp1['parameter'] = n + z
                        tmp1['all'] = tmp1[list(set(tmp1.columns).difference({"Time",'parameter'}))].sum(axis = 1)
                                     
                    else:
                        tmp2 = pd.read_csv(f"{in_dir}/{p}/data/data_{z}_{species}.csv", header = 0, index_col = None)
                        tmp2['Time'] = 10*tmp2['Time']
                        tmp2['parameter'] = n + z
                        tmp2['all'] = tmp2[list(set(tmp2.columns).difference({"Time",'parameter'}))].sum(axis = 1)
                            
            tmpc['Time'] = tmp1['Time']
            tmpc['parameter'] = tmp1['parameter']
            tmpc['bg_corrected'] = tmp1['all'] / tmp2['all']
            state = re.search(r"metacentric_([^_]+)_MCF", n).group(1)
            percentage = int(re.search(r"arms_([^_]+)P", n).group(1))
            fcCPC = tmpc.loc[tmpc['Time'] == timepoint, 'bg_corrected'].values[0]

            df.loc[len(df)] = [state, percentage, fcCPC]

        print(df)
        print(len(df))
        df.to_excel(f"/Users/catalinaalvarez/Documents/CPC_plots_2026/CPC_readouts/fcCPC/{name_plot}_{location[0]}_at_{timepoint}s.xlsx")

        fig = plt.figure(figsize = (5,4.5))
        sns.lineplot(data=df, x="percentage", y="fcCPC", hue="state", marker="o", markersize=3, palette="magma", linewidth=3)
        plt.ylabel(fr'fcCPC', fontsize=12)
        plt.xlabel("acH2A at the arms (%)", fontsize=12)
        plt.legend(title="Chromosome state")
        if location[0] == "ic":
            plt.title(fr"fcCPC at inner centromere ({timepoint} s)")
        else: 
            plt.title(fr"fcCPC at kinetochores ({timepoint} s)")    
        plt.savefig(f"/Users/catalinaalvarez/Documents/CPC_plots_2026/CPC_readouts/fcCPC/{name_plot}_{location[0]}_at_{timepoint}s.pdf")
        

        #DfcCPC
        if os.path.isdir(f"/Users/catalinaalvarez/Documents/CPC_plots_2026/CPC_readouts/DfcCPC/{name_folder}"):
                pass
        else:
            os.makedirs(f"/Users/catalinaalvarez/Documents/CPC_plots_2026/CPC_readouts/DfcCPC/{name_folder}")
            print(f"Made folder {name_folder}")
        df2 = pd.DataFrame(columns=["state", "percentage", "DfcCPC"])
        for i in range(0, len(df), 2): 
            state = "relaxed - tensed"
            percentage =  df['percentage'].iloc[i]
            DfcCPC =  df['fcCPC'].iloc[i] - df['fcCPC'].iloc[i+1]
            df2.loc[len(df2)] = [state, percentage, DfcCPC]

        print(df2)
        df2.to_excel(f"/Users/catalinaalvarez/Documents/CPC_plots_2026/CPC_readouts/DfcCPC/{name_plot}_{location[0]}_at_{timepoint}s.xlsx")

        fig = plt.figure(figsize = (5,4.5))
        sns.lineplot(data=df2, x="percentage", y="DfcCPC", marker="o", markersize=3, palette="magma", linewidth=3)
        plt.ylabel(fr'$\Delta fcCPC$', fontsize=12)
        plt.xlabel("acH2A at the arms (%)", fontsize=12)
        if location[0] == "ic":
            plt.title(fr"$\Delta fcCPC$ at inner centromere ({timepoint} s)")
        else: 
            plt.title(fr"$\Delta fcCPC$ at kinetochores ({timepoint} s)")    
        plt.savefig(f"/Users/catalinaalvarez/Documents/CPC_plots_2026/CPC_readouts/DfcCPC/{name_plot}_{location[0]}_at_{timepoint}s.pdf")


        #fcfcCPC
        if os.path.isdir(f"/Users/catalinaalvarez/Documents/CPC_plots_2026/CPC_readouts/fcfcDCPC/{name_folder}"):
                pass
        else:
            os.makedirs(f"/Users/catalinaalvarez/Documents/CPC_plots_2026/CPC_readouts/fcfcDCPC/{name_folder}")
            print(f"Made folder {name_folder}")

        df3 = pd.DataFrame(columns=["state", "percentage", "fcfcCPC"])
        for i in range(0, len(df), 2): 
            state = "relaxed - tensed"
            percentage =  df['percentage'].iloc[i]
            fcfcCPC =  df['fcCPC'].iloc[i] / df['fcCPC'].iloc[i+1]
            df3.loc[len(df3)] = [state, percentage, fcfcCPC]

        print(df3)
        df3.to_excel(f"/Users/catalinaalvarez/Documents/CPC_plots_2026/CPC_readouts/fcfcCPC/{name_plot}_{location[0]}_at_{timepoint}s.xlsx")

        fig = plt.figure(figsize = (5.5,4.5))
        sns.lineplot(data=df3, x="percentage", y="fcfcCPC", marker="o", markersize=3, palette="magma", linewidth=3)
        plt.ylabel(fr'fcfcCPC', fontsize=12)
        plt.xlabel("acH2A at the arms (%)", fontsize=12)
        # plt.ylim(1.7,2)
        if location[0] == "ic":
            plt.title(fr"fcfcCPC at inner centromere ({timepoint} s)")
        else: 
            plt.title(fr"fcfcCPC at kinetochores ({timepoint} s)")    
        plt.savefig(f"/Users/catalinaalvarez/Documents/CPC_plots_2026/CPC_readouts/fcfcCPC/{name_plot}_{location[0]}_at_{timepoint}s.pdf")


    else: 
        print("Check needed species or complete this code")


    
name_folder = "folder"
in_dir_ = "/Users/catalinaalvarez/Documents/CPC_plots_2026"
plot_list = [
            "05_20_26_metacentric_relaxed_MCF10A_chr19_PMP1_acH2A_arms_0P",
            "05_20_26_metacentric_tensed_MCF10A_chr19_PMP1_acH2A_arms_0P",
            "05_20_26_metacentric_relaxed_MCF10A_chr19_PMP1_acH2A_arms_5P",
            "05_20_26_metacentric_tensed_MCF10A_chr19_PMP1_acH2A_arms_5P",
            "05_20_26_metacentric_relaxed_MCF10A_chr19_PMP1_acH2A_arms_10P",
            "05_20_26_metacentric_tensed_MCF10A_chr19_PMP1_acH2A_arms_10P",
            "05_20_26_metacentric_relaxed_MCF10A_chr19_PMP1_acH2A_arms_15P",
            "05_20_26_metacentric_tensed_MCF10A_chr19_PMP1_acH2A_arms_15P",
            "05_20_26_metacentric_relaxed_MCF10A_chr19_PMP1_acH2A_arms_20P",
            "05_20_26_metacentric_tensed_MCF10A_chr19_PMP1_acH2A_arms_20P",
            "05_20_26_metacentric_relaxed_MCF10A_chr19_PMP1_acH2A_arms_25P",
            "05_20_26_metacentric_tensed_MCF10A_chr19_PMP1_acH2A_arms_25P",
            "05_20_26_metacentric_relaxed_MCF10A_chr19_PMP1_acH2A_arms_30P",
            "05_20_26_metacentric_tensed_MCF10A_chr19_PMP1_acH2A_arms_30P",
            "05_20_26_metacentric_relaxed_MCF10A_chr19_PMP1_acH2A_arms_35P",
            "05_20_26_metacentric_tensed_MCF10A_chr19_PMP1_acH2A_arms_35P",
            "05_20_26_metacentric_relaxed_MCF10A_chr19_PMP1_acH2A_arms_40P",
            "05_20_26_metacentric_tensed_MCF10A_chr19_PMP1_acH2A_arms_40P",
            "05_20_26_metacentric_relaxed_MCF10A_chr19_PMP1_acH2A_arms_45P",
            "05_20_26_metacentric_tensed_MCF10A_chr19_PMP1_acH2A_arms_45P",
            "05_20_26_metacentric_relaxed_MCF10A_chr19_PMP1_acH2A_arms_50P",
            "05_20_26_metacentric_tensed_MCF10A_chr19_PMP1_acH2A_arms_50P",
            "05_20_26_metacentric_relaxed_MCF10A_chr19_PMP1_acH2A_arms_55P",
            "05_20_26_metacentric_tensed_MCF10A_chr19_PMP1_acH2A_arms_55P",
            "05_20_26_metacentric_relaxed_MCF10A_chr19_PMP1_acH2A_arms_60P",
            "05_20_26_metacentric_tensed_MCF10A_chr19_PMP1_acH2A_arms_60P",
            "05_20_26_metacentric_relaxed_MCF10A_chr19_PMP1_acH2A_arms_65P",
            "05_20_26_metacentric_tensed_MCF10A_chr19_PMP1_acH2A_arms_65P",
            "05_20_26_metacentric_relaxed_MCF10A_chr19_PMP1_acH2A_arms_70P",
            "05_20_26_metacentric_tensed_MCF10A_chr19_PMP1_acH2A_arms_70P",
            "05_20_26_metacentric_relaxed_MCF10A_chr19_PMP1_acH2A_arms_75P",
            "05_20_26_metacentric_tensed_MCF10A_chr19_PMP1_acH2A_arms_75P",
            "05_20_26_metacentric_relaxed_MCF10A_chr19_PMP1_acH2A_arms_80P",
            "05_20_26_metacentric_tensed_MCF10A_chr19_PMP1_acH2A_arms_80P",
            "05_20_26_metacentric_relaxed_MCF10A_chr19_PMP1_acH2A_arms_85P",
            "05_20_26_metacentric_tensed_MCF10A_chr19_PMP1_acH2A_arms_85P",
            "05_20_26_metacentric_relaxed_MCF10A_chr19_PMP1_acH2A_arms_90P",
            "05_20_26_metacentric_tensed_MCF10A_chr19_PMP1_acH2A_arms_90P",
            "05_20_26_metacentric_relaxed_MCF10A_chr19_PMP1_acH2A_arms_95P",
            "05_20_26_metacentric_tensed_MCF10A_chr19_PMP1_acH2A_arms_95P",
            "05_20_26_metacentric_relaxed_MCF10A_chr19_PMP1_acH2A_arms_100P",
            "05_20_26_metacentric_tensed_MCF10A_chr19_PMP1_acH2A_arms_100P"
                                            ]

location = ["kt", 
            "bg"
                ]

plot_across_models('CPC', plot_list, in_dir_, location, 200 ,name_plot="05_20_26_metacentric_MCF10A_chr19_PMP1",active= 'all')

