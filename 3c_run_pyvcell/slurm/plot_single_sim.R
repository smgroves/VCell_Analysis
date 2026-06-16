#!/usr/bin/env Rscript
# plot_single_sim.R
# Command-line version of vcell_run_2025.R for use in SLURM array jobs.
# Generates heatmaps and line plots for ONE workspace folder.
#
# Usage:
#   Rscript plot_single_sim.R \
#       --workspace /path/to/workspace \
#       --var       _005_20_26_CPC_metacentric_relaxed_MCF10A_chr19_PMP1_kbind1_KmTTK5.4 \
#       --kt_width  Metacentric_Relaxed \
#       --funcpath  /path/to/functions_2026 \
#       --chr       chr19 \
#       --phase     PMP1

suppressPackageStartupMessages({
  library(argparser)
  library(ggplot2)
  library(ggrastr)
  library(png)
  library(gridExtra)
  library(purrr)
  library(latex2exp)
  library(stringr)
  library(tictoc)
  library(tidyverse)
  library(scales)
  library(pdftools)
})

# ── Parse arguments ───────────────────────────────────────────────────────────
p <- arg_parser("Plot heatmaps and line plots for one VCell simulation folder")
p <- add_argument(p, "--workspace", help = "Absolute path to workspace directory")
p <- add_argument(p, "--var",       help = "Workspace folder name for this simulation")
p <- add_argument(p, "--kt_width",  help = "Model type label (e.g. Metacentric_Relaxed)")
p <- add_argument(p, "--funcpath",  help = "Absolute path to functions_2026 directory")
p <- add_argument(p, "--chr",       help = "Chromosome (e.g. chr19)", default = "chr19")
p <- add_argument(p, "--phase",     help = "Cell-cycle phase (e.g. PMP1)",  default = "PMP1")
argv <- parse_args(p)

tic("total")

# ── Source all helper functions ───────────────────────────────────────────────
importPath  <- normalizePath(argv$workspace, mustWork = TRUE)
funcPath    <- normalizePath(argv$funcpath,  mustWork = TRUE)

functions <- file.path(funcPath, list.files(funcPath, recursive = TRUE))
for (f in functions) source(f)

# ── Chromosome geometry ── CHANGE if you scan different chromosomes ────────────
# These should match what build_chromosome sets for the chr / phase combination.
dataDim     <- c(136, 52)   # rows × cols (X × Y grid points)
chromWidth  <- 1.3           # um
chromHeight <- 3.4           # um

# ── Species lists (mirrors vcell_run_2025.R) ──────────────────────────────────
CPC_species        <- c("CPCa", "pH2A_SGO1_CPCa", "H3_CPCa", "pH3_CPCa", "SGO1_CPCa",
                        "CPCi", "pH2A_SGO1_CPCi", "H3_CPCi", "pH3_CPCi", "SGO1_CPCi")
pH3_species        <- c("pH3", "pH3_CPCa", "pH3_CPCi")
pH2A_species       <- c("pH2A", "pH2A_SGO1", "pH2A_SGO1_CPCa", "pH2A_SGO1_CPCi")
HASPIN_PLK1_species<- c("HASPINa", "HASPINi", "PLK1a", "PLK1i")
BUB1a_pKNL1_species<- c("BUB1a", "pKNL1", "pKNL1_bub1a", "BUB1a_pknl1")
SGO1_species       <- c("SGO1", "pH2A_SGO1", "pH2A_SGO1_CPCi", "pH2A_SGO1_CPCa",
                        "SGO1_CPCi", "SGO1_CPCa")
bound_CPC          <- c("bound_CPC")
bound_active_CPC   <- c("bound_active_CPC")
pNDC80_species     <- c("pNDC80", "pNDC80_TTKi", "pNDC80_pTTKi", "pNDC80_TTKa", "pNDC80_pTTKa")
pNDC80_total       <- c("pNDC80_total")
pH3S10rep          <- c("pH3S10rep")

H <- 7
heatmap_species   <- list(CPC_species, pH3_species, pH2A_species, SGO1_species,
                          bound_CPC, bound_active_CPC, pH3S10rep)
heatmap_info_list <- list("all CPC", "all pH3", "all pH2A", "all SGO1",
                          "all bound CPC", "all bound active CPC", "all pH3S10rep")

L <- 11
all_data <- list(CPC_species, pH3_species, pH2A_species, HASPIN_PLK1_species,
                 BUB1a_pKNL1_species, SGO1_species, bound_CPC, bound_active_CPC,
                 pNDC80_species, pNDC80_total, pH3S10rep)
all_species <- c(CPC_species, pH3_species, pH2A_species, HASPIN_PLK1_species,
                 BUB1a_pKNL1_species, SGO1_species, bound_CPC, bound_active_CPC,
                 pNDC80_species, pNDC80_total, pH3S10rep)

species_info_list <- list(
  c("CPC",             "Inactive CPC",    "Active CPC",    "CPC Activation",  TRUE,  FALSE, FALSE, TRUE),
  c("pH3_species",     "Inactive",        "Active",        "pH3 Species",     FALSE, FALSE, TRUE,  FALSE),
  c("pH2A_species",    "Inactive",        "Active",        "pH2A Species",    FALSE, FALSE, TRUE,  FALSE),
  c("HASPIN_PLK1",     "Inactive",        "Active",        "HASPIN Activ.",   FALSE, FALSE, TRUE,  FALSE),
  c("BUB1a_pKNL1",     "Inactive",        "Active",        "BUB1 recruit.",   FALSE, FALSE, TRUE,  FALSE),
  c("Sgo1",            "Inactive",        "Active",        "SGO1 Species",    FALSE, FALSE, TRUE,  FALSE),
  c("bound_CPC",       "Inactive",        "Active",        "Bound CPC",       FALSE, FALSE, TRUE,  FALSE),
  c("bound_active_CPC","Inactive",        "Active",        "Bound active CPC",FALSE, FALSE, TRUE,  FALSE),
  c("pNDC80_species",  "Inactive",        "Active",        "pNDC80 Species",  FALSE, FALSE, TRUE,  FALSE),
  c("pNDC80_total",    "Inactive",        "Active",        "SUM pNDC80",      FALSE, FALSE, TRUE,  FALSE),
  c("pH3S10rep",       "Inactive",        "Active",        "pH3S10 reporter", FALSE, FALSE, TRUE,  FALSE)
)

# ── Detect SimID and build paths ──────────────────────────────────────────────
sim_id      <- get_sim_id(argv$var, importPath)
importPath_new <- file.path(importPath, argv$var)
exportPath_new <- file.path(importPath, argv$var, "plots")

message("var:        ", argv$var)
message("sim_id:     ", sim_id)
message("importPath: ", importPath_new)
message("exportPath: ", exportPath_new)

# ── Run plots ─────────────────────────────────────────────────────────────────
if (file.exists(importPath_new)) {
  dir.create(exportPath_new, recursive = TRUE, showWarnings = FALSE)

  save_plots(
    sim_id,
    paste(argv$kt_width, "Model"),
    heatmap_species,
    heatmap_info_list,
    all_data,
    all_species,
    species_info_list,
    tInit            = 0,
    tSpan            = 500,
    desiredInterval  = 100,
    alternative_range = c(0, 1, 3, 5, 10, 20),
    cutoff           = list("CPC" = 12),
    funcPath,
    importPath_new,
    exportPath_new,
    argv$kt_width,
    movie            = FALSE,
    lineplots        = TRUE,
    KK_dist_relaxed  = 0.575,
    KK_dist_tensed   = 1.15,
    KT_width         = 0.075,
    KT_height        = 0.3,
    cohesin_width    = 0.1
  )
  message("Plots saved to: ", exportPath_new)
} else {
  stop("Workspace folder not found: ", importPath_new)
}

toc()
