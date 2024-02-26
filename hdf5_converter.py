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

    if len(sys.argv)>5:
        parser = argparse.ArgumentParser()
        parser.add_argument('file_name', metavar='N')
        parser.add_argument('dir_path', metavar='N')
        parser.add_argument('model_name', metavar='N')
        parser.add_argument('simulation_name', metavar='N')
        parser.add_argument(
            "--species",  # name on the CLI - drop the `--` for positional/required parameters
            nargs="*",  # 0 or more values expected => creates a list
            type=str,
            default=[],  # default if nothing is provided
        )
        # parse the command line
        args = parser.parse_args()
        file_name=args.file_name
        dir_path = args.dir_path
        model_name = args.model_name
        simulation_name = args.simulation_name
        species_list = args.species
        print(species_list)
    else:
        species_list = []

else:
    # Use example data
    file_name = "SimID_259656558_0__exported.hdf5"
    dir_path = "/Users/smgroves/Box/CPC_Model_Project/VCell_Exports/"
    model_name = "08_21_23_CPC_relaxed_RefModel_Mps1_phos_Plk1a transactiv_sarah"
    simulation_name = (
        "08_21_23_relaxed_RefModel_Mps1_phos_Plk1a_20Pac transactiv_KmMps1_5.4"
    )




def convert_hdf5_to_csv(
    file_name, dir_path="", model_name="", simulation_name="", species_list=[]
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
        print(len(h5.keys()), "simulation(s) found")
        for sim_key in h5.keys():
            sim_key_name = "_".join(sim_key.split("[")[1].split("]")[0].split(",")[0:2])
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
                            df = pd.DataFrame(arr[:, 0:64, i]) #changed for cytoplasmic simulations
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
    convert_hdf5_to_csv(file_name, dir_path, model_name, simulation_name, species_list)
    t2 = time.time()
    print("Processing took ", (t2 - t1), " seconds")
