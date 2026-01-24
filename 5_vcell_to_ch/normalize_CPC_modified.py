import matplotlib.pyplot as plt
import pandas as pd
import os
import numpy as np
# in_dir = "/Users/catalinaalvarez/Documents/cpc_data_2023/"
# folder_name = 'SimID_261879028_0__exported'
# model_name = "10_16_23_CPC_relaxed_RefModel_128x64"
# simulation_name = "10_16_23_relaxed_RefModel_Mps1_phos_Plk1a_20Pac_transactiv"
# outdir = '/Users/smgroves/Documents/GitHub/Cahn_Hilliard_Model/data/'
# timepoint = 500


def pad_with(vector, pad_width, iaxis, kwargs):
    pad_value = kwargs.get('padder', 0)
    vector[:pad_width[0]] = pad_value
    # <-- the only change (0 indicates no padding)
    if pad_width[1] != 0:
        vector[-pad_width[1]:] = pad_value


def prolong(uc, nxc, nyc):
    uf = np.zeros((2 * nxc, 2 * nyc))
    for i in range(nxc):
        for j in range(nyc):
            uf[2 * i][2 * j] = uf[2 * i + 1][2 * j] = uf[2 *
                                                         i][2 * j + 1] = uf[2 * i + 1][2 * j + 1] = uc[i][j]
    return uf


def rescale_vcell_output(folder_name, in_dir, model_name="", simulation_name="", timepoint=200,
                         timestep=10, min_mix=4, rescaling_factor=8.4):

    data = {}
    timeslice_id = "00" + str(int(timepoint/timestep))
    # CPC_species = ["CPCi",'CPCa','pH2A_Sgo1_CPCa', 'pH2A_Sgo1_CPCi', 'pH2A_Sgo1_pH3_CPCa', 'pH2A_Sgo1_pH3_CPCi','pH3_CPCa', 'pH3_CPCi']
    for file in os.listdir(os.path.join(in_dir, folder_name)):
        if "CPC" in file:
            if timeslice_id in file:
                name = file.split("0_")[-1].split(f"_{timeslice_id}.")[0]
                data[name] = pd.read_csv(os.path.join(in_dir, folder_name, file), sep=",",
                                         skiprows=10, header=None)

    sum_data = pd.DataFrame(
        0, columns=data["CPCi"].columns, index=data["CPCi"].index)
    for key in data.keys():
        sum_data = sum_data.add(data[key])

    sum_data_array = np.array(sum_data)
    sum_data_array = (sum_data_array - min_mix)/(rescaling_factor - min_mix)

    # pad the sides of the array with zeros so it is square
    width = sum_data_array.shape[0]-sum_data_array.shape[1]
    sum_data_array = (np.pad(
        sum_data_array, ((0, 0), (int(width/2), int(width/2))), pad_with, padder=0))

    nrows = sum_data_array.shape[0]
    ncols = sum_data_array.shape[1]
    sum_data_array.max()

    np.savetxt(os.path.join(in_dir, folder_name,
               f"{model_name}_{simulation_name}_{timepoint}_{nrows}x{ncols}.csv"), sum_data_array, delimiter=",")

    arr_2fold = prolong(sum_data_array, nrows, ncols)
    np.savetxt(os.path.join(in_dir, folder_name,
               f"{model_name}_{simulation_name}_{timepoint}_{arr_2fold.shape[0]}x{arr_2fold.shape[1]}.csv"), arr_2fold, delimiter=",")

    arr_4fold = prolong(arr_2fold, arr_2fold.shape[0], arr_2fold.shape[1])
    np.savetxt(os.path.join(in_dir, folder_name,
               f"{model_name}_{simulation_name}_{timepoint}_{arr_4fold.shape[0]}x{arr_4fold.shape[1]}.csv"), arr_4fold, delimiter=",")


def rescale_vcell_output_neg1_pos1(folder_names, in_dir, outdir, model_name="", simulation_name="", timepoint=200,
                                   timestep=10, min_mix=2, rescaling_factor=5, suffix="", species_name="CPC"):

    data = {}
    if timepoint == 0:
        timeslice_id = "0000"
    elif (timepoint < 100) and (timestep == 10):
        timeslice_id = "000" + str(int(timepoint/timestep))
    elif (timepoint < 100) and (timestep == 1):
        timeslice_id = "00" + str(int(timepoint/timestep))
    else:
        timeslice_id = "00" + str(int(timepoint/timestep))

    if len(folder_names) > 1:
        print(folder_names)
        for folder_name in folder_names:
            for file in os.listdir(os.path.join(in_dir, folder_name)):
                if species_name in file:
                    if timeslice_id in file:
                        name = file.split(
                            "0_")[-1].split(f"_{timeslice_id}.csv")[0]
                        print(name)
                        data[f"{name}_{folder_name}"] = pd.read_csv(os.path.join(in_dir, folder_name, file), sep=",",
                                                                    skiprows=10, header=None)

    else:
        folder_name = folder_names[0]

        print(simulation_name)
        # name = "CPC_all"
        # CPC_species = ["CPCi",'CPCa','pH2A_Sgo1_CPCa', 'pH2A_Sgo1_CPCi', 'pH2A_Sgo1_pH3_CPCa', 'pH2A_Sgo1_pH3_CPCi','pH3_CPCa', 'pH3_CPCi']
        for file in os.listdir(os.path.join(in_dir, folder_name)):

            if species_name in file:
                if timeslice_id in file:

                    name = file.split(
                        "0_")[-1].split(f"_{timeslice_id}.csv")[0]
                    data[name] = pd.read_csv(os.path.join(in_dir, folder_name, file), sep=",",
                                             skiprows=10, header=None)
    name = data.keys().__iter__().__next__()
    sum_data = pd.DataFrame(
        0, columns=data[name].columns, index=data[name].index)
    for key in data.keys():
        sum_data = sum_data.add(data[key])
    # drop any columns that are all na
    sum_data = sum_data.dropna(axis=1, how='all')
    sum_data_array = np.array(sum_data)
    sum_data_array = sum_data_array/len(folder_names)

    # sum_data_array = sum_data_array/rescaling_factor
    print(sum_data_array.max())
    print(sum_data_array.min())
    orig_max = sum_data_array.max()
    orig_min = sum_data_array.min()

    sum_data_array = (sum_data_array - min_mix) / \
        (rescaling_factor - min_mix)
    print(sum_data_array.max())
    print(sum_data_array.min())

    for r_idx, row in enumerate(sum_data_array):
        for c_idx, value in enumerate(row):
            if value == (- min_mix)/(rescaling_factor - min_mix):
                sum_data_array[r_idx][c_idx] = 0

    print(sum_data_array.max())
    print(sum_data_array.min())

    # pad the sides of the array with zeros so it is square
    width = sum_data_array.shape[0]-sum_data_array.shape[1]
    sum_data_array = (np.pad(
        sum_data_array, ((0, 0), (int(width/2), int(width/2))), pad_with, padder=0))

    nrows = sum_data_array.shape[0]
    ncols = sum_data_array.shape[1]
    sum_data_array = (2*sum_data_array) - 1
    print(sum_data_array.max())
    print(sum_data_array.min())

    np.savetxt(os.path.join(
        outdir, f"{species_name}_{simulation_name}_{timepoint}_{nrows}x{ncols}_{suffix}.csv"), sum_data_array, delimiter=",")

    # arr_2fold = prolong(sum_data_array, nrows, ncols)
    # print(arr_2fold.shape)
    # np.savetxt(os.path.join(
    #     outdir, f"{model_name}_{simulation_name}_{timepoint}_{arr_2fold.shape[0]}x{arr_2fold.shape[1]}_{suffix}.csv"), arr_2fold, delimiter=",")

    # #
    # arr_2fold = prolong(sum_data_array, nrows, ncols)
    # np.savetxt(os.path.join(outdir,folder_name,f"{model_name}_{simulation_name}_{timepoint}_{arr_2fold.shape[0]}x{arr_2fold.shape[1]}{suffix}.csv"), arr_2fold, delimiter=",")
    #
    # arr_4fold = prolong(arr_2fold, arr_2fold.shape[0], arr_2fold.shape[1])
    # np.savetxt(os.path.join(outdir,folder_name,f"{model_name}_{simulation_name}_{timepoint}_{arr_4fold.shape[0]}x{arr_4fold.shape[1]}{suffix}.csv"), arr_4fold, delimiter=",")
    return orig_max, orig_min
# rescale_vcell_output_neg1_pos1(folder_name, in_dir, outdir, model_name = model_name, simulation_name = simulation_name, timepoint = 100,
    #  timestep = 10, rescaling_factor = 10, suffix = "100s_10max_")


# in_dir = "/Users/smgroves/Documents/GitHub/VCell_Analysis/vcell_out/10_30_25_CPC_metacentric_transition_model"
# folder_name = "SimID_298553153_0__exported"
# model_name = "10_30_25 CPC_metacentric_transition_model"
# simulation_name = "11_06_2025_transition_model_2ummin_KTmovement_NDC80avail_0.1_fixed_delT_18s"
# outdir = "/Users/smgroves/Documents/GitHub/VCell_Analysis/4_vcell_to_ch/IC"
# rescale_vcell_output_neg1_pos1(folder_name, in_dir, outdir, model_name=model_name, simulation_name=simulation_name, timepoint=18,
#                                timestep=1, min_mix=2, rescaling_factor=20, suffix="_20max")

# in_dir = "/Users/smgroves/Documents/GitHub/VCell_Analysis/vcell_out/09_16_25_CPC_metacentric_tensed_model_v2"
# folder_name = "SimID_296945950_0__exported"
# model_name = "09_16_25_CPC_metacentric_tensed_model_v2"
# simulation_name = "09_16_25_metacentric_tensed_model"
# outdir = "/Users/smgroves/Documents/GitHub/VCell_Analysis/4_vcell_to_ch/IC"
# rescale_vcell_output_neg1_pos1(folder_name, in_dir, outdir, model_name=model_name, simulation_name=simulation_name, timepoint=120,
#                                timestep=10, min_mix=2, rescaling_factor=20, suffix="_20max")

# in_dir = "/Users/smgroves/Documents/GitHub/VCell_Analysis/vcell_out/_09_16_25_CPC_metacentric_relaxed_model"
# folder_name = "SimID_296945372_0__exported"
# model_name = "_09_16_25_CPC_metacentric_relaxed_model"
# simulation_name = "09_16_25_metacentric_relaxed_model"
# outdir = "/Users/smgroves/Documents/GitHub/VCell_Analysis/4_vcell_to_ch/IC"
# rescale_vcell_output_neg1_pos1(folder_name, in_dir, outdir, model_name=model_name, simulation_name=simulation_name, timepoint=120,
#                                timestep=10, min_mix=2, rescaling_factor=20, suffix="_20max")


# in_dir = '/Users/smgroves/Box/CPC_Model_Project/VCell_Exports/'
# folder_name = "SimID_298848254_0__exported"
# model_name = "11_07_25 CPC_metacentric_relaxed_MCF10A"
# simulation_name = "11_07_25_metacentric_relaxed_MCF10A"
# outdir = "/Users/smgroves/Documents/GitHub/VCell_Analysis/4_vcell_to_ch/IC/11_07_2025"
# rescale_vcell_output_neg1_pos1(folder_name, in_dir, outdir, model_name=model_name, simulation_name=simulation_name, timepoint=18,
#                                timestep=1, min_mix=1.5, rescaling_factor=8.4, suffix="_8.4max_1.5min")

# folder_name = "SimID_298847711_0__exported"
# model_name = "11_07_25 CPC_metacentric_tensed_model"
# simulation_name = "11_07_25_metacentric_tensed_MCF10A"
# rescale_vcell_output_neg1_pos1(folder_name, in_dir, outdir, model_name=model_name, simulation_name=simulation_name, timepoint=18,
#                                timestep=1, min_mix=1.5, rescaling_factor=8.4, suffix="_8.4max_1.5min")

# in_dir = '/Users/smgroves/Box/CPC_Model_Project/VCell_Exports/'

# min_mix = 0.5
# folder_names = ["SimID_299575713_1__exported", "SimID_299575713_3__exported"]
# model_name = "11_23_25 CPC_metacentric_relaxed_MCF10A"
# simulation_name = "11_24_25_metacentric_relaxed_MCF10A_condensation"
# rescale_vcell_output_neg1_pos1(folder_names, in_dir, outdir, model_name=model_name, simulation_name=simulation_name, timepoint=100,
#                                timestep=10, min_mix=min_mix, rescaling_factor=8.4, suffix=f"_8.4max_{min_mix}min", species_name="CPC_all")

# min_mix = 5
# rescaling_factor = 20
# folder_names = ["SimID_299707888_0__exported"]
# model_name = "11_23_25 CPC_metacentric_relaxed_MCF10A"
# simulation_name = "11_26_25_metacentric_relaxed_MCF10A_chr9-11_metaphase"
# rescale_vcell_output_neg1_pos1(folder_names, in_dir, outdir, model_name=model_name, simulation_name=simulation_name, timepoint=100,
#                                timestep=10, min_mix=min_mix, rescaling_factor=rescaling_factor, suffix=f"_{rescaling_factor}max_{min_mix}min", species_name="CPC_all")

# folder_names = ["SimID_299710798_0__exported"]
# model_name = "11_23_25 CPC_metacentric_tensed_MCF10A"
# simulation_name = "11_26_25 CPC_metacentric_tensed_MCF10A_chr9-11_metaphase"
# rescale_vcell_output_neg1_pos1(folder_names, in_dir, outdir, model_name=model_name, simulation_name=simulation_name, timepoint=100,
#                                timestep=10, min_mix=min_mix, rescaling_factor=rescaling_factor, suffix=f"_{rescaling_factor}max_{min_mix}min", species_name="CPC_all")

# in_dir = '/Users/smgroves/Documents/Github/VCell_Analysis/vcell_out'
# in_dir = '/Users/smgroves/Box/CPC_Model_Project/VCell_Exports/'
in_dir = '/Users/smgroves/Library/CloudStorage/Box-Box/CPC_Model_Project/VCell_Exports/'
outdir = "/Users/smgroves/Documents/GitHub/VCell_Analysis/5_vcell_to_ch/IC/01_16_2026"

# # min_max_dict = {}

# min_mix = 4.7
# rescaling_factor = 16.1
# folder_names = ["SimID_302779581_0__exported"]
# model_name = "01_14_26 CPC_metacentric_tensed_MCF10A_chr19_PMP1_CPCactive_newKcat"
# simulation_name = "01_14_26_metacentric_tensed_MCF10A_chr19_PMP1_active_kpp_CPCaIC"
# ma, mi = rescale_vcell_output_neg1_pos1(folder_names, in_dir, outdir, model_name=model_name, simulation_name=simulation_name, timepoint=100,
#                                         timestep=10, min_mix=min_mix, rescaling_factor=rescaling_factor, suffix=f"_{rescaling_factor}max_{min_mix}min", species_name="CPC_all")

# min_max_dict[simulation_name] = (ma, mi)

min_mixes = [4.25, 4.5, 4.75, 5.0]
rescaling_factors = [10,12,14,16]
folder_names = ["SimID_299716561_0__exported"]
# folder_names = ["SimID_302549931_0__exported"]
# folder_names = ['SimID_302551116_0__exported']
model_name = "11_23_25 CPC_metacentric_relaxed_MCF10A"
simulation_name = "11_26_25_metacentric_relaxed_MCF10A_chr19_PMP1"
# model_name = '01_14_26_CPC_metacentric_relaxed_MCF10A_chr19_PMP1_CPCactive_newKcat'
# simulation_name = "01_14_26_metacentric_relaxed_MCF10A_chr19_PMP1_active_CPCaIC"
for min_mix in min_mixes:
    for rescaling_factor in rescaling_factors:
        ma, mi = rescale_vcell_output_neg1_pos1(folder_names, in_dir, outdir, model_name=model_name, simulation_name=simulation_name, timepoint=100,
                                            timestep=10, min_mix=min_mix, rescaling_factor=rescaling_factor, suffix=f"_{rescaling_factor}max_{min_mix}min", species_name="CPC_all")
    print(f"min_mix: {min_mix}, rescaling_factor: {rescaling_factor}, max: {ma}, min: {mi}")
# ma, mi = rescale_vcell_output_neg1_pos1(folder_names, in_dir, outdir, model_name=model_name, simulation_name=simulation_name, timepoint=100,
                                        # timestep=10, min_mix=min_mix, rescaling_factor=rescaling_factor, suffix=f"_{rescaling_factor}max_{min_mix}min", species_name="CPC_all")

# min_max_dict[simulation_name] = (ma, mi)

# min_mix = 5.7
# rescaling_factor = 16
# folder_names = ["SimID_299731280_0__exported"]
# model_name = "11_26_25_metacentric_tensed_MCF10A_chr19_PMP2"
# simulation_name = "11_26_25_metacentric_tensed_MCF10A_chr19_PMP2"
# ma, mi = rescale_vcell_output_neg1_pos1(folder_names, in_dir, outdir, model_name=model_name, simulation_name=simulation_name, timepoint=50,
#                                         timestep=10, min_mix=min_mix, rescaling_factor=rescaling_factor, suffix=f"_{rescaling_factor}max_{min_mix}min", species_name="CPC_all")

# min_max_dict[simulation_name] = (ma, mi)

# min_mix = 5.1
# rescaling_factor = 15
# folder_names = ["SimID_299730628_0__exported"]
# model_name = "11_26_25_metacentric_relaxed_MCF10A_chr19_PMP2"
# simulation_name = "11_26_25_metacentric_relaxed_MCF10A_chr19_PMP2"
# ma, mi = rescale_vcell_output_neg1_pos1(folder_names, in_dir, outdir, model_name=model_name, simulation_name=simulation_name, timepoint=50,
#                                         timestep=10, min_mix=min_mix, rescaling_factor=rescaling_factor, suffix=f"_{rescaling_factor}max_{min_mix}min", species_name="CPC_all")

# min_max_dict[simulation_name] = (ma, mi)

# min_mix = 6.4
# rescaling_factor = 15.9
# folder_names = ["SimID_299732742_0__exported"]
# model_name = "11_26_25_metacentric_tensed_MCF10A_chr19_PMP3"
# simulation_name = "11_26_25_metacentric_tensed_MCF10A_chr19_PMP3"
# ma, mi = rescale_vcell_output_neg1_pos1(folder_names, in_dir, outdir, model_name=model_name, simulation_name=simulation_name, timepoint=50,
#                                         timestep=10, min_mix=min_mix, rescaling_factor=rescaling_factor, suffix=f"_{rescaling_factor}max_{min_mix}min", species_name="CPC_all")

# min_max_dict[simulation_name] = (ma, mi)

# min_mix = 5.9
# rescaling_factor = 15
# folder_names = ["SimID_299732060_0__exported"]
# model_name = "11_26_25_metacentric_relaxed_MCF10A_chr19_PMP3"
# simulation_name = "11_26_25_metacentric_relaxed_MCF10A_chr19_PMP3"
# ma, mi = rescale_vcell_output_neg1_pos1(folder_names, in_dir, outdir, model_name=model_name, simulation_name=simulation_name, timepoint=50,
#                                         timestep=10, min_mix=min_mix, rescaling_factor=rescaling_factor, suffix=f"_{rescaling_factor}max_{min_mix}min", species_name="CPC_all")

# min_max_dict[simulation_name] = (ma, mi)

# min_mix = 7.1
# rescaling_factor = 15
# folder_names = ["SimID_299733521_0__exported"]
# model_name = "11_26_25_metacentric_relaxed_MCF10A_chr19_PMP4"
# simulation_name = "11_26_25_metacentric_relaxed_MCF10A_chr19_PMP4"
# ma, mi = rescale_vcell_output_neg1_pos1(folder_names, in_dir, outdir, model_name=model_name, simulation_name=simulation_name, timepoint=50,
#                                         timestep=10, min_mix=min_mix, rescaling_factor=rescaling_factor, suffix=f"_{rescaling_factor}max_{min_mix}min", species_name="CPC_all")

# min_max_dict[simulation_name] = (ma, mi)

min_mix = 7.6
rescaling_factor = 15.8
# folder_names = ["SimID_299734152_0__exported"]
# model_name = "11_26_25_metacentric_tensed_MCF10A_chr19_PMP4"
# simulation_name = "11_26_25_metacentric_tensed_MCF10A_chr19_PMP4"
# ma, mi = rescale_vcell_output_neg1_pos1(folder_names, in_dir, outdir, model_name=model_name, simulation_name=simulation_name, timepoint=50,
#                                         timestep=10, min_mix=min_mix, rescaling_factor=rescaling_factor, suffix=f"_{rescaling_factor}max_{min_mix}min", species_name="CPC_all")

# min_max_dict[simulation_name] = (ma, mi)

# spinodal_point = ((3-np.sqrt(3))/6)*(rescaling_factor-min_mix)+min_mix
# # plot max and min for each on a double well distribution where the two wells are min_mix and rescaling factor
# # any sim with relaxed in the name should be shades of orange, and tensed should be shades of blue labeled by last 4 characters of sim name and relaxed or tensed
# fig, ax = plt.subplots()
# for sim_name in sorted(min_max_dict.keys()):
#     ma, mi = min_max_dict[sim_name]
#     if "relaxed" in sim_name:
#         ax.scatter(ma, mi, color='orange', label=f"{sim_name[-4:]} relaxed")
#     else:
#         ax.scatter(ma, mi, color='blue', label=f"{sim_name[-4:]} tensed")
# ax.set_xlabel("Max CPC concentration (orig units)")
# ax.set_ylabel("Min CPC concentration (orig units)")
# ax.set_title("Max and Min CPC concentrations across simulations")
# ax.axvline(x=spinodal_point, color='gray', linestyle='--',
#            label=f"Spinodal Point for max {rescaling_factor} and min {min_mix}")
# # ax.axhline(y=min_mix, color='gray', linestyle='--')
# ax.legend()
# plt.show()

# post transition sims
# min_mix = 7.6
# rescaling_factor = 15.8

# folder_names = ["SimID_299928075_0__exported"]
# model_name = "11_26_25 CPC_metacentric_transition_MCF10A_chr19_PMP4"
# simulation_name = "11_26_25_metacentric_transition_MCF10A_chr9_PMP4_transition_200s"
# ma, mi = rescale_vcell_output_neg1_pos1(folder_names, in_dir, outdir, model_name=model_name, simulation_name=simulation_name, timepoint=12,
#                                         timestep=1, min_mix=min_mix, rescaling_factor=rescaling_factor, suffix=f"_{rescaling_factor}max_{min_mix}min", species_name="CPC_all")
# folder_names = ["SimID_299928086_0__exported"]
# model_name = "11_26_25 CPC_metacentric_transition_MCF10A_chr19_PMP4"
# simulation_name = "11_26_25_metacentric_transition_MCF10A_chr9_PMP4_transition_100s"
# ma, mi = rescale_vcell_output_neg1_pos1(folder_names, in_dir, outdir, model_name=model_name, simulation_name=simulation_name, timepoint=12,
#                                         timestep=1, min_mix=min_mix, rescaling_factor=rescaling_factor, suffix=f"_{rescaling_factor}max_{min_mix}min", species_name="CPC_all")

# min_mix = 7.6
# rescaling_factor = 15.8
# folder_names = ["SimID_299928089_0__exported"]
# model_name = "11_26_25 CPC_metacentric_transition_MCF10A_chr19_PMP4"
# simulation_name = "11_26_25_metacentric_transition_MCF10A_chr9_PMP4_transition_50s"
# ma, mi = rescale_vcell_output_neg1_pos1(folder_names, in_dir, outdir, model_name=model_name, simulation_name=simulation_name, timepoint=17,
#                                         timestep=1, min_mix=min_mix, rescaling_factor=rescaling_factor, suffix=f"_{rescaling_factor}max_{min_mix}min", species_name="CPC_all")

# folder_names = ["SimID_300632276_0__exported"]
# model_name = "12_11_25_CPC_metacentric_transition_MCF10A_chr19_PMP3"
# simulation_name = "11_26_25_metacentric_transition_MCF10A_chr9_PMP3_transition_200s"
# ma, mi = rescale_vcell_output_neg1_pos1(folder_names, in_dir, outdir, model_name=model_name, simulation_name=simulation_name, timepoint=17,
#                                         timestep=1, min_mix=min_mix, rescaling_factor=rescaling_factor, suffix=f"_{rescaling_factor}max_{min_mix}min", species_name="CPC_all")


# folder_names = ["SimID_300540363_2__exported"]
# model_name = "11_26_25_metacentric_relaxed_MCF10A_chr19_PMP1"
# simulation_name = "11_26_25_metacentric_relaxed_MCF10A_chr19_PMP1_haspin_stripe_0.25"
# ma, mi = rescale_vcell_output_neg1_pos1(folder_names, in_dir, outdir, model_name=model_name, simulation_name=simulation_name, timepoint=200,
#                                         timestep=10, min_mix=min_mix, rescaling_factor=rescaling_factor, suffix=f"_{rescaling_factor}max_{min_mix}min", species_name="CPC_all")
# folder_names = ["SimID_300540363_3__exported"]
# model_name = "11_26_25_metacentric_relaxed_MCF10A_chr19_PMP1"
# simulation_name = "11_26_25_metacentric_relaxed_MCF10A_chr19_PMP1_haspin_stripe_0.3"
# ma, mi = rescale_vcell_output_neg1_pos1(folder_names, in_dir, outdir, model_name=model_name, simulation_name=simulation_name, timepoint=200,
#                                         timestep=10, min_mix=min_mix, rescaling_factor=rescaling_factor, suffix=f"_{rescaling_factor}max_{min_mix}min", species_name="CPC_all")

# folder_names = ["SimID_300632276_0__exported"]
# model_name = "12_11_25_CPC_metacentric_transition_MCF10A_chr19_PMP3"
# simulation_name = "11_26_25_metacentric_transition_MCF10A_chr9_PMP3"
# ma, mi = rescale_vcell_output_neg1_pos1(folder_names, in_dir, outdir, model_name=model_name, simulation_name=simulation_name, timepoint=17,
#                                         timestep=1, min_mix=min_mix, rescaling_factor=rescaling_factor, suffix=f"_{rescaling_factor}max_{min_mix}min", species_name="CPC_all")
