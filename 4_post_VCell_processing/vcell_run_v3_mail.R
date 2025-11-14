#########################################################
# Install all needed packages
options(repos = c(CRAN = "https://cloud.r-project.org"))
# install.packages(c("gifski","transformr"))
if (!requireNamespace("ggrastr", quietly = TRUE)) install.packages("ggrastr")
packages <- c("ggplot2","ggrastr","gganimate","gifski","av","transformr","png","gridExtra","purrr","latex2exp","stringr","lemon","utils","tictoc","tidyverse","tibble","scales", "xlsx", "pdftools", "png")
installed <- rownames(installed.packages())
for (pkg in packages) {
  if (!(pkg %in% installed)) {
    install.packages(pkg)
  }
}
lapply(packages, require, character.only = TRUE)

tic("total")


# CHANGE
funcPath<-"/Users/smgroves/Documents/Github/VCell_Analysis/functions"
importPath<-"/Users/smgroves/Box/CPC_Model_Project/VCell_Exports"
exportPath<-"/Users/smgroves/Box/CPC_Model_Project/vcell_plots"
# # #For metaphase chromosomes
dataDim=c(128,64)#edited
chromWidth=1.6 #um
chromHeight=3.2 #um

# Functions
functions<-list.files(funcPath,recursive=TRUE)
functions<-file.path(funcPath,functions)
for(i in functions){
  print(i)
  source(i)
}

dataDim=c(128,64) #edited

# ---------------- LISTS OF SPECIES ---------------

# Species Lists, add any that are required to be on one plot

CPC_species <-c("CPCa", "pH2A_Sgo1_CPCa", "pH3_CPCa", "CPCi", "pH2A_Sgo1_CPCi", "pH3_CPCi","H3_CPCi",'H3_CPCa')
Mps1_species <-c("Mps1a", "pMps1a", "Ndc80_Mps1a", "Ndc80_pMps1a", "pNdc80_Mps1a", "pNdc80_pMps1a", "Mps1i", "pMps1i", "Ndc80_Mps1i", "Ndc80_pMps1i", "pNdc80_Mps1i", "pNdc80_pMps1i")
Todd_species <-c("Plk1a", "Plk1i", "Haspina", "Haspini", "pH3", "pH3_CPCa", "pH3_CPCi", "pH2A_Sgo1_CPCi", "pH2A_Sgo1_CPCa")
pH3_species <- c("pH3", "pH3_CPCa", "pH3_CPCi")
pH2A_species <- c("pH2A", "pH2A_Sgo1", "pH2A_Sgo1_CPCa", "pH2A_Sgo1_CPCi")
Haspin_Plk1_species <- c("Haspina", "Haspini", "Plk1a", "Plk1i")
only_H3_H2A_species <- c("H3", "H2A")
Bub1a <- c("Bub1a")
pKnl1_Bub1a <- c("pKnl1_Bub1a")
Bub1a_pKnl1_species <- c("Bub1a", "pKnl1", "pKnl1_Bub1a")
Haspin_P_species <- c("Haspina", "Haspini", "Plk1a")
CPC_active_species <-c("pH2A_Sgo1_CPCa", "pH3_CPCa","CPCa",'H3_CPCa')
CPC_inactive_species <-c("CPCi", "pH2A_Sgo1_CPCi", "pH3_CPCi","H3_CPCi")
CPC_pH2A_species <-c( "pH2A_Sgo1_CPCa", "pH2A_Sgo1_CPCi")
CPC_pH3_species <-c( "pH3_CPCa", "pH3_CPCi","H3_CPCa","H3_CPCi")
Ndc80_species <-c("Ndc80", "pNdc80")

# ---------------- HEAT MAPS ---------------

# How many heat maps to return
# Change
H <- 7

heatmap_species <- vector("list", H)
heatmap_info_list <- vector("list", H)

# Change, IN ORDER
heatmap_species[[1]] <- CPC_species
heatmap_species[[2]] <- pH2A_species
heatmap_species[[3]] <- pH3_species
heatmap_species[[4]] <- CPC_active_species
heatmap_species[[5]] <- CPC_inactive_species
heatmap_species[[6]] <- CPC_pH2A_species
heatmap_species[[7]] <- CPC_pH3_species



# Change, name of plot in plot directory, also name in heatmap, IN ORDER
heatmap_info_list[[1]] <- c("all CPC")
heatmap_info_list[[2]] <- c("all pH2A")
heatmap_info_list[[3]] <- c("all pH3")
heatmap_info_list[[4]] <- c("All Active CPC")
heatmap_info_list[[5]] <- c("All Inactive CPC")
heatmap_info_list[[6]] <- c("All CPC bound to pH2A")
heatmap_info_list[[7]] <- c("All CPC bound to pH3")


# ---------------- LINE PLOTS ---------------
L <- 8

all_data <- vector("list", L)
species_info_list <- vector("list", L)

# Change, IN ORDER
all_species <- c(CPC_species, Mps1_species, Haspin_Plk1_species, pH3_species, pH2A_species, only_H3_H2A_species,Bub1a_pKnl1_species, Ndc80_species)

# Change, IN ORDER
all_data[[1]] <- CPC_species
all_data[[2]] <- Mps1_species
all_data[[3]] <- Haspin_Plk1_species
all_data[[4]] <- pH3_species
all_data[[5]] <- pH2A_species
all_data[[6]] <- only_H3_H2A_species
all_data[[7]] <- Bub1a_pKnl1_species
all_data[[8]] <- Ndc80_species


# Change, IN ORDER
species_info_list[[1]] <- c("CPC", "Inactive CPC", "Active CPC", "CPC Activation", TRUE, FALSE, FALSE, TRUE)
species_info_list[[2]] <- c("Mps1", "Inactive Mps1", "Active Mps1", "Mps1 Activation", TRUE, FALSE, FALSE, TRUE)
species_info_list[[3]] <- c("Haspin_Plk1_species", "Inactive Species", "Active Species", "All Species", FALSE, FALSE, TRUE, FALSE)
species_info_list[[4]] <- c("pH3_species", "Inactive pH3 Species", "Active pH3 Species", "All pH3 Species", FALSE, TRUE, TRUE, FALSE)
species_info_list[[5]] <- c("pH2A_species", "Inactive pH2A Species", "Active pH2A Species", "All pH2A Species", FALSE, TRUE, TRUE, FALSE)
species_info_list[[6]] <- c("H2A & H3", "Inactive H2A & H3", "Active H2A & H3", "H2A & H3", FALSE, FALSE, TRUE, FALSE)
species_info_list[[7]] <- c("Bub1a_pKnl1_species", "Inactive Species", "Active Species", "All Species", FALSE, FALSE, TRUE, FALSE)
species_info_list[[8]] <- c("Ndc80", "Inactive Ndc80", "Active Ndc80", "All Species", FALSE, FALSE, TRUE, FALSE)



# ---------------- SIMULATION SPECIFICS ---------------

# Model type, goes on the left of the heatmap
# Change
kt_width = c(
              # # "Tensed"
              # "Relaxed",
              # "Relaxed",
              # "Relaxed",
              "Metacentric_Relaxed",
              "Metacentric_Tensed"

             )

# All simulation IDs
# Change
sims <- c(
 
  # "SimID_262253748_0__exported"
 
  # "SimID_275966243_0__exported",
  # "SimID_275966243_1__exported",
  # "SimID_275966243_2__exported"
  # "SimID_276685993_0__exported"
  # "SimID_278919747_0__exported",
  # "SimID_278919749_0__exported"
  "SimID_298848254_0__exported",
  "SimID_298847711_0__exported"
  
  
)

# Folder naming corresponding to specific simulation ID
# Change
var <- c(
 
  # "10_25_23_400s_post_transition_base_20Pac"
  
  # "09_17_24_CPC_relaxed_RefModel_128x64_scan0",
  # "09_17_24_CPC_relaxed_RefModel_128x64_scan1",
  # "09_17_24_CPC_relaxed_RefModel_128x64_scan2"
  # "10_01_24_relaxed_RefModel_MonseData"
  # "Copy of 09_17_24_relaxed_RefModel_MCF10A_Bub1_CPC_values",
  # "Copy of 09_17_24_relaxed_RefModel_MCF10A_Bub1_CPC_Ndc80_values_low_Sgo1"
  # "_09_16_25_CPC_metacentric_relaxed_model"
  "11_07_25_metacentric_relaxed_MCF10A",
  "11_07_25_metacentric_tensed_MCF10A"
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
               tSpan=500, #400 for relaxed to tense
               desiredInterval=100,
               cutoff=5, #for heatmap color bar
               funcPath,
               importPath,
               exportPath_new,
               kt_width[i],
               movie = FALSE,
               lineplots=FALSE)

    
  }
}

