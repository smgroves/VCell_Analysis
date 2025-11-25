#########################################################
# Install all needed packages
options(repos = c(CRAN = "https://cloud.r-project.org"))
# install.packages(c("gifski","transformr"))
if (!requireNamespace("ggrastr", quietly = TRUE)) install.packages("ggrastr")
packages <- c("cetcolor","ggplot2","ggrastr","gganimate","gifski","av","transformr","png","gridExtra","purrr","latex2exp","stringr","lemon","utils","tictoc","tidyverse","tibble","scales", "xlsx", "pdftools", "png")
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
chromWidth=1.3 #um
chromHeight=4.5 #um
dataDim<-c(180,52)


# Functions
functions<-list.files(funcPath,recursive=TRUE)
functions<-file.path(funcPath,functions)
for(i in functions){
  print(i)
  source(i)
}

# dataDim=c(128,64) #edited

# ---------------- LISTS OF SPECIES ---------------

# Species Lists, add any that are required to be on one plot
CPC_species <-c("CPCa", "pH2A_SGO1_CPCa", "H3_CPCa", "pH3_CPCa", "SGO1_CPCa", "CPCi", "pH2A_SGO1_CPCi", "H3_CPCi", "pH3_CPCi", "SGO1_CPCi")
pNDC80_species <-c("pNDC80_TTKa", "pNDC80_pTTKa", "pNDC80_TTKi", "pNDC80_pTTKi")
pH3_species <- c("pH3", "pH3_CPCa", "pH3_CPCi")
pH2A_species <- c("pH2A", "pH2A_SGO1", "pH2A_SGO1_CPCa", "pH2A_SGO1_CPCi")
HASPIN_PLK1_species <- c("HASPINa", "HASPINi", "PLK1a", "PLK1i")
BUB1a_pKNL1_species <- c("BUB1a", "pKNL1", "BUB1a_pKNL1", "BUB1a_his") #, "Bub1a_his"
SGO1_species <- c("SGO1", "pH2A_SGO1", "pH2A_SGO1_CPCi", "pH2A_SGO1_CPCa", "SGO1_CPCi", "SGO1_CPCa")
bound_CPC <- c("bound_CPC")
bound_active_CPC <- c("bound_active_CPC")
boundactive_CPC_pNDC80 <- c("boundactive_CPC_pNDC80")
# CPC_species <-c("CPCa", "pH2A_SGO1_CPCa", "pH3_CPCa", "CPCi", "pH2A_SGO1_CPCi", "pH3_CPCi","H3_CPCi",'H3_CPCa')
# TTK_species <-c("TTKa", "pTTKa", "NDC80_TTKa", "NDC80_pTTKa", "pNDC80_TTKa", "pNDC80_pTTKa", "TTKi", "pTTKi", "NDC80_TTKi", "NDC80_pTTKi", "pNDC80_TTKi", "pNDC80_pTTKi")
# Todd_species <-c("PLK1a", "PLK1i", "HASPINa", "HASPINi", "pH3", "pH3_CPCa", "pH3_CPCi", "pH2A_SGO1_CPCi", "pH2A_SGO1_CPCa")
# pH3_species <- c("pH3", "pH3_CPCa", "pH3_CPCi")
# pH2A_species <- c("pH2A", "pH2A_SGO1", "pH2A_SGO1_CPCa", "pH2A_SGO1_CPCi")
# HASPIN_PLK1_species <- c("HASPINa", "HASPINi", "PLK1a", "PLK1i")
# only_H3_H2A_species <- c("H3", "H2A")
# BUB1a <- c("BUB1a")
# # BUB1a_pKNL1_species <- c("BUB1a", "pKNL1", "pKNL1_BUB1a")
# HASPIN_P_species <- c("HASPINa", "HASPINi", "PLK1a")
# CPC_active_species <-c("pH2A_SGO1_CPCa", "pH3_CPCa","CPCa",'H3_CPCa')
# CPC_inactive_species <-c("CPCi", "pH2A_SGO1_CPCi", "pH3_CPCi","H3_CPCi")
# CPC_pH2A_species <-c( "pH2A_SGO1_CPCa", "pH2A_SGO1_CPCi")
# CPC_pH3_species <-c( "pH3_CPCa", "pH3_CPCi","H3_CPCa","H3_CPCi")
# NDC80_species <-c("NDC80", "pNDC80")

# ---------------- HEAT MAPS ---------------
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
L <- 10
 
all_data <- vector("list", L)
species_info_list <- vector("list", L)
all_species <- c(CPC_species, pNDC80_species, pH3_species, pH2A_species, HASPIN_PLK1_species, BUB1a_pKNL1_species, SGO1_species, bound_CPC, bound_active_CPC, boundactive_CPC_pNDC80)


# Change, IN ORDER
all_data[[1]] <- CPC_species
all_data[[2]] <- pNDC80_species
all_data[[3]] <- pH3_species
all_data[[4]] <- pH2A_species
all_data[[5]] <- HASPIN_PLK1_species
all_data[[6]] <- BUB1a_pKNL1_species
all_data[[7]] <- SGO1_species
all_data[[8]] <- bound_CPC
all_data[[9]] <- bound_active_CPC
all_data[[10]] <- boundactive_CPC_pNDC80


 
# Change, IN ORDER
species_info_list[[1]] <- c("CPC", "Inactive CPC", "Active CPC", "CPC Activation", TRUE, FALSE, FALSE, TRUE)
species_info_list[[2]] <- c("pNDC80_species", "Inactive Species", "Active Species", "All Species", FALSE, FALSE, TRUE, FALSE)
species_info_list[[3]] <- c("pH3_species", "Inactive Species", "Active Species", "All Species", FALSE, FALSE, TRUE, FALSE)
species_info_list[[4]] <- c("pH2A_species", "Inactive Species", "Active Species", "All Species", FALSE, FALSE, TRUE, FALSE)
species_info_list[[5]] <- c("HASPIN_PLK1_species", "Inactive Species", "Active Species", "All Species", FALSE, FALSE, TRUE, FALSE)
species_info_list[[6]] <- c("Bub1a_pKnl1_spaecies", "Inactive Species", "Active Species", "All Species", FALSE, FALSE, TRUE, FALSE)
species_info_list[[7]] <- c("Sgo1", "Inactive Species", "Active Species", "All Species", FALSE, FALSE, TRUE, FALSE)
species_info_list[[8]] <- c("bound_CPC", "Inactive Species", "Active Species", "All Species", FALSE, FALSE, TRUE, FALSE)
species_info_list[[9]] <- c("bound_active_CPC", "Inactive Species", "Active Species", "All Species", FALSE, FALSE, TRUE, FALSE)
species_info_list[[10]] <- c("boundactive_CPC_pNDC80", "Inactive Species", "Active Species", "All Species", FALSE, FALSE, TRUE, FALSE)


# # How many heat maps to return
# # Change
# H <- 7

# heatmap_species <- vector("list", H)
# heatmap_info_list <- vector("list", H)

# # Change, IN ORDER
# heatmap_species[[1]] <- CPC_species
# heatmap_species[[2]] <- pH2A_species
# heatmap_species[[3]] <- pH3_species
# heatmap_species[[4]] <- CPC_active_species
# heatmap_species[[5]] <- CPC_inactive_species
# heatmap_species[[6]] <- CPC_pH2A_species
# heatmap_species[[7]] <- CPC_pH3_species



# # Change, name of plot in plot directory, also name in heatmap, IN ORDER
# heatmap_info_list[[1]] <- c("all CPC")
# heatmap_info_list[[2]] <- c("all pH2A")
# heatmap_info_list[[3]] <- c("all pH3")
# heatmap_info_list[[4]] <- c("All Active CPC")
# heatmap_info_list[[5]] <- c("All Inactive CPC")
# heatmap_info_list[[6]] <- c("All CPC bound to pH2A")
# heatmap_info_list[[7]] <- c("All CPC bound to pH3")


# # ---------------- LINE PLOTS ---------------
# L <- 7

# all_data <- vector("list", L)
# species_info_list <- vector("list", L)

# # Change, IN ORDER
# all_species <- c(CPC_species, TTK_species, HASPIN_PLK1_species, pH3_species, pH2A_species, only_H3_H2A_species, NDC80_species)

# # Change, IN ORDER
# all_data[[1]] <- CPC_species
# all_data[[2]] <- TTK_species
# all_data[[3]] <- HASPIN_PLK1_species
# all_data[[4]] <- pH3_species
# all_data[[5]] <- pH2A_species
# all_data[[6]] <- only_H3_H2A_species
# all_data[[7]] <- NDC80_species


# # Change, IN ORDER
# species_info_list[[1]] <- c("CPC", "Inactive CPC", "Active CPC", "CPC Activation", TRUE, FALSE, FALSE, TRUE)
# species_info_list[[2]] <- c("TTK", "Inactive TTK", "Active TTK", "TTK Activation", TRUE, FALSE, FALSE, TRUE)
# species_info_list[[3]] <- c("HASPIN_PLK1_species", "Inactive Species", "Active Species", "All Species", FALSE, FALSE, TRUE, FALSE)
# species_info_list[[4]] <- c("pH3_species", "Inactive pH3 Species", "Active pH3 Species", "All pH3 Species", FALSE, TRUE, TRUE, FALSE)
# species_info_list[[5]] <- c("pH2A_species", "Inactive pH2A Species", "Active pH2A Species", "All pH2A Species", FALSE, TRUE, TRUE, FALSE)
# species_info_list[[6]] <- c("H2A & H3", "Inactive H2A & H3", "Active H2A & H3", "H2A & H3", FALSE, FALSE, TRUE, FALSE)
# species_info_list[[7]] <- c("NDC80", "Inactive NDC80", "Active NDC80", "All Species", FALSE, FALSE, TRUE, FALSE)


kt_width = c("Metacentric_Relaxed" )

# All simulation IDs
sims <- c( "SimID_299564396_0__exported")

# Simulation name i.e. folder
sim_names <- c( "11_24_25_metacentric_relaxed_MCF10A")

#########################################################


for(i in 1:length(sims)){
  if(file.exists(importPath) == TRUE){
    print(importPath)
    
    sweep_name<-sim_names[i]
    
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
               tSpan=500, 
               desiredInterval=100,
               cutoff=list("CPC"=4), #for heatmap color bar
               funcPath,
               importPath,
               exportPath_new,
               kt_width[i],
               movie = TRUE,
               lineplots=TRUE,
               KK_dist_relaxed = 0.575,
               KK_dist_tensed = 1.15,
               KT_width= 0.075,
               KT_height = 0.3,
               cohesin_width = 0.1)
    
  }
}

