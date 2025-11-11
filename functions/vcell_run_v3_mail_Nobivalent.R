#########################################################
# Install all needed packages
packages <- c("ggplot2","gridExtra","purrr","latex2exp","stringr","lemon","utils","tictoc","tidyverse","tibble","scales", "xlsx", "pdftools", "rhdf5", "png")
lapply(packages, require, character.only = TRUE)
tic("total")


# CHANGE
funcPath<-"/Users/catalinaalvarez/Documents/GitHub/VCell_Analysis/functions"
importPath<-"/Users/catalinaalvarez/Documents/CPC_data_2025"
exportPath<-"/Users/catalinaalvarez/Documents/CPC_plots_2025"
desktop<-"/Users/catalinaalvarez/Desktop"


# Functions
functions<-list.files(funcPath,recursive=TRUE)
functions<-file.path(funcPath,functions)
for(i in functions){
  print(i)
  source(i)
}

# # #For metaphase chromosomes
dataDim=c(128,64)#edited
chromWidth=1.6 #um
chromHeight=3.2 #um

# #For prometaphase chromosomes
# dataDim=c(208,64)#edited
# chromWidth=1.6 #um
# chromHeight=5.2 #um

# ---------------- LISTS OF SPECIES ---------------

# Species Lists, add any that are required to be on one plot

CPC_species <-c("CPCa", "pH2A_Sgo1_CPCa", "H3_CPCa", "pH3_CPCa", "Sgo1_CPCa", "CPCi", "pH2A_Sgo1_CPCi", "H3_CPCi", "pH3_CPCi", "Sgo1_CPCi")
Mps1_species <-c("Mps1a", "pMps1a", "Ndc80_Mps1a", "Ndc80_pMps1a", "pNdc80_Mps1a", "pNdc80_pMps1a", "Mps1i", "pMps1i", "Ndc80_Mps1i", "Ndc80_pMps1i", "pNdc80_Mps1i", "pNdc80_pMps1i")
Todd_species <-c("Plk1a", "Plk1i", "Haspina", "Haspini", "pH3", "pH3_CPCa", "pH3_CPCi", "pH2A_Sgo1_CPCi", "pH2A_Sgo1_CPCa")
H3_CPC_species  <- c("H3_CPCa", "H3_CPCi")
H2_species <- c("H2A")
pH3_species <- c("pH3", "pH3_CPCa", "pH3_CPCi")
pH2A_species <- c("pH2A", "pH2A_Sgo1", "pH2A_Sgo1_CPCa", "pH2A_Sgo1_CPCi")
Haspin_Plk1_species <- c("Haspina", "Haspini", "Plk1a", "Plk1i")
only_H3_H2A_species <- c("H3", "H2A")
Bub1a <- c("Bub1a")
pKnl1_Bub1a <- c("pKnl1_Bub1a")
Bub1a_pKnl1_species <- c("Bub1a", "pKnl1", "pKnl1_Bub1a", "Bub1a_his") #, "Bub1a_his"
Haspin_P_species <- c("Haspina", "Haspini", "Plk1a")
Sgo1_species <- c("Sgo1", "pH2A_Sgo1", "pH2A_Sgo1_CPCi", "pH2A_Sgo1_CPCa", "Sgo1_CPCi", "Sgo1_CPCa")
CPC <- c("CPCi", "CPCa")
pH2A <- c("pH2A")
CPC_all <- c("CPC_all")
# boundCPC <- c("boundCPC")
# unboundCPC <- c("unboundCPC")

# ---------------- HEAT MAPS ---------------

# How many heat maps to return
# Change
H <- 4

heatmap_species <- vector("list", H)
heatmap_info_list <- vector("list", H)

# Change, IN ORDER
heatmap_species[[1]] <- CPC_species
heatmap_species[[2]] <- pH2A_species
heatmap_species[[3]] <- pH3_species
heatmap_species[[4]] <- Sgo1_species
# heatmap_species[[5]] <- H3_CPC_species
# heatmap_species[[6]] <- H2_species

# Change, name of plot in plot directory, also name in heatmap, IN ORDER
heatmap_info_list[[1]] <- c("all CPC")
heatmap_info_list[[2]] <- c("all pH2A")
heatmap_info_list[[3]] <- c("all pH3")
heatmap_info_list[[4]] <- c("all Sgo1")
# heatmap_info_list[[5]] <- c("all H3_CPC")
# heatmap_info_list[[6]] <- c("all H2A")


# ---------------- LINE PLOTS ---------------
L <- 9
 
all_data <- vector("list", L)
species_info_list <- vector("list", L)
 
# Change, IN ORDER
#all_species <- c(CPC_species)
#all_species <- c(Mps1_species)
#all_species <- c(Haspin_Plk1_species)
#all_species <- c(pH3_species)
#all_species <- c(pH2A_species)
#all_species <- c(only_H3_H2A_species)
#all_species <- c(Sgo1_species)
all_species <- c(CPC_species, Mps1_species, Haspin_Plk1_species, pH3_species, pH2A_species, only_H3_H2A_species,Bub1a_pKnl1_species, Sgo1_species, CPC_all)
#all_species <- c(CPC_all)

# Change, IN ORDER
all_data[[1]] <- CPC_species
all_data[[2]] <- Mps1_species
all_data[[3]] <- Haspin_Plk1_species
all_data[[4]] <- pH3_species
all_data[[5]] <- pH2A_species
all_data[[6]] <- only_H3_H2A_species
all_data[[7]] <- Bub1a_pKnl1_species
all_data[[8]] <- Sgo1_species
all_data[[9]] <- CPC_all
# all_data[[2]] <- boundCPC
# all_data[[3]] <- unboundCPC
 
# Change, IN ORDER
species_info_list[[1]] <- c("CPC", "Inactive CPC", "Active CPC", "CPC Activation", TRUE, FALSE, FALSE, TRUE)
species_info_list[[2]] <- c("Mps1", "Inactive Mps1", "Active Mps1", "Mps1 Activation", TRUE, FALSE, FALSE, TRUE)
species_info_list[[3]] <- c("Haspin_Plk1_species", "Inactive Species", "Active Species", "All Species", FALSE, FALSE, TRUE, FALSE)
species_info_list[[4]] <- c("pH3_species", "Inactive pH3 Species", "Active pH3 Species", "All pH3 Species", FALSE, TRUE, TRUE, FALSE)
species_info_list[[5]] <- c("pH2A_species", "Inactive pH2A Species", "Active pH2A Species", "All pH2A Species", FALSE, TRUE, TRUE, FALSE)
species_info_list[[6]] <- c("H2A & H3", "Inactive H2A & H3", "Active H2A & H3", "H2A & H3", FALSE, FALSE, TRUE, FALSE)
species_info_list[[7]] <- c("Bub1a_pKnl1_spaecies", "Inactive Species", "Active Species", "All Species", FALSE, FALSE, TRUE, FALSE)
species_info_list[[8]] <- c("Sgo1", "Inactive Sgo1", "Active Sgo1", "All Sgo1", FALSE, FALSE, TRUE, FALSE)
species_info_list[[9]] <- c("CPC_all", "Inactive CPC_all", "Active CPC_all", "All CPC_all", FALSE, FALSE, TRUE, FALSE)
# species_info_list[[2]] <- c("bound", "Inactive bound", "Active bound", "All bound", FALSE, FALSE, TRUE, FALSE)
# species_info_list[[3]] <- c("unbound", "Inactive unbound", "Active unbound", "All unbound", FALSE, FALSE, TRUE, FALSE)

# ---------------- SIMULATION SPECIFICS ---------------

# Model type, goes on the left of the heatmap
# Change
kt_width = c(
  # "Metacentric_Relaxed",
  # "Metacentric_Tensed",
  # "Telocentric_Relaxed"
  # "Telocentric_Tensed"
  "Metacentric_Relaxed",
  "Metacentric_Relaxed",
  "Metacentric_Relaxed",
  "Metacentric_Relaxed",
  "Metacentric_Relaxed",
  "Metacentric_Relaxed",
  "Metacentric_Relaxed",
  "Metacentric_Relaxed",
  "Metacentric_Relaxed",
  "Metacentric_Relaxed",
  "Metacentric_Relaxed",
  "Metacentric_Relaxed"
  # "Prometaphase_Relaxed",
  # "Prometaphase_Relaxed",
  # "Prometaphase_Relaxed",
  # "Prometaphase_Relaxed",
  # "Prometaphase_Relaxed",
  # "Prometaphase_Relaxed",
  # "Prometaphase_Relaxed",
  # "Prometaphase_Relaxed",
  # "Prometaphase_Relaxed"
)

# All simulation IDs
# Change
sims <- c(
  "SimID_298738806_0__exported",
  "SimID_298815735_0__exported",
  "SimID_298815738_0__exported",
  "SimID_298815741_0__exported",
  "SimID_298815744_0__exported",
  "SimID_298815747_0__exported",
  "SimID_298815750_0__exported",
  "SimID_298815753_0__exported",
  "SimID_298815756_0__exported",
  "SimID_298815759_0__exported",
  "SimID_298816645_0__exported",
  "SimID_298816648_0__exported"
)

# Folder naming corresponding to specific simulation ID
# Change
var <- c(
  "11_07_25_metacentric_relaxed_HeLa_Iarms",
  "11_10_25_metacentric_relaxed_HeLa_Iarms_50P_CPC",
  "11_10_25_metacentric_relaxed_HeLa_Iarms_50P_Sgo1",
  "11_10_25_metacentric_relaxed_HeLa_Iarms_50P_Plk1",
  "11_10_25_metacentric_relaxed_HeLa_Iarms_50P_Haspin",
  "11_10_25_metacentric_relaxed_HeLa_Iarms_50P_Mps1",
  "11_10_25_metacentric_relaxed_HeLa_Iarms_50P_CPC_Sgo1",
  "11_10_25_metacentric_relaxed_HeLa_Iarms_50P_Plk1_Sgo1",
  "11_10_25_metacentric_relaxed_HeLa_Iarms_50P_Haspin_Sgo1",
  "11_10_25_metacentric_relaxed_HeLa_Iarms_50P_Mps1_Sgo1",
  "11_10_25_metacentric_relaxed_HeLa_Iarms_50P_Bub1",
  "11_10_25_metacentric_relaxed_HeLa_Iarms_50P_Bub1_Sgo1"
)
#########################################################


for(i in 1:length(sims)){
  if(file.exists(importPath) == TRUE){
    
    
    sweep_name<-var[i]
    
    print(sweep_name)
    

    dir.create(file.path(exportPath, sweep_name))
    exportPath_new <- paste(exportPath, sweep_name, sep="/")

    
    save_plots(sims[i],
               paste(kt_width[i], "Model"),
               heatmap_species,
               heatmap_info_list,
               all_data,
               all_species,
               species_info_list,
               tInit=0,
               tSpan=500, #400 for relaxed to tensed
               desiredInterval=100,
               cutoff=5, #for heatmap color bar
               funcPath,
               importPath,
               exportPath_new,
               kt_width[i])

  }
}

