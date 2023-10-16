import pandas as pd
import os

in_dir = "/Users/smgroves/Box/CPC_Model_Project/VCell_Exports/"

folder_name = 'SimID_261581379_0__exported'
model_name = "08_21_23_CPC_relaxed_RefModel_Mps1_phos_Plk1a transactiv_sarah"
simulation_name = "08_21_23_relaxed_RefModel_Mps1_phos_Plk1a_20Pac transactiv_KmMps1_5.4"
timepoint = 400

data = {}
timestep = 10
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

print(sum_data.max().max())