# Copied from vcell_run_v3_mail.R by Sarah Groves on Nov 27 2023
# To be used with arguments on the command line (or in full run bash script with Python hdf5 converter)

# old version would take in SimID and names
#input = importPath/SimID_NNNNN_X__exported/SimID_NNNNN_X__Slice_XY_0_species_time.csv
# new CLI version: DATA = ${OUTPUT}/${SIM_NAME}/data
# new input: DATA/SimID_0_Slice_XY_0_species_time.csv for each simulation name

#CHANGES NEEDED: 
#########################################################
# Install all needed packages
# install.packages('argparser', repos = "http://cran.us.r-project.org")
packages <- c("ggplot2","gridExtra","purrr","latex2exp","stringr","lemon","utils","tictoc","tidyverse","tibble","scales", "xlsx", "pdftools", "rhdf5", "rgoogleslides", "googleCloudStorageR", "png", 'argparser')
lapply(packages, require, character.only = TRUE, quietly=TRUE)
tic("total")


# CHANGE Paths for rivanna version
funcPath<-"/Users/smgroves/Documents/Github/VCell_Analysis/functions_CLI"
# importPath<-"/Users/smgroves/Box/CPC_Model_Project/VCell_Exports"
# importPath<- "/Users/smgroves/Documents/GitHub/VCell_Analysis/vcell_out/_06_23_23_model1/base_model_KdpNdc80pMps1___kpp___0_1_scan1/"
# exportPath<-"/Users/smgroves/Documents/GitHub/VCell_Analysis/vcell_out/_06_23_23_model1"
# exportPath<-"/Users/smgroves/Documents/GitHub/VCell_Analysis/vcell_out/_06_23_23_model1/base_model_KdpNdc80pMps1___kpp___0_1_scan1/plots"


# Functions
functions<-list.files(funcPath,recursive=TRUE)
functions<-file.path(funcPath,functions)
for(i in functions){
  # print(i)
  source(i)
}


p <- arg_parser("Plot heatmaps and lineplots for a VCell Simulation")
# p <- add_argument(p, "sim", help="SimID")
p <- add_argument(p, "var", help="Simulation name") #$SIM_NAME
p <- add_argument(p, "importPath", help="Import Path to /data folder") #$DATA
p <- add_argument(p, "exportPath", help="Export Path to Model Level Folder") #$PLOTS

p <- add_argument(p, "--kt_width", help="Tensed or Relaxed", default = "Relaxed")
# p <- add_argument(p, "--dataDim", help="Dimensions of data", default=c(128,64))
p <- add_argument(p, "--tSpan", help="Total time of simulation", default=500)


# Parse the command line arguments
argv <- parse_args(p)

dataDim <- c(128,64)


# ---------------- SIMULATION SPECIFICS ---------------
# Model type, goes on the left of the heatmap
# kt_width <- argv$kt_width
# All simulation IDs
sim <- 0 #argv$sim
# Folder naming corresponding to specific simulation ID
var <-argv$var
importPath <-argv$importPath
exportPath <-argv$exportPath

kt_width<- argv$kt_width #"Relaxed"
# var <- "base_model_KdpNdc80pMps1___kpp___0_1_scan1"

# ---------------- LISTS OF SPECIES ---------------

# Species Lists, add any that are required to be on one plot

CPC_species <-c("CPCa", "pH2A_Sgo1_CPCa", "pH3_CPCa", "pH2A_Sgo1_pH3_CPCa", "CPCi", "pH2A_Sgo1_CPCi", "pH3_CPCi", "pH2A_Sgo1_pH3_CPCi")
Mps1_species <-c("Mps1a", "pMps1a", "Ndc80_Mps1a", "Ndc80_pMps1a", "pNdc80_Mps1a", "pNdc80_pMps1a", "Mps1i", "pMps1i", "Ndc80_Mps1i", "Ndc80_pMps1i", "pNdc80_Mps1i", "pNdc80_pMps1i")
Todd_species <-c("Plk1a", "Plk1i", "Haspina", "Haspini", "pH3", "pH3_CPCa", "pH3_CPCi", "pH2A_Sgo1_CPCi", "pH2A_Sgo1_CPCa")
pH3_species <- c("pH3", "pH3_CPCa", "pH3_CPCi", "pH2A_Sgo1_pH3_CPCa", "pH2A_Sgo1_pH3_CPCi")
pH2A_species <- c("pH2A", "pH2A_Sgo1", "pH2A_Sgo1_CPCa", "pH2A_Sgo1_CPCi", "pH2A_Sgo1_pH3_CPCi", "pH2A_Sgo1_pH3_CPCa")
Haspin_Plk1_species <- c("Haspina", "Haspini", "Plk1a", "Plk1i")
only_H3_H2A_species <- c("H3", "H2A")
Bub1a <- c("Bub1a")
pKnl1_Bub1a <- c("pKnl1_Bub1a")
Bub1a_pKnl1_species <- c("Bub1a", "pKnl1", "pKnl1_Bub1a")
Haspin_P_species <- c("Haspina", "Haspini", "Plk1a")

# ---------------- HEAT MAPS ---------------
# How many heat maps to return
# Change
H <- 3

heatmap_species <- vector("list", H)
heatmap_info_list <- vector("list", H)

# Change, IN ORDER
heatmap_species[[1]] <- CPC_species
heatmap_species[[2]] <- pH2A_species
heatmap_species[[3]] <- pH3_species


# Change, name of plot in plot directory, also name in heatmap, IN ORDER
heatmap_info_list[[1]] <- c("all CPC")
heatmap_info_list[[2]] <- c("all pH2A")
heatmap_info_list[[3]] <- c("all pH3")


# ---------------- LINE PLOTS ---------------
L <- 7

all_data <- vector("list", L)
species_info_list <- vector("list", L)

# Change, IN ORDER
all_species <- c(CPC_species, Mps1_species, Haspin_Plk1_species, pH3_species, pH2A_species, only_H3_H2A_species,Bub1a_pKnl1_species)

# Change, IN ORDER
all_data[[1]] <- CPC_species
all_data[[2]] <- Mps1_species
all_data[[3]] <- Haspin_Plk1_species
all_data[[4]] <- pH3_species
all_data[[5]] <- pH2A_species
all_data[[6]] <- only_H3_H2A_species
all_data[[7]] <- Bub1a_pKnl1_species


# Change, IN ORDER
species_info_list[[1]] <- c("CPC", "Inactive CPC", "Active CPC", "CPC Activation", TRUE, FALSE, FALSE, TRUE)
species_info_list[[2]] <- c("Mps1", "Inactive Mps1", "Active Mps1", "Mps1 Activation", TRUE, FALSE, FALSE, TRUE)
species_info_list[[3]] <- c("Haspin_Plk1_species", "Inactive Species", "Active Species", "All Species", FALSE, FALSE, TRUE, FALSE)
species_info_list[[4]] <- c("pH3_species", "Inactive pH3 Species", "Active pH3 Species", "All pH3 Species", FALSE, TRUE, TRUE, FALSE)
species_info_list[[5]] <- c("pH2A_species", "Inactive pH2A Species", "Active pH2A Species", "All pH2A Species", FALSE, TRUE, TRUE, FALSE)
species_info_list[[6]] <- c("H2A & H3", "Inactive H2A & H3", "Active H2A & H3", "H2A & H3", FALSE, FALSE, TRUE, FALSE)
species_info_list[[7]] <- c("Bub1a_pKnl1_species", "Inactive Species", "Active Species", "All Species", FALSE, FALSE, TRUE, FALSE)

#########################################################
print(importPath)
print(exportPath)
# if(file.exists(importPath) == TRUE){
  
  print(var)
  
  save_plots(sim,
              paste(kt_width, "Model"),
              heatmap_species,
              heatmap_info_list,
              all_data,
              all_species,
              species_info_list,
              tInit=0,
              tSpan=500, #400 for relaxed to tense
              desiredInterval=100,
              cutoff=5, #for heatmap color bar
              funcPath,
              importPath,
              exportPath,
              kt_width
             )

  # vcell_table(sims[i],
              # var[i],
              # tPoints=c(200, 400),
              # all_species=CPC_species,
              # name='CPC',
              # chromWidth=1.6,
              # chromHeight=3.5,
              # dataDim=c(149,68),
              # row_1=1,
              # row_2=dataDim[1],
              # col_1=1,
              # col_2=dataDim[2],
              # importPath,
              # exportPath_new)
              # 
  
# }

