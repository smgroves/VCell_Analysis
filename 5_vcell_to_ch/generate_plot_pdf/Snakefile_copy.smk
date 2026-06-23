import os
from pathlib import Path
import glob

# Configuration
FOLDER_NAME = "CPC_all_06_13_26_metacentric_relaxed_MCF10A_chr19_PMP1_HASPINInh_97P_50_136x136__"
SIM_SET = "06_23_2026"
BASEDIR = "/Users/smgroves/Documents/GitHub/VCell_Analysis/5_vcell_to_ch"
ICDIR = os.path.join(BASEDIR, "IC", SIM_SET)
OUTDIR = os.path.join(BASEDIR, "output", SIM_SET, FOLDER_NAME)
INTDIR = os.path.join(BASEDIR, "int", SIM_SET, FOLDER_NAME)
SCRIPTDIR = os.path.join(BASEDIR, "generate_plot_pdf")
SOLVERDIR = os.path.join(BASEDIR, "CahnHilliard_MATLAB_solvers")
# maca64 for Apple Silicon
MATLAB_BIN = "/Applications/MATLAB_R2023b.app/bin/maca64/MATLAB" #for iMac
# MATLAB_BIN = "/Applications/MATLAB_R2023a.app/bin/maci64/MATLAB" #for Mac

DT = 2.5e-5
DT_OUT = 10
STEPS = 2000
ACTUAL_FINAL_TIME = DT * (STEPS)  # Total simulation time

# Create int directory if it doesn't exist
os.makedirs(INTDIR, exist_ok=True)

# Find all initial condition CSV files matching the folder name


def find_ic_files(icdir, folder_name):
    """Find all initial condition CSV files matching pattern FOLDER_NAME*max_*min.csv"""
    pattern = os.path.join(icdir, f"{folder_name}*max_*min.csv")
    ic_files = glob.glob(pattern)
    basenames = [os.path.basename(f) for f in ic_files]
    # Remove .csv extension
    prefixes = [name[:-4] for name in basenames]
    print(f"Found {len(prefixes)} IC files matching {folder_name}:")
    for p in prefixes[:5]:
        print(f"  - {p}")
    if len(prefixes) > 5:
        print(f"  ... and {len(prefixes) - 5} more")
    return prefixes


IC_SIMULATIONS = find_ic_files(ICDIR, FOLDER_NAME)

# Find all simulation prefixes by looking for movie.mp4 files


def find_simulation_prefixes(outdir):
    """Find all unique simulation prefixes from movie.mp4 files"""
    movie_files = glob.glob(os.path.join(outdir, "*movie.mp4"))
    prefixes = []
    for movie_file in movie_files:
        # Remove 'movie.mp4' from the end to get the prefix
        basename = os.path.basename(movie_file)
        prefix = basename.replace("movie.mp4", "")
        prefixes.append(prefix)
    print(f"Found {len(prefixes)} completed simulations:")
    for p in prefixes[:5]:
        print(f"  - {p}")
    if len(prefixes) > 5:
        print(f"  ... and {len(prefixes) - 5} more")
    return prefixes


SIMULATIONS = find_simulation_prefixes(OUTDIR)

if not SIMULATIONS and not IC_SIMULATIONS:
    raise ValueError(
        f"No simulation files or IC files found in {OUTDIR} or {ICDIR}")

# IMPORTANT: Use IC_SIMULATIONS as the target list
# This ensures new IC files trigger new simulations
ALL_SIMS = IC_SIMULATIONS

print(f"\nTarget simulations: {len(ALL_SIMS)}")
print(f"  - Already completed: {len(SIMULATIONS)}")
print(f"  - To be run: {len(ALL_SIMS) - len(SIMULATIONS)}")

rule all:
    input:
        os.path.join(SCRIPTDIR, f"summary_output/{FOLDER_NAME}_analysis.pdf"),
        os.path.join(SCRIPTDIR, f"summary_output/{FOLDER_NAME}_summary.csv")

rule run_ch_simulation:
    input:
        ic_file = os.path.join(ICDIR, "{ic_simulation}.csv")
    output:
        movie = os.path.join(OUTDIR, "{ic_simulation}movie.mp4"),
        phi = os.path.join(OUTDIR, "{ic_simulation}phi.csv"),
        final_phi = os.path.join(OUTDIR, "{ic_simulation}final_phi.csv")
    params:
        epsilon2 = 0.0089**2,  # epsilon = 0.0089 for 10A
        dt = DT,
        max_it = 2000,
        dt_out = DT_OUT,
        boundary = 'neumann',
        outdir = OUTDIR,
        solverdir = SOLVERDIR
    shell:
        """
        {MATLAB_BIN} -nodisplay -nosplash -nodesktop -r \
        "try; \
            cd('{params.solverdir}'); \
            if ~exist('{params.outdir}', 'dir'); \
                mkdir('{params.outdir}'); \
            end; \
            phi0 = readmatrix('{input.ic_file}'); \
            ny = size(phi0,2); \
            pathname = '{params.outdir}/{wildcards.ic_simulation}'; \
            [t_out, phi_t, delta_mass_t, E_t] = CahnHilliard_SAV(phi0, \
                't_iter', {params.max_it}, \
                'dt', {params.dt}, \
                'epsilon2', {params.epsilon2}, \
                'boundary', '{params.boundary}', \
                'printphi', true, \
                'pathname', pathname, \
                'dt_out', {params.dt_out}); \
            writematrix(phi_t(:,:,end), sprintf('%sfinal_phi.csv', pathname)); \
            writematrix(delta_mass_t, sprintf('%smass_uncentered.csv', pathname)); \
            writematrix(E_t, sprintf('%senergy.csv', pathname)); \
            filename = strcat(pathname, 'movie'); \
            ch_movie_from_file_fast(strcat(pathname,'phi.csv'), t_out, ny, 'filename', filename, 'dtframes', 1); \
            exit(0); \
        catch e; \
            disp(getReport(e)); \
            exit(1); \
        end"
        """

rule matlab_level_set:
    input:
        phi = os.path.join(OUTDIR, "{simulation}phi.csv"),
        movie = os.path.join(OUTDIR, "{simulation}movie.mp4")
    output:
        radius_data = os.path.join(INTDIR, "{simulation}radius_data.csv")
    params:
        dt = DT,
        dt_out = DT_OUT
    shell:
        """
        {MATLAB_BIN} -nodisplay -nosplash -nodesktop -r \
        "try; cd('{SCRIPTDIR}'); calculate_level_set_radius('{input.phi}', {params.dt}, {params.dt_out}, '{output.radius_data}'); exit(0); catch e; disp(getReport(e)); exit(1); end"
        """

rule python_analysis:
    input:
        final_phi = os.path.join(OUTDIR, "{simulation}final_phi.csv"),
        phi = os.path.join(OUTDIR, "{simulation}phi.csv"),
        radius_data = os.path.join(INTDIR, "{simulation}radius_data.csv"),
        movie = os.path.join(OUTDIR, "{simulation}movie.mp4")
    output:
        plots = os.path.join(INTDIR, "{simulation}analysis_plots.npz")
    params:
        dt = DT,
        dt_out = DT_OUT,
        sim_name = "{simulation}"
    shell:
        """
        python {SCRIPTDIR}/analyze_single_simulation.py \
            --final-phi {input.final_phi} \
            --phi {input.phi} \
            --radius-data {input.radius_data} \
            --dt {params.dt} \
            --dt-out {params.dt_out} \
            --sim-name {params.sim_name} \
            --output {output.plots}
        """

rule combine_pdfs:
    input:
        expand(os.path.join(INTDIR, "{simulation}analysis_plots.npz"),
               simulation=ALL_SIMS)
    output:
        os.path.join(SCRIPTDIR, f"summary_output/{FOLDER_NAME}_analysis.pdf")
    params:
        intdir = INTDIR
    shell:
        """
        python {SCRIPTDIR}/create_combined_pdf.py \
            --outdir {params.intdir} \
            --output {output}
        """

rule create_summary_table:
    input:
        expand(os.path.join(INTDIR, "{simulation}radius_data.csv"),
               simulation=ALL_SIMS)
    output:
        os.path.join(SCRIPTDIR, f"summary_output/{FOLDER_NAME}_summary.csv")
    params:
        intdir = INTDIR,
        actual_final_time = ACTUAL_FINAL_TIME
    shell:
        """
        python {SCRIPTDIR}/create_summary_table.py \
            --intdir {params.intdir} \
            --actual-final-time {params.actual_final_time} \
            --output {output}
        """
