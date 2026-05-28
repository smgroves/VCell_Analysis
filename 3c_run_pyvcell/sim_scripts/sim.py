# Author: Sarah Groves 05/21/2026
import os
from pathlib import Path
from pyvcell.sim_results.result import Result
import pyvcell.vcml as vc
import shutil

# parameters we will want to be open to the user for parameter scans
# IC
# kintetic parameters
# chromosome type/size + combinatorial other changes
# - length
# - scaling factor
# kinetochore location


def run_simulation(biomodel, simulation, run_name: str, fields=None, local=True, overwrite=False) -> Result:
    """Run a simulation and save output to a named directory.
    pyvcell automatically saves to a randomized directory; this function renames that directory to something more meaningful.
    Parameters:
    biomodel: The BioModel to simulate.
    simulation: The Simulation to run.
    run_name: A name for this run, used to rename the output directory.
    fields: Optional list of field names to include in the output; if None, all fields are included.
    Returns:
    A Result object pointing to the output of this simulation.
    """
    if local:

        result = vc.simulate(biomodel, simulation, fields=fields)
    else:
        pass  # placeholder for remote execution code; once I figure out what the outputs look like this will be an option
    print("Simulation completed. Processing results...")
    named_dir = result.solver_output_dir.parent / run_name
    if named_dir.exists():
        if overwrite:
            print(
                f"Warning: Run '{run_name}' already exists at {named_dir} and will be overwritten. Continue? (y/n)")
            choice = input().lower()
            if choice != 'y':
                raise FileExistsError(
                    f"Run '{run_name}' already exists at {named_dir}. Choose a different name or delete it first.")
            else:
                # delete named_dir and all its contents
                shutil.rmtree(named_dir)
        else:
            raise FileExistsError(
                f"Run '{run_name}' already exists at {named_dir} and overwrite = False. Choose a different name or delete it first.")
    print("Saved simulation output to temporary directory:", result.solver_output_dir)
    result.solver_output_dir.rename(named_dir)
    print("Renamed output directory to:", named_dir)
    # Return a fresh Result pointing at the renamed directory
    return Result(solver_output_dir=named_dir, sim_id=result.sim_id, job_id=result.job_id)


def load_result(run_name: str, workspace: str | Path | None = None) -> Result:
    """Reload a Result from a previously named run."""
    ws = Path(workspace) if workspace else vc.get_workspace_dir()
    named_dir = ws / run_name

    if not named_dir.exists():
        raise FileNotFoundError(f"No run named '{run_name}' found in {ws}")

    fvinput = next((f for f in os.listdir(named_dir)
                   if f.endswith(".fvinput")), None)
    if fvinput is None:
        raise FileNotFoundError(
            f"No .fvinput file found in {named_dir} — directory may be incomplete")

    sim_id = int(fvinput.split("_")[1])
    job_id = int(fvinput.split("_")[2])
    return Result(solver_output_dir=named_dir, sim_id=sim_id, job_id=job_id)
