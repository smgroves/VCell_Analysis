# VCell_Analysis

**Note: All code was written by humans. Claude was used to generate READMEs and tutorials for general use.**

Computational pipeline for studying **inner centromeric condensate dynamics** during mitosis, with a focus on the Chromosomal Passenger Complex (CPC). The pipeline integrates multi-source RNA-seq data, reaction-diffusion PDE simulations in VCell, and Cahn-Hilliard phase-field modeling to study how CPC localizes to and is maintained at the inner centromere.

## Pipeline Overview

```
RNA-seq (TCGA / MCF10A / TNBC)
    → [1] Preprocessing & clustering
    → [2] RNA-to-protein inference
    → [3] VCell PDE simulations  (3a: validation | 3b: HPC | 3c: PyVCell)
    → [4] Post-simulation analysis (HDF5 → CSV → R visualizations)
    → [5] Cahn-Hilliard phase-field modeling (normalization + Snakemake)
```

## Tutorials

Step-by-step annotated walkthroughs are in the [`tutorials/`](tutorials/) folder:

| Tutorial | Format | Description |
|----------|--------|-------------|
| [00 — Overview](tutorials/00_overview.md) | Markdown | Project background, pipeline diagram, environment setup |
| [01 — RNA Analysis](tutorials/01_rna_analysis.ipynb) | Notebook | TPM normalization, PCA, hierarchical clustering of RNA-seq data |
| [02 — RNA to Protein](tutorials/02_rna_to_protein.md) | Markdown | CSN inference model; setting VCell initial conditions |
| [03a — VCell Validation](tutorials/03a_vcell_gui_validation.md) | Markdown | Mass conservation checks before running production simulations |
| [03b — HPC/SLURM](tutorials/03b_hpc_vcell.md) | Markdown | Running VCell on Rivanna via Singularity containers |
| [03c — PyVCell](tutorials/03c_pyvcell.ipynb) | Notebook | Running VCell locally with the Python API |
| [04 — Post-Processing](tutorials/04_post_processing.md) | Markdown | HDF5 → CSV conversion; R heatmaps, line plots, and movies |
| [05 — VCell to Cahn-Hilliard](tutorials/05_vcell_to_ch.md) | Markdown | CPC normalization and Snakemake-driven CH simulation pipeline |

**Start here:** [tutorials/00_overview.md](tutorials/00_overview.md)

## Environment Setup

```bash
# Python
conda env create -f py_environment.yml
conda activate VCell_Analysis

# R packages
# See tutorials/00_overview.md for the full install command
```

## Repository Structure

```
VCell_Analysis/
├── tutorials/               ← Start here
├── 1_rna_analysis/          ← RNA-seq preprocessing
├── 2_rna_to_protein/        ← CSN protein inference
├── 3a_VCell_GUI/            ← Mass conservation validation
├── 3b_cli_VCell/            ← SLURM scripts for HPC
├── 3c_run_pyvcell/          ← PyVCell Python API
├── 4_post_VCell_processing/ ← HDF5 conversion + R visualization
├── 5_vcell_to_ch/           ← Normalization + Cahn-Hilliard pipeline
├── functions/               ← Shared R utilities
├── functions_SG/            ← Extended R function library
├── vcell_models/            ← VCML model files
└── vcell_out/               ← Simulation outputs
```
