#!/usr/bin/env bash
# sim_worker.sh  — SLURM array-job worker
# Runs one (param1, param2) combination:
#   1. Python: build relaxed model, set params, simulate, export CSVs
#   2. Python: build tensed model from relaxed result, simulate, export CSVs
#   3. R:      generate plots for both workspace folders
#
# Env vars injected by submit_scan.sh via --export:
#   REPO_DIR, CONDA_ENV, R_MODULE, PARAMS_FILE, VCML_FILE
#   CHR, PHASE, KT_LOC, RUN_PREFIX
#SBATCH --nodes=1
#SBATCH --ntasks=1

set -euo pipefail

echo "=== sim_worker  SLURM_ARRAY_TASK_ID=${SLURM_ARRAY_TASK_ID}  $(date) ==="

# ── Read this job's parameters from the TSV (skip header, pick row by index) ──
IDX=${SLURM_ARRAY_TASK_ID}
PARAMS_ROW=$(awk -v i="$IDX" 'NR == i+1' "$PARAMS_FILE")   # row 1 = first combo

P1_NAME=$(echo "$PARAMS_ROW" | awk '{print $2}')
P1_VAL=$(echo  "$PARAMS_ROW" | awk '{print $3}')
P2_NAME=$(echo "$PARAMS_ROW" | awk '{print $4}')
P2_VAL=$(echo  "$PARAMS_ROW" | awk '{print $5}')

# Use %g to strip trailing zeros: 1.0→1, 0.50→0.5, 5.40→5.4
P1_TAG=$(printf "%g" "$P1_VAL")
P2_TAG=$(printf "%g" "$P2_VAL")

echo "Parameters: ${P1_NAME}=${P1_VAL}  ${P2_NAME}=${P2_VAL}"

# ── Construct deterministic run names (same formula used in Python script) ────
RELAXED_RUN="${RUN_PREFIX}_relaxed_MCF10A_${CHR}_${PHASE}_${P1_NAME}${P1_TAG}_${P2_NAME}${P2_TAG}"
TENSED_RUN="${RUN_PREFIX}_tensed_MCF10A_${CHR}_${PHASE}_${P1_NAME}${P1_TAG}_${P2_NAME}${P2_TAG}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE="${REPO_DIR}/workspace"

# ── Activate conda environment ────────────────────────────────────────────────
module purge
module load miniforge
# shellcheck source=/dev/null
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate "$CONDA_ENV"

# ── Run simulation + CSV export ───────────────────────────────────────────────
echo "--- Python simulation  $(date) ---"
python "${SCRIPT_DIR}/run_single_param.py" \
    --vcml_file        "$VCML_FILE" \
    --chr              "$CHR" \
    --phase            "$PHASE" \
    --kt_loc           "$KT_LOC" \
    --param1_name      "$P1_NAME" \
    --param1_val       "$P1_VAL" \
    --param2_name      "$P2_NAME" \
    --param2_val       "$P2_VAL" \
    --run_name_relaxed "$RELAXED_RUN" \
    --run_name_tensed  "$TENSED_RUN" \
    --workspace        "$WORKSPACE"

echo "--- Simulation complete  $(date) ---"

# ── Generate plots with R ─────────────────────────────────────────────────────
echo "--- R plots  $(date) ---"
module load "$R_MODULE"

Rscript "${SCRIPT_DIR}/plot_single_sim.R" \
    --workspace "$WORKSPACE" \
    --var       "$RELAXED_RUN" \
    --kt_width  "Metacentric_Relaxed" \
    --funcpath  "${REPO_DIR}/functions_2026" \
    --chr       "$CHR" \
    --phase     "$PHASE"

Rscript "${SCRIPT_DIR}/plot_single_sim.R" \
    --workspace "$WORKSPACE" \
    --var       "$TENSED_RUN" \
    --kt_width  "Metacentric_Tensed" \
    --funcpath  "${REPO_DIR}/functions_2026" \
    --chr       "$CHR" \
    --phase     "$PHASE"

echo "=== sim_worker done  $(date) ==="
