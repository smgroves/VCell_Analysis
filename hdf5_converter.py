import pandas as pd
import h5py
import os


def convert_hdf5_to_csv(file_name, dir_path, model_name = "", simulation_name = ""):
    output_folder = f"{dir_path}/{file_name.split('.')[0]}"
    #make directory if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    with h5py.File(f"{dir_path}/{file_name}", 'r') as h5:
        print(len(h5.keys()), "simulation(s) found")
        for sim_key in h5.keys():
            sim_key_name = ("_".join(sim_key.split("[")[1].split("]")[0].split(",")[0:2]))
            print(sim_key_name)
            timesteps = h5[sim_key]['TIMES'][:]
            for key in h5[sim_key].keys():
                try:
                    print(key)
                    # convert 3D numpy array to multiple 2D numpy arrays
                    arr = h5[sim_key][key]["DataValues (XYT)"][:]
                    for i in range(arr.shape[2]):
                        header_text = f"Model: {model_name}\n" \
                                        f"Simulation: {simulation_name}\n" \
                                        f"(SimID_{sim_key_name} (PDE Simulation)) \n" \
                                        f"Sim time range ({min(timesteps)} {max(timesteps)}) (saved timepoints {len(timesteps)}) \n" \
                                        f"Number of variables {len(h5[sim_key].keys())-2} \n" \
                                        f"Variable names {h5[sim_key].keys()} \n \n" \
                                        f"2D Slice for variable {key} at time {timesteps[i]} in plane XY at Z = 0 \n \n" \
                                        "X in rows, Y in columns \n"
                        with open(f"{output_folder}/SimID_{sim_key_name}__Slice_XY_0_{key}_00{i}.csv", 'w') as f:
                            f.write(header_text)
                            f.close()
                        df = pd.DataFrame(arr[:,:,i])
                        df.to_csv(f"{output_folder}/SimID_{sim_key_name}__Slice_XY_0_{key}_00{i}.csv", index=False, mode = 'a', header = False)
                except ValueError: pass

# example run
dir_path = '/Users/smgroves/Box/CPC_Model_Project/VCell_Exports/'
file_name = 'SimID_259656558_0__exported.hdf5'
model_name = "08_21_23_CPC_relaxed_RefModel_Mps1_phos_Plk1a transactiv_sarah"
simulation_name = "08_21_23_relaxed_RefModel_Mps1_phos_Plk1a_20Pac transactiv_KmMps1_5.4"

convert_hdf5_to_csv(file_name, dir_path, model_name, simulation_name)