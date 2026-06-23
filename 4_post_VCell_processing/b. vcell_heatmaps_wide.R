#########################################################
# Heatmaps-only script for a double-width chromosome model.
# Geometry: same height as chr19 PMP1, but twice the width
#   (104 cols instead of 52, 2.6 um instead of 1.3 um).
# Line plots are NOT generated here.
#########################################################

packages <- c("ggplot2", "ggrastr", "png", "gridExtra", "purrr",
               "latex2exp", "stringr", "utils", "tictoc", "tidyverse",
               "scales", "pdftools")
lapply(packages, require, character.only = TRUE)
tic("total")

# CHANGE: Folder paths
script_dir  <- normalizePath(dirname(rstudioapi::getSourceEditorContext()$path), mustWork = FALSE)
funcPath<-"/Users/smgroves/Documents/GitHub/VCell_Analysis/functions_2026"
importPath<-"/Users/smgroves/Library/CloudStorage/Box-Box/Research/JanesLab/CPC_Model_Project/VCell_Exports"
exportPath<-"/Users/smgroves/Library/CloudStorage/Box-Box/Research/JanesLab/CPC_Model_Project/vcell_plots"

    ##NEEED
# latex2exp     
# pdftools

# Source helper functions
functions <- file.path(funcPath, list.files(funcPath, recursive = TRUE))
for (f in functions) source(f)

# CHANGE: Chromosome geometry — double width relative to chr19 PMP1
dataDim     <- c(136, 104)   # rows (height) x cols (width); cols = 52 * 2
chromWidth  <- 2.6           # um  (1.3 * 2)
chromHeight <- 3.4           # um  (unchanged)

# ---------------- SPECIES LISTS ---------------

CPC_species        <- c("CPCa", "pH2A_SGO1_CPCa", "H3_CPCa", "pH3_CPCa", "SGO1_CPCa",
                        "CPCi", "pH2A_SGO1_CPCi", "H3_CPCi", "pH3_CPCi", "SGO1_CPCi")
pH3_species        <- c("pH3", "pH3_CPCa", "pH3_CPCi")
pH2A_species       <- c("pH2A", "pH2A_SGO1", "pH2A_SGO1_CPCa", "pH2A_SGO1_CPCi")
SGO1_species       <- c("SGO1", "pH2A_SGO1", "pH2A_SGO1_CPCi", "pH2A_SGO1_CPCa",
                        "SGO1_CPCi", "SGO1_CPCa")
bound_CPC          <- c("bound_CPC")
bound_active_CPC   <- c("bound_active_CPC")
pH3S10rep          <- c("pH3S10rep")

# ---------------- HEATMAP CONFIGURATION ---------------

H <- 7
heatmap_species   <- vector("list", H)
heatmap_info_list <- vector("list", H)

heatmap_species[[1]] <- CPC_species
heatmap_species[[2]] <- bound_CPC
heatmap_species[[3]] <- bound_active_CPC
heatmap_species[[4]] <- pH3_species
heatmap_species[[5]] <- pH2A_species
heatmap_species[[6]] <- SGO1_species
heatmap_species[[7]] <- pH3S10rep

heatmap_info_list[[1]] <- "all CPC"
heatmap_info_list[[2]] <- "all bound CPC"
heatmap_info_list[[3]] <- "all bound active CPC"
heatmap_info_list[[4]] <- "all pH3"
heatmap_info_list[[5]] <- "all pH2A"
heatmap_info_list[[6]] <- "all SGO1"
heatmap_info_list[[7]] <- "all pH3S10rep"

# ---------------- COMPUTED FUNCTIONS (R-side, no pre-generated CSVs needed) ---------------
# If a species CSV is absent, these are summed from their components on the fly.
# Set to NULL to disable and rely entirely on pre-generated CSVs.

compute_functions <- list(
  bound_CPC        = c("pH2A_SGO1_CPCa", "H3_CPCa", "pH3_CPCa", "SGO1_CPCa",
                       "pH2A_SGO1_CPCi", "H3_CPCi", "pH3_CPCi", "SGO1_CPCi"),
  bound_active_CPC = c("pH2A_SGO1_CPCa", "H3_CPCa", "pH3_CPCa", "SGO1_CPCa"),
  CPC_all          = c("CPCa", "pH2A_SGO1_CPCa", "H3_CPCa", "pH3_CPCa", "SGO1_CPCa",
                       "CPCi", "pH2A_SGO1_CPCi", "H3_CPCi", "pH3_CPCi", "SGO1_CPCi"),
  CPCa_total       = c("CPCa", "pH2A_SGO1_CPCa", "H3_CPCa", "pH3_CPCa", "SGO1_CPCa"),
  pNDC80_total     = c("pNDC80", "pNDC80_TTKi", "pNDC80_pTTKi", "pNDC80_TTKa", "pNDC80_pTTKa"),
  pKNL1_all        = c("pKNL1", "pKNL1_bub1a")
)

# ---------------- SIMULATION SPECIFICS ---------------

# CHANGE: model-type label for each sim (appears on left of heatmap)
kt_width <- c(
  "Metacentric_Relaxed"
)

# CHANGE: SimID folder names (inside the workspace subfolder)
sims <- c(
  "SimID_316812427_0__exported" 
)

# CHANGE: workspace subfolder names (one per sim, same order as sims)
var <- c(
  "06_19_26_metacentric_MCF10A_double_tensed_relaxed_chr19_PMP1"
)

# CHANGE: heatmap time points (index into the saved timepoints)
alternative_range <- c(0, 10, 20, 25, 30, 40, 50)

# CHANGE: color-bar ceiling per species group
cutoff <- list("CPC" = 11)

# CHANGE: tSpan must match what was saved in the simulation (seconds)
tSpan <- 500

# -------------------------------------------------------

for (i in 1:length(sims)) {

  sweep_name     <- var[i]
  exportPath_new <- file.path(exportPath, sweep_name)

  print(sweep_name)
  print(sims[i])

  if (!file.exists(file.path(importPath, sims[i]))) {
    warning(paste0("SimID folder not found, skipping: ", file.path(importPath, sims[i])))
    next
  }

  dir.create(exportPath_new, recursive = TRUE, showWarnings = FALSE)

  for (hm in 1:H) {
    vcell_heatmap(
      SimID             = sims[i],
      names             = paste(kt_width[i], "Model"),
      species           = heatmap_species[[hm]],
      speciesName       = heatmap_info_list[[hm]],
      cutoff_color      = cutoff,
      tInit             = 0,
      tSpan             = tSpan,
      tInterval         = 10,
      desiredInterval   = 1,
      nHeatmaps         = length(alternative_range),
      alternative_range = alternative_range,
      importPath        = importPath,
      exportPath        = exportPath_new,
      compute_functions = compute_functions,
      devices           = "png",
      show_plot         = FALSE
    )
  }

  message("Heatmaps saved to: ", exportPath_new)
}

toc()
