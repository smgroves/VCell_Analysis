#########################################################
# Install all needed packages
packages <- c("ggplot2","gridExtra","purrr","latex2exp","stringr","lemon","utils","tictoc","tidyverse","tibble","scales", "xlsx", "pdftools", "rhdf5", "rgoogleslides", "googleCloudStorageR", "png")
lapply(packages, require, character.only = TRUE)
tic("total")


# CHANGE
funcPath<-"/Users/smgroves/Documents/Github/VCell_Analysis/functions"
importPath<-"/Users/smgroves/Box/CPC_Model_Project/VCell_Exports"
exportPath<-"/Users/smgroves/Box/CPC_Model_Project/vcell_plots"
# desktop<-"/Users/sam/Desktop"


# Functions
functions<-list.files(funcPath,recursive=TRUE)
functions<-file.path(funcPath,functions)
for(i in functions){
  print(i)
  source(i)
}

dataDim=c(149,68)

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


# H <- 2
# 
# heatmap_species <- vector("list", H)
# heatmap_info_list <- vector("list", H)
# 
# # Change, IN ORDER
# heatmap_species[[1]] <- Bub1a
# heatmap_species[[2]] <- pKnl1_Bub1a
# 
# 
# 
# # Change, name of plot in plot directory, also name in heatmap, IN ORDER
# heatmap_info_list[[1]] <- c("Bub1a")
# heatmap_info_list[[2]] <- c("pKnl1_Bub1a")



# ---------------- LINE PLOTS ---------------
L <- 6

all_data <- vector("list", L)
species_info_list <- vector("list", L)

# Change, IN ORDER
all_species <- c(CPC_species, Mps1_species, Haspin_Plk1_species, pH3_species, pH2A_species, only_H3_H2A_species)

# Change, IN ORDER
all_data[[1]] <- CPC_species
all_data[[2]] <- Mps1_species
all_data[[3]] <- Haspin_Plk1_species
all_data[[4]] <- pH3_species
all_data[[5]] <- pH2A_species
all_data[[6]] <- only_H3_H2A_species

# Change, IN ORDER
species_info_list[[1]] <- c("CPC", "Inactive CPC", "Active CPC", "CPC Activation", TRUE, FALSE, FALSE, TRUE)
species_info_list[[2]] <- c("Mps1", "Inactive Mps1", "Active Mps1", "Mps1 Activation", TRUE, FALSE, FALSE, TRUE)
species_info_list[[3]] <- c("Haspin_Plk1_species", "Inactive Species", "Active Species", "All Species", FALSE, FALSE, TRUE, FALSE)
species_info_list[[4]] <- c("pH3_species", "Inactive pH3 Species", "Active pH3 Species", "All pH3 Species", FALSE, TRUE, TRUE, FALSE)
species_info_list[[5]] <- c("pH2A_species", "Inactive pH2A Species", "Active pH2A Species", "All pH2A Species", FALSE, TRUE, TRUE, FALSE)
species_info_list[[6]] <- c("H2A & H3", "Inactive H2A & H3", "Active H2A & H3", "H2A & H3", FALSE, FALSE, TRUE, FALSE)


# 
# # How many line plots to return
# # Change
# L <- 6
# 
# all_data <- vector("list", L)
# species_info_list <- vector("list", L)
# 
# # Change, IN ORDER
# all_species <- c(Bub1a_pKnl1_species, Haspin_P_species)
# 
# # Change, IN ORDER
# all_data[[1]] <- Bub1a_pKnl1_species
# all_data[[2]] <- Haspin_P_species
# 
# 
# # Change, IN ORDER
# 
# species_info_list[[1]] <- c("Bub1a_pKnl1_species", "Inactive Species", "Active Species", "All Species", FALSE, FALSE, TRUE, FALSE)
# species_info_list[[2]] <- c("Haspin_Plk1_species", "Inactive Species", "Active Species", "All Species", FALSE, FALSE, TRUE, FALSE)
# 


# ---------------- SIMULATION SPECIFICS ---------------

# Model type, goes on the left of the heatmap
# Change
kt_width = c('Relaxed')

# All simulation IDs
# Change
sims <- c(
  "SimID_259801922_0__exported",
  "SimID_259801920_0__exported"
  # "SimID_259918334_0__exported"
)

# Folder naming corresponding to specific simulation ID
# Change
var <- c(
  "08_21_23_relaxed_RefModel_Mps1_phos_Plk1a_20Pac transactiv",
  "08_21_23_relaxed_RefModel_Mps1_phos_Plk1s transactiv"
  # "08_29_23_tensed_CPCic_from_relaxed_20Pac"
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
               cutoff=10,
               funcPath,
               importPath,
               exportPath_new,
               kt_width[i])
    
    # vcell_table(sims[i],
    #             var[i],
    #             tPoints=c(200, 500),
    #             all_species=CPC_species,
    #             name='CPC',
    #             chromWidth=1.6,
    #             chromHeight=3.5,
    #             dataDim=c(149,68),
    #             row_1=1,
    #             row_2=dataDim[1],
    #             col_1=1,
    #             col_2=dataDim[2],
    #             importPath,
    #             exportPath_new)
    
    
  }
}

################################# GOOGLE SLIDES #####################################

# Change
# sims <- c(
#   "SimID_259214167_0__exported",
#   "SimID_259214167_1__exported",
#   "SimID_259214167_2__exported",
#   "SimID_259214167_3__exported",
#   "SimID_259214167_4__exported",
#   "SimID_259214167_5__exported",
#   "SimID_259214165_0__exported",
#   "SimID_259214169_0__exported",
#   "SimID_259214169_1__exported"
# 
# )
# 
# # Change 
# var <- c(
#   "Module1 Plk1a_fracs III - Plk1a_frac 0.05p",
#   "Module1 Plk1a_fracs III - Plk1a_frac 0.1p",
#   "Module1 Plk1a_fracs III - Plk1a_frac 0.2p",
#   "Module1 Plk1a_fracs III - Plk1a_frac 0.5p",
#   "Module1 Plk1a_fracs III - Plk1a_frac 0.8p",
#   "Module1 Plk1a_fracs III - Plk1a_frac 1.0p",
#   "Module Plk1a_frac 2.5p",
#   "Module1 Plk1a_fracs II - Plk1a_frac 0.3p",
#   "Module1 Plk1a_fracs II - Plk1a_frac 0.4p"
# )



# --------------- Authorizing -------------------

# Change
Sys.setenv("GCS_DEFAULT_BUCKET" = "vcell_bucket")
# Change
Sys.setenv("GCS_AUTH_FILE"="C:/Users/sam/Downloads/disco-basis-393613-adc3747a6a2d.json")
# Change
gcs_global_bucket("vcell_bucket")

# Change
authorize("648818067522-j37u914d2bao6372o6jgorq7glnc25eg.apps.googleusercontent.com",
          "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")

# Change
gcs_auth("C:/Users/sam/Downloads/disco-basis-393613-adc3747a6a2d.json")

# Change
slide_plots <- c("all CPC_heatmap",
                 # "all Mps1a_heatmap",
                 # "all Mps1i_heatmap",
                 "all pH2A_heatmap",
                 "all pH3_heatmap",
                 "CPC_plot_1",
                 # "Mps1_plot_1",
                 # "Haspin_Plk1_species",
                 "pH2A_species_plot_1",
                 "pH3_species_plot_1",
                 "H2A & H3_plot_1"
                 # "CPC_table"
)

slide_plots <- c("Bub1a_heatmap",
                 "pKnl1_Bub1a_heatmap",
                 "Bub1a_pKnl1_species_plot_1",
                 "Haspin_Plk1_species_plot_1")


# Simulations 7/31/2023 FOR EXISTING SLIDES
slide_id <- "1EoyU_1Zwd4oMmmsyoXnGonG5AgTn1hdI2VHr5m6EO4c"


# Change ONLY IF YOU WANT NEW SLIDES
title <- "Module 1 Simulations 8/7/2023"
# MAKE A NEW SLIDE_ID FOR A NEW PRESENTATION
slide_id <- rgoogleslides::create_slides(title)


for(i in 1:length(sims)){
  if(file.exists("/Users/sam/Research/JanesLab/vcell_data") == TRUE){
    
    # what to name the output graph file, as a string "name" 
    # sweep_name<-paste("Relaxed_Base model", var[i])
    sweep_name<-var[i]
    
    dir.create(file.path(exportPath, sweep_name))
    exportPath_n <- paste(exportPath, sweep_name, sep="/")
    
    populate_slides(
                    exportPath_n,
                    slide_id,
                    var[i],
                    slide_plots
                    )
    
    
  }
}







