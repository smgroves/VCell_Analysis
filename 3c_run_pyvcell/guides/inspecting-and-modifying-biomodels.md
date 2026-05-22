# Inspecting and Modifying Biomodels

This guide covers how to read and modify the attributes of a `BioModel` loaded from a VCML file or built programmatically. All examples assume:

```python
import pyvcell.vcml as vc

bio_model = vc.load_vcml_file("my_model.vcml")
model = bio_model.model
```

---

## Model-level inventory

```python
model.species_names       # list[str] — all species names
model.compartment_names   # list[str] — all compartment/structure names
model.reaction_names      # list[str] — all reaction names
model.parameter_names     # list[str] — all model-parameter names
model.parameter_values    # dict[str, float | str] — name → value for every parameter,
                          #   including kinetics params as "reaction_name.param_name"
```

---

## Reactions

### Listing all reactions

```python
model.reaction_names   # list[str] — names only

for rxn in model.reactions:
    print(rxn.name, rxn.compartment_name)
```

### Reading a specific reaction

```python
rxn = model.get_reaction("pNDC80rep_dephos")

rxn.name             # str
rxn.compartment_name # str
rxn.reversible       # bool
rxn.is_flux          # bool — True for membrane transport (flux step)
rxn.reactants        # list[SpeciesReference]
rxn.products         # list[SpeciesReference]
rxn.kinetics         # Kinetics | None

# Kinetics type and its parameters
rxn.kinetics.kinetics_type          # e.g. "MassAction" or "GeneralKinetics"
rxn.kinetics.kinetics_parameters    # list[KineticsParameter]
```

### Listing all kinetics parameters for a reaction

```python
rxn.kinetics.kinetics_parameters   # list[KineticsParameter]

for p in rxn.kinetics.kinetics_parameters:
    print(p.name, p.value, p.role, p.unit)
```

### Reading a specific kinetics parameter

Two equivalent ways:

```python
# 1. Iterate over the kinetics parameters directly
for p in rxn.kinetics.kinetics_parameters:
    print(p.name, p.value, p.role, p.unit)

# 2. Dot-notation lookup via the model (works for both ModelParameters and KineticsParameters)
kf = model.get_parameter("pNDC80rep_dephos.Kf")
print(kf.value)
```

### Modifying kinetics parameters

```python
# Via the model convenience method
model.set_parameter_value("pNDC80rep_dephos.Kf", 0.05)

# Or directly on the parameter object
for p in rxn.kinetics.kinetics_parameters:
    if p.name == "Kf":
        p.value = 0.05
```

### Modifying other reaction attributes

```python
rxn.reversible = False
rxn.is_flux     = True
rxn.name        = "pNDC80rep_dephos_v2"
```

---

## Species

### Listing all species

```python
model.species_names   # list[str] — names only

for sp in model.species:
    print(sp.name, sp.compartment_name)
```

### Reading a specific species

```python
sp = model.get_species("pNDC80rep")

sp.name              # str
sp.compartment_name  # str — which compartment this species lives in
```

Modify by direct assignment:

```python
sp.compartment_name = "nucleus"
```

### `model.species` vs `app.species_mappings`

Every species appears in two places with different responsibilities:

| Task | Use |
|---|---|
| Check which compartment a species lives in | `model.get_species("H3").compartment_name` |
| Add or rename a species | `model.species` |
| Set/read initial concentration | `app.get_species_mapping("H3").init_conc` |
| Set/read diffusion coefficient | `app.get_species_mapping("H3").diff_coef` |
| Set/read boundary conditions | `app.get_species_mapping("H3").boundary_values` |
| Check what `vcField()` expressions are used | `app.get_species_mapping("H3").expressions` |
| Iterate all spatial configs across applications | `app.species_mappings` |

`model.species` holds the biochemical definition (existence, compartment) shared across all applications. `app.species_mappings` holds the spatial/numerical settings (initial conditions, diffusion, boundaries) for a specific application — each application can have different values for the same species.

---

## Compartments / Structures

### Listing all compartments

```python
model.compartment_names   # list[str] — names only

for comp in model.compartments:
    print(comp.name, comp.dim)   # dim: 3 = volume, 2 = membrane
```

### Reading a specific compartment

```python
comp = model.get_compartment("cytoplasm")

comp.name  # str
comp.dim   # int — 3 for volumes, 2 for membranes
```

---

## Model parameters (global constants)

### Listing all parameters

```python
model.parameter_names    # list[str] — names only
model.parameter_values   # dict[str, float | str] — name → value for all parameters,
                         #   including kinetics params as "reaction_name.param_name"

# Iterate over global model parameters only (excludes kinetics parameters)
for param in model.model_parameters:
    print(param.name, param.value, param.unit)
```

### Reading a specific parameter

```python
param = model.get_parameter("kon")

param.name   # str
param.value  # float | str — numeric value or expression string
param.role   # str — e.g. "model_parameter"
param.unit   # str

# Modify
param.value = 1.5
# or equivalently:
model.set_parameter_value("kon", 1.5)
```

---

## Reactants and products

`rxn.reactants` and `rxn.products` are lists of `SpeciesReference`:

```python
ref = rxn.reactants[0]

ref.name              # str — species name
ref.stoichiometry     # int
ref.species_ref_type  # SpeciesRefType.reactant | .product | .modifier

# Modify stoichiometry
ref.stoichiometry = 2

# Add a new reactant
rxn.reactants.append(
    vc.SpeciesReference(
        name="ATP",
        stoichiometry=1,
        species_ref_type=vc.SpeciesRefType.reactant,
    )
)
```

---

## Application-level (spatial) attributes

Spatial initial conditions and diffusion coefficients live on the `Application`, not the `Model`.

```python
bio_model.application_names   # list[str] — names of all applications
bio_model.simulation_names    # list[str] — all simulation names across all applications

# Iterate over applications
for app in bio_model.applications:
    print(app.name)

app = bio_model.applications[0]  # or iterate by name

# Species mapping: initial concentration and diffusion coefficient
sm = app.get_species_mapping("pNDC80rep")
sm.init_conc  # float | str | None
sm.diff_coef  # float | str | None
sm.boundary_values  # list[float | str | None] — [Xm, Xp, Ym, Yp, Zm, Zp]

# Modify
sm.init_conc = "10 + sin(x)"
sm.diff_coef = 1e-4

# Reaction enabled/disabled per application
rm = app.reaction_mappings[0]
rm.reaction_name  # str
rm.included       # bool
rm.included = False  # disable reaction in this application
```

---

## Simulations

```python
app.simulation_names   # list[str] — names of all simulations in this application

for sim in app.simulations:
    print(sim.name, sim.duration)

sim = app.simulations[0]

sim.name              # str
sim.duration          # float
sim.output_time_step  # float
sim.mesh_size         # tuple[int, int, int]

# Modify
sim.duration         = 200.0
sim.output_time_step = 0.5
sim.mesh_size        = (64, 64, 64)
```

---

## Geometry

The `Geometry` object lives on an `Application` and defines the spatial domain.

```python
app = bio_model.applications[0]
geo = app.geometry

geo.name    # str
geo.dim     # int — 0 (compartmental), 1, 2, or 3
geo.origin  # tuple[float, float, float] — (X, Y, Z) origin
geo.extent  # tuple[float, float, float] — (X, Y, Z) size
geo.image   # Image | None — present for image-based geometries

geo.subvolume_names     # list[str] — all volume domain names
geo.surface_class_names # list[str] — all membrane/surface domain names
```

### Subvolumes (volume domains)

```python
geo.subvolume_names   # list[str] — names only

for sv in geo.subvolumes:
    print(sv.name, sv.subvolume_type, sv.analytic_expr)

sv = geo.subvolumes[0]

sv.name             # str
sv.handle           # int — numeric index used internally
sv.subvolume_type   # SubVolumeType: analytic | image | csg | compartmental
sv.analytic_expr    # str | None — mathematical expression (analytic type only)
sv.image_pixel_value  # int | None — pixel value (image type only)

# Modify the shape of an analytic subvolume
sv.analytic_expr = "(pow(x-5,2) + pow(y-5,2) + pow(z-5,2)) < pow(4,2)"
sv.name = "nucleus"
```

### Surface classes (membrane domains)

```python
geo.surface_class_names   # list[str] — names only

for sc in geo.surface_classes:
    print(sc.name, sc.subvolume_ref_1, sc.subvolume_ref_2)

sc = geo.surface_classes[0]

sc.name             # str
sc.subvolume_ref_1  # str — one adjacent subvolume
sc.subvolume_ref_2  # str — other adjacent subvolume

# Modify
sc.name = "nuclear_membrane"
```

### Adding new domains

```python
# Background (fills everywhere — always use for the "outside" domain)
extracellular = geo.add_background("extracellular")

# Sphere defined by analytic expression
cell = geo.add_sphere("cell", radius=4.0, center=(5.0, 5.0, 5.0))

# Membrane between two subvolumes
plasma_membrane = geo.add_surface("plasma_membrane", cell, extracellular)
```

### Modifying extent and origin

```python
geo.origin = (0.0, 0.0, 0.0)
geo.extent = (20.0, 20.0, 20.0)
```

### Image-based geometry

For image-based geometries, the pixel data is stored on `geo.image`:

```python
img = geo.image

img.name               # str
img.size               # tuple[int, int, int] — (X, Y, Z) voxel dimensions
img.pixel_classes      # list[PixelClass] — pixel value → name mappings

# Access the raw data as a (Z, Y, X) uint8 numpy array
arr = img.ndarray_3d_u8

# Replace the image from a numpy array
geo.image = vc.Image.from_ndarray_3d_u8(new_arr, name="updated_image")
```

Each subvolume in an image geometry has an `image_pixel_value` that maps it to a pixel class:

```python
for sv in geo.subvolumes:
    print(sv.name, sv.image_pixel_value)
```

### Visualizing geometry

```python
geo.plot()                    # interactive PyVista render
geo.plot(resolution=100)      # higher resolution for analytic geometries
geo.plot(save_path="geo.png") # save without displaying
```

---

## Quick-reference

| What | Get all | Get specific | Modify | Add new |
|---|---|---|---|---|
| **Species** | `model.species` / `model.species_names` | `model.get_species("A")` | `sp.compartment_name = "..."` | `model.add_species("A", compartment)` |
| **Compartments** | `model.compartments` / `model.compartment_names` | `model.get_compartment("cyt")` | `comp.name = "..."` | `model.add_compartment("cyt", dim=3)` |
| **Reactions** | `model.reactions` / `model.reaction_names` | `model.get_reaction("r1")` | `rxn.reversible = False` | `model.add_reaction_mass_action(...)` |
| **Kinetics parameters** | `rxn.kinetics.kinetics_parameters` | `model.get_parameter("r1.Kf")` | `model.set_parameter_value("r1.Kf", v)` | — (set at reaction creation) |
| **Global parameters** | `model.model_parameters` / `model.parameter_names` | `model.get_parameter("kon")` | `model.set_parameter_value("kon", v)` | `model.add_model_parameter("kon", 1.0)` |
| **All parameter values** | `model.parameter_values` | — | — | — |
| **Stoichiometry** | `rxn.reactants` / `rxn.products` | `rxn.reactants[i]` | `rxn.reactants[i].stoichiometry = n` | `rxn.reactants.append(vc.SpeciesReference(...))` |
| **Applications** | `biomodel.applications` / `biomodel.application_names` | `biomodel.applications[i]` | — | `biomodel.add_application("app1", geo)` |
| **Simulations** | `app.simulations` / `app.simulation_names` | `app.simulations[i]` | `sim.duration = 200.0` | `app.add_sim("sim1", duration, dt, mesh)` |
| **Species mapping** | `app.species_mappings` | `app.get_species_mapping("A")` | `sm.init_conc = "..."` | `app.map_species("A", init_conc, diff_coef)` |
| **Reaction mapping** | `app.reaction_mappings` | `app.reaction_mappings[i]` | `rm.included = False` | `app.map_reaction("r1", enabled=True)` |
| **Compartment mapping** | `app.compartment_mappings` | `app.compartment_mappings[i]` | `cm.size_exp = "..."` | `app.map_compartment("cyt", domain)` |
| **Volume domains** | `geo.subvolumes` / `geo.subvolume_names` | `geo.subvolumes[i]` | `sv.analytic_expr = "..."` | `geo.add_background("name")` / `geo.add_sphere(...)` |
| **Membrane domains** | `geo.surface_classes` / `geo.surface_class_names` | `geo.surface_classes[i]` | `sc.name = "..."` | `geo.add_surface("name", sv1, sv2)` |
| **Image data** | — | `geo.image.ndarray_3d_u8` | `geo.image = vc.Image.from_ndarray_3d_u8(arr, name)` | `vc.Image.from_ndarray_3d_u8(arr, name)` |
| **Geometry extent/origin** | — | `geo.extent` / `geo.origin` | `geo.extent = (20., 20., 20.)` | — |
