# Module 2: RNA-to-Protein Inference

**Location:** `2_rna_to_protein/`

## Purpose

VCell reaction-diffusion simulations require **initial protein concentrations** and **kinetic parameters** for each molecular species in the model. While transcriptomic data (Module 1) gives us relative mRNA levels across cell types, mRNA abundance does not directly equal protein abundance due to post-transcriptional regulation, translation efficiency, and protein turnover.

This module uses a **Context-Specific Network (CSN) inference approach** (from Kevin's lab) to estimate relative protein abundances from RNA-seq data by calibrating against available proteomics datasets.

---

## Data Sources

### Proteomics references

| File | Description |
|------|-------------|
| `CCLE_Protein.xlsx` | CCLE protein abundance across cancer cell lines (TMT-MS/MS) |
| `TableS2_MouseRefSWATH.xlsx` | Mouse reference proteome (SWATH-MS) |
| `Hela_selected_genes_Proteomics.csv` | HeLa cell proteomics for CPC network genes |
| `bc_CCLE_TMT_model_proteins.csv` | Breast cancer CCLE protein subset |

### RNA-seq input

The combined normalized RNA-seq table from Module 1:
`1_rna_analysis/data/rnaseq_network_genes_TCGA_MCF10A_CCLE_ZHAO_for_pinferna.csv`

---

## CSN Inference Model

The core inference is implemented in MATLAB:

- `CSN_Inference_Model_from_Kevin/CSN_Inference_Comparison.m`
- `CSN_Inference_Model_from_Kevin/CSN_Inference_Comparison_original.m`

### Conceptual approach

The CSN model addresses the **RNA-to-protein translation problem** by:

1. Starting with mRNA expression levels for each network gene across multiple samples
2. Using a reference proteomics dataset to learn the scaling relationship between RNA and protein for each gene
3. Predicting protein abundances in samples where only RNA-seq data is available (e.g., MCF10A)

This is particularly important for the CPC network because several subunits (AURKB, INCENP, BIRC5) are known to be regulated post-transcriptionally during mitosis.

### MATLAB script workflow (`CSN_Inference_Comparison.m`)

```matlab
% 1. Load RNA-seq data (from Module 1 output)
rna_data = readtable('rnaseq_network_genes_TCGA_MCF10A_CCLE_ZHAO_for_pinferna.csv');

% 2. Load proteomics reference
protein_ref = readtable('CCLE_Protein.xlsx');

% 3. Intersect genes and samples present in both datasets
% (only genes with both RNA and protein measurements can be calibrated)

% 4. Fit a linear model per gene: protein ~ alpha * RNA + beta
% alpha = translation efficiency scaling factor
% beta  = basal protein level independent of mRNA

% 5. Apply fitted models to predict protein abundance in MCF10A
% These predictions become initial conditions in the VCell model
```

---

## Fold-Enrichment Analysis

`CSN_Inference_Model_from_Kevin/fold-enrichment.xlsx` and the R script `functions_SG/fold_enrich.R` contain fold-enrichment calculations comparing:

- CPC network gene expression in TNBC vs. normal breast tissue
- Active vs. inactive kinase/phosphatase ratios

These fold-enrichment values are used to:
- Validate that modeled protein ratios are biologically reasonable
- Set relative concentrations when absolute proteomics data is unavailable

---

## How Protein Abundances Enter VCell

After inference, the estimated protein concentrations (in µM or relative units) are manually entered into the VCell model as **initial conditions** for each molecular species. In the VCML files (`vcell_models/vcml/`), look for the `<InitialCondition>` elements for each species in the `MathDescription`.

Key species with fitted initial conditions:
- `CPCa`, `CPCi` — active/inactive CPC
- `HASPINa`, `HASPINi` — HASPIN kinase (phosphorylates H3T3)
- `PLK1a`, `PLK1i` — PLK1 (phosphorylates HASPIN)
- `TTKa`, `TTKi` — TTK/Mps1 (error-correction kinase)
- `BUB1a` — BUB1 (phosphorylates H2A)
- `NDC80` — NDC80 kinetochore complex

---

## Practical Notes

- The MATLAB scripts require access to the large proteomics Excel files. If running for the first time, ensure the CCLE protein file (~60 MB) is downloaded and the path is updated in the script.
- The key output of this module is not a file but a set of **numerical values** that are transcribed into the VCell VCML model. Check the model file comments for which version of the inference was used.
- The `breast_subset_TCGA_log2TPM.csv` in `2_rna_to_protein/` is an intermediate table used to compare TCGA expression against CCLE prior to protein inference.
