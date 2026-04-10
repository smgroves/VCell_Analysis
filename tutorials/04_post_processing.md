# Module 4: Post-VCell Processing

**Location:** `4_post_VCell_processing/`

## Purpose

After a VCell simulation completes, the raw output is an HDF5 file containing 3D arrays (X × Y × T) for each molecular species. This module converts that output into analysis-ready CSVs and generates the standard set of visualizations: spatial heatmaps, line plots at key positions, and movies.

The module has two stages:
1. **Python:** `hdf5_converter.py` — extract per-species, per-timepoint 2D slices as CSV files
2. **R:** `vcell_run_2025.R` + function library in `functions_SG/` — visualize and summarize

---

## Stage 1: HDF5 to CSV Conversion (Python)

### Script: `hdf5_converter.py`

VCell exports simulation data in HDF5 format. The internal structure is:

```
reports.h5
└── [SimID_XXXXXXXXX, 0]    ← simulation key (ID + replicate)
    ├── TIMES               ← array of timepoints (seconds)
    ├── CPCa
    │   └── DataValues (XYT)   ← 3D array: shape (nX, nY, nT)
    ├── CPCi
    │   └── DataValues (XYT)
    ├── pH3
    │   └── DataValues (XYT)
    └── ...  (one entry per species)
```

`hdf5_converter.py` reads this structure and writes one CSV per (species, timepoint) combination.

### Command-line usage

```bash
python hdf5_converter.py \
    <file_name>          \   # e.g., "SimID_296945372_0__exported.hdf5"
    <dir_path>           \   # directory containing the HDF5 file
    <model_name>         \   # human-readable model label (goes in CSV header)
    <simulation_name>        # human-readable sim label (goes in CSV header)
```

**Example:**
```bash
python hdf5_converter.py \
    "SimID_296945372_0__exported.hdf5" \
    "/path/to/Box/CPC_Model_Project/VCell_Exports" \
    "_09_16_25_CPC_metacentric_relaxed_model" \
    "09_16_25_metacentric_relaxed_model"
```

To extract only specific species (faster for large files):
```bash
python hdf5_converter.py \
    "SimID_296945372_0__exported.hdf5" \
    "/path/to/Box/CPC_Model_Project/VCell_Exports" \
    "model_name" \
    "sim_name" \
    --species CPCa CPCi pH3 pNDC80
```

### Output structure

The script creates a folder named `SimID_XXXXXXXXX_0__exported/` in `dir_path`, containing one CSV per species per timepoint:

```
SimID_296945372_0__exported/
├── SimID_296945372_0__Slice_XY_0_CPCa_0000.csv     ← CPCa at t=0
├── SimID_296945372_0__Slice_XY_0_CPCa_0001.csv     ← CPCa at t=10s
├── SimID_296945372_0__Slice_XY_0_CPCa_0002.csv     ← CPCa at t=20s
├── ...
├── SimID_296945372_0__Slice_XY_0_CPCi_0000.csv
├── ...
└── SimID_296945372_0__Slice_XY_0_CPC_all_FUNCTION_0000.csv   ← computed sum
```

**CSV format:** Each file has a 10-line header with metadata (model name, simulation name, timepoint, variable name), followed by the 2D concentration matrix (X rows × Y columns, no index or column headers).

```
Model: _09_16_25_CPC_metacentric_relaxed_model
Simulation: 09_16_25_metacentric_relaxed_model
(SimID_296945372_0 (PDE Simulation))
Sim time range (0.0 500.0) (saved timepoints 51)
Number of variables 48
...
2D Slice for variable CPCa at time 0.0 in plane XY at Z = 0

X in rows, Y in columns

1.23,1.45,1.67,...
...
```

### Default species list

If no `--species` argument is given, the converter extracts these ~48 species:

**State variables:** `BUB1a`, `BUB1a_his`, `BUB1a_pKNL1`, `CPCa`, `CPCi`, `H2A`, `H3`, `H3_CPCa`, `H3_CPCi`, `HASPINa`, `HASPINi`, `I`, `KNL1`, `NDC80`, `NDC80_TTKa/i`, `NDC80_pTTKa/i`, `pH2A`, `pH2A_SGO1`, `pH2A_SGO1_CPCa/i`, `pH3`, `pH3_CPCa/i`, `pKNL1`, `PLK1a/i`, `pTTKa/i`, `pNDC80` and NDC80 phosphoforms, `SGO1` and complexes, `TTKa/i`

**Computed functions** (marked `_FUNCTION` in filename): `CPC_all`, `CPCi_total`, `CPCa_total`, `pH2_all`, `bound_CPC`, `bound_active_CPC`, `boundactive_CPC_pNDC80`

### HPC variant

`hdf5_converter_Rivanna.py` handles the slightly different directory structure produced by the VCell CLI on Rivanna, where the HDF5 file is named `reports.h5` and sits directly in the output directory.

---

## Stage 2: Visualization with R

### Script: `vcell_run_2025.R`

This is the main R analysis script. It sources all functions from `functions_SG/` and orchestrates heatmap and line plot generation.

### Setup: Paths

At the top of the script, update these four paths:

```r
funcPath   <- "/path/to/VCell_Analysis/functions"          # R function library
importPath <- "/path/to/Box/VCell_Exports"                 # folder containing SimID_*/ directories
exportPath <- "/path/to/Box/vcell_plots"                   # where output figures go
```

### Setup: Geometry parameters

The chromosome geometry parameters must match the model that was simulated:

```r
# Metacentric chromosome (standard model):
dataDim    <- c(144, 52)    # grid points (X, Y)
chromWidth <- 1.3           # µm (Y dimension)
chromHeight <- 3.6          # µm (X dimension)
```

### Configuring species groups

Species are organized into named groups for plotting. Each group generates one heatmap and one set of line plots. Edit these lists to add/remove species:

```r
CPC_species      <- c("CPCa", "pH2A_SGO1_CPCa", "H3_CPCa", "pH3_CPCa",
                       "SGO1_CPCa", "CPCi", "pH2A_SGO1_CPCi", "H3_CPCi",
                       "pH3_CPCi", "SGO1_CPCi")

pNDC80_species   <- c("pNDC80_TTKa", "pNDC80_pTTKa", "pNDC80_TTKi", "pNDC80_pTTKi")

# Other groups: pH3_species, pH2A_species, HASPIN_PLK1_species,
#               BUB1a_pKNL1_species, SGO1_species, bound_CPC, bound_active_CPC
```

To generate plots for additional groups, uncomment the corresponding lines in the `heatmap_species` and `all_data` sections.

### Specifying simulations to analyze

```r
# Model geometry type label (used in plot titles and file names)
kt_width <- c("Metacentric_Relaxed")

# SimID folder names (from hdf5_converter.py output)
sims <- c("SimID_296945372_0__exported")

# Human-readable label for this simulation (used in plot titles)
var <- c("09_16_25 CPC_metacentric_relaxed_model")
```

Multiple simulations can be analyzed in a loop by adding entries to each vector.

### Key function: `save_plots()`

`save_plots()` (defined in `functions_SG/save_plots.R`) is the main workhorse. Key arguments:

| Argument | Description |
|----------|-------------|
| `sims[i]` | SimID folder name |
| `kt_width[i]` | Model label for plot annotations |
| `heatmap_species` | List of species groups for heatmaps |
| `tInit`, `tSpan` | Time range to plot (seconds) |
| `desiredInterval` | Timepoints to include (every N seconds) |
| `cutoff` | Color scale maximum for each species group (e.g., `list("CPC"=11)`) |
| `KK_dist_relaxed` | Inner kinetochore position from centromere (µm); relaxed = 0.575 µm |
| `KK_dist_tensed` | Tensed state kinetochore position = 1.15 µm |
| `KT_width` | Kinetochore width (µm) = 0.075 |
| `KT_height` | Kinetochore height (µm) = 0.3 |
| `movie` | `TRUE` to generate animated heatmap movie |
| `lineplots` | `TRUE` to generate temporal line plots |

### Running the script

```bash
Rscript vcell_run_2025.R
```

Or source interactively in RStudio.

### Output

All plots are saved to `exportPath/<var>/`:

| File pattern | Description |
|-------------|-------------|
| `*_heatmap_*.pdf` | Spatial heatmap at each timepoint |
| `*_lineplot_*.pdf` | Temporal line plots at centromere vs. kinetochore |
| `*_movie_*.mp4` | Animated heatmap time-lapse (if `movie=TRUE`) |
| `*_slides_*.pdf` | Combined PDF slide deck |

---

## Running the full pipeline locally

`full_run_local.sh` wraps both stages for a local run:

```bash
cd 4_post_VCell_processing/
# Update MODEL_NAME and OUTPUT path in the script, then:
bash full_run_local.sh
```

This runs `hdf5_converter_Rivanna.py` on the output directory, then calls `vcell_run_v3_CL.R` (the command-line argument version of the R script) for each simulation subdirectory.

---

## R function library overview (`functions_SG/`)

| File | Role |
|------|------|
| `vcell_process_v2.R` | Reads CSV files, reshapes to long format, joins geometry info |
| `vcell_heatmap.R` | Generates 2D spatial heatmaps with kinetochore/centromere annotations |
| `vcell_plots_WORKING.R` | Line plots of concentration vs. time at specific spatial positions |
| `vcell_analyze.R` | Summary statistics and position-specific metrics |
| `all_plot.R` | Multi-panel figure assembly |
| `save_plots.R` | Orchestrates the full plot generation workflow |
| `heatmap_movie.R` | Assembles PNG frames into `.mp4` movies |
| `kin_conc_rect.R` | Computes concentration integrals over rectangular kinetochore region |
| `fold_enrich.R` | Fold-enrichment of CPC at centromere vs. arms |
| `Trap.R`, `SimpInt.R` | Numerical integration (trapezoidal, Simpson's rule) |
