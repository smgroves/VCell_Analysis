# test heatmap
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

dataDim=c(128,64) #edited
CPC_species <-c("CPCa", "pH2A_Sgo1_CPCa", "pH3_CPCa", "pH2A_Sgo1_pH3_CPCa", "CPCi", "pH2A_Sgo1_CPCi", "pH3_CPCi", "pH2A_Sgo1_pH3_CPCi")
H <- 1

heatmap_species <- vector("list", H)
heatmap_info_list <- vector("list", H)

heatmap_species[[1]] <- CPC_species
heatmap_info_list[[1]] <- c("all CPC")

hm = 1
kt_width = c("Relaxed")
sims = c("SimID_270418727_0__exported")
vars = c("03_25_24_relaxed_RefModel")
dir.create(file.path(exportPath, vars[1]))
exportPath_new <- paste(exportPath, vars[1], sep="/")

heatmap<-vcell_heatmap(
  SimID=sims,
  names=paste(kt_width[i], "Model"),
  species=heatmap_species[[hm]],
  speciesName=heatmap_info_list[[hm]],
  cutoff_color=10,
  tInit=0,
  tSpan=500,
  tInterval=10,
  desiredInterval=100,
  dataDim=c(128,64), #updated
  row_1=1,
  row_2=dataDim[1],
  col_1=1,
  col_2=dataDim[2],
  chromWidth=1.6, #um
  chromHeight=3.2, #um #updated
  importPath=importPath,
  exportPath=exportPath_new)
