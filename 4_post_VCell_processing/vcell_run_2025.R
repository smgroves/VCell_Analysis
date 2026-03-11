#########################################################
# Install all needed packages
packages <- c("ggplot2","ggrastr","png","gridExtra","purrr","latex2exp","stringr","lemon","utils","tictoc","tidyverse","tibble","scales", "xlsx", "pdftools", "rhdf5", "png")
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
# dataDim=c(128,64)#edited
# chromWidth=1.6 #um
# chromHeight=3.2 #um

# #For prometaphase chromosomes
# dataDim=c(208,64)#edited
# chromWidth=1.6 #um
# chromHeight=5.2 #um

# #For metaphase chromosomes
dataDim=c(144,52)#edited
chromWidth=1.3 #um
chromHeight=3.6 #um

# ---------------- LISTS OF SPECIES ---------------

# Species Lists, add any that are required to be on one plot

CPC_species <-c("CPCa", "pH2A_SGO1_CPCa", "H3_CPCa", "pH3_CPCa", "SGO1_CPCa", "CPCi", "pH2A_SGO1_CPCi", "H3_CPCi", "pH3_CPCi", "SGO1_CPCi")
pNDC80_species <-c("pNDC80", "pNDC80_TTKa", "pNDC80_pTTKa", "pNDC80_TTKi", "pNDC80_pTTKi")
pH3_species <- c("pH3", "pH3_CPCa", "pH3_CPCi")
pH2A_species <- c("pH2A", "pH2A_SGO1", "pH2A_SGO1_CPCa", "pH2A_SGO1_CPCi")
HASPIN_PLK1_species <- c("HASPINa", "HASPINi", "PLK1a", "PLK1i")
BUB1a_pKNL1_species <- c("BUB1a", "pKNL1", "BUB1a_pKNL1", "BUB1a_his") #, "Bub1a_his"
SGO1_species <- c("SGO1", "pH2A_SGO1", "pH2A_SGO1_CPCi", "pH2A_SGO1_CPCa", "SGO1_CPCi", "SGO1_CPCa")
bound_CPC <- c("bound_CPC")
bound_active_CPC <- c("bound_active_CPC")
boundactive_CPC_pNDC80 <- c("boundactive_CPC_pNDC80")

# ---------------- HEAT MAPS ---------------

# How many heat maps to return
# Change
H <- 8

heatmap_species <- vector("list", H)
heatmap_info_list <- vector("list", H)

# Change, IN ORDER
heatmap_species[[1]] <- CPC_species
heatmap_species[[2]] <- pNDC80_species
heatmap_species[[3]] <- pH3_species
heatmap_species[[4]] <- pH2A_species
heatmap_species[[5]] <- SGO1_species
heatmap_species[[6]] <- bound_CPC
heatmap_species[[7]] <- bound_active_CPC
heatmap_species[[8]] <- boundactive_CPC_pNDC80


# Change, name of plot in plot directory, also name in heatmap, IN ORDER
heatmap_info_list[[1]] <- c("all CPC")
heatmap_info_list[[2]] <- c("all pNDC80")
heatmap_info_list[[3]] <- c("all pH3")
heatmap_info_list[[4]] <- c("all pH2A")
heatmap_info_list[[5]] <- c("all SGO1")
heatmap_info_list[[6]] <- c("all bound CPC")
heatmap_info_list[[7]] <- c("all bound active CPC")
heatmap_info_list[[8]] <- c("all bound active CPC and pNDC80")


# ---------------- LINE PLOTS ---------------
# L <- 10
#  
# all_data <- vector("list", L)
# species_info_list <- vector("list", L)
# all_species <- c(CPC_species, pNDC80_species, pH3_species, pH2A_species, HASPIN_PLK1_species, BUB1a_pKNL1_species, SGO1_species, bound_CPC, bound_active_CPC, boundactive_CPC_pNDC80)
# 
# 
# # Change, IN ORDER
# all_data[[1]] <- CPC_species
# all_data[[2]] <- pNDC80_species
# all_data[[3]] <- pH3_species
# all_data[[4]] <- pH2A_species
# all_data[[5]] <- HASPIN_PLK1_species
# all_data[[6]] <- BUB1a_pKNL1_species
# all_data[[7]] <- SGO1_species
# all_data[[8]] <- bound_CPC
# all_data[[9]] <- bound_active_CPC
# all_data[[10]] <- boundactive_CPC_pNDC80
# 
# 
#  
# # Change, IN ORDER
# species_info_list[[1]] <- c("CPC", "Inactive CPC", "Active CPC", "CPC Activation", TRUE, FALSE, FALSE, TRUE)
# species_info_list[[2]] <- c("pNDC80_species", "Inactive Species", "Active Species", "All Species", FALSE, FALSE, TRUE, FALSE)
# species_info_list[[3]] <- c("pH3_species", "Inactive Species", "Active Species", "All Species", FALSE, FALSE, TRUE, FALSE)
# species_info_list[[4]] <- c("pH2A_species", "Inactive Species", "Active Species", "All Species", FALSE, FALSE, TRUE, FALSE)
# species_info_list[[5]] <- c("HASPIN_PLK1_species", "Inactive Species", "Active Species", "All Species", FALSE, FALSE, TRUE, FALSE)
# species_info_list[[6]] <- c("Bub1a_pKnl1_spaecies", "Inactive Species", "Active Species", "All Species", FALSE, FALSE, TRUE, FALSE)
# species_info_list[[7]] <- c("Sgo1", "Inactive Species", "Active Species", "All Species", FALSE, FALSE, TRUE, FALSE)
# species_info_list[[8]] <- c("bound_CPC", "Inactive Species", "Active Species", "All Species", FALSE, FALSE, TRUE, FALSE)
# species_info_list[[9]] <- c("bound_active_CPC", "Inactive Species", "Active Species", "All Species", FALSE, FALSE, TRUE, FALSE)
# species_info_list[[10]] <- c("boundactive_CPC_pNDC80", "Inactive Species", "Active Species", "All Species", FALSE, FALSE, TRUE, FALSE)


# ---------------- SIMULATION SPECIFICS ---------------

# Model type, goes on the left of the heatmap
# Change
kt_width = c(
  # "Metacentric_Relaxed",
  # "Metacentric_Tensed",
  # "Telocentric_Relaxed"
  # "Telocentric_Tensed"
  # "Prometaphase_Relaxed"
  "Metacentric_Relaxed"
  # "Metacentric_Tensed"
  
  
)

# All simulation IDs
# Change
sims <- c(
  # "SimID_300540363_0__exported"
  # "SimID_300540363_1__exported"
  # "SimID_300540363_2__exported"
  "SimID_302551116_0__exported"
)

# Folder naming corresponding to specific simulation ID
# Change
var <- c(
  # "11_26_25_metacentric_relaxed_MCF10A_chr19_PMP1_haspin_stripe_0.15"
  # "11_26_25_metacentric_relaxed_MCF10A_chr19_PMP1_haspin_stripe_0.2"
  # "11_26_25_metacentric_relaxed_MCF10A_chr19_PMP1_haspin_stripe_0.25"
  "01_14_26_metacentric_relaxed_MCF10A_chr19_PMP1_active_kpp_CPCaIC_100s"
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
               tSpan=100, #400 for relaxed to tensed
               desiredInterval=10,
               cutoff=list("CPC"=11), #for heatmap color bar
              #  cutoff=3, #for heatmap color bar
               funcPath,
               importPath,
               exportPath_new,
               kt_width[i],
               movie = FALSE,
               lineplots=TRUE,
               KK_dist_relaxed = 0.575,
               KK_dist_tensed = 1.15,
               KT_width= 0.075,
               KT_height = 0.3,
               cohesin_width = 0.1)

  }
}

