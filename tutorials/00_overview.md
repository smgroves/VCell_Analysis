# VCell_Analysis Pipeline Overview

## Biological Context

This repository supports a computational study of **inner centromeric condensate dynamics** during mitosis, focusing on the **Chromosomal Passenger Complex (CPC)** — a key regulator of chromosome alignment and error correction at the kinetochore. The CPC (comprising AURKB, INCENP, CDCA8/Borealin, and BIRC5/Survivin) localizes to the inner centromere during mitosis and phosphorylates multiple substrates including Histone H3 (pH3), Histone H2A (pH2A), NDC80, and KNL1.

The central question is: **how does the spatial distribution of CPC and its regulatory network produce robust, condensate-like enrichment at the inner centromere, and how does this change as chromosomes transition from a relaxed (no tension) to tensed (bi-oriented, pulling) state?**

The pipeline integrates:
1. Multi-source RNA-seq data to set protein abundance levels
2. Reaction-diffusion PDE simulations in VCell to model molecular dynamics
3. Cahn-Hilliard phase-field modeling to study condensate behavior

---

## Pipeline Architecture

```
RNA-seq data (TCGA, MCF10A, TNBC)
        |
        v
[Module 1] RNA preprocessing & clustering
   - TPM normalization, PCA, hierarchical clustering
   - Outputs: normalized expression tables for network inference
        |
        v
[Module 2] RNA-to-protein inference (CSN model)
   - Translates mRNA levels to relative protein abundances
   - Outputs: protein abundance estimates used as VCell ICs
        |
        v
[Module 3a] VCell model validation (mass conservation)
   - Verifies biochemical reaction network before running
        |
        v
[Module 3b/3c] VCell simulation execution
   - 3b: HPC/SLURM execution via Singularity container
   - 3c: Local execution via PyVCell Python API
   - Outputs: HDF5 files with 2D spatiotemporal concentration fields
        |
        v
[Module 4] Post-VCell processing
   - HDF5 -> CSV conversion (Python)
   - Visualization: heatmaps, line plots, movies (R)
        |
        v
[Module 5] VCell -> Cahn-Hilliard handoff
   - Normalize CPC concentration fields to [-1, +1]
   - Run Cahn-Hilliard simulations (MATLAB) via Snakemake
   - Analyze condensate morphology (radius, energy, mass)
```

---

## Directory Structure

```
VCell_Analysis/
├── 1_rna_analysis/          # RNA-seq preprocessing and PCA/clustering
│   ├── preprocessing_zhao.py
│   ├── rnaseq_clustering.py
│   └── data/
├── 2_rna_to_protein/        # CSN-based RNA-to-protein inference
│   └── CSN_Inference_Model_from_Kevin/
├── 3a_VCell_GUI/            # Mass conservation validation scripts
├── 3b_cli_VCell/            # SLURM scripts for HPC execution
├── 3c_run_pyvcell/          # Python API for local VCell execution
├── 4_post_VCell_processing/ # HDF5 conversion + R visualization pipeline
│   ├── hdf5_converter.py
│   ├── vcell_run_2025.R
│   └── full_run_local.sh
├── 5_vcell_to_ch/           # Normalization + Cahn-Hilliard Snakemake pipeline
│   ├── normalize_CPC_modified.py
│   └── generate_plot_pdf/
│       ├── Snakefile
│       └── analyze_single_simulation.py
├── functions/               # Shared R utility functions
├── functions_SG/            # Extended R function library
├── vcell_models/            # VCML model files
│   └── vcml/
├── vcell_out/               # VCell simulation outputs (HDF5/CSV)
├── plotting_functions/      # Standalone plotting scripts
├── protein_abundance/       # Protein abundance data
└── image_analysis/          # Cell size metrics from Volocity
```

---

## VCell Model Overview

The core VCell models (`vcell_models/vcml/`) describe the CPC regulatory network as a **2D reaction-diffusion PDE system** on a rectangular domain representing a chromosome cross-section. Key features:

- **Geometry**: Metacentric chromosome (144 × 52 grid points, ~1.3 µm × 3.6 µm)
- **Three model states**:
  - **Relaxed**: no kinetochore pulling force; CPC concentrated at inner centromere
  - **Tensed**: kinetochore pulling force applied; chromosome under tension
  - **Transition**: models the relaxed-to-tensed switch
- **Key molecular species** (~40 total):
  - CPC forms: `CPCa` (active), `CPCi` (inactive), and complexes with pH2A, pH3, SGO1
  - NDC80 forms: `NDC80`, `pNDC80` and TTK-bound variants
  - Kinase/phosphatase states: `HASPINa/i`, `PLK1a/i`, `TTKa/i`, `BUB1a`
  - Histone marks: `pH2A`, `pH3`, `SGO1` and complexes

---

## Environment Setup

### Python environment

Install from the provided conda environment file:

```bash
conda env create -f py_environment.yml
conda activate VCell_Analysis
```

Key Python packages: `pandas`, `numpy`, `scipy`, `scikit-learn`, `matplotlib`, `seaborn`, `h5py`, `pyvcell`

### R environment

Required packages (install in R):
```r
install.packages(c("ggplot2", "ggrastr", "gridExtra", "purrr", "latex2exp",
                   "stringr", "lemon", "tictoc", "tidyverse", "tibble",
                   "scales", "xlsx", "pdftools"))
# Bioconductor
BiocManager::install("rhdf5")
```

### Path conventions

Most scripts use hardcoded absolute paths (e.g., `importPath`, `exportPath`). These should be updated to match your local setup or Box sync location at the top of each script before running.

---

## Tutorial Index

| Tutorial | Format | Description |
|----------|--------|-------------|
| [01_rna_analysis.ipynb](01_rna_analysis.ipynb) | Notebook | RNA-seq preprocessing, PCA, clustering |
| [02_rna_to_protein.md](02_rna_to_protein.md) | Markdown | RNA-to-protein inference with CSN model |
| [03a_vcell_gui_validation.md](03a_vcell_gui_validation.md) | Markdown | VCell model mass conservation checks |
| [03b_hpc_vcell.md](03b_hpc_vcell.md) | Markdown | Running VCell on HPC via SLURM |
| [03c_pyvcell.ipynb](03c_pyvcell.ipynb) | Notebook | Running VCell locally with PyVCell |
| [04_post_processing.md](04_post_processing.md) | Markdown | HDF5 conversion and R visualization |
| [05_vcell_to_ch.md](05_vcell_to_ch.md) | Markdown | Normalization and Cahn-Hilliard pipeline |
