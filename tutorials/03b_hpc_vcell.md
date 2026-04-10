# Module 3b: Running VCell Simulations on HPC (Rivanna/SLURM)

**Location:** `3b_cli_VCell/`

## Purpose

For production runs — especially parameter scans over many simulation conditions — VCell is run on the **Rivanna HPC cluster** at UVA using a Singularity container. This avoids the overhead of the VCell GUI and enables batch submission of many simulations in parallel.

The three SLURM scripts in `3b_cli_VCell/` correspond to the three steps of the HPC workflow.

---

## Prerequisites

- Access to Rivanna (`ssh <username>@rivanna.hpc.virginia.edu`)
- Access to the `janeslab` SLURM account (`#SBATCH --account=janeslab`)
- Docker/Singularity available on the cluster (`module load singularity`)
- A VCML model file (from `vcell_models/vcml/`) uploaded to the cluster

---

## Step 1: Pull the VCell Singularity Image

**Script:** `1_load_sif.slurm`

```bash
#!/bin/bash
#SBATCH -N 1
#SBATCH --ntasks-per-node=16
#SBATCH --account=janeslab
#SBATCH --time=10
#SBATCH --mem=20G
#SBATCH --partition=standard

module load singularity

singularity pull /home/${USER}/vcell_misc/vcell_sif.sif \
    docker://ghcr.io/virtualcell/biosimulators_vcell:latest
```

This downloads the official VCell Docker image and converts it to a Singularity `.sif` file stored in your home directory. This only needs to be done once (or when you want to update to a newer VCell version).

**Submit:**
```bash
sbatch 1_load_sif.slurm
```

---

## Step 2: Convert VCML to OMEX

**Script:** `2_convert_vcml.slurm`

```bash
#!/bin/bash
#SBATCH ...  # same resource request as above

module load singularity

SIF=/home/${USER}/vcell_misc/vcell_sif.sif
INPUT=/scratch/${USER}/vcell_in/vcml_files   # directory containing .vcml files
OUTPUT=/scratch/${USER}/vcell_out

singularity run ${SIF} convert -i ${INPUT} -o ${OUTPUT} -vcml
```

### What this does

VCell's CLI takes **OMEX** files (a standardized archive format), not raw VCML files. This step converts your `.vcml` model files into the OMEX format.

**Before submitting:**
1. Copy your VCML file to `/scratch/${USER}/vcell_in/vcml_files/` on Rivanna
2. Update `INPUT` and `OUTPUT` paths if using a non-standard directory structure

**Submit:**
```bash
sbatch 2_convert_vcml.slurm
```

---

## Step 3: Run the Simulation

**Script:** `3_run_sif.slurm`

```bash
#!/bin/bash
#SBATCH -N 1
#SBATCH --ntasks-per-node=16
#SBATCH --account=janeslab
#SBATCH --time=10:00:00    # 10 hours for full production runs
#SBATCH --mem=50G
#SBATCH --partition=standard

module load singularity

SIF=/home/${USER}/vcell_misc/vcell_sif.sif
INPUT=/scratch/${USER}/vcell_in/slurm6.omex  # the OMEX file from Step 2
OUTPUT=/scratch/${USER}/vcell_out

singularity run ${SIF} -i ${INPUT} -o ${OUTPUT}
```

### Key parameters to adjust

| Parameter | Default | Notes |
|-----------|---------|-------|
| `--time` | `10:00:00` | Increase for long simulations (>500s model time) |
| `--mem` | `50G` | Reduce for small models; increase for large meshes |
| `INPUT` | `slurm6.omex` | Update to your actual OMEX filename |
| `OUTPUT` | `/scratch/.../vcell_out` | Where HDF5 output will be written |

**Submit:**
```bash
sbatch 3_run_sif.slurm
```

---

## Output

The VCell CLI writes a `reports.h5` file (HDF5 format) to `OUTPUT`. This file contains all simulation results and is processed in **Module 4** using `hdf5_converter.py`.

Directory structure after a successful run:
```
/scratch/${USER}/vcell_out/
└── reports.h5           # all species, all timepoints, all spatial positions
```

---

## Checking job status

```bash
# View running/queued jobs
squeue -u ${USER}

# View output log
cat slurm-<JOBID>.out

# Check how long a job ran
sacct -j <JOBID> --format=JobID,Elapsed,State
```

---

## Transferring output back to your local machine

Once the simulation completes, transfer the HDF5 file from Rivanna to your local machine or Box:

```bash
# From your local machine
scp <username>@rivanna.hpc.virginia.edu:/scratch/<username>/vcell_out/reports.h5 \
    /path/to/local/VCell_Exports/
```

Then proceed to Module 4 for HDF5 conversion and visualization.

---

## Troubleshooting

| Issue | Likely cause | Fix |
|-------|-------------|-----|
| Job immediately fails | Singularity image not found | Re-run `1_load_sif.slurm` |
| `reports.h5` is empty | VCML conversion failed | Check the OMEX file is valid; re-run Step 2 |
| Out of memory | Model mesh too large | Increase `--mem` or reduce mesh resolution in VCell GUI |
| Simulation timeout | Model runtime too long | Increase `--time`; consider reducing output frequency |
