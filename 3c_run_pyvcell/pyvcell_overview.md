# PyVCell: Overview of Snakemake Pipeline
This document explains how to use the Snakefile in this folder to run many simulations of a VCell model on different initial conditions.

## Pipeline steps

### 1. Check CSV for initial conditions
The pipeline should be pointed to a particular CSV of initial conditions, with columns = samples and rows = proteins in the VCell model. It will check if any of the samples are new.

### 2. Run pyvcell: relaxed simulation 
This step should: 
- read in parameters from a yml file (transition time, t_out, etc)
- load the relaxed state vcml
- run the model with the initial conditions from the CSV
- output concentrations of species for set timepoints for relaxed state

### 3. Transition simulation
- check if a vcml file already exists for the transition model; if available, load
- if no file, use field data and adapted model and save to vcml
- run a transition simulation 
- output concentrations of species for set timepoints for tensed state

The files related to rules 2 and 3 are:

```
run_CPC_model.py
sim_scripts/            # functions used in run_CPC_model.py
├── load.py             # loading the model, field data, etc
├── build.py            # changing relaxed to transition
├── sim.py              # simulations of the model
├── utils.py             # extra functions
└── process.py          # processing outputs
```

### 3. Run plotting and summary statistics code
This pulls in the code from 4_post_VCell_processing, or uses pyvcell functions to plot the results both as a sanity check and as final results. 
