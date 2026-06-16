#########################################################
# Install all needed packages
packages <- c("ggplot2","ggrastr","png","gridExtra","purrr","latex2exp","stringr","utils","tictoc","tidyverse","tibble","scales", "pdftools", "rhdf5", "png")
lapply(packages, require, character.only = TRUE)
tic("total")

# CHANGE: Folder paths
funcPath<-"/Users/smgroves/Documents/GitHub/VCell_Analysis/functions_2026"
importPath<-"/Users/smgroves/Library/CloudStorage/Box-Box/Research/CPC_Model_Project/VCell_Exports"
exportPath<-"/Users/smgroves/Library/CloudStorage/Box-Box/Research/CPC_Model_Project/vcell_plots"


# Functions
functions<-list.files(funcPath,recursive=TRUE)
functions<-file.path(funcPath,functions)
for(i in functions){
  print(i)
  source(i)
}

#CHANGE: Chromosome geometry
# Chr19 - PMP1
dataDim=c(136,52)#edited
chromWidth=1.3 #um
chromHeight=3.4 #um

# ---------------- LISTS OF SPECIES ---------------

# Species Lists, add any that are required to be on one plot

CPC_species <-c("CPCa", "pH2A_SGO1_CPCa", "H3_CPCa", "pH3_CPCa", "SGO1_CPCa", "CPCi", "pH2A_SGO1_CPCi", "H3_CPCi", "pH3_CPCi", "SGO1_CPCi")
pH3_species <- c("pH3", "pH3_CPCa", "pH3_CPCi")
pH2A_species <- c("pH2A", "pH2A_SGO1", "pH2A_SGO1_CPCa", "pH2A_SGO1_CPCi")
HASPIN_PLK1_species <- c("HASPINa", "HASPINi", "PLK1a", "PLK1i")
BUB1a_pKNL1_species <- c("BUB1a",  "pKNL1", "pKNL1_bub1a", "BUB1a_pknl1")
SGO1_species <- c("SGO1", "pH2A_SGO1", "pH2A_SGO1_CPCi", "pH2A_SGO1_CPCa", "SGO1_CPCi", "SGO1_CPCa")
bound_CPC <- c("bound_CPC")
bound_active_CPC <- c("bound_active_CPC")
pNDC80_species <- c("pNDC80", "pNDC80_TTKi", "pNDC80_pTTKi", "pNDC80_TTKa", "pNDC80_pTTKa")
pNDC80_total <- c("pNDC80_total")
pH3S10rep <- c("pH3S10rep")

# ---------------- HEAT MAPS ---------------

# How many heat maps to return
# Change
H <- 2

heatmap_species <- vector("list", H)
heatmap_info_list <- vector("list", H)

# Change, IN ORDER
heatmap_species[[1]] <- bound_CPC
heatmap_species[[2]] <- bound_active_CPC
# heatmap_species[[3]] <- CPC_species

# heatmap_species[[4]] <- pH3_species
# heatmap_species[[5]] <- pH2A_species
# heatmap_species[[6]] <- SGO1_species
# heatmap_species[[7]] <- pH3S10rep

# Change, name of plot in plot directory, also name in heatmap, IN ORDER
heatmap_info_list[[1]] <- c("all bound CPC")
heatmap_info_list[[2]] <- c("all bound active CPC")
# heatmap_info_list[[3]] <- c("all CPC")

# heatmap_info_list[[4]] <- c("all pH3")
# heatmap_info_list[[5]] <- c("all pH2A")
# heatmap_info_list[[6]] <- c("all SGO1")
# heatmap_info_list[[7]] <- c("all pH3S10rep")


# ---------------- LINE PLOTS ---------------
# L <- 1
#  
# all_data <- vector("list", L)
# species_info_list <- vector("list", L)
# all_species <- c(CPC_species)#, pH3_species, pH2A_species, HASPIN_PLK1_species, BUB1a_pKNL1_species, SGO1_species, bound_CPC, bound_active_CPC, pNDC80_species, pNDC80_total, pH3S10rep)
# 
# 
# # Change, IN ORDER
# all_data[[1]] <- CPC_species
# all_data[[2]] <- pH3_species
# all_data[[3]] <- pH2A_species
# all_data[[4]] <- HASPIN_PLK1_species
# all_data[[5]] <- BUB1a_pKNL1_species
# all_data[[6]] <- SGO1_species
# all_data[[7]] <- bound_CPC
# all_data[[8]] <- bound_active_CPC
# all_data[[9]] <- pNDC80_species
# all_data[[10]] <- pNDC80_total
# all_data[[11]] <- pH3S10rep
 
# Change, IN ORDER
#species_info_list[[1]] <- c("File name for saving plot", "Title on plots with only inactive species", "Title on plots with only active species", "Title on plots with both active and inactive species",
                            # SUM:"sums of inactive and active species should be added" (Active: Black, Solid & Inactive: Black, Dashed), 
                            # TOTAL: "sum of all species should be added",
                            # FULL: "all species should be added to line plots",
                            # COLLAPSIBLE: "whether only the top 4 species and their sums/total should be specified")
species_info_list[[1]] <- c("CPC", "Inactive CPC", "Active CPC", "CPC Activation", TRUE, FALSE, FALSE, TRUE)
# species_info_list[[2]] <- c("pH3_species", "Inactive Species", "Active Species", "pH3 Species", FALSE, FALSE, TRUE, FALSE)
# species_info_list[[3]] <- c("pH2A_species", "Inactive Species", "Active Species", "pH2A Species", FALSE, FALSE, TRUE, FALSE)
# species_info_list[[4]] <- c("HASPIN_PLK1_species", "Inactive Species", "Active Species", "HASPIN Activation", FALSE, FALSE, TRUE, FALSE)
# species_info_list[[5]] <- c("Bub1a_pKnl1_species", "Inactive Species", "Active Species", "BUB1 recruitment", FALSE, FALSE, TRUE, FALSE)
# species_info_list[[6]] <- c("Sgo1", "Inactive Species", "Active Species", "SGO1 Species", FALSE, FALSE, TRUE, FALSE)
# species_info_list[[7]] <- c("bound_CPC", "Inactive Species", "Active Species", "Bound CPC", FALSE, FALSE, TRUE, FALSE)
# species_info_list[[8]] <- c("bound_active_CPC", "Inactive Species", "Active Species", "Bound active CPC", FALSE, FALSE, TRUE, FALSE)
# species_info_list[[9]] <- c("pNDC80_species", "Inactive Species", "Active Species", "pNDC80 Species", FALSE, FALSE, TRUE, FALSE)
# species_info_list[[10]] <- c("pNDC80_total", "Inactive Species", "Active Species", "SUM of pNDC80 Species", FALSE, FALSE, TRUE, FALSE)
# species_info_list[[11]] <- c("pH3S10rep", "Inactive Species", "Active Species", "pH3S10 reporter", FALSE, FALSE, TRUE, FALSE)

# ---------------- SIMULATION SPECIFICS ---------------

# Model type, goes on the left of the heatmap
# Change
kt_width = c(

  "Metacentric_Tensed"
# "Metacentric_Relaxed"
)

# All simulation IDs
# Change
sims <- c(
  # "SimID_316157798_0__exported"
  # "SimID_316030881_0__exported"
  # "SimID_316157808_5__exported"
  "SimID_316194425_0__exported"
  )

# Folder naming corresponding to specific simulation ID
# Change
var <- c(
  # "06_10_26_metacentric_relaxed_MCF10A_chr19_PMP1"
  # "06_10_26_metacentric_transition_tensed_MCF10A_chr19_PMP1_t_transition_scan_200"
  "06_10_26_metacentric_transition_tensed_MCF10A_chr19_PMP1_t_0_just_stretch"
  
)
#########################################################

print("Running plots...")
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
               tSpan=20, 
               desiredInterval=1,
               # alternative_range <- NULL, #when equal spacing is enough on heatmaps
               alternative_range <- c(0,2,5,10,17,20), #alternative desired time points to be plotted on heatmaps
               cutoff=list("CPC"=14), #for heatmap color bar
               funcPath,
               importPath,
               exportPath_new,
               kt_width[i],
               movie = FALSE,
               lineplots=TRUE,
               KK_dist_relaxed = 0.575,
               KK_dist_tensed = 1.15,
               KT_width= 0.075,
               KT_height = 0.3, #0.3 um in model
               cohesin_width = 0.1) #0.1 um in model

  }

  # cpc_data <- get_cumulative_bound_CPC(
  # SimID         = sims[i],
  # tInit         = 0,
  # tSpan         = 500,
  # importPath    = importPath,
  # exportPath    = exportPath_new,
  # dataDim       = dataDim,
  # chromWidth    = chromWidth,
  # chromHeight   = chromHeight,
  # kt_width      = kt_width[i]
  # )
}

