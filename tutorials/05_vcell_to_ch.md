# Module 5: VCell to Cahn-Hilliard Handoff

**Location:** `5_vcell_to_ch/`

## Purpose

The final stage of the pipeline takes the steady-state CPC concentration field from a VCell simulation and uses it as the **initial condition (IC)** for a Cahn-Hilliard (CH) phase-field simulation. The CH model treats the CPC condensate as a phase-separating system and predicts condensate morphology (shape, size, energy) from the VCell-derived protein distribution.

This module has two parts:
1. **`normalize_CPC_modified.py`** — rescales the VCell CPC concentration field to the [-1, +1] range expected by the CH solver and saves it as a CSV initial condition
2. **`generate_plot_pdf/Snakefile`** — orchestrates the CH simulation, analysis, and summary PDF generation using Snakemake

---

## Part 1: Normalizing VCell Output

### Script: `normalize_CPC_modified.py`

#### What it does

The CH solver operates on a field `phi` ∈ [-1, +1], where:
- `phi = +1` represents the condensate-rich phase (high CPC)
- `phi = -1` represents the condensate-poor phase (low CPC)
- `phi = 0` is the spinodal boundary

VCell outputs CPC concentrations in µM (micromolar). The normalization transforms those concentrations into this `phi` space using two parameters:

- **`min_mix`**: the lower concentration threshold (µM). Concentrations below this are set to the background value (`phi ≈ -1` after transformation). Represents the minimum CPC concentration considered "in the condensate" boundary.
- **`rescaling_factor`**: the upper concentration threshold (µM). Corresponds to `phi = +1` (fully condensed phase).

The mapping is:
$$\phi = 2 \cdot \frac{[\text{CPC}]_{\text{sum}} - \text{min\_mix}}{\text{rescaling\_factor} - \text{min\_mix}} - 1$$

Any concentration exactly at zero (background regions) gets set to `phi = 0`.

#### Aggregating CPC species

The VCell model tracks CPC in many biochemical forms (`CPCa`, `CPCi`, `pH2A_SGO1_CPCa`, `pH3_CPCa`, etc.). All CPC-containing species are summed into a single total CPC field before normalization:

$$[\text{CPC}]_{\text{sum}} = \sum_{\text{all CPC forms}} [\text{CPC}_i]$$

In the CSV file output, the species tagged with `CPC_all` (the `_FUNCTION` files from `hdf5_converter.py`) already represent this sum as computed within VCell.

#### Padding to a square grid

The VCell geometry for the metacentric chromosome is **rectangular** (e.g., 144 × 52 grid points). The CH solver requires a **square** domain. The script zero-pads the left and right sides to make the array square:

```
Before:   [144 × 52]
After:    [144 × 144]  (46 columns of zeros added on each side)
```

This places the chromosome cross-section in the center of the square domain, surrounded by zero-concentration background.

#### Output files

Each call to `rescale_vcell_output_neg1_pos1()` saves one CSV to the `IC/` directory:

```
IC/<date>/<species>_<simulation_name>_<timepoint>_<nrows>x<ncols>_<suffix>.csv
```

Example:
```
IC/04_03_2026/CPC_all_03_30_26_metacentric_transition_MCF10A_chr19_PMP1_Gaussian_X_and_Y_KT_Bar_pull_simplified_17_144x144_16max_6.5min.csv
```

The filename encodes: species, simulation, timepoint (17s), grid size (144×144), and the normalization parameters (`16max`, `6.5min`).

### Running the script

Edit the variables at the bottom of `normalize_CPC_modified.py`:

```python
# Paths
in_dir = '/path/to/Box/CPC_Model_Project/VCell_Exports/'
outdir = "/path/to/VCell_Analysis/5_vcell_to_ch/IC/<date>/"

# Simulation folders to aggregate
folder_names = ["SimID_308691339_0__exported"]

# Labels
model_name = ['02_23_26 CPC_metacentric_transition_MCF10A_chr19_PMP1']
simulation_name = ['03_30_26_metacentric_transition_MCF10A_chr19_PMP1_Gaussian_X_and_Y_KT_Bar_pull_simplified']

# Which timepoint to use (seconds)
timepoint = 17   # for transition model; use 100-200 for relaxed/tensed

# Normalization parameters (tune these — see below)
min_mix = 6.5
rescaling_factor = 16.0

# Optionally sweep parameter space:
min_mixes = [5.2, 5.5, 5.7, 6.0, 6.2, 6.5, 7.0]
rescaling_factors = [8.0, 8.4, 8.8, 9.0, 10.0, 11.0, 12.0, 13.0, 14.0, 15.0, 16.0]
```

Then run:
```bash
python normalize_CPC_modified.py
```

### Choosing `min_mix` and `rescaling_factor`

These parameters control whether the CPC concentration field will phase-separate in the CH simulation. The **spinodal point** — the concentration at which phase separation is energetically favorable — for a symmetric double-well potential is:

$$[\text{CPC}]_{\text{spinodal}} = \frac{3 - \sqrt{3}}{6} \cdot (\text{rescaling\_factor} - \text{min\_mix}) + \text{min\_mix}$$

Values above the spinodal → condensed phase (high phi); values below → background phase (low phi).

**Practical guidance:**
- If the entire field ends up as phi ≈ +1 (over-condensed), lower `rescaling_factor` or raise `min_mix`
- If nothing condenses (phi ≈ -1 everywhere), lower `min_mix` or raise `rescaling_factor`
- The typical approach is to do a **parameter sweep** (nested loop over `min_mixes` and `rescaling_factors`) and run the CH Snakemake pipeline for all ICs, then inspect the outputs

---

## Part 2: Cahn-Hilliard Simulation Pipeline (Snakemake)

### Script: `generate_plot_pdf/Snakefile`

The Snakefile orchestrates the full downstream analysis after normalization. It is designed to handle **batches of initial conditions** — one CH simulation per IC CSV — in parallel.

### Prerequisites

- **Snakemake** installed (`pip install snakemake`)
- **MATLAB** installed locally (path set in `MATLAB_BIN`)
- MATLAB Cahn-Hilliard solver functions in `CahnHilliard_MATLAB_solvers/`

### Configuration (top of Snakefile)

```python
FOLDER_NAME = "CPC_all_03_30_26_metacentric_transition_..."  # prefix matching IC files
SIM_SET     = "04_03_2026"                                   # date tag for I/O organization
BASEDIR     = "/path/to/VCell_Analysis/5_vcell_to_ch"

# CH solver parameters
DT      = 2.5e-5    # CH timestep
DT_OUT  = 10        # save every 10 steps
STEPS   = 2000      # total CH iterations (final time = DT * STEPS = 0.05)
epsilon2 = 0.0089**2  # interface width parameter (MCF10A-specific)
```

Update `BASEDIR` and `MATLAB_BIN` for your system before running.

### Snakemake rules

The pipeline has 5 rules that execute in order:

```
IC CSV file
    │
    ▼ rule run_ch_simulation  (MATLAB)
phi.csv + final_phi.csv + movie.mp4
    │
    ├──▼ rule matlab_level_set  (MATLAB)
    │        radius_data.csv
    │
    └──▼ rule python_analysis  (Python)
             analysis_plots.npz
                 │
    ┌────────────┤
    │            │
    ▼            ▼
rule combine_pdfs    rule create_summary_table
<FOLDER>_analysis.pdf   <FOLDER>_summary.csv
```

#### Rule 1: `run_ch_simulation`

Calls the MATLAB function `CahnHilliard_SAV()` (Scalar Auxiliary Variable scheme for energy stability). Inputs: IC CSV. Outputs:

| File | Description |
|------|-------------|
| `{sim}phi.csv` | phi field at every `DT_OUT` step (all timepoints concatenated) |
| `{sim}final_phi.csv` | phi field at the last timepoint only |
| `{sim}movie.mp4` | Animation of phi evolving over time |
| `{sim}mass_uncentered.csv` | Mass conservation diagnostic |
| `{sim}energy.csv` | Total free energy over time |

Key MATLAB parameters passed via the Snakefile:
- `epsilon2`: interface width squared. Smaller = sharper condensate boundary
- `boundary`: `'neumann'` (zero-flux) boundary conditions
- `max_it`: number of CH iterations

#### Rule 2: `matlab_level_set`

Calls `calculate_level_set_radius()` in MATLAB to extract the **condensate radius** over time from the phi field. This measures the size of the high-phi (condensate) region by finding the zero contour of phi and computing the effective radius of the enclosed area.

Output: `{sim}radius_data.csv` — columns: time, radius, area

#### Rule 3: `python_analysis`

Runs `analyze_single_simulation.py` on each completed simulation to compute:
- Radial profiles of phi
- Energy landscape metrics
- Comparison of initial vs. final condensate shape
- Summary plots (saved as `.npz` for later combination)

#### Rule 4: `combine_pdfs`

Gathers all `analysis_plots.npz` files, renders them as pages, and combines into a single PDF in `generate_plot_pdf/summary_output/`.

#### Rule 5: `create_summary_table`

Aggregates `radius_data.csv` files from all simulations into a single summary CSV with one row per simulation, containing final radius, final energy, and other metrics. Useful for comparing across the `min_mix` / `rescaling_factor` parameter sweep.

### Running the pipeline

```bash
cd 5_vcell_to_ch/generate_plot_pdf/

# Dry run to see what will be executed
snakemake -n

# Run with N parallel jobs
snakemake --cores 4

# Force re-run of a specific rule
snakemake --forcerun run_ch_simulation --cores 4
```

Snakemake automatically determines which IC files are new (not yet run) and submits only those jobs, skipping already-completed simulations.

### Output directory structure

```
5_vcell_to_ch/
├── IC/<date>/             # Input: normalized IC CSVs from normalize_CPC_modified.py
├── output/<date>/<FOLDER_NAME>/   # CH simulation outputs (phi.csv, movie.mp4, etc.)
├── int/<date>/<FOLDER_NAME>/      # Intermediate analysis (radius_data.csv, analysis_plots.npz)
└── generate_plot_pdf/
    └── summary_output/
        ├── <FOLDER_NAME>_analysis.pdf   # Combined figure PDF
        └── <FOLDER_NAME>_summary.csv    # Summary table
```

---

## Interpreting CH Outputs

### `phi.csv`

The core output. Each row is a full flattened 2D phi field at one timepoint. Use the grid dimensions (`ny` from the IC file) to reshape:

```python
import numpy as np
phi_all = np.loadtxt("simulation_phi.csv", delimiter=",")
ny = 144  # from IC filename
phi_t = phi_all.reshape(-1, ny, ny)  # shape: (n_timepoints, ny, ny)
```

### `radius_data.csv`

Contains the condensate radius as a function of CH time. A stable, non-zero radius indicates a persistent condensate. A radius that goes to zero indicates the condensate dissolved (IC was below the spinodal for this parameter set).

### `energy.csv`

The CH free energy (Ginzburg-Landau functional). Should decrease monotonically for a correctly behaved simulation. Non-monotonic energy may indicate too large a timestep (decrease `DT`).

### `_analysis.pdf`

Contains:
- Final phi field heatmap
- Phi profile along the chromosome axis
- Radius vs. time plot
- Energy vs. time plot

Comparing this PDF across simulations in the parameter sweep reveals which `min_mix`/`rescaling_factor` combinations produce condensates consistent with experimental CPC localization patterns.
