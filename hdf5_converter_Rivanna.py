import pandas as pd
import h5py
import os
import sys
import time
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

# read in arguments from command line using sys.argv
if True:
    dir_path = sys.argv[1]
    model_name = sys.argv[2]
    file_name = sys.argv[3]


else:
    # Use example data
    model_name = "_10_16_23"
    dir_path = f"/Users/smgroves/Documents/GitHub/VCell_Analysis/vcell_out/{model_name}"
    file_name = "reports.h5"


def convert_h5_to_csvs(
    dir_path,
    model_name,
    file_name="reports.h5",
    species_list=[],
    sim_key_name="0",
    overwrite=True,
):
    if len(species_list) == 0:
        default_species = [
            "Bub1a",
            "Bub1a_his",
            "CPCa",
            "CPCi",
            "H2A",
            "H3",
            "Haspina",
            "Haspini",
            "Knl1",
            "Mps1a",
            "Mps1i",
            "Ndc80",
            "Ndc80_Mps1a",
            "Ndc80_Mps1i",
            "Ndc80_pMps1a",
            "Ndc80_pMps1i",
            "pH2A",
            "pH2A_Sgo1",
            "pH2A_Sgo1_CPCa",
            "pH2A_Sgo1_CPCi",
            "pH2A_Sgo1_pH3_CPCa",
            "pH2A_Sgo1_pH3_CPCi",
            "pH3",
            "pH3_CPCa",
            "pH3_CPCi",
            "pKnl1",
            "pKnl1_Bub1a",
            "Plk1a",
            "Plk1i",
            "pMps1a",
            "pMps1i",
            "pNdc80",
            "pNdc80_Mps1a",
            "pNdc80_Mps1i",
            "pNdc80_pMps1a",
            "pNdc80_pMps1i",
            "Sgo1",
        ]
        print(f"Using default species list of length {len(default_species)}")
    else:
        default_species = species_list
        print(f"Using species list of length {len(default_species)}")
    with h5py.File(f"{dir_path}/{file_name}", "r") as h5:
        simulation_names = [
            "_".join(i.split("_")[1:]) for i in list(h5[f"{model_name}.sedml"].keys())
        ]
        for simulation_name in simulation_names:
            species = []
            for i in h5[f"{model_name}.sedml"][f"report_{simulation_name}"].attrs[
                "sedmlDataSetNames"
            ]:
                if i.decode("utf-8").split("[")[0] not in species:
                    species.append(i.decode("utf-8").split("[")[0])
            # for each species, grab the correct 3D numpy array, and then for each timepoint save the numpy array as a csv
            # output_folder = f"{dir_path}/{simulation_name}/data"
            # # make directory if it doesn't exist
            # if not os.path.exists(output_folder):
            #     os.makedirs(output_folder)
            # else:
            #     if overwrite:
            #         print("Overwriting existing files")
            #     else:
            #         print("Not overwriting existing files")
            #         continue
            # plot_folder = f"{dir_path}/{simulation_name}/plots"
            # # make directory if it doesn't exist
            # if not os.path.exists(plot_folder):
            #     os.makedirs(plot_folder)
            # else:
            #     if overwrite:
            #         print("Overwriting existing files")
            #     else:
            #         print("Not overwriting existing files")
            #         continue
            print(simulation_name)
            timesteps = h5[f"{model_name}.sedml"][f"report_{simulation_name}"].attrs[
                "times"
            ]
            ndim = h5[f"{model_name}.sedml"][f"report_{simulation_name}"].ndim
            if ndim == 5:
                print("5D array found, reading in parameter scan")
                for p in range(
                    h5[f"{model_name}.sedml"][f"report_{simulation_name}"].shape[1]
                ):
                    output_folder = f"{dir_path}/{simulation_name}_scan{p}/data/"
                    if not os.path.exists(output_folder):
                        os.makedirs(output_folder)
                    else:
                        if overwrite:
                            print("Overwriting existing files")
                        else:
                            print("Not overwriting existing files")
                            continue
                    plot_folder = f"{dir_path}/{simulation_name}_scan{p}/plots/"
                    # make directory if it doesn't exist
                    if not os.path.exists(plot_folder):
                        os.makedirs(plot_folder)
                    else:
                        if overwrite:
                            print("Overwriting existing files")
                        else:
                            print("Not overwriting existing files")
                            continue
                    print(species)
                    for k, key in enumerate(species):
                        if key in default_species:
                            print(key)
                            arr = h5[f"{model_name}.sedml"][
                                f"report_{simulation_name}"
                            ][k, p, :, :, :]
                            # sns.heatmap(arr, vmin = 0, cmap = 'Blues', square = True, )
                            # plt.title(key)
                            # plt.show()
                            for i in range(arr.shape[2]):
                                header_text = (
                                    f"Model: {model_name}\n"
                                    f"Simulation: {simulation_name}\n"
                                    f"(SimID_{sim_key_name} (PDE Simulation)) \n"
                                    f"Sim time range ({min(timesteps)} {max(timesteps)}) (saved timepoints {len(timesteps)}) \n"
                                    f"Number of variables {len(species)} \n"
                                    f"Variable names {species} \n \n"
                                    f"2D Slice for variable {key} at time {timesteps[i]} in plane XY at Z = 0 \n \n"
                                    "X in rows, Y in columns \n"
                                )
                                with open(
                                    f"{output_folder}/SimID_{sim_key_name}__Slice_XY_0_{key}_{i:04d}.csv",
                                    "w",
                                ) as f:
                                    f.write(header_text)
                                    f.close()
                                df = pd.DataFrame(arr[:, :, i])
                                df.to_csv(
                                    f"{output_folder}/SimID_{sim_key_name}__Slice_XY_0_{key}_{i:04d}.csv",
                                    index=False,
                                    mode="a",
                                    header=False,
                                )
            else:
                output_folder = f"{dir_path}/{simulation_name}/data"
                # make directory if it doesn't exist
                if not os.path.exists(output_folder):
                    os.makedirs(output_folder)
                else:
                    if overwrite:
                        print("Overwriting existing files")
                    else:
                        print("Not overwriting existing files")
                        continue
                plot_folder = f"{dir_path}/{simulation_name}/plots"
                # make directory if it doesn't exist
                if not os.path.exists(plot_folder):
                    os.makedirs(plot_folder)
                else:
                    if overwrite:
                        print("Overwriting existing files")
                    else:
                        print("Not overwriting existing files")
                        continue
                for k, key in enumerate(species):
                    if key in default_species:
                        print(key)
                        arr = h5[f"{model_name}.sedml"][f"report_{simulation_name}"][
                            k, :, :, :
                        ]
                        # sns.heatmap(arr, vmin = 0, cmap = 'Blues', square = True, )
                        # plt.title(key)
                        # plt.show()
                        for i in range(arr.shape[2]):
                            header_text = (
                                f"Model: {model_name}\n"
                                f"Simulation: {simulation_name}\n"
                                f"(SimID_{sim_key_name} (PDE Simulation)) \n"
                                f"Sim time range ({min(timesteps)} {max(timesteps)}) (saved timepoints {len(timesteps)}) \n"
                                f"Number of variables {len(species)} \n"
                                f"Variable names {species} \n \n"
                                f"2D Slice for variable {key} at time {timesteps[i]} in plane XY at Z = 0 \n \n"
                                "X in rows, Y in columns \n"
                            )
                            with open(
                                f"{output_folder}/SimID_{sim_key_name}__Slice_XY_0_{key}_{i:04d}.csv",
                                "w",
                            ) as f:
                                f.write(header_text)
                                f.close()
                            df = pd.DataFrame(arr[:, :, i])
                            df.to_csv(
                                f"{output_folder}/SimID_{sim_key_name}__Slice_XY_0_{key}_{i:04d}.csv",
                                index=False,
                                mode="a",
                                header=False,
                            )


if __name__ == "__main__":
    t1 = time.time()
    # convert_hdf5_to_csv(file_name, dir_path, model_name, simulation_name)
    convert_h5_to_csvs(dir_path=dir_path, model_name=model_name)
    t2 = time.time()
    print("Processing took ", (t2 - t1), " seconds")
