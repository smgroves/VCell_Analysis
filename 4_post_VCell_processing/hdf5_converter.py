import pandas as pd
import h5py
import os
import sys
import time
import seaborn as sns
import matplotlib.pyplot as plt
import argparse

# read in arguments from command line using sys.argv
if True:
    file_name = sys.argv[1]
    dir_path = sys.argv[2]
    model_name = sys.argv[3]
    simulation_name = sys.argv[4]
    width = int(sys.argv[5])

    if len(sys.argv) > 6:
        parser = argparse.ArgumentParser()
        parser.add_argument('file_name', metavar='N')
        parser.add_argument('dir_path', metavar='N')
        parser.add_argument('model_name', metavar='N')
        parser.add_argument('simulation_name', metavar='N')
        parser.add_argument('width', metavar='N', type=int)
        parser.add_argument(
            "--species",  # name on the CLI - drop the `--` for positional/required parameters
            nargs="*",  # 0 or more values expected => creates a list
            type=str,
            default=[],  # default if nothing is provided
        )
        # parse the command line
        args = parser.parse_args()
        file_name = args.file_name
        dir_path = args.dir_path
        model_name = args.model_name
        simulation_name = args.simulation_name
        width = args.width
        species_list = args.species
        print(species_list)
    else:
        species_list = []

else:
    # Use example data
    file_name = "SimID_259656558_0__exported.hdf5"
    dir_path = "/Users/smgroves/Box/CPC_Model_Project/VCell_Exports/"
    model_name = "08_21_23_CPC_relaxed_RefModel_TTK_phos_PLK1a transactiv_sarah"
    simulation_name = (
        "08_21_23_relaxed_RefModel_TTK_phos_PLK1a_20Pac transactiv_KmTTK_5.4"
    )


def convert_hdf5_to_csv(
    file_name, dir_path="", model_name="", simulation_name="", species_list=[], width=64
):
    if len(species_list) == 0:
        default_species = [
            "BUB1a",
            "BUB1a_his",
            "BUB1a_pKNL1",
            "CPCa",
            "CPCi",
            "H2A",
            "H3",
            "H3_CPCa",
            "H3_CPCi",
            "HASPINa",
            "HASPINi",
            "I",
            "KNL1",
            "NDC80",
            "NDC80_TTKa",
            "NDC80_TTKi",
            "NDC80_pTTKa",
            "NDC80_pTTKi",
            "pH2A",
            "pH2A_SGO1",
            "pH2A_SGO1_CPCa",
            "pH2A_SGO1_CPCi",
            "pH3",
            "pH3_CPCa",
            "pH3_CPCi",
            "pKNL1",
            "PLK1a",
            "PLK1i",
            "pTTKa",
            "pTTKi",
            "pNDC80",
            "pNDC80_TTKa",
            "pNDC80_TTKi",
            "pNDC80_pTTKa",
            "pNDC80_pTTKi",
            "SGO1",
            "SGO1_CPCi",
            "SGO1_CPCa",
            "SGO1_CPCi_pH3",
            "SGO1_CPCa_pH3",
            "TTKa",
            "TTKi",
        ]
        default_functions = [
            "CPC_all",
            "CPCi_total",
            "CPCa_total",
            "pH2_all",
            "bound_CPC",
            "bound_active_CPC",
            "boundactive_CPC_pNDC80"
        ]
        default_species = default_species + default_functions

        print(f"Using default species list of length {len(default_species)}")
    else:
        default_species = species_list
        print(f"Using species list of length {len(default_species)}")
    with h5py.File(f"{dir_path}/{file_name}", "r") as h5:
        print(len(h5.keys()), "simulation(s) found")
        for sim_key in h5.keys():
            sim_key_name = "_".join(sim_key.split(
                "[")[1].split("]")[0].split(",")[0:2])
            print(sim_key_name)
            output_folder = f"{dir_path}/SimID_{sim_key_name}__exported"
            # make directory if it doesn't exist
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)
            timesteps = h5[sim_key]["TIMES"][:]
            for key in h5[sim_key].keys():
                if key in default_species:
                    try:
                        print(key)
                        # convert 3D numpy array to multiple 2D numpy arrays
                        arr = h5[sim_key][key]["DataValues (XYT)"][:]
                        for i in range(arr.shape[2]):
                            header_text = (
                                f"Model: {model_name}\n"
                                f"Simulation: {simulation_name}\n"
                                f"(SimID_{sim_key_name} (PDE Simulation)) \n"
                                f"Sim time range ({min(timesteps)} {max(timesteps)}) (saved timepoints {len(timesteps)}) \n"
                                f"Number of variables {len(h5[sim_key].keys())-2} \n"
                                f"Variable names {list(h5[sim_key].keys())} \n \n"
                                f"2D Slice for variable {key} at time {timesteps[i]} in plane XY at Z = 0 \n \n"
                                "X in rows, Y in columns \n"
                            )
                            with open(
                                f"{output_folder}/SimID_{sim_key_name}__Slice_XY_0_{key}_{i:04d}.csv",
                                "w",
                            ) as f:
                                f.write(header_text)
                                f.close()
                            df = pd.DataFrame(arr[:, 0:width, i])
                            if key in default_functions:
                                df.to_csv(
                                    f"{output_folder}/SimID_{sim_key_name}__Slice_XY_0_{key}_FUNCTION_{i:04d}.csv",
                                    index=False,
                                    mode="a",
                                    header=False,
                                )
                            else:
                                df.to_csv(
                                    f"{output_folder}/SimID_{sim_key_name}__Slice_XY_0_{key}_{i:04d}.csv",
                                    index=False,
                                    mode="a",
                                    header=False,
                                )
                    except ValueError:
                        pass


if __name__ == "__main__":
    t1 = time.time()
    convert_hdf5_to_csv(file_name, dir_path, model_name,
                        simulation_name, species_list, width)
    t2 = time.time()
    print("Processing took ", (t2 - t1), " seconds")
