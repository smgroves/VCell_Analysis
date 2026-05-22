# Simulation Reference

This guide covers running local simulations with pyvcell, managing output directories, accessing results, and chaining simulations with field data.

---

## Basic workflow

```python
import pyvcell.vcml as vc

biomodel = vc.load_vcml_file("my_model.vcml")

# Run by simulation name or Simulation object
result = vc.simulate(biomodel, "sim1")
result = vc.simulate(biomodel, app.simulations[0])
```

`simulate()` signature:

```python
vc.simulate(biomodel, simulation, fields=None) -> Result
```

| Parameter | Type | Description |
|---|---|---|
| `biomodel` | `Biomodel` | The model to simulate |
| `simulation` | `Simulation \| str` | Simulation object or its name |
| `fields` | `list[Field] \| None` | Optional field data for initial conditions |

---

## Output directory

By default, output is written to `./workspace/out_dir_<random>/`. Each call to `simulate()` creates a fresh subdirectory.

### Changing the workspace

```python
# Check where output will go
vc.get_workspace_dir()   # returns Path, default is cwd / "workspace"

# Change it before simulating
vc.set_workspace_dir("/path/to/my/output")

result = vc.simulate(biomodel, "sim1")
```

`set_workspace_dir` takes effect globally for all subsequent `simulate()` calls in the session.

### Finding the output directory

```python
result.solver_output_dir        # Path to the specific run's output folder
result.solver_output_dir.name   # just the folder name, e.g. "out_dir_abc123"
                                # — use this as data_name when chaining simulations
```

### Output directory contents

```
out_dir_abc123/
├── SimID_946368938_0_.log          # time points and variable metadata
├── SimID_946368938_0_.mesh         # mesh geometry
├── SimID_946368938_0_.functions    # derived variable definitions
├── SimID_946368938_0_.hdf5         # post-processing data
├── SimID_946368938_0_00.zip        # compressed time-step data
└── zarr/                           # zarr dataset (created automatically)
```

### Cleaning up

```python
result.cleanup()   # deletes the entire output directory — irreversible
```

---

## Configuring a simulation

Simulations are defined on an `Application` before running:

```python
app = biomodel.applications[0]

sim = app.add_sim(
    name="sim1",
    duration=200.0,           # end time
    output_time_step=1.0,     # how often to save output
    mesh_size=(64, 64, 1),    # (nx, ny, nz) — use nz=1 for 2D
)

# Modify an existing simulation
sim.duration         = 400.0
sim.output_time_step = 0.5
sim.mesh_size        = (128, 128, 1)
```

---

## Accessing results

```python
result = vc.simulate(biomodel, "sim1")

result.time_points          # list[float] — output times in seconds
result.channel_data         # list[ChannelMetadata] — one entry per variable
result.concentrations       # 2D array (time × channel) of domain-mean values
result.volume_variable_names  # list of volume variable name strings
```

### Channels

```python
result.get_channel_ids()            # list of all channel label strings
ch = result.get_channel("Ran_cyt")  # ChannelMetadata for one channel

ch.label        # str
ch.domain_name  # str
ch.mean_values  # per-time mean concentrations
ch.min_values   # per-time minimum
ch.max_values   # per-time maximum
```

### Spatial data

```python
# 3D numpy array (z, y, x) for a channel at one time point
arr = result.get_slice("Ran_cyt", time_index=5)

# All time values, or a single one
result.time_points                  # list[float]
result.get_time_axis(time_index=5)  # single float
result.get_time_axis()              # all times

# Raw zarr access
result.zarr_dataset
```

### Post-processing

```python
result.post_processing   # HDF5 post-processing data (statistics, images)
```

---

## Visualization

```python
p = result.plotter

p.plot_concentrations()                                       # mean conc vs. time
p.plot_slice_2d(time_index=0, channel_name="Ran_cyt", z_index=0)  # 2D image
p.plot_slice_3d(time_index=0, channel_id="Ran_cyt")           # 3D scatter
p.plot_averages()                                             # min/mean/max envelopes

anim = p.animate_channel_3d("Ran_cyt")   # FuncAnimation over time
anim.save("output.gif", writer="pillow")
```

See [visualization-reference.md](visualization-reference.md) for the full list.

---

## Simulating with field data

Use field data to supply spatial initial conditions from a numpy array or a previous simulation.

### From a numpy array

```python
# Create empty Field objects matching every vcField() in the model
fields = vc.Field.create_fields(bio_model=biomodel, sim=sim)

# Populate with your data (shape must match sim.mesh_array_shape)
fields[0].data_nD = my_image_array
fields[1].data_nD = np.zeros(sim.mesh_array_shape)

result = vc.simulate(biomodel, sim, fields=fields)
```

`Field.create_fields(random=True)` fills with random data instead of zeros — useful for quick tests.

### Chaining from a previous simulation

```python
result1 = vc.simulate(biomodel, "sim1")

# Use sim1's output directory name as the data_name
dataset_name = result1.solver_output_dir.name

for sm in app2.species_mappings:
    sm.init_conc = f"vcField('{dataset_name}', '{sm.species_name}', 0.0, 'Volume')"

result2 = vc.simulate(biomodel, "sim2")  # no fields= needed — data is on disk
```

See [field-data-reference.md](field-data-reference.md) for more on field data.

---

## Updating a model before simulating

After making programmatic changes (parameters, geometry, species), round-trip through libvcell to regenerate math before simulating:

```python
biomodel = vc.update_biomodel(biomodel)
result = vc.simulate(biomodel, "sim1")
```

This is especially important after changing geometry or adding/removing species.

---

## Error handling

`simulate()` raises `ValueError` in three situations:

| Error | Cause |
|---|---|
| `"Failed to get solver input files: ..."` | VCML→solver conversion failed (bad model) |
| `".fvinput file or .vcg file not found"` | Conversion produced no output |
| `"Error in solve: <code>"` | Solver returned a non-zero exit code |

On failure, the partial output directory is left on disk and is not cleaned up automatically:

```python
try:
    result = vc.simulate(biomodel, "sim1")
except ValueError as e:
    print(f"Simulation failed: {e}")
    # inspect workspace dir for log files if needed
```

---

## Quick-reference

| Task | Code |
|---|---|
| Run a simulation | `vc.simulate(biomodel, "sim1")` |
| Check output location | `vc.get_workspace_dir()` |
| Change output location | `vc.set_workspace_dir("/my/path")` |
| Find this run's folder | `result.solver_output_dir` |
| Get time points | `result.time_points` |
| Get all channel names | `result.get_channel_ids()` |
| Get mean concentrations | `result.concentrations` |
| Get 3D array for a channel | `result.get_slice("Ran_cyt", time_index=0)` |
| Plot concentrations | `result.plotter.plot_concentrations()` |
| Delete output | `result.cleanup()` |
| Update model before sim | `biomodel = vc.update_biomodel(biomodel)` |
| Run with field data | `vc.simulate(biomodel, sim, fields=fields)` |
| Chain from previous sim | `f"vcField('{result1.solver_output_dir.name}', 'var', 0.0, 'Volume')"` |
