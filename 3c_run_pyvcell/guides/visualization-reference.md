# Visualization Reference

Quick reference for all plotting and animation options in pyvcell.

---

## Geometry

```python
geo.plot()
geo.plot(resolution=100)        # higher resolution for analytic geometries (default 50)
geo.plot(save_path="geo.png")   # save instead of (or in addition to) displaying
```

Renders each subvolume as a distinct color in a 3D PyVista scene, displayed via matplotlib.
Image-based geometries use their native pixel resolution; analytic geometries are rasterized at `resolution` grid points per axis.

---

## Simulation results

All methods are accessed via `result.plotter` after running a simulation:

```python
result = vc.simulate(biomodel, "sim_name")
p = result.plotter
```

### Concentrations over time

```python
p.plot_concentrations()
p.plot_concentrations(save_path="conc.png")
```

Line plot of mean concentration vs. time for every species/channel. One line per channel, legend included.

### 2D spatial slice

```python
p.plot_slice_2d(time_index=0, channel_name="Ran_cyt", z_index=10)
p.plot_slice_2d(time_index=5, channel_name="Ran_cyt", z_index=10, save_path="slice.png")
```

Shows a single XY plane at `z_index` for the chosen time point and species. Uses `plt.imshow()`.

| Parameter | Type | Description |
|---|---|---|
| `time_index` | int | Index into saved output time points (0-based) |
| `channel_name` | str | Species/variable label (e.g. `"s0"`, `"Ran_cyt"`) |
| `z_index` | int | Z-plane to slice through |
| `save_path` | str \| None | Optional file path to save figure |

### 3D scatter plot

```python
p.plot_slice_3d(time_index=3, channel_id="Ran_cyt")
p.plot_slice_3d(time_index=3, channel_id="Ran_cyt", save_path="3d.png")
```

Plots all spatial voxels as a 3D scatter, colored by concentration (viridis colormap). Useful for a quick spatial overview.

| Parameter | Type | Description |
|---|---|---|
| `time_index` | int | Index into saved output time points |
| `channel_id` | str | Species/variable label |
| `save_path` | str \| None | Optional file path to save figure |

### Post-processing: per-variable statistics

```python
p.plot_averages()
```

2×2 grid of envelope plots (min/mean/max shading) over time, one panel per tracked variable.

### Post-processing: image data

```python
p.plot_image(image_index=0, time_index=5)
```

Displays a 2D post-processing image (e.g. a fluorescence channel) at a given time point.

---

## Animations

All animation methods return a `matplotlib.animation.FuncAnimation` that can be displayed inline in Jupyter or saved to a file.

### Animate species over time (3D)

```python
anim = p.animate_channel_3d(channel_id="Ran_cyt")
anim = p.get_3d_slice_animation(channel_id="Ran_cyt", interval=200)  # interval in ms
```

Cycles through all saved time points as a 3D scatter animation.

```python
# Save to GIF
anim.save("output.gif", writer="pillow")

# Display inline in Jupyter
from IPython.display import HTML
HTML(anim.to_jshtml())
```

### Animate post-processing image over time

```python
anim = p.animate_image(image_index=0)
anim = p.get_image_animation(image_index=0, interval=200)
```

---

## VTK mesh visualization

Accessed via `result.vtk_data`:

```python
from pathlib import Path

# Render a single time point (saves screenshot as .png)
result.vtk_data.plot(mesh_file=Path("output.vtu"))

# Write an animation movie over all time points
result.vtk_data.write_mesh_animation(
    mesh_file=Path("output.vtu"),
    filename=Path("animation.mp4"),
)
```

---

## Interactive 3D widget (Jupyter only)

```python
from pyvcell.sim_results.widget import App

app = App(vtk_data=result.vtk_data)
await app.run(height=1000)
```

Launches a trame-based interactive viewer with:
- Variable selector dropdown
- Time slider
- Clipping slider
- Live 3D mesh with scalar coloring

Requires `trame-jupyter-extension` to be installed.

---

## Accessing raw data for custom plots

```python
# 3D numpy array (z, y, x) at a given time and channel
arr = result.get_slice(channel_id="Ran_cyt", time_index=3)

# Time points (seconds)
result.time_points   # list[float]

# Per-channel statistics (min/mean/max per time point)
for ch in result.channel_data:
    print(ch.label, ch.mean_values)

# Direct zarr access
result.zarr_dataset  # zarr.Group
```

---

## Quick-reference table

| What you want | Method | Returns |
|---|---|---|
| View geometry | `geo.plot()` | None |
| Concentration vs. time | `result.plotter.plot_concentrations()` | None |
| 2D spatial slice | `result.plotter.plot_slice_2d(t, channel, z)` | None |
| 3D spatial scatter | `result.plotter.plot_slice_3d(t, channel)` | None |
| Per-variable statistics | `result.plotter.plot_averages()` | None |
| Post-processing image | `result.plotter.plot_image(img_idx, t)` | None |
| 3D animation | `result.plotter.animate_channel_3d(channel)` | `FuncAnimation` |
| Image animation | `result.plotter.animate_image(img_idx)` | `FuncAnimation` |
| VTK mesh screenshot | `result.vtk_data.plot(mesh_file)` | None |
| VTK mesh animation | `result.vtk_data.write_mesh_animation(mesh, out)` | None |
| Interactive viewer | `await App(vtk_data=...).run()` | Trame layout |
| Raw 3D array | `result.get_slice(channel, time_index)` | `ndarray (z,y,x)` |
