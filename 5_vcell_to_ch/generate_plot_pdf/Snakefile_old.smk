import os
from pathlib import Path
import glob

# Configuration
FOLDER_NAME = "CPC_all_11_26_25_metacentric_relaxed_MCF10A_chr19_PMP1_100_"
BASEDIR = "/Users/smgroves/Documents/GitHub/VCell_Analysis/5_vcell_to_ch"
OUTDIR = os.path.join(BASEDIR, "output/01_16_2026", FOLDER_NAME)
INTDIR = os.path.join(BASEDIR, "int", FOLDER_NAME)
SCRIPTDIR = os.path.join(BASEDIR, "generate_plot_pdf")
MATLAB_BIN = "/Applications/MATLAB_R2023b.app/bin/maca64/MATLAB"  # maca64 for Apple Silicon
DT = 2.5e-5
DT_OUT = 10

# Extract the folder name for use in output filename

# Create int directory if it doesn't exist
os.makedirs(INTDIR, exist_ok=True)

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
    print(f"Found {len(prefixes)} simulations:")
    for p in prefixes:
        print(f"  - {p}")
    return prefixes

SIMULATIONS = find_simulation_prefixes(OUTDIR)

if not SIMULATIONS:
    raise ValueError(f"No simulation files found in {OUTDIR}")

rule all:
    input:
        os.path.join(SCRIPTDIR, f"{FOLDER_NAME}_analysis.pdf"),      
        os.path.join(SCRIPTDIR, f"{FOLDER_NAME}_summary.csv")


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
               simulation=SIMULATIONS)
    output:
        os.path.join(SCRIPTDIR, f"{FOLDER_NAME}_analysis.pdf")
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
               simulation=SIMULATIONS)
    output:
        os.path.join(SCRIPTDIR, f"{FOLDER_NAME}_summary.csv")
    params:
        intdir = INTDIR
    shell:
        """
        python {SCRIPTDIR}/create_summary_table.py \
            --intdir {params.intdir} \
            --output {output}
        """