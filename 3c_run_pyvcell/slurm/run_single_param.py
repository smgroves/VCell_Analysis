"""
run_single_param.py
Run one (param1, param2) combination of the CPC model:
  - relaxed simulation
  - tensed simulation (built from relaxed output)
  - export CSVs from both runs (zarr → SimID_*__exported/)

Called by sim_worker.sh with explicit --run_name_relaxed / --run_name_tensed
so the naming is controlled entirely from the shell side.
"""

import argparse
import sys
import warnings
from pathlib import Path
from colorama import Fore, Style, init as _colorama_init

warnings.filterwarnings("ignore")
_colorama_init(autoreset=True)

# ── ensure sim_scripts is on the path ─────────────────────────────────────────
_THIS = Path(__file__).resolve()
_REPO = _THIS.parent.parent.parent          # VCell_Analysis/
sys.path.insert(0, str(_REPO / "3c_run_pyvcell"))

import sim_scripts as ss
import pyvcell.vcml as vc


# ─────────────────────────────────────────────────────────────────────────────
def set_parameters(model, param1_name: str, param1_val: float,
                   param2_name: str, param2_val: float) -> None:
    """
    Set two named model parameters to the given values.
    Uses the pyvcell model.set_parameter_value() API.
    Raises ValueError if either parameter name is not found in the model.
    """
    available = set(model.parameter_values.keys())
    for name, val in [(param1_name, param1_val), (param2_name, param2_val)]:
        if name not in available:
            raise ValueError(
                f"Parameter '{name}' not found in model.\n"
                f"Available parameters: {sorted(available)}"
            )
        model.set_parameter_value(name, val)
        print(f"  set {name} = {val}")


# ─────────────────────────────────────────────────────────────────────────────
def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run a single parameter-scan point (relaxed + tensed)."
    )
    parser.add_argument("--vcml_file",         required=True,
                        help="Absolute path to the base relaxed VCML file.")
    parser.add_argument("--chr",               default="chr19")
    parser.add_argument("--phase",             default="PMP1")
    parser.add_argument("--kt_loc",            default="metacentric")
    parser.add_argument("--param1_name",       required=True,
                        help="Name of first parameter to scan.")
    parser.add_argument("--param1_val",        type=float, required=True,
                        help="Value for parameter 1.")
    parser.add_argument("--param2_name",       required=True,
                        help="Name of second parameter to scan.")
    parser.add_argument("--param2_val",        type=float, required=True,
                        help="Value for parameter 2.")
    parser.add_argument("--run_name_relaxed",  required=True,
                        help="Workspace folder name for the relaxed run.")
    parser.add_argument("--run_name_tensed",   required=True,
                        help="Workspace folder name for the tensed run.")
    parser.add_argument("--workspace",         default=None,
                        help="Absolute path to workspace directory. "
                             "Defaults to pyvcell's configured workspace.")
    args = parser.parse_args()

    workspace = Path(args.workspace) if args.workspace else vc.get_workspace_dir()
    print(f"{Fore.CYAN}Workspace: {workspace}")

    # ── Load and customise the model ─────────────────────────────────────────
    print(f"{Fore.GREEN}Loading model: {args.vcml_file}")
    bio_model = ss.load_model(args.vcml_file)

    print(f"{Fore.GREEN}Building chromosome geometry ({args.chr}, {args.phase}, {args.kt_loc})...")
    chr_model = ss.build_chromosome(
        relaxed_model=bio_model,
        chr=args.chr,
        phase=args.phase,
        KT_loc=args.kt_loc,
    )

    # ── CHANGE: set scan parameters AFTER build_chromosome so geometry ────────
    # ── scaling doesn't reset them. ───────────────────────────────────────────
    print(f"{Fore.GREEN}Setting scan parameters...")
    set_parameters(chr_model.model,
                   args.param1_name, args.param1_val,
                   args.param2_name, args.param2_val)

    # ── Relaxed simulation ────────────────────────────────────────────────────
    sim = chr_model.applications[0].simulations[0]
    print(f"{Fore.GREEN}Running relaxed simulation: {args.run_name_relaxed}")
    result_relaxed = ss.run_simulation(
        biomodel=chr_model,
        simulation=sim.name,
        run_name=args.run_name_relaxed,
        fields=None,
        local=True,
        overwrite=True,
    )
    print(f"  solver_output_dir: {result_relaxed.solver_output_dir}")

    print(f"{Fore.GREEN}Exporting CSVs for relaxed run...")
    ss.export_result_to_csv(result_relaxed, include_summary_functions=True)

    # ── Tensed simulation (built from relaxed output) ─────────────────────────
    print(f"{Fore.GREEN}Building tensed model from relaxed output...")
    tensed_model = ss.build_tensed_model(chr_model, application="Spatial")

    # Re-apply scan parameters to the tensed model
    set_parameters(tensed_model.model,
                   args.param1_name, args.param1_val,
                   args.param2_name, args.param2_val)

    sim_tensed = tensed_model.applications[0].simulations[0]
    print(f"{Fore.GREEN}Running tensed simulation: {args.run_name_tensed}")
    result_tensed = ss.run_simulation(
        biomodel=tensed_model,
        simulation=sim_tensed.name,
        run_name=args.run_name_tensed,
        fields=None,
        local=True,
        overwrite=True,
    )
    print(f"  solver_output_dir: {result_tensed.solver_output_dir}")

    print(f"{Fore.GREEN}Exporting CSVs for tensed run...")
    ss.export_result_to_csv(result_tensed, include_summary_functions=True)

    print(f"{Fore.GREEN}Done: {args.param1_name}={args.param1_val} "
          f"{args.param2_name}={args.param2_val}")


if __name__ == "__main__":
    main()
