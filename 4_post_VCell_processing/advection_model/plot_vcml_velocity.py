"""
plot_vcml_velocity.py
=====================
Parse a VCell .vcml file and plot the velocity function (X and/or Y)
for any species as a function of x (at a fixed y) or y (at a fixed x).
Can also produce a 2D heatmap of velocity over the full domain, and
overlay actual VCell output CSV data for direct comparison.

Multiple SimulationSpecs are supported.  Use --simspec to select one.

Usage (command line):
    python plot_vcml_velocity.py model.vcml --list
    python plot_vcml_velocity.py model.vcml --species H2A --axis x --y 1.8
    python plot_vcml_velocity.py model.vcml --species H2A --mode 2d
    python plot_vcml_velocity.py model.vcml --species H2A --mode compare
    python plot_vcml_velocity.py model.vcml --species H2A --mode overlay \\
        --csv SimID_307011475_0__Slice_XY_0_H2A_velocityX_0000.csv

Usage (as a module):
    from plot_vcml_velocity import VCMLVelocityPlotter
    plotter = VCMLVelocityPlotter("model.vcml")
    plotter.list_simspecs()
    plotter.use_simspec("Spatial Gaussian X no cross product")
    plotter.plot_1d("H2A", axis="x", fixed_coord=1.8)
    plotter.plot_2d("H2A")
    plotter.overlay_vcell_csv("H2A",
        csv_path="SimID_307011475_0__Slice_XY_0_H2A_velocityX_0000.csv")
"""

import xml.etree.ElementTree as ET
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.patches as mpatches
import re
import argparse
import sys
from pathlib import Path

VCELL_NS = "http://sourceforge.net/projects/vcell/vcml"


# ---------------------------------------------------------------------------
# VCell expression -> NumPy-evaluable Python string
# ---------------------------------------------------------------------------

def _vcell_to_python(expr):
    """Convert a VCell boolean-arithmetic expression to numpy-evaluable Python."""
    expr = re.sub(r'\^', '**', expr)
    expr = re.sub(r'&&', '*', expr)
    expr = re.sub(r'\|\|', '+', expr)
    for fn in ('exp', 'sqrt', 'abs', 'log', 'log10', 'sin', 'cos', 'tan', 'pow'):
        expr = re.sub(r'\b' + fn + r'\b', 'np.' + fn, expr)
    expr = re.sub(r'\bmax\b', 'np.maximum', expr)
    expr = re.sub(r'\bmin\b', 'np.minimum', expr)
    return expr


# ---------------------------------------------------------------------------
# Scalar parameter resolution
# ---------------------------------------------------------------------------

def _resolve_scalar(expr, known, depth=0):
    """Resolve a string expression to float using known scalars. Returns None if impossible."""
    if depth > 20 or expr is None:
        return None
    expr = str(expr).strip()
    try:
        return float(expr)
    except ValueError:
        pass
    if re.search(r'\bx\b|\by\b|\bt\b', expr):
        return None
    subst = expr
    for name, val in known.items():
        if isinstance(val, (int, float)):
            subst = re.sub(r'\b' + re.escape(name) + r'\b', str(val), subst)
    subst = re.sub(r'\^', '**', subst)
    try:
        return float(eval(subst, {"__builtins__": {}},
                          {"max": max, "min": min, "abs": abs,
                           "exp": np.exp, "sqrt": np.sqrt}))
    except Exception:
        return None


def _iterative_resolve(raw, seed=None, passes=12):
    """Repeatedly resolve raw string expressions to floats using seed scalars."""
    resolved = dict(seed or {})
    for name, val in raw.items():
        try:
            resolved[name] = float(val)
        except (ValueError, TypeError):
            pass
    for _ in range(passes):
        changed = False
        for name, val in raw.items():
            if name in resolved:
                continue
            r = _resolve_scalar(str(val), resolved)
            if r is not None:
                resolved[name] = r
                changed = True
        if not changed:
            break
    return resolved


# ---------------------------------------------------------------------------
# VCell output CSV parser
# ---------------------------------------------------------------------------

def load_vcell_velocity_csv(csv_path):
    """
    Load a VCell 2D-slice output CSV (e.g. Slice_XY_0_H2A_velocityX_0000.csv).

    VCell CSV format:
      - Several header lines (model name, sim name, time range, variable names)
      - A blank line
      - A line "2D Slice for variable <name> at time <t> ..."
      - A blank line
      - "X in rows, Y in columns"
      - Data rows: each row is one X position, columns are Y positions

    IMPORTANT axis convention:
      In VCell, "X in rows" corresponds to the long spatial axis (chrH),
      and "Y in columns" corresponds to the short axis (chrW).
      So arr[row_i, col_j] = v(y_spatial_i, x_spatial_j) in standard (x,y) terms.
      We transpose on return so the result is indexed [x_col, y_row] -> but
      we return the raw array plus metadata so callers can choose.

    Returns
    -------
    dict with keys:
        'array'    : 2D numpy array, shape (n_vcell_rows, n_vcell_cols),
                     where rows index the chrH (spatial-Y) axis and
                     cols index the chrW (spatial-X) axis.
        'variable' : variable name string from header
        'time'     : float, simulation time
        'n_rows'   : int, number of rows (= n_y_pixels = chrH / dy)
        'n_cols'   : int, number of cols (= n_x_pixels = chrW / dx)
    """
    csv_path = Path(csv_path)
    with open(csv_path) as f:
        lines = f.readlines()

    # Find the "2D Slice" metadata line to get variable name and time
    variable = None
    time_val = 0.0
    data_start = None
    for i, line in enumerate(lines):
        m = re.search(r'2D Slice for variable\s+(\S+)\s+at time\s+([\d.eE+\-]+)', line)
        if m:
            variable = m.group(1)
            time_val = float(m.group(2))
        if 'X in rows' in line:
            data_start = i + 1
            break

    if data_start is None:
        raise ValueError(
            f"Could not find 'X in rows' marker in {csv_path.name}. "
            "Is this a VCell 2D slice CSV?"
        )

    rows = []
    for line in lines[data_start:]:
        line = line.strip()
        if not line:
            continue
        vals = [float(v) for v in line.rstrip(',').split(',')]
        rows.append(vals)

    arr = np.array(rows)
    # Drop all-NaN trailing columns (VCell sometimes adds a trailing comma)
    col_all_nan = np.all(np.isnan(arr), axis=0)
    arr = arr[:, ~col_all_nan]

    return {
        'array': arr,
        'variable': variable or csv_path.stem,
        'time': time_val,
        'n_rows': arr.shape[0],   # spatial-Y (chrH) direction
        'n_cols': arr.shape[1],   # spatial-X (chrW) direction
    }


# ---------------------------------------------------------------------------
# Main plotter class
# ---------------------------------------------------------------------------

class VCMLVelocityPlotter:
    """
    Parse a VCell .vcml file and evaluate/plot velocity expressions for
    any SimulationSpec and species.
    """

    def __init__(self, vcml_path):
        self.vcml_path = Path(vcml_path)
        self._tree = ET.parse(vcml_path)
        self._root = self._tree.getroot()

        self._model_param_raw = {}
        self._global_params = {}
        # simspec_name -> {"params": dict, "funcs": dict, "velocities": dict}
        self._simspecs = {}
        self._active_simspec = ""

        self._parse_model_params()
        self._parse_all_simspecs()
        if self._simspecs:
            self._active_simspec = list(self._simspecs.keys())[0]

    @staticmethod
    def _tag(local):
        return f"{{{VCELL_NS}}}{local}"

    def _parse_model_params(self):
        raw = {}
        for p in self._root.iter(self._tag("Parameter")):
            name = p.get("Name")
            if name and p.text:
                raw[name] = p.text.strip()
        self._model_param_raw = raw
        self._global_params = _iterative_resolve(raw)

    def _parse_all_simspecs(self):
        for ss in self._root.iter(self._tag("SimulationSpec")):
            ss_name = ss.get("Name", "unnamed")
            math = ss.find(self._tag("MathDescription"))
            if math is None:
                continue
            func_raw = {}
            for fn in math.iter(self._tag("Function")):
                fname = fn.get("Name", "")
                if fn.text:
                    func_raw[fname] = fn.text.strip()
            math_params = _iterative_resolve(func_raw, seed=dict(self._global_params))
            velocities = {}
            for fname, fexpr in func_raw.items():
                if fname.endswith("_velocityX"):
                    sp = fname[:-len("_velocityX")]
                    velocities.setdefault(sp, {})["X"] = fexpr
                elif fname.endswith("_velocityY"):
                    sp = fname[:-len("_velocityY")]
                    velocities.setdefault(sp, {})["Y"] = fexpr
            self._simspecs[ss_name] = {
                "params": math_params,
                "funcs": func_raw,
                "velocities": velocities,
            }

    # ------------------------------------------------------------------
    # SimulationSpec selection
    # ------------------------------------------------------------------

    def list_simspecs(self):
        print(f"\nSimulationSpecs in {self.vcml_path.name}:")
        for name, data in self._simspecs.items():
            marker = " <-- active" if name == self._active_simspec else ""
            print(f"  '{name}'  ({len(data['velocities'])} species with velocity){marker}")
        print()

    def use_simspec(self, name):
        if name not in self._simspecs:
            raise ValueError(
                f"SimulationSpec '{name}' not found. "
                f"Available: {list(self._simspecs.keys())}"
            )
        self._active_simspec = name

    @property
    def _active(self):
        return self._simspecs[self._active_simspec]

    @property
    def params(self):
        return self._active["params"]

    @property
    def species_list(self):
        return sorted(self._active["velocities"].keys())

    # ------------------------------------------------------------------
    # Domain
    # ------------------------------------------------------------------

    @property
    def x_min(self):
        return 0.0

    @property
    def x_max(self):
        return self.params.get("chrW", 1.3)

    @property
    def y_min(self):
        return 0.0

    @property
    def y_max(self):
        return self.params.get("chrH", 4.5)

    # ------------------------------------------------------------------
    # Species listing
    # ------------------------------------------------------------------

    def list_species(self):
        vd = self._active["velocities"]
        print(f"\nSpecies with velocity definitions  [simspec: '{self._active_simspec}']")
        print(f"  {'Species':<40} {'Has V_x':<10} {'Has V_y'}")
        print("  " + "-" * 62)
        for sp in sorted(vd):
            vx = "yes" if "X" in vd[sp] else "no"
            vy = "yes" if "Y" in vd[sp] else "no"
            print(f"  {sp:<40} {vx:<10} {vy}")
        print()

    def get_velocity_expr(self, species, component="X"):
        vd = self._active["velocities"]
        if species not in vd:
            raise ValueError(
                f"Species '{species}' not found in simspec '{self._active_simspec}'. "
                f"Use list_species() to see available species."
            )
        comp = component.upper()
        if comp not in vd[species]:
            raise ValueError(
                f"No velocity component '{comp}' defined for '{species}' "
                f"in simspec '{self._active_simspec}'."
            )
        return vd[species][comp]

    # ------------------------------------------------------------------
    # Expression evaluation
    # ------------------------------------------------------------------

    def _eval_namespace(self, x, y):
        ns = dict(np=np)
        ns.update(self.params)
        ns["x"] = x
        ns["y"] = y
        return ns

    def _evaluate(self, expr, x, y):
        """Evaluate a velocity expression, inlining x/y-dependent Function refs."""
        py_expr = _vcell_to_python(expr)
        ns = self._eval_namespace(x, y)
        func_raw = self._active["funcs"]
        for _ in range(10):
            tokens = re.findall(r'\b([A-Za-z_][A-Za-z0-9_]*)\b', py_expr)
            missing = [n for n in tokens
                       if n not in ns and n != "np" and n in func_raw]
            if not missing:
                break
            for fname in missing:
                sub_py = _vcell_to_python(func_raw[fname])
                py_expr = re.sub(r'\b' + re.escape(fname) + r'\b',
                                 f'({sub_py})', py_expr)
        result = eval(py_expr, {"__builtins__": {}}, ns)
        return np.asarray(result, dtype=float)

    # ------------------------------------------------------------------
    # Region annotation helpers
    # ------------------------------------------------------------------

    def _kt_bounds(self):
        p = self.params
        kin_y1 = p.get("kin_y1")
        kin_y2 = p.get("kin_y2")
        L_x1   = p.get("L_kin_x1", p.get("edge", 0.0))
        L_x2   = p.get("L_kin_x2")
        R_x1   = p.get("R_kin_x1")
        R_x2   = p.get("R_kin_x2")
        if None in (kin_y1, kin_y2, L_x2, R_x1, R_x2):
            return None
        return kin_y1, kin_y2, L_x1, L_x2, R_x1, R_x2

    def _shade_kt_regions_1d(self, ax, sweep_axis):
        bounds = self._kt_bounds()
        if bounds is None:
            return
        kin_y1, kin_y2, L_x1, L_x2, R_x1, R_x2 = bounds
        kw = dict(alpha=0.12, color="#444444")
        ylim = ax.get_ylim()
        if sweep_axis == "x":
            ax.axvspan(L_x1, L_x2, **kw)
            ax.axvspan(R_x1, R_x2, **kw)
            for mid, lbl in (((L_x1 + L_x2) / 2, "L-KT"),
                              ((R_x1 + R_x2) / 2, "R-KT")):
                ax.text(mid, ylim[1], lbl, ha="center", va="top",
                        fontsize=7, color="#333333")
        else:
            ax.axvspan(kin_y1, kin_y2, **kw)
            ax.text((kin_y1 + kin_y2) / 2, ylim[1], "KT",
                    ha="center", va="top", fontsize=7, color="#333333")

    def _draw_kt_boxes(self, ax):
        bounds = self._kt_bounds()
        if bounds is None:
            return
        kin_y1, kin_y2, L_x1, L_x2, R_x1, R_x2 = bounds
        kw = dict(linewidth=1.5, edgecolor="k", facecolor="none", ls="--")
        ax.add_patch(mpatches.Rectangle(
            (L_x1, kin_y1), L_x2 - L_x1, kin_y2 - kin_y1, **kw))
        ax.add_patch(mpatches.Rectangle(
            (R_x1, kin_y1), R_x2 - R_x1, kin_y2 - kin_y1, **kw))

    # ------------------------------------------------------------------
    # 1D line plot
    # ------------------------------------------------------------------

    def plot_1d(
        self,
        species,
        axis="x",
        fixed_coord=None,
        component="X",
        n_points=500,
        ax=None,
        save_path=None,
        title=None,
        show_regions=True,
    ):
        """
        Plot velocity component vs. one spatial axis.

        Parameters
        ----------
        species : str, list of str, or "all"
        axis : "x" | "y"   -- the axis to sweep
        fixed_coord : float, optional  (defaults to domain midpoint)
        component : "X" | "Y"
        n_points : int
        ax : matplotlib Axes, optional
        save_path : str, optional
        title : str, optional
        show_regions : bool
        """
        if species == "all":
            slist = self.species_list
        elif isinstance(species, str):
            slist = [species]
        else:
            slist = list(species)

        axis = axis.lower()
        component = component.upper()

        if fixed_coord is None:
            fixed_coord = (self.y_max / 2.0) if axis == "x" else (self.x_max / 2.0)

        if axis == "x":
            sweep = np.linspace(self.x_min, self.x_max, n_points)
            x_arr, y_arr = sweep, np.full_like(sweep, fixed_coord)
            xlabel = "x (um)"
            fixed_label = f"y = {fixed_coord:.4f} um"
        else:
            sweep = np.linspace(self.y_min, self.y_max, n_points)
            x_arr, y_arr = np.full_like(sweep, fixed_coord), sweep
            xlabel = "y (um)"
            fixed_label = f"x = {fixed_coord:.4f} um"

        if ax is None:
            fig, ax = plt.subplots(figsize=(9, 4))
        else:
            fig = ax.get_figure()

        plotted = 0
        for sp in slist:
            if component not in self._active["velocities"].get(sp, {}):
                continue
            try:
                vel = self._evaluate(
                    self._active["velocities"][sp][component], x_arr, y_arr
                )
                ax.plot(sweep, vel, label=sp, lw=1.5)
                plotted += 1
            except Exception as exc:
                print(f"  Warning: could not evaluate {sp}: {exc}")

        if plotted == 0:
            print("No species could be evaluated.")
            return fig, ax

        ax.axhline(0, color="k", lw=0.5, ls="--")
        ax.set_xlabel(xlabel, fontsize=12)
        ax.set_ylabel(f"V_{component.lower()} (um/s)", fontsize=12)
        ax.set_title(
            title or (
                f"V_{component.lower()} vs {axis}  |  {fixed_label}\n"
                f"[simspec: {self._active_simspec}]"
            ),
            fontsize=11,
        )
        if show_regions:
            self._shade_kt_regions_1d(ax, axis)
        if len(slist) <= 20:
            ax.legend(fontsize=8, ncol=2, loc="best")
        ax.tick_params(labelsize=10)
        plt.tight_layout()
        if save_path:
            fig.savefig(save_path, dpi=150, bbox_inches="tight")
            print(f"Saved: {save_path}")
        return fig, ax

    # ------------------------------------------------------------------
    # 2D heatmap
    # ------------------------------------------------------------------

    def plot_2d(
        self,
        species,
        component="X",
        nx=200,
        ny=400,
        save_path=None,
        title=None,
        cmap="RdBu_r",
        symmetric_clim=True,
    ):
        """2D colour map of a velocity component over the full (x, y) domain."""
        component = component.upper()
        expr = self.get_velocity_expr(species, component)

        x1d = np.linspace(self.x_min, self.x_max, nx)
        y1d = np.linspace(self.y_min, self.y_max, ny)
        xx, yy = np.meshgrid(x1d, y1d)
        vel = self._evaluate(expr, xx, yy)

        fig, ax = plt.subplots(figsize=(4, 8))
        if symmetric_clim:
            vmax = float(np.nanmax(np.abs(vel)))
            vmax = vmax if vmax > 0 else 1.0
            norm = mcolors.TwoSlopeNorm(vmin=-vmax, vcenter=0.0, vmax=vmax)
        else:
            norm = None

        im = ax.pcolormesh(xx, yy, vel, cmap=cmap, norm=norm, shading="auto")
        fig.colorbar(im, ax=ax, label=f"V_{component.lower()} (um/s)")
        ax.set_xlabel("x (um)", fontsize=12)
        ax.set_ylabel("y (um)", fontsize=12)
        ax.set_title(
            title or f"{species}  V_{component.lower()}\n[{self._active_simspec}]",
            fontsize=11,
        )
        ax.set_aspect("equal")
        self._draw_kt_boxes(ax)
        plt.tight_layout()
        if save_path:
            fig.savefig(save_path, dpi=150, bbox_inches="tight")
            print(f"Saved: {save_path}")
        return fig, ax

    # ------------------------------------------------------------------
    # Quiver plot
    # ------------------------------------------------------------------

    def plot_quiver(self, species, nx=30, ny=60, save_path=None, title=None):
        """Vector field quiver plot.  Uses both X and Y if available."""
        vd = self._active["velocities"].get(species, {})
        x1d = np.linspace(self.x_min, self.x_max, nx)
        y1d = np.linspace(self.y_min, self.y_max, ny)
        xx, yy = np.meshgrid(x1d, y1d)

        vx = self._evaluate(vd["X"], xx, yy) if "X" in vd else np.zeros_like(xx)
        vy = self._evaluate(vd["Y"], xx, yy) if "Y" in vd else np.zeros_like(yy)

        fig, ax = plt.subplots(figsize=(4, 8))
        speed = np.sqrt(vx**2 + vy**2)
        ax.quiver(xx, yy, vx, vy, speed, cmap="viridis")
        ax.set_xlabel("x (um)", fontsize=12)
        ax.set_ylabel("y (um)", fontsize=12)
        ax.set_title(title or f"{species} velocity field\n[{self._active_simspec}]",
                     fontsize=11)
        ax.set_aspect("equal")
        self._draw_kt_boxes(ax)
        plt.tight_layout()
        if save_path:
            fig.savefig(save_path, dpi=150, bbox_inches="tight")
        return fig, ax

    # ------------------------------------------------------------------
    # Multi-simspec comparison
    # ------------------------------------------------------------------

    def compare_simspecs(
        self,
        species,
        axis="x",
        fixed_coord=None,
        component="X",
        n_points=500,
        save_path=None,
    ):
        """Plot V_x (or V_y) vs x (or y) for every SimulationSpec side by side."""
        n = len(self._simspecs)
        fig, axes = plt.subplots(1, n, figsize=(5 * n, 4), sharey=True)
        if n == 1:
            axes = [axes]

        original = self._active_simspec
        for ax_i, ssname in zip(axes, self._simspecs.keys()):
            self.use_simspec(ssname)
            try:
                self.plot_1d(species, axis=axis, fixed_coord=fixed_coord,
                             component=component, n_points=n_points, ax=ax_i,
                             title=ssname, show_regions=True)
            except Exception as exc:
                ax_i.set_title(f"{ssname}\n(error: {exc})", fontsize=9)
        self.use_simspec(original)

        fig.suptitle(
            f"{species}  V_{component.lower()} vs {axis} - all SimulationSpecs",
            fontsize=12, y=1.02,
        )
        plt.tight_layout()
        if save_path:
            fig.savefig(save_path, dpi=150, bbox_inches="tight")
            print(f"Saved: {save_path}")
        return fig, axes

    # ------------------------------------------------------------------
    # VCell CSV overlay  (new function)
    # ------------------------------------------------------------------

    def overlay_vcell_csv(
        self,
        species,
        csv_path,
        component="X",
        axis="x",
        fixed_coord=None,
        n_points=500,
        save_path=None,
        title=None,
        show_2d=True,
        show_1d=True,
    ):
        """
        Overlay actual VCell simulation output against the analytic velocity
        expression, both as a 1D line comparison and a side-by-side 2D map.

        VCell CSV axis convention
        -------------------------
        VCell exports 2D slices with "X in rows, Y in columns".
        In VCell's coordinate system for this chromosome model:
          - Rows index the long axis (chrH, spatial Y in our convention)
          - Cols index the short axis (chrW, spatial X in our convention)
        So: csv_array[row_i, col_j] = velocity at (x = col_j * dx, y = row_i * dy)

        Parameters
        ----------
        species : str
            Species name to evaluate from the vcml (e.g. "H2A").
        csv_path : str or Path
            Path to the VCell output CSV slice file.
        component : "X" | "Y"
            Velocity component.
        axis : "x" | "y"
            Axis to sweep for the 1D comparison plot.
        fixed_coord : float, optional
            Fixed value of the other coordinate for the 1D slice.
            Defaults to the domain midpoint along the non-swept axis.
        n_points : int
            Resolution of the analytic curve in the 1D plot.
        save_path : str, optional
            If given, save the figure to this path.
        title : str, optional
            Override the figure suptitle.
        show_2d : bool
            Include side-by-side 2D heatmap panels (default True).
        show_1d : bool
            Include 1D line comparison panel (default True).
        """
        component = component.upper()
        axis = axis.lower()

        # -- Load CSV data --------------------------------------------------
        csv_data = load_vcell_velocity_csv(csv_path)
        arr = csv_data['array']          # shape (n_rows, n_cols)
                                         # rows = spatial-Y (chrH), cols = spatial-X (chrW)
        n_rows, n_cols = arr.shape       # n_rows ~ chrH/dy, n_cols ~ chrW/dx

        # Build spatial coordinate arrays matching the CSV grid
        x_csv = np.linspace(self.x_min, self.x_max, n_cols)   # chrW axis
        y_csv = np.linspace(self.y_min, self.y_max, n_rows)    # chrH axis

        # -- Evaluate analytic velocity on the same grid --------------------
        xx_csv, yy_csv = np.meshgrid(x_csv, y_csv)   # shapes (n_rows, n_cols)
        expr = self.get_velocity_expr(species, component)
        vel_analytic = self._evaluate(expr, xx_csv, yy_csv)

        # -- Difference map -------------------------------------------------
        diff = vel_analytic - arr

        # -- Set up figure layout -------------------------------------------
        n_panels = (2 if show_2d else 0) + (1 if show_2d else 0) + (1 if show_1d else 0)
        # Always do: [analytic 2D] [csv 2D] [diff 2D] [1D comparison]
        has_2d = show_2d
        has_1d = show_1d

        if has_2d and has_1d:
            fig = plt.figure(figsize=(16, 8))
            ax_a  = fig.add_subplot(1, 4, 1)   # analytic 2D
            ax_c  = fig.add_subplot(1, 4, 2)   # VCell CSV 2D
            ax_d  = fig.add_subplot(1, 4, 3)   # difference
            ax_1d = fig.add_subplot(1, 4, 4)   # 1D line
        elif has_2d:
            fig = plt.figure(figsize=(12, 8))
            ax_a = fig.add_subplot(1, 3, 1)
            ax_c = fig.add_subplot(1, 3, 2)
            ax_d = fig.add_subplot(1, 3, 3)
            ax_1d = None
        else:
            fig, ax_1d = plt.subplots(figsize=(9, 4))
            ax_a = ax_c = ax_d = None

        # Shared colour scale for analytic and CSV panels
        vmax = max(float(np.nanmax(np.abs(vel_analytic))),
                   float(np.nanmax(np.abs(arr))))
        if vmax == 0:
            vmax = 1.0
        norm_vel = mcolors.TwoSlopeNorm(vmin=-vmax, vcenter=0.0, vmax=vmax)

        dmax = float(np.nanmax(np.abs(diff)))
        if dmax == 0:
            dmax = 1.0
        norm_diff = mcolors.TwoSlopeNorm(vmin=-dmax, vcenter=0.0, vmax=dmax)

        cmap_vel  = "RdBu_r"
        cmap_diff = "PiYG"

        # -- 2D panels -------------------------------------------------------
        if has_2d:
            for ax_panel, data, panel_title, norm, cmap in [
                (ax_a,  vel_analytic, f"Analytic\n{species} V_{component.lower()}", norm_vel,  cmap_vel),
                (ax_c,  arr,          f"VCell output\n(t={csv_data['time']:.1f} s)",norm_vel,  cmap_vel),
                (ax_d,  diff,         "Analytic - VCell",                           norm_diff, cmap_diff),
            ]:
                im = ax_panel.pcolormesh(xx_csv, yy_csv, data,
                                         cmap=cmap, norm=norm, shading="auto")
                fig.colorbar(im, ax=ax_panel,
                             label=f"V_{component.lower()} (um/s)", shrink=0.6)
                ax_panel.set_xlabel("x (um)", fontsize=10)
                ax_panel.set_ylabel("y (um)", fontsize=10)
                ax_panel.set_title(panel_title, fontsize=10)
                ax_panel.set_aspect("equal")
                self._draw_kt_boxes(ax_panel)

        # -- 1D comparison panel --------------------------------------------
        if has_1d:
            if fixed_coord is None:
                fixed_coord = (self.y_max / 2.0) if axis == "x" else (self.x_max / 2.0)

            if axis == "x":
                # Sweep across x, find the nearest row in the CSV data
                sweep = np.linspace(self.x_min, self.x_max, n_points)
                x_eval = sweep
                y_eval = np.full_like(sweep, fixed_coord)
                xlabel = "x (um)"
                fixed_label = f"y = {fixed_coord:.4f} um"

                # Extract the CSV row nearest to fixed_coord
                row_idx = int(round(fixed_coord / self.y_max * (n_rows - 1)))
                row_idx = np.clip(row_idx, 0, n_rows - 1)
                csv_1d = arr[row_idx, :]          # shape (n_cols,)
                csv_sweep = x_csv                  # x coordinates
                actual_y = y_csv[row_idx]
                slice_desc = (f"y = {fixed_coord:.4f} um  "
                              f"(CSV row {row_idx}, y_actual = {actual_y:.4f} um)")
            else:
                # Sweep across y, find the nearest col in the CSV data
                sweep = np.linspace(self.y_min, self.y_max, n_points)
                x_eval = np.full_like(sweep, fixed_coord)
                y_eval = sweep
                xlabel = "y (um)"
                fixed_label = f"x = {fixed_coord:.4f} um"

                col_idx = int(round(fixed_coord / self.x_max * (n_cols - 1)))
                col_idx = np.clip(col_idx, 0, n_cols - 1)
                csv_1d = arr[:, col_idx]           # shape (n_rows,)
                csv_sweep = y_csv                  # y coordinates
                actual_x = x_csv[col_idx]
                slice_desc = (f"x = {fixed_coord:.4f} um  "
                              f"(CSV col {col_idx}, x_actual = {actual_x:.4f} um)")

            # Evaluate analytic on the 1D sweep
            vel_1d = self._evaluate(expr, x_eval, y_eval)

            ax_1d.plot(sweep, vel_1d, lw=2, color="steelblue", label="Analytic (vcml)")
            ax_1d.plot(csv_sweep, csv_1d, lw=1.5, color="tomato",
                       ls="--", label=f"VCell output (t={csv_data['time']:.1f} s)")
            ax_1d.axhline(0, color="k", lw=0.5, ls=":")
            ax_1d.set_xlabel(xlabel, fontsize=11)
            ax_1d.set_ylabel(f"V_{component.lower()} (um/s)", fontsize=11)
            ax_1d.set_title(
                f"1D slice: {slice_desc}", fontsize=9
            )
            ax_1d.legend(fontsize=9)
            ax_1d.tick_params(labelsize=9)
            self._shade_kt_regions_1d(ax_1d, axis)

            # Print RMS difference for the 1D slice
            rms = float(np.sqrt(np.nanmean((vel_1d - np.interp(sweep, csv_sweep, csv_1d))**2)))
            print(f"  1D slice RMS difference (analytic - VCell): {rms:.6f} um/s")

        # -- Overall stats ---------------------------------------------------
        rms_2d = float(np.sqrt(np.nanmean(diff**2)))
        max_diff = float(np.nanmax(np.abs(diff)))
        print(f"  2D grid RMS difference: {rms_2d:.6f} um/s")
        print(f"  2D grid max |difference|: {max_diff:.6f} um/s")

        fig.suptitle(
            title or (
                f"{species}  V_{component.lower()} comparison: analytic vs VCell output\n"
                f"[simspec: {self._active_simspec}]"
            ),
            fontsize=11, y=1.01,
        )
        plt.tight_layout()
        if save_path:
            fig.savefig(save_path, dpi=150, bbox_inches="tight")
            print(f"Saved: {save_path}")
        return fig

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def print_params(self, simspec=None):
        ss = simspec or self._active_simspec
        p = self._simspecs[ss]["params"]
        print(f"\nResolved parameters  [simspec: {ss}]")
        for k, v in sorted(p.items()):
            print(f"  {k:<40} = {v}")
        print()


# ---------------------------------------------------------------------------
# Standalone: compare any custom velocity function against a VCell CSV
# ---------------------------------------------------------------------------

def compare_custom_velocity(
    csv_path,
    custom_velocity,
    axis="x",
    fixed_coord=None,
    n_points=500,
    x_range=(0.0, 1.3),
    y_range=(0.0, 3.6),
    extra_params=None,
    component_label="x",
    csv_label=None,
    custom_label="Custom expression",
    save_path=None,
    title=None,
    kt_bounds=None,
):
    """
    Compare any custom velocity function against a VCell output CSV slice,
    producing the same 1D line-comparison plot as the rightmost panel of
    overlay_vcell_csv().

    This is a fully standalone function — it does not require a vcml file
    or a VCMLVelocityPlotter instance.

    Parameters
    ----------
    csv_path : str or Path
        Path to a VCell 2D-slice output CSV file.

    custom_velocity : str or callable
        The velocity function to evaluate.  Three forms are accepted:

        1. VCell-style string  (&&, ^, boolean masks as 0/1):
               "((x - x_mid) / delT) * ((y >= kin_y1) && (y <= kin_y2))"
           Named parameters must be supplied via `extra_params`.

        2. Python/numpy string  (uses np., **, standard comparisons):
               "(x - 0.65) / 17.1 * (y >= 1.65) * (y <= 1.95)"
           Named parameters must be supplied via `extra_params`.

        3. Python callable  f(x, y) -> array:
               lambda x, y: (x - 0.65) / 17.1 * (y >= 1.65) * (y <= 1.95)
           x and y will be passed as numpy arrays.

    axis : "x" | "y"
        Which spatial axis to sweep in the 1D plot.

    fixed_coord : float, optional
        Fixed value of the other coordinate.  Defaults to midpoint of that
        axis range.

    n_points : int
        Number of evaluation points along the sweep axis (default 500).

    x_range : (float, float)
        (x_min, x_max) of the spatial domain in um.  Default (0.0, 1.3).

    y_range : (float, float)
        (y_min, y_max) of the spatial domain in um.  Default (0.0, 3.6).

    extra_params : dict, optional
        Named scalar parameters available to string expressions.
        Example: {"x_mid": 0.65, "delT": 17.1, "kin_y1": 1.65, "kin_y2": 1.95}

    component_label : str
        Label for the velocity component axis (default "x").

    csv_label : str, optional
        Legend label for the VCell data line.  Defaults to filename + time.

    custom_label : str
        Legend label for the custom expression line (default "Custom expression").

    save_path : str, optional
        If given, save the figure to this path.

    title : str, optional
        Override the default plot title.

    kt_bounds : tuple or None, optional
        Kinetochore region bounds for shading:
        (kin_y1, kin_y2, L_x1, L_x2, R_x1, R_x2)  -- all in um.
        Shading is skipped if None.

    Returns
    -------
    fig : matplotlib Figure
    ax  : matplotlib Axes

    Examples
    --------
    # VCell-style string with named params:
    compare_custom_velocity(
        "myfile.csv",
        custom_velocity="((x - x_mid) / delT) * ((y >= kin_y1) && (y <= kin_y2))",
        extra_params={"x_mid": 0.65, "delT": 17.1, "kin_y1": 1.65, "kin_y2": 1.95},
        axis="x", fixed_coord=1.8,
    )

    # Python/numpy string:
    compare_custom_velocity(
        "myfile.csv",
        custom_velocity="(x - 0.65) / 17.1 * (y >= 1.65) * (y <= 1.95)",
        axis="x", fixed_coord=1.8,
    )

    # Python callable:
    compare_custom_velocity(
        "myfile.csv",
        custom_velocity=lambda x, y: (x - 0.65) / 17.1 * (y >= 1.65) * (y <= 1.95),
        axis="x", fixed_coord=1.8,
    )
    """
    # -- Determine how to call the custom velocity --------------------------
    if callable(custom_velocity):
        def _eval_custom(x, y):
            return np.asarray(custom_velocity(x, y), dtype=float)
    else:
        # String: auto-detect VCell vs Python by presence of && or ^
        expr_str = str(custom_velocity)
        is_vcell = ("&&" in expr_str or "^" in expr_str)
        if is_vcell:
            py_expr = _vcell_to_python(expr_str)
        else:
            py_expr = expr_str

        params = dict(extra_params or {})

        def _eval_custom(x, y):
            ns = dict(np=np)
            ns.update(params)
            ns["x"] = x
            ns["y"] = y
            result = eval(py_expr, {"__builtins__": {}}, ns)
            return np.asarray(result, dtype=float)

    # -- Load CSV -----------------------------------------------------------
    csv_data = load_vcell_velocity_csv(csv_path)
    arr      = csv_data["array"]          # shape (n_rows=chrH, n_cols=chrW)
    n_rows, n_cols = arr.shape

    x_min, x_max = x_range
    y_min, y_max = y_range

    x_csv = np.linspace(x_min, x_max, n_cols)
    y_csv = np.linspace(y_min, y_max, n_rows)

    # -- Set up 1D slice ----------------------------------------------------
    axis = axis.lower()
    if fixed_coord is None:
        fixed_coord = ((y_max + y_min) / 2.0) if axis == "x" else ((x_max + x_min) / 2.0)

    if axis == "x":
        sweep       = np.linspace(x_min, x_max, n_points)
        x_eval      = sweep
        y_eval      = np.full_like(sweep, fixed_coord)
        xlabel      = "x (um)"
        fixed_label = f"y = {fixed_coord:.4f} um"

        row_idx  = int(round((fixed_coord - y_min) / (y_max - y_min) * (n_rows - 1)))
        row_idx  = int(np.clip(row_idx, 0, n_rows - 1))
        csv_1d   = arr[row_idx, :]
        csv_x    = x_csv
        actual_fixed = y_csv[row_idx]
        slice_desc   = (f"y = {fixed_coord:.4f} um  "
                        f"(CSV row {row_idx}, y_actual = {actual_fixed:.4f} um)")
    else:
        sweep       = np.linspace(y_min, y_max, n_points)
        x_eval      = np.full_like(sweep, fixed_coord)
        y_eval      = sweep
        xlabel      = "y (um)"
        fixed_label = f"x = {fixed_coord:.4f} um"

        col_idx  = int(round((fixed_coord - x_min) / (x_max - x_min) * (n_cols - 1)))
        col_idx  = int(np.clip(col_idx, 0, n_cols - 1))
        csv_1d   = arr[:, col_idx]
        csv_x    = y_csv
        actual_fixed = x_csv[col_idx]
        slice_desc   = (f"x = {fixed_coord:.4f} um  "
                        f"(CSV col {col_idx}, x_actual = {actual_fixed:.4f} um)")

    # -- Evaluate custom velocity on the 1D sweep ---------------------------
    vel_custom = _eval_custom(x_eval, y_eval)

    # -- Build default CSV label --------------------------------------------
    if csv_label is None:
        fname = Path(csv_path).name
        csv_label = f"VCell output: {fname}  (t={csv_data['time']:.1f} s)"

    # -- Plot ---------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(8, 4))

    ax.plot(sweep, vel_custom, lw=2.0, color="steelblue", label=custom_label)
    ax.plot(csv_x, csv_1d,    lw=1.5, color="tomato", ls="--", label=csv_label)
    ax.axhline(0, color="k", lw=0.5, ls=":")

    ax.set_xlabel(xlabel, fontsize=12)
    ax.set_ylabel(f"V_{component_label} (um/s)", fontsize=12)
    ax.set_title(title or f"1D slice: {slice_desc}", fontsize=10)
    ax.legend(fontsize=9)
    ax.tick_params(labelsize=10)

    # -- Shade kinetochore regions if bounds provided -----------------------
    if kt_bounds is not None:
        kin_y1, kin_y2, L_x1, L_x2, R_x1, R_x2 = kt_bounds
        kw = dict(alpha=0.12, color="#444444")
        ylim = ax.get_ylim()
        if axis == "x":
            ax.axvspan(L_x1, L_x2, **kw)
            ax.axvspan(R_x1, R_x2, **kw)
            for mid, lbl in (((L_x1 + L_x2) / 2, "L-KT"),
                              ((R_x1 + R_x2) / 2, "R-KT")):
                ax.text(mid, ylim[1], lbl, ha="center", va="top",
                        fontsize=7, color="#333333")
        else:
            ax.axvspan(kin_y1, kin_y2, **kw)
            ax.text((kin_y1 + kin_y2) / 2, ylim[1], "KT",
                    ha="center", va="top", fontsize=7, color="#333333")

    # -- Print stats --------------------------------------------------------
    csv_interp = np.interp(sweep, csv_x, csv_1d)
    rms  = float(np.sqrt(np.nanmean((vel_custom - csv_interp) ** 2)))
    maxd = float(np.nanmax(np.abs(vel_custom - csv_interp)))
    print(f"  RMS difference (custom - VCell): {rms:.6f} um/s")
    print(f"  Max |difference|:                {maxd:.6f} um/s")

    plt.tight_layout()
    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches="tight")
        print(f"Saved: {save_path}")
    return fig, ax


# ---------------------------------------------------------------------------
# Command-line interface
# ---------------------------------------------------------------------------

def _build_parser():
    p = argparse.ArgumentParser(
        description="Plot VCell VCML velocity functions.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List SimulationSpecs and their species:
  python plot_vcml_velocity.py model.vcml --list

  # 1D sweep V_x vs x (y fixed at midpoint):
  python plot_vcml_velocity.py model.vcml --species H2A

  # Fix y at a specific value:
  python plot_vcml_velocity.py model.vcml --species H2A --axis x --y 1.8

  # Sweep vs y at a fixed x:
  python plot_vcml_velocity.py model.vcml --species H2A --axis y --x 0.65

  # All species on one axes:
  python plot_vcml_velocity.py model.vcml --species all --axis x --y 1.8

  # Pick a specific SimulationSpec:
  python plot_vcml_velocity.py model.vcml --species H2A \\
      --simspec "Spatial Gaussian X no cross product"

  # Compare all SimulationSpecs side by side:
  python plot_vcml_velocity.py model.vcml --species H2A --mode compare

  # 2D heatmap:
  python plot_vcml_velocity.py model.vcml --species H2A --mode 2d

  # Overlay VCell output CSV (2D maps + 1D slice):
  python plot_vcml_velocity.py model.vcml --species H2A --mode overlay \\
      --csv SimID_307011475_0__Slice_XY_0_H2A_velocityX_0000.csv

  # Overlay, 1D slice only at y=1.8:
  python plot_vcml_velocity.py model.vcml --species H2A --mode overlay \\
      --csv myfile.csv --axis x --y 1.8 --no-2d

  # Save output:
  python plot_vcml_velocity.py model.vcml --species H2A --save vel_H2A.png
""",
    )
    p.add_argument("vcml", help="Path to the .vcml file")
    p.add_argument("--species", default="H2A",
                   help="Species name, comma-separated list, or 'all'")
    p.add_argument("--component", default="X", choices=["X", "Y"],
                   help="Velocity component (default: X)")
    p.add_argument("--axis", default="x", choices=["x", "y"],
                   help="Sweep axis for 1D/compare/overlay plots (default: x)")
    p.add_argument("--x", type=float, default=None,
                   help="Fixed x for --axis y plots (default: x_mid)")
    p.add_argument("--y", type=float, default=None,
                   help="Fixed y for --axis x plots (default: y_mid)")
    p.add_argument("--mode", default="1d",
                   choices=["1d", "2d", "quiver", "compare", "overlay"],
                   help="Plot mode (default: 1d)")
    p.add_argument("--simspec", default=None,
                   help="SimulationSpec name to use (default: first one found)")
    p.add_argument("--csv", default=None,
                   help="Path to VCell output CSV slice file (for --mode overlay)")
    p.add_argument("--no-2d", action="store_true",
                   help="In overlay mode, show 1D comparison only")
    p.add_argument("--no-1d", action="store_true",
                   help="In overlay mode, show 2D maps only")
    p.add_argument("--save", default=None, help="Save figure to this path")
    p.add_argument("--list", action="store_true",
                   help="List SimulationSpecs and species, then exit")
    p.add_argument("--params", action="store_true",
                   help="Print resolved parameters and exit")
    p.add_argument("--n", type=int, default=500,
                   help="Number of points for 1D sweep (default: 500)")
    return p


def main():
    parser = _build_parser()
    args = parser.parse_args()

    plotter = VCMLVelocityPlotter(args.vcml)

    if args.simspec:
        plotter.use_simspec(args.simspec)

    if args.list:
        plotter.list_simspecs()
        plotter.list_species()
        sys.exit(0)

    if args.params:
        plotter.print_params()
        sys.exit(0)

    if args.species == "all":
        sp_arg = "all"
    elif "," in args.species:
        sp_arg = [s.strip() for s in args.species.split(",")]
    else:
        sp_arg = args.species

    if args.mode == "1d":
        fixed = args.y if args.axis == "x" else args.x
        plotter.plot_1d(sp_arg, axis=args.axis, fixed_coord=fixed,
                        component=args.component, n_points=args.n,
                        save_path=args.save)
        plt.show()

    elif args.mode == "2d":
        sp = sp_arg if isinstance(sp_arg, str) else sp_arg[0]
        plotter.plot_2d(sp, component=args.component, save_path=args.save)
        plt.show()

    elif args.mode == "quiver":
        sp = sp_arg if isinstance(sp_arg, str) else sp_arg[0]
        plotter.plot_quiver(sp, save_path=args.save)
        plt.show()

    elif args.mode == "compare":
        sp = sp_arg if isinstance(sp_arg, str) else sp_arg[0]
        fixed = args.y if args.axis == "x" else args.x
        plotter.compare_simspecs(sp, axis=args.axis, fixed_coord=fixed,
                                 component=args.component, n_points=args.n,
                                 save_path=args.save)
        plt.show()

    elif args.mode == "overlay":
        if not args.csv:
            parser.error("--mode overlay requires --csv <path>")
        sp = sp_arg if isinstance(sp_arg, str) else sp_arg[0]
        fixed = args.y if args.axis == "x" else args.x
        plotter.overlay_vcell_csv(
            sp,
            csv_path=args.csv,
            component=args.component,
            axis=args.axis,
            fixed_coord=fixed,
            n_points=args.n,
            save_path=args.save,
            show_2d=not args.no_2d,
            show_1d=not args.no_1d,
        )
        plt.show()


if __name__ == "__main__":
    main()