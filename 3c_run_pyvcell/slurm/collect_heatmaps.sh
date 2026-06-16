#!/usr/bin/env bash
# collect_heatmaps.sh  — SLURM collect job
# Runs after all array tasks succeed (--dependency=afterok).
# Reads params.tsv to reconstruct folder names, then calls the R
# collect_plots() function to assemble:
#   1. bound-CPC heatmaps (all scan points, relaxed + tensed)
#   2. CPC activation heatmaps
#   3. CPC line plots
# All PDFs land in  workspace/scan_results/
#SBATCH --nodes=1
#SBATCH --ntasks=1

# Env vars injected by submit_scan.sh:
#   REPO_DIR, CONDA_ENV, R_MODULE, PARAMS_FILE, CHR, PHASE, KT_LOC, RUN_PREFIX

set -euo pipefail

echo "=== collect_heatmaps  $(date) ==="

module purge
module load "$R_MODULE"

WORKSPACE="${REPO_DIR}/workspace"
FUNCPATH="${REPO_DIR}/functions_2026"
OUT_DIR="${WORKSPACE}/scan_results"
mkdir -p "$OUT_DIR"

# ── Build the list of workspace folder names from params.tsv ─────────────────
# Skip the header line; for each row: col3=p1_val col5=p2_val col2=p1_name col4=p2_name
RELAXED_FOLDERS=()
TENSED_FOLDERS=()

while IFS=$'\t' read -r idx p1_name p1_val p2_name p2_val; do
    [[ "$idx" == "idx" ]] && continue          # skip header
    P1_TAG=$(printf "%g" "$p1_val")
    P2_TAG=$(printf "%g" "$p2_val")
    RELAXED_FOLDERS+=("${RUN_PREFIX}_relaxed_MCF10A_${CHR}_${PHASE}_${p1_name}${P1_TAG}_${p2_name}${P2_TAG}")
    TENSED_FOLDERS+=("${RUN_PREFIX}_tensed_MCF10A_${CHR}_${PHASE}_${p1_name}${P1_TAG}_${p2_name}${P2_TAG}")
done < "$PARAMS_FILE"

N_RELAXED=${#RELAXED_FOLDERS[@]}
N_TENSED=${#TENSED_FOLDERS[@]}
echo "Collecting ${N_RELAXED} relaxed + ${N_TENSED} tensed folders"

# ── Helper: build a comma-separated R character vector literal ────────────────
to_r_vector () {
    local -a arr=("$@")
    local r_vec="c("
    for name in "${arr[@]}"; do
        r_vec+="\"${name}\","
    done
    r_vec="${r_vec%,})"   # strip trailing comma
    echo "$r_vec"
}

RELAXED_R=$(to_r_vector "${RELAXED_FOLDERS[@]}")
TENSED_R=$(to_r_vector  "${TENSED_FOLDERS[@]}")
ALL_R=$(to_r_vector "${RELAXED_FOLDERS[@]}" "${TENSED_FOLDERS[@]}")

# ── Call collect_plots for each plot type ─────────────────────────────────────
Rscript - << RSCRIPT
suppressPackageStartupMessages({
  library(pdftools)
  library(png)
  library(grid)
})

funcPath <- "${FUNCPATH}"
functions <- file.path(funcPath, list.files(funcPath, recursive = TRUE))
for (f in functions) source(f)

workspace  <- "${WORKSPACE}"
out_dir    <- "${OUT_DIR}"

relaxed_folders <- ${RELAXED_R}
tensed_folders  <- ${TENSED_R}
all_folders     <- ${ALL_R}

# ── Relaxed: bound-CPC heatmap ────────────────────────────────────────────────
message("Collecting relaxed bound-CPC heatmaps...")
collect_plots(
  plot_name      = "all bound CPC_heatmap",
  var            = relaxed_folders,
  workspace_path = workspace,
  output_path    = out_dir,
  output_name    = "relaxed_bound_CPC_heatmap_scan"
)

# ── Tensed: bound-CPC heatmap ─────────────────────────────────────────────────
message("Collecting tensed bound-CPC heatmaps...")
collect_plots(
  plot_name      = "all bound CPC_heatmap",
  var            = tensed_folders,
  workspace_path = workspace,
  output_path    = out_dir,
  output_name    = "tensed_bound_CPC_heatmap_scan"
)

# ── Relaxed: total CPC heatmap ────────────────────────────────────────────────
message("Collecting relaxed total CPC heatmaps...")
collect_plots(
  plot_name      = "all CPC_heatmap",
  var            = relaxed_folders,
  workspace_path = workspace,
  output_path    = out_dir,
  output_name    = "relaxed_CPC_heatmap_scan"
)

# ── Tensed: total CPC heatmap ─────────────────────────────────────────────────
message("Collecting tensed total CPC heatmaps...")
collect_plots(
  plot_name      = "all CPC_heatmap",
  var            = tensed_folders,
  workspace_path = workspace,
  output_path    = out_dir,
  output_name    = "tensed_CPC_heatmap_scan"
)

# ── CPC line plots (relaxed + tensed together) ────────────────────────────────
message("Collecting CPC line plots...")
collect_plots(
  plot_name      = "CPC_plot",
  var            = all_folders,
  workspace_path = workspace,
  output_path    = out_dir,
  output_name    = "CPC_lineplot_scan"
)

message("All PDFs saved to: ${OUT_DIR}")
RSCRIPT

echo "=== collect_heatmaps done  $(date) ==="
echo "Output PDFs:"
ls -lh "${OUT_DIR}"/*.pdf 2>/dev/null || echo "  (none found)"
