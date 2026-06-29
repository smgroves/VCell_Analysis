#!/usr/bin/env python3
"""
vcell_heatmap_movie.py
======================
Render VCell simulation concentration heatmaps as an MP4 or GIF.

Each frame is the summed concentration of one or more species at a single
timepoint, coloured with the viridis palette to match vcell_heatmap.R output.

Dependencies
------------
    pip install numpy matplotlib imageio imageio-ffmpeg Pillow

Usage (module)
--------------
    from vcell_heatmap_movie import make_heatmap_movie

    make_heatmap_movie(
        sim_id      = "SimID_316523018_0__exported",
        species     = ["CPCa", "pH2A_SGO1_CPCa", "H3_CPCa", "pH3_CPCa", "SGO1_CPCa",
                       "CPCi", "pH2A_SGO1_CPCi", "H3_CPCi", "pH3_CPCi", "SGO1_CPCi"],
        import_path = "/path/to/VCell_Exports",
        export_path = "/path/to/output",
        species_name = "all CPC",
        fps          = 10,
    )

Usage (script)
--------------
    python vcell_heatmap_movie.py
    (edit the "── configuration ──" block at the bottom)
"""

import io
import os
import re
import sys
import numpy as np
import copy
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.ticker as mticker
from pathlib import Path
from typing import Optional

try:
    import imageio
except ImportError:
    sys.exit("imageio not found. Install with: pip install imageio imageio-ffmpeg Pillow")

try:
    from PIL import Image
except ImportError:
    sys.exit("Pillow not found. Install with: pip install Pillow")


# ── file-name pattern ──────────────────────────────────────────────────────────
# Matches: SimID_xxx_Slice_XY_0_SpeciesName_0042.csv
_FNAME_RE = re.compile(r"[A-Za-z0-9_]*_Slice_XY_\d+_(.+)_(\d{4})\.csv$")


def _load_matrix(
    sim_folder: str,
    all_files: list,
    species: str,
    tp_str: str,
    n_rows: int,
    n_cols: int,
    leader: int,
) -> Optional[np.ndarray]:
    """Load one species CSV and return an (n_rows × n_cols) float32 array, or None."""
    pat = re.compile(
        r"[A-Za-z0-9_]*_Slice_XY_\d+_"
        + re.escape(species)
        + r"_"
        + re.escape(tp_str)
        + r"\.csv$"
    )
    matches = [f for f in all_files if pat.match(f)]
    if not matches:
        return None
    filepath = os.path.join(sim_folder, matches[0])
    try:
        mat = np.loadtxt(filepath, delimiter=",", skiprows=leader, dtype=np.float32)
        return mat[:n_rows, :n_cols]
    except Exception as exc:
        print(f"  Warning: could not read '{matches[0]}': {exc} — skipping")
        return None


def make_heatmap_movie(
    sim_id: str,
    species: list,
    import_path: str,
    export_path: str,
    # ── species / data options ─────────────────────────────────────────────────
    species_name: str = "species",
    compute_functions: Optional[dict] = None,
    # ── geometry (must match VCell model) ─────────────────────────────────────
    dat_dim: tuple = (136, 52),        # (n_rows, n_cols)
    chrom_width: float = 1.3,          # µm — X axis
    chrom_height: float = 3.4,         # µm — Y axis
    leader: int = 10,                  # CSV header lines to skip
    # ── video options ─────────────────────────────────────────────────────────
    fps: int = 10,
    output_format: str = "mp4",        # "mp4" or "gif"
    # ── colour-bar ────────────────────────────────────────────────────────────
    max_color: Optional[float] = None, # None → auto from data
    # ── figure layout ─────────────────────────────────────────────────────────
    dpi: int = 150,
    fig_width: float = 3.5,            # inches
    fig_height: float = 8.0,           # inches
    rescale_timepoints: Optional[float] = None,  # None → no rescaling
) -> str:
    """
    Build an MP4 or GIF heatmap movie from VCell CSV slice files.

    Parameters
    ----------
    sim_id           SimID folder name (e.g. "SimID_316523018_0__exported").
    species          Species names to sum each frame.
    import_path      Root folder containing sim_id.
    export_path      Destination folder for the video file.
    species_name     Label for the file name and colour-bar title.
    compute_functions  dict mapping a derived species to its component species.
                     Used when no CSV exists for a species on disk, e.g.
                     {"bound_CPC": ["pH2A_SGO1_CPCa", "H3_CPCa", ...]}.
    dat_dim          (n_rows, n_cols) of each concentration matrix.
    chrom_width      Chromosome width in µm (X axis extent).
    chrom_height     Chromosome height in µm (Y axis extent).
    leader           Header lines to skip in each CSV (default 10).
    fps              Frames per second in the output video.
    output_format    "mp4" (requires imageio-ffmpeg) or "gif" (requires Pillow).
    max_color        Fixed colour-bar ceiling; None → infer from global max.
    dpi              Render resolution for each frame.
    fig_width        Figure width in inches.
    fig_height       Figure height in inches.

    Returns
    -------
    Absolute path to the saved video file.
    """
    n_rows, n_cols = dat_dim

    # ── normalise SimID (append _exported if missing) ─────────────────────────
    if not re.search(r"exported", sim_id):
        sim_id = sim_id + "_exported"

    sim_folder = os.path.join(import_path, sim_id)
    if not os.path.isdir(sim_folder):
        raise FileNotFoundError(f"Simulation folder not found: {sim_folder}")

    all_files = os.listdir(sim_folder)

    # ── collect all wanted species names (including compute_functions components)
    wanted_species = set(species)
    if compute_functions:
        for comps in compute_functions.values():
            wanted_species.update(comps)

    # ── discover timepoints present for any wanted species ────────────────────
    timepoint_set = set()
    for fname in all_files:
        m = _FNAME_RE.match(fname)
        if m and m.group(1) in wanted_species:
            timepoint_set.add(m.group(2))   # e.g. "0042"

    timepoints = sorted(timepoint_set)
    if not timepoints:
        raise ValueError(
            f"No matching CSV files found in {sim_folder} for species {species}"
        )
    print(f"SimID {sim_id}: {len(timepoints)} timepoints "
          f"({timepoints[0]} … {timepoints[-1]})")

    # ── load and sum species for every timepoint ──────────────────────────────
    frames = []
    for tp in timepoints:
        matrices = []
        for sp in species:
            mat = _load_matrix(sim_folder, all_files, sp, tp, n_rows, n_cols, leader)
            if mat is None and compute_functions and sp in compute_functions:
                # sum component matrices as fallback
                comp_mats = [
                    _load_matrix(sim_folder, all_files, c, tp, n_rows, n_cols, leader)
                    for c in compute_functions[sp]
                ]
                comp_mats = [m for m in comp_mats if m is not None]
                if comp_mats:
                    mat = sum(comp_mats)
            if mat is not None:
                matrices.append(mat)

        M = np.clip(sum(matrices), 0, None) if matrices else np.zeros((n_rows, n_cols), dtype=np.float32)
        frames.append(M)

    # ── determine colour-bar maximum ──────────────────────────────────────────
    # Dict form: {"CPC": 11} → look up by species_name substring; unmatched → auto
    if isinstance(max_color, dict):
        matched = None
        for k, v in max_color.items():
            if k in species_name:
                matched = float(v)
                break
        max_color = matched  # None → fall through to auto-computation below

    if max_color is None:
        global_max = float(max(m.max() for m in frames)) if frames else 1.0
        if global_max >= 10:
            max_color = float(10 * np.ceil(global_max / 10))
        elif global_max > 0:
            max_color = float(np.ceil(global_max))
        else:
            max_color = 1.0

    max_color = float(max_color)
    print(f"  Colour-bar max = {max_color:.3g}  |  fps = {fps}")

    # ── prepare output path ───────────────────────────────────────────────────
    os.makedirs(export_path, exist_ok=True)
    out_stem = re.sub(r"\s+", "_", species_name)
    suffix = "mp4" if output_format == "mp4" else "gif"
    out_path = os.path.join(export_path, f"{out_stem}_heatmap.{suffix}")

    # ── render each frame to an RGB numpy array ───────────────────────────────
    tick_vals = [0, max_color / 4, max_color / 2, 3 * max_color / 4, max_color]
    tick_labs = [f"{v:.3g}" for v in tick_vals]

    # Values above max_color → white (set_over); clip=False routes them there
    cmap = copy.copy(plt.cm.viridis)
    cmap.set_over("white")
    norm = mcolors.Normalize(vmin=0, vmax=max_color, clip=False)

    rgba_frames = []
    for idx, (tp, M) in enumerate(zip(timepoints, frames)):
        fig, ax = plt.subplots(figsize=(fig_width, fig_height), dpi=dpi)

        im = ax.imshow(
            M,
            origin="lower",          # row 0 → bottom of plot (Y = 0)
            aspect="equal",
            extent=[0, chrom_width, 0, chrom_height],
            norm=norm,
            cmap=cmap,
            interpolation="nearest",
        )

        ax.set_xlabel("X (µm)", fontsize=11, fontweight="bold")
        ax.set_ylabel("Y (µm)", fontsize=11, fontweight="bold")
        ax.xaxis.set_major_locator(mticker.LinearLocator(3))
        ax.yaxis.set_major_locator(mticker.LinearLocator(4))
        ax.xaxis.set_major_formatter(mticker.FormatStrFormatter("%.1f"))
        ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.1f"))
        ax.tick_params(labelsize=9)
        #convert timepoint to min sec
        if rescale_timepoints is not None:
            tp = int(tp) * rescale_timepoints
        tp_min = int(tp) // 60
        tp_sec = int(tp) % 60
        ax.set_title(f"{species_name}\nt = {tp_min} min {tp_sec} s", fontsize=12)

        cbar = fig.colorbar(
            im, ax=ax, orientation="horizontal", fraction=0.046, pad=0.12,
            extend="max",            # shows the white wedge at the high end
        )
        cbar.set_label(f"[{species_name}] (µM)", fontsize=9)
        cbar.set_ticks(tick_vals)
        cbar.set_ticklabels(tick_labs)
        cbar.ax.tick_params(labelsize=8)

        fig.tight_layout()

        # rasterise to RGB via PNG round-trip (robust across matplotlib backends)
        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=dpi, bbox_inches="tight")
        buf.seek(0)
        img = Image.open(buf).convert("RGB")
        rgba_frames.append(np.array(img))
        plt.close(fig)

        if (idx + 1) % 20 == 0 or idx == len(timepoints) - 1:
            print(f"  Rendered {idx + 1}/{len(timepoints)} frames")

    # ── write video file ──────────────────────────────────────────────────────
    print(f"Writing {output_format.upper()} → {out_path}")
    if output_format == "mp4":
        with imageio.get_writer(out_path, fps=fps, codec="libx264", quality=8) as writer:
            for frame in rgba_frames:
                writer.append_data(frame)
    else:
        # GIF: all frames must be same size (they are, from tight layout + fixed dpi)
        imageio.v3.imwrite(out_path, rgba_frames, loop=0, duration=1000 // fps)

    print(f"Saved: {out_path}")
    return out_path


# ══════════════════════════════════════════════════════════════════════════════
# ── configuration ─────────────────────────────────────────────────────────────
# Edit this block and run: python vcell_heatmap_movie.py
# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":

    import_path = "/Users/smgroves/Library/CloudStorage/Box-Box/Research/CPC_Model_Project/VCell_Exports"
    export_path = "/Users/smgroves/Library/CloudStorage/Box-Box/Research/CPC_Model_Project/vcell_plots"

    # ── chromosome geometry ────────────────────────────────────────────────────
    dat_dim      = (136, 104)   # (n_rows, n_cols); use (136, 104) for double-wide
    chrom_width  = 2.6         # µm; use 2.6 for double-wide
    chrom_height = 3.4         # µm

    # ── species groups (one movie per group) ──────────────────────────────────
    CPC_species      = ["CPCa", "pH2A_SGO1_CPCa", "H3_CPCa", "pH3_CPCa", "SGO1_CPCa",
                        "CPCi", "pH2A_SGO1_CPCi", "H3_CPCi", "pH3_CPCi", "SGO1_CPCi"]
    pH3_species      = ["pH3", "pH3_CPCa", "pH3_CPCi"]
    pH2A_species     = ["pH2A", "pH2A_SGO1", "pH2A_SGO1_CPCa", "pH2A_SGO1_CPCi"]
    SGO1_species     = ["SGO1", "pH2A_SGO1", "pH2A_SGO1_CPCi", "pH2A_SGO1_CPCa",
                        "SGO1_CPCi", "SGO1_CPCa"]
    bound_CPC        = ["bound_CPC"]
    bound_active_CPC = ["bound_active_CPC"]
    pH3S10rep        = ["pH3S10rep"]

    # R-side compute_functions: used when the species CSV does not exist on disk
    compute_functions = {
        "bound_CPC":        ["pH2A_SGO1_CPCa", "H3_CPCa", "pH3_CPCa", "SGO1_CPCa",
                             "pH2A_SGO1_CPCi", "H3_CPCi", "pH3_CPCi", "SGO1_CPCi"],
        "bound_active_CPC": ["pH2A_SGO1_CPCa", "H3_CPCa", "pH3_CPCa", "SGO1_CPCa"],
        "CPC_all":            ["CPCa",'CPCi',
                               "pH2A_SGO1_CPCa", "H3_CPCa", "pH3_CPCa", "SGO1_CPCa",
                             "pH2A_SGO1_CPCi", "H3_CPCi", "pH3_CPCi", "SGO1_CPCi"],
        "CPC_active":         ["CPCa","pH2A_SGO1_CPCa", "H3_CPCa", "pH3_CPCa", "SGO1_CPCa"],
        "CPC_inactive":       ["CPCi","pH2A_SGO1_CPCi", "H3_CPCi", "pH3_CPCi", "SGO1_CPCi"],
        "pH3_all":            ["pH3", "pH3_CPCa", "pH3_CPCi"],
        "pH2A_all":           ["pH2A", "pH2A_SGO1", "pH2A_SGO1_CPCa", "pH2A_SGO1_CPCi"],
        "SGO1_all":           ["SGO1", "pH2A_SGO1", "pH2A_SGO1_CPCi", "pH2A_SGO1_CPCa", "SGO1_CPCi", "SGO1_CPCa"],  
    }

    heatmap_groups = [
        # (CPC_species,      "all_CPC",             compute_functions),
        # (bound_CPC,        "all_bound_CPC",        compute_functions),
        # (bound_active_CPC, "all_bound_active_CPC", compute_functions),
        (pH3_species,      "all_pH3",              compute_functions),
        (pH2A_species,     "all_pH2A",             compute_functions),
        (SGO1_species,     "all_SGO1",             compute_functions),
        (pH3S10rep,        "pH3S10rep",            None),
    ]

    # ── simulations to process ─────────────────────────────────────────────────
    sims = [
        "SimID_317322923_0__exported",
    ]

    sim_names = ["06_19_26_metacentric_MCF10A_double_tensed_relaxed_chr19_PMP1_seconds",]

    # ── video settings ─────────────────────────────────────────────────────────
    FPS           = 10            # frames per second
    OUTPUT_FORMAT = "mp4"         # "mp4" or "gif"
    MAX_COLOR     = 11          # None → auto; or e.g. 11.0 to fix the scale
    DPI           = 300
    FIG_WIDTH     = 6           # inches
    FIG_HEIGHT    = 8.0           # inches

    # ── run ────────────────────────────────────────────────────────────────────
    for sim_id,sim_name in zip(sims, sim_names):
        sim_export = os.path.join(export_path, sim_name)
        for sp_list, sp_name, cf in heatmap_groups:
            try:
                make_heatmap_movie(
                    sim_id            = sim_id,
                    species           = sp_list,
                    import_path       = import_path,
                    export_path       = sim_export,
                    species_name      = sp_name,
                    compute_functions = cf,
                    dat_dim           = dat_dim,
                    chrom_width       = chrom_width,
                    chrom_height      = chrom_height,
                    fps               = FPS,
                    output_format     = OUTPUT_FORMAT,
                    max_color         = {"CPC":MAX_COLOR},
                    dpi               = DPI,
                    fig_width         = FIG_WIDTH,
                    fig_height        = FIG_HEIGHT,
                    rescale_timepoints = 3 #outputs every 1/8 sec in sim = 3 sec real life
                )
            except Exception as exc:
                print(f"ERROR for {sim_id} / {sp_name}: {exc}")
