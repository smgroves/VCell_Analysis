"""
Functions for processing and exporting pyvcell simulation results.

These functions mirror the workflow of
``4_post_VCell_processing/hdf5_converter.py`` but work **directly from the
zarr files** that pyvcell writes into the workspace directory, so no separate
HDF5 export step is needed.

Data layout in the zarr
-----------------------
The zarr produced by pyvcell has shape ``(T, C, Z, X, Y)``:

* **T** – number of saved timepoints
* **C** – number of channels (species, fluxes, parameters, …)
* **Z** – 1 for a 2-D simulation (the single z-slice)
* **X, Y** – spatial grid dimensions

Each channel is described by a ``ChannelMetadata`` object accessible via
``result.channel_data``; the key attributes are ``index``, ``label``, and
``domain_name``.  Channels whose ``domain_name`` is non-empty live on a
model compartment (e.g. ``"chromosome"``) and vary in space.

Output format (matches hdf5_converter)
---------------------------------------
``export_result_to_csv`` writes one CSV per variable per timepoint:

    <output_dir>/SimID_{sim_id}_{job_id}__Slice_XY_0_{label}_{t_idx:04d}.csv

Each file starts with a metadata header (plain text lines) followed by the
2-D concentration array – X positions in rows, Y positions in columns –
with no index or column labels, exactly as ``hdf5_converter.py`` produces.

Author: Sarah Groves  05/21/2026
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional, Union

import numpy as np
import pandas as pd
from pyvcell.sim_results.result import Result

# ─────────────────────────────────────────────────────────────────────────────
# Default species list
# ─────────────────────────────────────────────────────────────────────────────
# Labels must exactly match the strings stored in the zarr channel metadata.
# Note: a few names differ from the old hdf5_converter defaults because pyvcell
# uses lowercase in some multi-word labels (e.g. "BUB1a_pknl1" not "BUB1a_pKNL1").
# Labels absent from the zarr are silently skipped and reported.

DEFAULT_SPECIES: list[str] = [
    "BUB1a",
    "BUB1a_pknl1",       # hdf5_converter called this "BUB1a_pKNL1"
    "CPCa",
    "CPCi",
    "H2A",
    "H3",
    "H3_CPCa",
    "H3_CPCi",
    "H3S10rep",
    "HASPINa",
    "HASPINi",
    "I",
    "KNL1",
    "NDC80",
    "NDC80_TTKa",
    "NDC80_TTKi",
    "NDC80_pTTKa",
    "NDC80_pTTKi",
    "pH2A",
    "pH2A_SGO1",
    "pH2A_SGO1_CPCa",
    "pH2A_SGO1_CPCi",
    "pH3",
    "pH3_CPCa",
    "pH3_CPCi",
    "pH3S10rep",
    "pKNL1",
    "pKNL1_bub1a",
    "PLK1a",
    "PLK1i",
    "pTTKa",
    "pTTKi",
    "pNDC80",
    "pNDC80_TTKa",
    "pNDC80_TTKi",
    "pNDC80_pTTKa",
    "pNDC80_pTTKi",
    "SGO1",
    "SGO1_CPCi",
    "SGO1_CPCa",
    "TTKa",
    "TTKi",
]

# Composite summary functions (NOT stored in zarr; compute with
# compute_summary_functions() and pass to export_arrays_to_csv() if needed).
SUMMARY_FUNCTIONS: list[str] = [
    "CPC_all",
    "CPCa_total",
    "CPCi_total",
    "pH2_all",
    "bound_CPC",
    "bound_active_CPC",
]


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def list_available_channels(
    result: Result,
    domain: Optional[str] = None,
    print_output: bool = True,
) -> list[str]:
    """Return (and optionally print) channel labels in the result's zarr.

    Parameters
    ----------
    result : Result
        A pyvcell ``Result`` object.
    domain : str | None
        When given, return only channels whose ``domain_name`` equals *domain*
        (e.g. ``"chromosome"``).  ``None`` returns every channel.
    print_output : bool
        Print the list to stdout.  Default ``True``.

    Returns
    -------
    list[str]
        Channel labels in index order.
    """
    channels = result.channel_data
    if domain is not None:
        channels = [ch for ch in channels if ch.domain_name == domain]
    labels = [ch.label for ch in channels]
    if print_output:
        for ch in channels:
            domain_tag = f"  [{ch.domain_name}]" if ch.domain_name else ""
            print(f"  {ch.index:>3d}  {ch.label}{domain_tag}")
    return labels


def get_species_array(
    result: Result,
    label: str,
    time_index: Optional[int] = None,
) -> np.ndarray:
    """Read a single channel from the zarr as a NumPy array.

    Parameters
    ----------
    result : Result
        A pyvcell ``Result`` object.
    label : str
        Zarr channel label (e.g. ``"CPCa"``).  Case-sensitive.
    time_index : int | None
        * If an integer, returns a 2-D array of shape ``(X, Y)`` at that
          saved timepoint index.
        * If ``None``, returns a 3-D array of shape ``(T, X, Y)`` covering
          all timepoints.

    Returns
    -------
    np.ndarray

    Raises
    ------
    KeyError
        If *label* is not found in the zarr channel metadata.
    """
    label_to_ch = {ch.label: ch for ch in result.channel_data}
    if label not in label_to_ch:
        raise KeyError(
            f"Label '{label}' not found in zarr.  "
            "Call list_available_channels(result) to see what is available."
        )

    ch_idx = label_to_ch[label].index
    z = result.zarr_dataset  # shape (T, C, Z, X, Y)

    if time_index is not None:
        return np.asarray(z[time_index, ch_idx, 0, :, :])   # (X, Y)
    return np.asarray(z[:, ch_idx, 0, :, :])                # (T, X, Y)


# ─────────────────────────────────────────────────────────────────────────────
# Main export function
# ─────────────────────────────────────────────────────────────────────────────

def export_result_to_csv(
    result: Result,
    species_list: Optional[list[str]] = None,
    output_dir: Optional[Union[str, Path]] = None,
) -> Path:
    """Export simulation results to CSV files, one per variable per timepoint.

    Replicates the output format of ``hdf5_converter.convert_hdf5_to_csv``
    but reads directly from the zarr written by pyvcell, so no intermediate
    HDF5 export is required.

    Each output file is named::

        SimID_{sim_id}_{job_id}__Slice_XY_0_{label}_{t_idx:04d}.csv

    and contains a plain-text metadata header followed by the 2-D spatial
    array (X rows, Y columns) with no pandas index or column headers.

    Parameters
    ----------
    result : Result
        A pyvcell ``Result`` object (from :func:`run_simulation` or
        :func:`load_result`).
    species_list : list[str] | None
        Channel labels to export.  When ``None``, uses :data:`DEFAULT_SPECIES`.
        Labels are matched case-sensitively against the zarr metadata; call
        :func:`list_available_channels` to see exact names.
        Labels absent from the zarr are skipped and reported.
    output_dir : str | Path | None
        Destination folder.  Defaults to
        ``<solver_output_dir>/exported/``, i.e. a subfolder inside the
        simulation's workspace directory.

    Returns
    -------
    Path
        Absolute path to the output folder.

    Example
    -------
    ::

        result = ss.run_simulation(biomodel, sim.name, run_name="my_run")
        out = ss.export_result_to_csv(result)
        # CSVs are at workspace/my_run/exported/SimID_*__Slice_XY_0_CPCa_0000.csv, …

    Notes
    -----
    Composite summary functions (``CPC_all``, ``CPCa_total``, etc.) are
    **not** stored in the zarr.  Use :func:`compute_summary_functions` to
    derive them from species arrays, then pass the result to
    :func:`export_arrays_to_csv`.
    """
    solver_dir = Path(result.solver_output_dir)
    out = Path(output_dir) if output_dir is not None else solver_dir / "exported"
    out.mkdir(parents=True, exist_ok=True)

    # build label → channel map
    label_to_ch = {ch.label: ch for ch in result.channel_data}
    export_labels = species_list if species_list is not None else DEFAULT_SPECIES

    z = result.zarr_dataset          # (T, C, Z, X, Y)
    times = result.time_points       # list[float]
    sim_id = f"{result.sim_id}_{result.job_id}"
    run_name = solver_dir.name

    found: list[str] = []
    missing: list[str] = []

    for label in export_labels:
        if label not in label_to_ch:
            missing.append(label)
            continue

        ch_idx = label_to_ch[label].index
        found.append(label)

        for t_idx, t_val in enumerate(times):
            # zarr[time, channel, z_slice, X, Y] → squeeze z → (X, Y)
            arr = np.asarray(z[t_idx, ch_idx, 0, :, :])

            header = (
                f"Run: {run_name}\n"
                f"SimID: {sim_id}\n"
                f"Sim time range ({times[0]} {times[-1]}) "
                f"(saved timepoints {len(times)})\n"
                f"2D Slice for variable {label} at time {t_val} "
                f"in plane XY at Z = 0\n"
                "X in rows, Y in columns\n"
            )
            fname = out / f"SimID_{sim_id}__Slice_XY_0_{label}_{t_idx:04d}.csv"
            with open(fname, "w") as fh:
                fh.write(header)
            pd.DataFrame(arr).to_csv(fname, index=False, header=False, mode="a")

    print(
        f"Exported {len(found)} variable(s) × {len(times)} timepoint(s) → {out}"
    )
    if missing:
        _summary_missing = [m for m in missing if m in SUMMARY_FUNCTIONS]
        _other_missing = [m for m in missing if m not in SUMMARY_FUNCTIONS]
        if _other_missing:
            print(f"  Warning – labels not found in zarr (skipped): {_other_missing}")
        if _summary_missing:
            print(
                f"  Note – summary functions not in zarr (use compute_summary_functions): "
                f"{_summary_missing}"
            )
    return out


def export_arrays_to_csv(
    arrays: dict[str, np.ndarray],
    times: list[float],
    sim_id: str,
    run_name: str,
    output_dir: Union[str, Path],
) -> Path:
    """Write a dictionary of ``(T, X, Y)`` arrays to CSV files.

    Companion to :func:`compute_summary_functions`: takes its output dict
    and writes it in the same format as :func:`export_result_to_csv`.

    Parameters
    ----------
    arrays : dict[str, np.ndarray]
        Mapping from label → array of shape ``(T, X, Y)``.
    times : list[float]
        Saved timepoint values (length must equal ``T``).
    sim_id : str
        Simulation identifier string, e.g. ``"1498686365_0"``.
    run_name : str
        Human-readable run name (used in the CSV header).
    output_dir : str | Path
        Folder where CSV files are written (created if absent).

    Returns
    -------
    Path
        Absolute path to *output_dir*.
    """
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    for label, arr in arrays.items():
        for t_idx, t_val in enumerate(times):
            header = (
                f"Run: {run_name}\n"
                f"SimID: {sim_id}\n"
                f"Sim time range ({times[0]} {times[-1]}) "
                f"(saved timepoints {len(times)})\n"
                f"2D Slice for variable {label} at time {t_val} "
                f"in plane XY at Z = 0\n"
                "X in rows, Y in columns\n"
            )
            fname = out / f"SimID_{sim_id}__Slice_XY_0_{label}_FUNCTION_{t_idx:04d}.csv"
            with open(fname, "w") as fh:
                fh.write(header)
            pd.DataFrame(arr[t_idx]).to_csv(fname, index=False, header=False, mode="a")

    print(f"Exported {len(arrays)} function(s) × {len(times)} timepoint(s) → {out}")
    return out


# ─────────────────────────────────────────────────────────────────────────────
# Composite summary functions
# ─────────────────────────────────────────────────────────────────────────────

def compute_summary_functions(result: Result) -> dict[str, np.ndarray]:
    """Compute composite summary functions from species arrays.

    These quantities are defined as ``AnnotatedFunction`` elements in the
    VCML model but are **not** stored in the zarr output.  Formulas are
    taken directly from the VCML file::

        CPC_all         = CPCa + pH2A_SGO1_CPCa + H3_CPCa + pH3_CPCa
                          + SGO1_CPCa + CPCi + pH2A_SGO1_CPCi + H3_CPCi
                          + pH3_CPCi + SGO1_CPCi
        CPCa_total      = CPCa + pH2A_SGO1_CPCa + H3_CPCa + pH3_CPCa
                          + SGO1_CPCa
        CPCi_total      = CPCi + pH2A_SGO1_CPCi + H3_CPCi + pH3_CPCi
                          + SGO1_CPCi
        bound_CPC       = pH2A_SGO1_CPCa + pH2A_SGO1_CPCi + H3_CPCa
                          + H3_CPCi + pH3_CPCa + pH3_CPCi + SGO1_CPCa
                          + SGO1_CPCi
        bound_active_CPC = pH2A_SGO1_CPCa + H3_CPCa + pH3_CPCa + SGO1_CPCa
        pH2_all         = pH2A + pH2A_SGO1 + pH2A_SGO1_CPCa + pH2A_SGO1_CPCi

    Parameters
    ----------
    result : Result
        A pyvcell ``Result`` object.

    Returns
    -------
    dict[str, np.ndarray]
        Mapping from function name → array of shape ``(T, X, Y)``.

    Example
    -------
    ::

        funcs = ss.compute_summary_functions(result)
        ss.export_arrays_to_csv(
            arrays=funcs,
            times=result.time_points,
            sim_id=f"{result.sim_id}_{result.job_id}",
            run_name=result.solver_output_dir.name,
            output_dir=result.solver_output_dir / "exported",
        )
    """
    def _g(label: str) -> np.ndarray:
        """Fetch (T, X, Y) array for *label*."""
        return get_species_array(result, label)

    CPC_all = (
        _g("CPCa") + _g("pH2A_SGO1_CPCa") + _g("H3_CPCa") + _g("pH3_CPCa")
        + _g("SGO1_CPCa")
        + _g("CPCi") + _g("pH2A_SGO1_CPCi") + _g("H3_CPCi") + _g("pH3_CPCi")
        + _g("SGO1_CPCi")
    )
    CPCa_total = (
        _g("CPCa") + _g("pH2A_SGO1_CPCa") + _g("H3_CPCa")
        + _g("pH3_CPCa") + _g("SGO1_CPCa")
    )
    CPCi_total = (
        _g("CPCi") + _g("pH2A_SGO1_CPCi") + _g("H3_CPCi")
        + _g("pH3_CPCi") + _g("SGO1_CPCi")
    )
    bound_CPC = (
        _g("pH2A_SGO1_CPCa") + _g("pH2A_SGO1_CPCi")
        + _g("H3_CPCa") + _g("H3_CPCi")
        + _g("pH3_CPCa") + _g("pH3_CPCi")
        + _g("SGO1_CPCa") + _g("SGO1_CPCi")
    )
    bound_active_CPC = (
        _g("pH2A_SGO1_CPCa") + _g("H3_CPCa")
        + _g("pH3_CPCa") + _g("SGO1_CPCa")
    )
    pH2_all = (
        _g("pH2A") + _g("pH2A_SGO1")
        + _g("pH2A_SGO1_CPCa") + _g("pH2A_SGO1_CPCi")
    )

    return {
        "CPC_all":          CPC_all,
        "CPCa_total":       CPCa_total,
        "CPCi_total":       CPCi_total,
        "bound_CPC":        bound_CPC,
        "bound_active_CPC": bound_active_CPC,
        "pH2_all":          pH2_all,
    }
