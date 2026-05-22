# Field Data Reference

Field data are spatial arrays (numpy arrays matching the simulation mesh) that can be used as initial conditions for species in a spatial simulation. Common use cases:

- **Chaining simulations** — use the output of one simulation as the initial condition for the next
- **Synthetic or image-based initial conditions** — supply data from microscopy images, analytic functions, or other external sources

Field data is referenced inside `SpeciesMapping.init_conc` (and other expression strings) using the `vcField()` syntax.

---

## The `vcField()` expression

```python
vcField('dataset_name', 'variable_name', time, 'Volume')
```

| Argument | Type | Description |
|---|---|---|
| `dataset_name` | str | Identifier for the data source — a simulation output directory name or any label you choose |
| `variable_name` | str | Name of the variable (species) within that dataset |
| `time` | float | Time point to sample |
| `'Volume'` | str | Domain type — currently only `'Volume'` is supported |

Set it directly on a species mapping:

```python
sm = app.get_species_mapping("H3")
sm.init_conc = "vcField('_02_23_PMP1_relaxed', 'H3', 0.0, 'Volume')"

# Or combine with an expression
sm.init_conc = "2.0 * vcField('_02_23_PMP1_relaxed', 'H3', 0.0, 'Volume')"
```

---

## The `Field` class

`Field` is the Python object that holds the data behind a `vcField()` reference.

```python
import pyvcell.vcml as vc
import numpy as np

field = vc.Field(
    data_name="my_dataset",   # must match first argument of vcField()
    var_name="H3",            # must match second argument
    time=0.0,                 # must match third argument
    data_nD=np.zeros((50, 50, 50)),  # shape must match simulation mesh
)

field.expression  # returns "vcField('my_dataset', 'H3', 0.0, 'Volume')"
```

### Attributes

| Attribute | Type | Description |
|---|---|---|
| `data_name` | str | Dataset identifier — matches first arg of `vcField()` |
| `var_name` | str | Variable name — matches second arg |
| `time` | float | Time point — matches third arg |
| `data_nD` | ndarray | Spatial data array; shape must match `sim.mesh_array_shape` |

### `field.expression`

Convenience property that generates the `vcField()` string:

```python
sm.init_conc = field.expression
sm.init_conc = f"4.0 * {field.expression}"
```

---

## Workflow 1: Synthetic or image-based initial conditions

Use `Field.create_fields()` to generate empty `Field` objects matching every `vcField()` reference already in the model, then populate them with your data.

```python
biomodel = vc.load_vcml_file("my_model.vcml")
app = biomodel.applications[0]
sim = app.simulations[0]

# Create empty Field objects matching the model's vcField() references
fields = vc.Field.create_fields(bio_model=biomodel, sim=sim)

# Inspect what was found
for f in fields:
    print(f)  # Field(data_name=..., var_name=..., time=..., shape=...)

# Fill with your data (shape must match sim.mesh_array_shape)
fields[0].data_nD = my_image_array
fields[1].data_nD = np.zeros(sim.mesh_array_shape)

# Run — pyvcell writes the fields to disk before invoking the solver
result = vc.simulate(biomodel=biomodel, simulation=sim, fields=fields)
```

`create_fields()` accepts a `random=True` flag to pre-fill with random data instead of zeros — useful for quick tests:

```python
fields = vc.Field.create_fields(bio_model=biomodel, sim=sim, random=True)
result = vc.simulate(biomodel=biomodel, simulation=sim, fields=fields)
```

---

## Workflow 2: Chaining simulations

Use the output directory name of a completed simulation as the `data_name` in the next simulation's `vcField()` expressions.

```python
# Run first simulation
sim1 = app.simulations[0]
result1 = vc.simulate(biomodel=biomodel, simulation=sim1)

# The output directory name becomes the dataset_name
dataset_name = result1.solver_output_dir.name  # e.g. "out_dir_abc123"

# Point the second simulation's initial conditions at sim1's output
sim2_app = biomodel.applications[1]
for sm in sim2_app.species_mappings:
    sm.init_conc = f"vcField('{dataset_name}', '{sm.species_name}', 0.0, 'Volume')"

# Run second simulation (no fields= needed — data is already on disk)
sim2 = sim2_app.simulations[0]
result2 = vc.simulate(biomodel=biomodel, simulation=sim2)
```

---

## Reading and writing field data files

### Read from a file

```python
from pathlib import Path

# File whose name follows the template pattern (standard output from pyvcell)
field = vc.Field.read(file_path=Path("SimID_SIMULATIONKEY_JOBINDEX_my_dataset_H3_0_0_Volume.fdat"))

# File with a non-standard name — supply dataset name and time explicitly
field = vc.Field.read(
    file_path=Path("custom_name.fdat"),
    dataset_name_and_time=("my_dataset", 0.0),
)
```

### Write to a file

```python
field = vc.Field(data_name="my_dataset", var_name="H3", time=0.0, data_nD=arr)

# Generate the standard template filename
filename = field.create_template_filename()
# → "SimID_SIMULATIONKEY_JOBINDEX_my_dataset_H3_0_0_Volume.fdat"

field.write(file_path=Path("output_dir") / filename)
```

---

## Inspecting `vcField()` references in a model

`field_data_refs()` parses all `vcField()` calls in a model's species mappings and returns them as a set of tuples:

```python
refs = vc.field_data_refs(bio_model=biomodel, simulation_name="sim1")

for data_name, var_name, var_type, time in refs:
    print(data_name, var_name, time)
# _02_23_PMP1_relaxed  H3    0.0
# _02_23_PMP1_relaxed  NuMA  0.0
```

Each tuple is `(data_name, var_name, VariableType, time)`. This is what `Field.create_fields()` calls internally.

---

## File naming convention

Field data files on disk follow this pattern:

```
SimID_SIMULATIONKEY_JOBINDEX_{data_name}_{var_name}_{time_whole}_{time_frac}_Volume.fdat
```

For example, `time=0.5` becomes `0_5`, and `time=10.0` becomes `10_0`. pyvcell handles this automatically when you call `field.write()` or `Field.create_fields()` + `simulate(..., fields=fields)`.

---

## Quick-reference

| Task | Code |
|---|---|
| Reference field data in an expression | `sm.init_conc = "vcField('name', 'var', 0.0, 'Volume')"` |
| Get expression string from a Field | `field.expression` |
| Create empty fields from model | `vc.Field.create_fields(bio_model, sim)` |
| Create random fields (for testing) | `vc.Field.create_fields(bio_model, sim, random=True)` |
| Run with field data | `vc.simulate(biomodel, sim, fields=fields)` |
| Chain from previous sim output | `result1.solver_output_dir.name` → use as `data_name` |
| Read field from file | `vc.Field.read(Path("file.fdat"))` |
| Write field to file | `field.write(Path("dir") / field.create_template_filename())` |
| Find all vcField references | `vc.field_data_refs(bio_model, simulation_name)` |
