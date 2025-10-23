# based on the tutorial https://github.com/virtualcell/pyvcell/blob/main/examples/scripts/fielddata_from_sim_workflow.py
import os
import shutil
import tempfile
from pathlib import Path

import pyvcell.vcml as vc

with tempfile.TemporaryDirectory() as temp_dir_name, Path(
        temp_dir_name) as temp_dir:
    # ----- make a workspace
    workspace_dir = temp_dir / "vcell_sim_workspace"
    sim1_dir = workspace_dir / "sim1_dir"
    if sim1_dir.exists():
        shutil.rmtree(sim1_dir)
    sim2_dir = workspace_dir / "sim2_dir"
    if sim2_dir.exists():
        shutil.rmtree(sim2_dir)

    # ---- read in VCML file
    model_relaxed = Path(os.getcwd()) / "vcell_models" / "vcml" / \
        "_09_16_25_CPC_metacentric_relaxed_model_v2"
    bio_model1 = vc.load_vcml_file(model_relaxed)

    model_transition = Path(os.getcwd()) / "vcell_models" / "vcml" / \
        "_09_16_25_CPC_metacentric_transition_model"
    bio_model2 = vc.load_vcml_file(model_transition)

    # ---- get the application and the species mappings for species "s0" and "s1"
    app = bio_model1.applications[0]
    # make a single loop that loops through each species to build a mapping, then set the initial concentration of that mapping based on data

    # TODO figure out how to set based on RNAseq input
    for s in app.species_mappings:
        s.init_conc = ""  # pull from RNA-seq data value

    sim = bio_model1.applications[0].simulations[0]

    # ---- run simulation, store in sim1_dir, and plot results
    # >>>>> This forms the data for the "Field Data" identified by 'sim1_dir' <<<<<<
    sim1_result = vc.simulate(biomodel=bio_model1, simulation=sim.name)
    print([c.label for c in sim1_result.channel_data])
    print(sim1_result.time_points[::11])
    sim1_result.plotter.plot_concentrations()
    sim1_result_dirname = sim1_result.solver_output_dir.name

    # TODO save output from sim1_result to h5 or csvs

    # ----- use field data from sim1_dir to set initial concentration of species "s0"
    app2 = bio_model2.applications[0]
    sim2 = bio_model2.applications[0].simulations[0]

    # TODO instead of loop here, make a function that sets initial concentrations based on species name
    for s in app2.species_mappings:
        s.init_conc = (
            f"vcField('{sim1_result_dirname}','s0',0.0,'Volume') * vcField('{sim1_result_dirname}','s1',0.0,'Volume')"
        )

    # ---- run transition simulation and store in sim2_dir
    # note that the solution of s0 draws from the data from sim1_dir
    sim2_result = vc.simulate(biomodel=bio_model2, simulation=sim2.name)
    sim2_result.plotter.plot_concentrations()
    sim2_result.cleanup()

    # TODO save output from sim2_result to h5 or csvs
