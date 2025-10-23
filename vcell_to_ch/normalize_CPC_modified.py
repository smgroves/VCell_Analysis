import pandas as pd
import os
import numpy as np
in_dir = "/Users/catalinaalvarez/Documents/cpc_data_2023/"

# folder_name = 'SimID_261879028_0__exported'
# model_name = "10_16_23_CPC_relaxed_RefModel_128x64"
# simulation_name = "10_16_23_relaxed_RefModel_Mps1_phos_Plk1a_20Pac_transactiv"
# outdir = '/Users/smgroves/Documents/GitHub/Cahn_Hilliard_Model/data/'
# timepoint = 500

def pad_with(vector, pad_width, iaxis, kwargs):
    pad_value = kwargs.get('padder', 0)
    vector[:pad_width[0]] = pad_value
    if pad_width[1] != 0:                      # <-- the only change (0 indicates no padding)
        vector[-pad_width[1]:] = pad_value

def prolong(uc, nxc, nyc):
    uf = np.zeros((2 * nxc, 2 * nyc))
    for i in range(nxc):
        for j in range(nyc):
            uf[2 * i][2 * j] = uf[2 * i + 1][2 * j] = uf[2 * i][2 * j + 1] = uf[2 * i + 1][2 * j + 1] = uc[i][j]
    return uf

def rescale_vcell_output(folder_name, in_dir, model_name = "", simulation_name = "", timepoint = 200,
                         timestep = 10, min_mix = 4, rescaling_factor = 8.4):

    data = {}
    timeslice_id = "00" + str(int(timepoint/timestep))
    # CPC_species = ["CPCi",'CPCa','pH2A_Sgo1_CPCa', 'pH2A_Sgo1_CPCi', 'pH2A_Sgo1_pH3_CPCa', 'pH2A_Sgo1_pH3_CPCi','pH3_CPCa', 'pH3_CPCi']
    for file in os.listdir(os.path.join(in_dir,folder_name)):
        if "CPC" in file:
            if timeslice_id in file:
                name = file.split("0_")[-1].split(f"_{timeslice_id}.")[0]
                data[name] = pd.read_csv(os.path.join(in_dir,folder_name,file), sep=",",
                                         skiprows = 10, header = None)

    sum_data = pd.DataFrame(0, columns = data["CPCi"].columns, index = data["CPCi"].index)
    for key in data.keys():
        sum_data = sum_data.add(data[key])

    sum_data_array = np.array(sum_data)
    sum_data_array = (sum_data_array - min_mix)/(rescaling_factor - min_mix)


    #pad the sides of the array with zeros so it is square
    width = sum_data_array.shape[0]-sum_data_array.shape[1]
    sum_data_array = (np.pad(sum_data_array, ((0, 0), (int(width/2), int(width/2))), pad_with, padder=0))

    nrows= sum_data_array.shape[0]
    ncols= sum_data_array.shape[1]
    sum_data_array.max()

    np.savetxt(os.path.join(in_dir,folder_name,f"{model_name}_{simulation_name}_{timepoint}_{nrows}x{ncols}.csv"), sum_data_array, delimiter=",")

    arr_2fold = prolong(sum_data_array, nrows, ncols)
    np.savetxt(os.path.join(in_dir,folder_name,f"{model_name}_{simulation_name}_{timepoint}_{arr_2fold.shape[0]}x{arr_2fold.shape[1]}.csv"), arr_2fold, delimiter=",")

    arr_4fold = prolong(arr_2fold, arr_2fold.shape[0], arr_2fold.shape[1])
    np.savetxt(os.path.join(in_dir,folder_name,f"{model_name}_{simulation_name}_{timepoint}_{arr_4fold.shape[0]}x{arr_4fold.shape[1]}.csv"), arr_4fold, delimiter=",")

def rescale_vcell_output_neg1_pos1(folder_name, in_dir, outdir, model_name = "", simulation_name = "", timepoint = 200,
                         timestep = 10, min_mix = 2, rescaling_factor = 5, suffix = ""):

    data = {}
    if timepoint == 0:
        timeslice_id = "0000"
    elif timepoint < 100:
        timeslice_id= "000" + str(int(timepoint/timestep))
    else:
        timeslice_id = "00" + str(int(timepoint/timestep))

    print(timeslice_id)
    # CPC_species = ["CPCi",'CPCa','pH2A_Sgo1_CPCa', 'pH2A_Sgo1_CPCi', 'pH2A_Sgo1_pH3_CPCa', 'pH2A_Sgo1_pH3_CPCi','pH3_CPCa', 'pH3_CPCi']
    for file in os.listdir(os.path.join(in_dir,folder_name)):
        if "CPC" in file:
            if timeslice_id in file:
                name = file.split("0_")[-1].split(f"_{timeslice_id}.csv")[0]
                print(name)
                data[name] = pd.read_csv(os.path.join(in_dir,folder_name,file), sep=",",
                                         skiprows = 10, header = None)

    sum_data = pd.DataFrame(0, columns = data["CPCi"].columns, index = data["CPCi"].index)
    for key in data.keys():
        sum_data = sum_data.add(data[key])

    sum_data_array = np.array(sum_data)
    #sum_data_array = sum_data_array/rescaling_factor
    print(sum_data_array.max())
    print(sum_data_array.min())
    sum_data_array = (sum_data_array - min_mix)/(rescaling_factor - min_mix)
    print(sum_data_array.max())
    print(sum_data_array.min())
    
    for r_idx, row in enumerate(sum_data_array):
        for c_idx, value in enumerate(row):
            if value == (- min_mix)/(rescaling_factor - min_mix):
                sum_data_array[r_idx][c_idx] = 0
    
    print(sum_data_array.max())
    print(sum_data_array.min())

    #pad the sides of the array with zeros so it is square
    width = sum_data_array.shape[0]-sum_data_array.shape[1]

    sum_data_array = (np.pad(sum_data_array, ((0, 0), (int(width/2), int(width/2))), pad_with, padder=0))
    nrows= sum_data_array.shape[0]
    ncols= sum_data_array.shape[1]
    sum_data_array = (2*sum_data_array) - 1
    print(sum_data_array.max())
    print(sum_data_array.min())

    np.savetxt(os.path.join(outdir,f"{model_name}_{simulation_name}_{timepoint}_{nrows}x{ncols}_{suffix}.csv"), sum_data_array, delimiter=",")
    
    arr_2fold = prolong(sum_data_array, nrows, ncols)
    print(arr_2fold.shape)
    np.savetxt(os.path.join(outdir,f"{model_name}_{simulation_name}_{timepoint}_{arr_2fold.shape[0]}x{arr_2fold.shape[1]}_{suffix}.csv"), arr_2fold, delimiter=",")

    #
    # arr_2fold = prolong(sum_data_array, nrows, ncols)
    # np.savetxt(os.path.join(outdir,folder_name,f"{model_name}_{simulation_name}_{timepoint}_{arr_2fold.shape[0]}x{arr_2fold.shape[1]}{suffix}.csv"), arr_2fold, delimiter=",")
    #
    # arr_4fold = prolong(arr_2fold, arr_2fold.shape[0], arr_2fold.shape[1])
    # np.savetxt(os.path.join(outdir,folder_name,f"{model_name}_{simulation_name}_{timepoint}_{arr_4fold.shape[0]}x{arr_4fold.shape[1]}{suffix}.csv"), arr_4fold, delimiter=",")

# rescale_vcell_output_neg1_pos1(folder_name, in_dir, outdir, model_name = model_name, simulation_name = simulation_name, timepoint = 100,
                        #  timestep = 10, rescaling_factor = 10, suffix = "100s_10max_")

# folder_name ="SimID_270418727_0__exported"
# model_name = "03_25_24_CPC_relaxed_RefModel_128x64"
# simulation_name = "03_25_24_relaxed_RefModel"
# outdir = '/Users/smgroves/Documents/GitHub/Cahn_Hilliard_Model/data/'
# rescale_vcell_output_neg1_pos1(folder_name, in_dir, outdir, model_name = model_name, simulation_name = simulation_name, timepoint = 200,
#                          timestep = 10, rescaling_factor = 5, suffix = "200s_5max")
# # rescale_vcell_output_neg1_pos1(folder_name, in_dir, outdir, model_name = model_name, simulation_name = simulation_name, timepoint = 200,
# #                          timestep = 10, rescaling_factor = 10, suffix = "200s_10max")
# # rescale_vcell_output_neg1_pos1(folder_name, in_dir, outdir, model_name = model_name, simulation_name = simulation_name, timepoint = 200,
# #                          timestep = 10, rescaling_factor = 7, suffix = "200s_7max")

# folder_name = "SimID_270418727_0__exported"
# model_name="03_25_24_CPC_relaxed_RefModel_128x64"
# simulation_name ="03_25_24_relaxed_RefModel"
# outdir = '/Users/smgroves/Documents/GitHub/Cahn_Hilliard_Model/data/'
# for timepoint in [100,200,300,400]:
#     rescale_vcell_output_neg1_pos1(folder_name, in_dir, outdir, model_name = model_name, simulation_name = simulation_name, timepoint = timepoint,
#                          timestep = 10, rescaling_factor = 8.4, suffix = f"{timepoint}s_8.4max")

# folder_name = "SimID_270510934_0__exported"
# model_name="03_25_24_CPC_tensed_RefModel_128x64"
# simulation_name ="04_02_24_tensed_RefModel"
# outdir = '/Users/smgroves/Documents/GitHub/Cahn_Hilliard_Model/data/'
# for timepoint in [100,200,300,400]:
#     rescale_vcell_output_neg1_pos1(folder_name, in_dir, outdir, model_name = model_name, simulation_name = simulation_name, timepoint = timepoint,
#                          timestep = 10, rescaling_factor = 8.4, suffix = f"{timepoint}s_8.4max")

# folder_name = "SimID_262253748_0__exported"
# model_name="10_24_23_CPC_tensed_RefModel_128x64_post_transition"
# simulation_name ="10_25_23_400s_post_transition_base_20Pac"
# outdir = '/Users/smgroves/Documents/GitHub/Cahn_Hilliard_Model/data/'
# for timepoint in [00, 100,200,300,400]:
#     print(timepoint)
#     rescale_vcell_output_neg1_pos1(folder_name, in_dir, outdir, model_name = model_name, simulation_name = simulation_name, timepoint = timepoint,
#                          timestep = 10, rescaling_factor = 8.4, suffix = f"{timepoint}s_8.4max")

# folder_name = "SimID_261879028_0__exported"
# model_name="10_16_23_CPC_relaxed_RefModel_128x64"
# simulation_name ="10_16_23_relaxed_RefModel_Mps1_phos_Plk1a_20Pac_transactiv"
# outdir = '/Users/smgroves/Documents/GitHub/Cahn_Hilliard_Model/data/'
# for timepoint in [00, 100,200,300,400]:
#     print(timepoint)
#     rescale_vcell_output_neg1_pos1(folder_name, in_dir, outdir, model_name = model_name, simulation_name = simulation_name, timepoint = timepoint,
#                          timestep = 10, rescaling_factor = 8.4, suffix = f"{timepoint}s_8.4max")
    

# folder_name = "SimID_272623071_0__exported"
# model_name="10_24_23_CPC_tensed_RefModel_128x64_post_transition"
# simulation_name ="07_14_24_500s_post_transition_base_20Pac"
# outdir = '/Users/smgroves/Documents/GitHub/Cahn_Hilliard_Model/data/'
# for timepoint in [00, 10, 20, 50]:
#     print(timepoint)
#     rescale_vcell_output_neg1_pos1(folder_name, in_dir, outdir, model_name = model_name, simulation_name = simulation_name, timepoint = timepoint,
#                          timestep = 10, rescaling_factor = 8.4, suffix = f"{timepoint}s_8.4max")
    

# folder_name = "SimID_261879028_0__exported"
# model_name="10_16_23_CPC_relaxed_RefModel_128x64"
# simulation_name ="10_16_23_relaxed_RefModel_Mps1_phos_Plk1a_20Pac_transactiv"
# outdir = '/Users/smgroves/Documents/GitHub/Cahn_Hilliard_Model/data/'
# for timepoint in [50, 70]:
#     print(timepoint)
#     rescale_vcell_output_neg1_pos1(folder_name, in_dir, outdir, model_name = model_name, simulation_name = simulation_name, timepoint = timepoint,
#                          timestep = 10, rescaling_factor = 8.4, suffix = f"{timepoint}s_8.4max")


folder_name = "SimID_296831234_2__exported"
model_name= "09_16_25 CPC_metacentric_relaxed_model "
simulation_name = "09_30_25_metacentric_relaxed_model_HeLa_CPC_Sgo1low_pH2Ainh_1"
outdir = '/Users/catalinaalvarez/Documents/cpc_ch_data_2025/'
rescale_vcell_output_neg1_pos1(folder_name, in_dir, outdir, model_name = model_name, simulation_name = simulation_name, timepoint = 200,
                         timestep = 10, min_mix = 2, rescaling_factor = 5, suffix = "0s_8.4max")
    
# folder_name = "SimID_261879026_0__exported"
# model_name="10_16_23_CPC_relaxed_RefModel_128x64"
# simulation_name ="10_16_23_relaxed_RefModel_Mps1_phos_Plk1a_transactiv"
# outdir = '/Users/smgroves/Documents/GitHub/Cahn_Hilliard_Model/data/'
# rescale_vcell_output_neg1_pos1(folder_name, in_dir, outdir, model_name = model_name, simulation_name = simulation_name, timepoint = 70,
#                          timestep = 10, rescaling_factor = 8.4, suffix = f"70s_8.4max")