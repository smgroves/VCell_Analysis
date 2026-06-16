#!/usr/bin/env bash
# submit_scan.sh
# Submits a 2-D parameter scan as a SLURM array job, then a dependent
# collect job that assembles the bound-CPC heatmaps into one PDF.
#
# Usage:  bash submit_scan.sh
# Adjust the CHANGE sections below; everything else should be portable.

set -euo pipefail

# ══════════════════════════════════════════════════════════════════════════════
# CHANGE: paths
# ══════════════════════════════════════════════════════════════════════════════
REPO_DIR="/project/YOUR_GROUP/YOUR_USERNAME/VCell_Analysis"   # absolute path on cluster
CONDA_ENV="vcell"                                              # conda env with pyvcell + pandas + zarr
R_MODULE="R/4.3.1"                                            # module name for R on the cluster

VCML_FILE="${REPO_DIR}/vcell_models/vcml/_005_20_26_CPC_metacentric_relaxed_MCF10A_chr19_PMP1.vcml"

CHR="chr19"
PHASE="PMP1"
KT_LOC="metacentric"
RUN_PREFIX="_005_20_26_CPC_${KT_LOC}"    # prepended to every run folder name

# ══════════════════════════════════════════════════════════════════════════════
# CHANGE: parameters to scan
# ══════════════════════════════════════════════════════════════════════════════
PARAM1_NAME="kbind"
PARAM1_VALUES=(0.1 0.5 1.0 5.0 10.0)

PARAM2_NAME="KmTTK"
PARAM2_VALUES=(1.0 2.7 5.4 10.0)

# ══════════════════════════════════════════════════════════════════════════════
# CHANGE: SLURM resource requests
# ══════════════════════════════════════════════════════════════════════════════
PARTITION="standard"
SIM_TIME="4:00:00"     # wall time per simulation job (relax + tense sequentially)
SIM_MEM="16G"
SIM_CPUS=4

COLLECT_TIME="1:00:00"
COLLECT_MEM="8G"

# ══════════════════════════════════════════════════════════════════════════════
# Derived paths (no changes needed below this line)
# ══════════════════════════════════════════════════════════════════════════════
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PARAMS_FILE="${SCRIPT_DIR}/params.tsv"
LOG_DIR="${SCRIPT_DIR}/logs"
mkdir -p "$LOG_DIR"

# ── Build the params.tsv (one row per (p1, p2) combination) ──────────────────
printf "idx\tp1_name\tp1_val\tp2_name\tp2_val\n" > "$PARAMS_FILE"
idx=1
for p1 in "${PARAM1_VALUES[@]}"; do
    for p2 in "${PARAM2_VALUES[@]}"; do
        printf "%d\t%s\t%s\t%s\t%s\n" "$idx" "$PARAM1_NAME" "$p1" "$PARAM2_NAME" "$p2" >> "$PARAMS_FILE"
        ((idx++))
    done
done
N=$((idx - 1))
echo "Generated ${N} parameter combinations → ${PARAMS_FILE}"

# ── Submit simulation array job ───────────────────────────────────────────────
ARRAY_JOB_OUT=$(sbatch \
    --partition="${PARTITION}" \
    --time="${SIM_TIME}" \
    --mem="${SIM_MEM}" \
    --cpus-per-task="${SIM_CPUS}" \
    --nodes=1 \
    --ntasks=1 \
    --array="1-${N}%20" \
    --job-name="vcell_scan" \
    --output="${LOG_DIR}/scan_%A_%a.out" \
    --error="${LOG_DIR}/scan_%A_%a.err" \
    --export="ALL,REPO_DIR=${REPO_DIR},CONDA_ENV=${CONDA_ENV},R_MODULE=${R_MODULE},PARAMS_FILE=${PARAMS_FILE},VCML_FILE=${VCML_FILE},CHR=${CHR},PHASE=${PHASE},KT_LOC=${KT_LOC},RUN_PREFIX=${RUN_PREFIX}" \
    "${SCRIPT_DIR}/sim_worker.sh")

ARRAY_JOB_ID=$(echo "$ARRAY_JOB_OUT" | awk '{print $NF}')
echo "Array job submitted: ${ARRAY_JOB_ID}  (${N} tasks, max 20 concurrent)"

# ── Submit collect job (runs only if all array tasks succeed) ─────────────────
sbatch \
    --partition="${PARTITION}" \
    --time="${COLLECT_TIME}" \
    --mem="${COLLECT_MEM}" \
    --cpus-per-task=1 \
    --nodes=1 \
    --ntasks=1 \
    --job-name="vcell_collect" \
    --output="${LOG_DIR}/collect_%j.out" \
    --error="${LOG_DIR}/collect_%j.err" \
    --dependency="afterok:${ARRAY_JOB_ID}" \
    --export="ALL,REPO_DIR=${REPO_DIR},CONDA_ENV=${CONDA_ENV},R_MODULE=${R_MODULE},PARAMS_FILE=${PARAMS_FILE},CHR=${CHR},PHASE=${PHASE},KT_LOC=${KT_LOC},RUN_PREFIX=${RUN_PREFIX}" \
    "${SCRIPT_DIR}/collect_heatmaps.sh"

echo "Collect job submitted (waits for all ${ARRAY_JOB_ID} tasks to succeed)"
echo ""
echo "Monitor with:"
echo "  squeue -u \$USER"
echo "  tail -f ${LOG_DIR}/scan_${ARRAY_JOB_ID}_1.out"
