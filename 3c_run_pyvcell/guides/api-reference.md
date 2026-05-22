# API Reference

All public names are available under `import pyvcell.vcml as vc`.

---

## Loading and saving models

| Function | Description |
|---|---|
| `vc.load_vcml_file(path)` | Load a Biomodel from a `.vcml` file. |
| `vc.load_vcml_url(url)` | Load a Biomodel from a URL pointing to a VCML file. |
| `vc.load_vcml_str(vcml_str)` | Parse a VCML XML string into a Biomodel. |
| `vc.write_vcml_file(biomodel, path)` | Write a Biomodel to a `.vcml` file. |
| `vc.to_vcml_str(biomodel)` | Serialize a Biomodel to a VCML XML string. |
| `vc.load_sbml_file(path)` | Load a Biomodel from an SBML file. |
| `vc.load_sbml_url(url)` | Load a Biomodel from a URL pointing to an SBML file. |
| `vc.load_sbml_str(sbml_str)` | Convert an SBML XML string to a Biomodel. |
| `vc.write_sbml_file(biomodel, path)` | Write a Biomodel to an SBML file. |
| `vc.to_sbml_str(biomodel)` | Export a Biomodel to an SBML XML string. |
| `vc.load_antimony_file(path)` | Load a Biomodel from an Antimony file. |
| `vc.load_antimony_str(antimony_str)` | Parse an Antimony string into a Biomodel. |
| `vc.write_antimony_file(biomodel, path)` | Write a Biomodel to an Antimony file. |
| `vc.to_antimony_str(biomodel)` | Export a Biomodel to an Antimony string. |

---

## Running simulations

| Function | Description |
|---|---|
| `vc.simulate(biomodel, simulation, fields=None)` | Run a local finite-volume simulation; returns a `Result`. `simulation` can be a `Simulation` object or name string. Pass `fields` to supply field data initial conditions. |
| `vc.get_workspace_dir()` | Return the current directory where simulation output is written. |
| `vc.set_workspace_dir(path)` | Change the output directory for simulations. |
| `vc.update_biomodel(biomodel)` | Refresh a Biomodel by round-tripping through VCML (regenerates math and geometry). Useful after programmatic edits. |

---

## Field data

| Function / Method | Description |
|---|---|
| `vc.Field(data_name, var_name, time, data_nD)` | Create a field data object holding a spatial numpy array for use as an initial condition. |
| `field.expression` | Returns the `vcField('name', 'var', time, 'Volume')` string to paste into `init_conc`. |
| `Field.create_fields(biomodel, sim, random=False)` | Create empty (or random) `Field` objects matching every `vcField()` reference in the simulation. |
| `Field.read(file_path, dataset_name_and_time=None)` | Load a `Field` from a `.fdat` file. |
| `field.write(file_path)` | Write a `Field` to a `.fdat` file. |
| `field.create_template_filename()` | Generate the standard filename for a field data file. |
| `vc.field_data_refs(biomodel, simulation_name)` | Return the set of all `vcField()` references found in a simulation's species mappings, as `(data_name, var_name, VariableType, time)` tuples. |

---

## Remote (VCell server)

| Function / Method | Description |
|---|---|
| `vc.connect(login=False)` | Open a session with the VCell server. Pass `login=True` for authenticated access (required to save models or run remote simulations). |
| `vc.logout()` | Clear the cached authenticated session. |
| `session.load_biomodel(id)` | Load a Biomodel from the VCell server by ID. |
| `session.list_biomodels()` | List Biomodels accessible on the server. |
| `session.save_biomodel(biomodel, name=None)` | Save a Biomodel to the VCell server (requires authentication). |
| `session.run_sim(biomodel, simulation, ...)` | Save, run, and export a simulation on the server (blocking). Returns a TensorStore. |
| `session.start_sim(biomodel, simulation, ...)` | Start a remote simulation without blocking. Returns a `SimulationJob`. |
| `job.status` | Poll the server and return the current simulation status. |
| `job.wait(timeout=None)` | Block until the simulation finishes; raises on failure. |
| `job.export(variable_names=None, ...)` | Export results as N5 and return a TensorStore. |

---

## Biomodel

```python
biomodel = vc.Biomodel(name="my_model", model=model)
```

| Attribute / Method | Description |
|---|---|
| `biomodel.model` | The `Model` object containing species, reactions, and parameters. |
| `biomodel.applications` | List of `Application` objects (spatial configurations). |
| `biomodel.application_names` | List of application name strings. |
| `biomodel.simulation_names` | List of all simulation names across all applications. |
| `biomodel.add_application(name, geometry)` | Create and attach a new `Application`. |

---

## Model

```python
model = vc.Model(name="biochemistry")
```

| Attribute / Method | Description |
|---|---|
| `model.species` | List of all `Species`. |
| `model.species_names` | List of species name strings. |
| `model.get_species(name)` | Return the `Species` with that name; raises `ValueError` if not found. |
| `model.add_species(name, compartment)` | Create and add a new species. |
| `model.compartments` | List of all `Compartment` objects. |
| `model.compartment_names` | List of compartment name strings. |
| `model.get_compartment(name)` | Return the `Compartment` with that name. |
| `model.add_compartment(name, dim)` | Create and add a compartment (`dim=3` for volume, `dim=2` for membrane). |
| `model.reactions` | List of all `Reaction` objects. |
| `model.reaction_names` | List of reaction name strings. |
| `model.get_reaction(name)` | Return the `Reaction` with that name. |
| `model.add_reaction_mass_action(name, comp, reactants, products, kf, kr)` | Create and add a mass-action reaction. |
| `model.model_parameters` | List of global `ModelParameter` objects (excludes kinetics parameters). |
| `model.parameter_names` | List of all parameter name strings (global and kinetics). |
| `model.parameter_values` | Dict of all parameter values; kinetics parameters keyed as `"reaction.param"`. |
| `model.get_parameter(name)` | Return a `ModelParameter` or `KineticsParameter`. Use `"reaction.param"` dot notation for kinetics parameters. |
| `model.add_model_parameter(name, value)` | Create and add a global model parameter. |
| `model.set_parameter_value(name, value)` | Update any parameter's value (supports dot notation). |

---

## Species

```python
sp = model.get_species("Ran")
```

| Attribute | Description |
|---|---|
| `sp.name` | Species name. |
| `sp.compartment_name` | Name of the compartment this species lives in. |

---

## Compartment

```python
comp = model.get_compartment("cytoplasm")
```

| Attribute | Description |
|---|---|
| `comp.name` | Compartment name. |
| `comp.dim` | Dimensionality: `3` for volumes, `2` for membranes. |

---

## Reaction

```python
rxn = model.get_reaction("pNDC80_dephos")
```

| Attribute | Description |
|---|---|
| `rxn.name` | Reaction name. |
| `rxn.compartment_name` | Compartment where the reaction occurs. |
| `rxn.reversible` | `True` if the reaction is reversible. |
| `rxn.is_flux` | `True` if this is a membrane transport (flux) step. |
| `rxn.reactants` | List of `SpeciesReference` objects. |
| `rxn.products` | List of `SpeciesReference` objects. |
| `rxn.kinetics` | `Kinetics` object with the rate law, or `None`. |

---

## Kinetics

```python
rxn.kinetics.kinetics_type          # e.g. "MassAction"
rxn.kinetics.kinetics_parameters    # list[KineticsParameter]
```

| Attribute | Description |
|---|---|
| `kinetics.kinetics_type` | Rate law type string (e.g. `"MassAction"`, `"GeneralKinetics"`). |
| `kinetics.kinetics_parameters` | List of `KineticsParameter` objects for this reaction. |

---

## ModelParameter / KineticsParameter

```python
param = model.get_parameter("kon")
kp    = model.get_parameter("pNDC80_dephos.Kf")
```

| Attribute | Description |
|---|---|
| `param.name` | Parameter name. |
| `param.value` | Numeric value or expression string. |
| `param.role` | Role descriptor (e.g. `"model_parameter"`, `"forward rate constant"`). |
| `param.unit` | Unit string. |
| `kp.reaction_name` | (`KineticsParameter` only) Name of the owning reaction. |

---

## SpeciesReference

```python
ref = rxn.reactants[0]
```

| Attribute | Description |
|---|---|
| `ref.name` | Name of the referenced species. |
| `ref.stoichiometry` | Stoichiometric coefficient. |
| `ref.species_ref_type` | `SpeciesRefType.reactant`, `.product`, or `.modifier`. |

---

## Application

```python
app = biomodel.applications[0]
```

| Attribute / Method | Description |
|---|---|
| `app.name` | Application name. |
| `app.geometry` | The `Geometry` object for this application. |
| `app.species_mappings` | List of `SpeciesMapping` objects (spatial configs for each species). |
| `app.compartment_mappings` | List of `CompartmentMapping` objects. |
| `app.reaction_mappings` | List of `ReactionMapping` objects (enabled/disabled per reaction). |
| `app.simulations` | List of `Simulation` objects. |
| `app.simulation_names` | List of simulation name strings. |
| `app.application_parameters` | List of application-level `ApplicationParameter` overrides. |
| `app.get_species_mapping(species_name)` | Return the `SpeciesMapping` for a species; raises `ValueError` if not found. |
| `app.map_species(species, init_conc, diff_coef)` | Create and add a `SpeciesMapping`. |
| `app.map_compartment(compartment, domain)` | Map a compartment to a geometry domain. |
| `app.map_reaction(reaction, enabled)` | Enable or disable a reaction in this application. |
| `app.add_sim(name, duration, output_time_step, mesh_size)` | Create and add a `Simulation`. |

---

## SpeciesMapping

```python
sm = app.get_species_mapping("Ran")
```

| Attribute | Description |
|---|---|
| `sm.species_name` | Name of the species being mapped. |
| `sm.init_conc` | Initial concentration — a number, expression string, or `vcField(...)` reference. |
| `sm.diff_coef` | Diffusion coefficient — a number or expression string. |
| `sm.boundary_values` | List of 6 boundary values `[Xm, Xp, Ym, Yp, Zm, Zp]`, each a number or string. |
| `sm.expressions` | List of all string expressions among `init_conc`, `diff_coef`, and `boundary_values`. |

---

## Simulation

```python
sim = app.simulations[0]
```

| Attribute | Description |
|---|---|
| `sim.name` | Simulation name. |
| `sim.duration` | End time of the simulation. |
| `sim.output_time_step` | Time interval between saved outputs. |
| `sim.mesh_size` | `(nx, ny, nz)` mesh resolution. |
| `sim.mesh_array_shape` | Reduced shape tuple — drops trailing `1` dimensions for 1D/2D meshes. |

---

## Geometry

```python
geo = app.geometry
```

| Attribute / Method | Description |
|---|---|
| `geo.name` | Geometry name. |
| `geo.dim` | Dimensionality (`0` compartmental, `1`, `2`, or `3`). |
| `geo.origin` | `(X, Y, Z)` origin of the domain. |
| `geo.extent` | `(X, Y, Z)` size of the domain. |
| `geo.image` | `Image` object for image-based geometries, or `None`. |
| `geo.subvolumes` | List of `SubVolume` objects (volume domains). |
| `geo.subvolume_names` | List of subvolume name strings. |
| `geo.surface_classes` | List of `SurfaceClass` objects (membrane domains). |
| `geo.surface_class_names` | List of surface class name strings. |
| `geo.add_background(name)` | Add a background (fills everywhere) analytic subvolume. |
| `geo.add_sphere(name, radius, center)` | Add a spherical analytic subvolume. |
| `geo.add_surface(name, sv1, sv2)` | Add a membrane surface between two subvolumes. |
| `geo.plot(resolution=50, save_path=None)` | Render the geometry using PyVista. |
| `geo.to_segmented_image(resolution=50)` | Convert to a `SegmentedImageGeometry` (discretized on a grid). |

---

## SubVolume

```python
sv = geo.subvolumes[0]
```

| Attribute | Description |
|---|---|
| `sv.name` | Subvolume name. |
| `sv.subvolume_type` | `SubVolumeType.analytic`, `.image`, `.csg`, or `.compartmental`. |
| `sv.analytic_expr` | Mathematical expression defining the region (analytic type only). |
| `sv.image_pixel_value` | Pixel value mapping to this region (image type only). |

---

## Image

```python
img = geo.image
```

| Attribute / Method | Description |
|---|---|
| `img.name` | Image name. |
| `img.size` | `(X, Y, Z)` voxel dimensions. |
| `img.pixel_classes` | List of `PixelClass` objects mapping pixel values to names. |
| `img.ndarray_3d_u8` | Decompress and return the image as a `(Z, Y, X)` uint8 numpy array. |
| `Image.from_ndarray_3d_u8(arr, name)` | Create an `Image` from a `(Z, Y, X)` uint8 numpy array. |

---

## Result

```python
result = vc.simulate(biomodel, sim)
```

| Attribute / Method | Description |
|---|---|
| `result.time_points` | List of output time values (seconds). |
| `result.channel_data` | List of `ChannelMetadata` objects (one per species/variable). |
| `result.concentrations` | 2D array of mean concentrations `(time × channel)`. |
| `result.volume_variable_names` | Names of volume variables in the results. |
| `result.get_slice(channel_id, time_index)` | Return a `(Z, Y, X)` numpy array for a channel at a time point. |
| `result.get_channel(label)` | Return `ChannelMetadata` for a channel by label. |
| `result.get_channel_ids()` | List of all channel label strings. |
| `result.plotter` | `Plotter` object for visualization. |
| `result.vtk_data` | `VtkData` object for VTK mesh access. |
| `result.solver_output_dir` | `Path` to the simulation output directory (use `.name` as `data_name` for field data chaining). |
| `result.cleanup()` | Delete the output directory. |

---

## Plotter

```python
p = result.plotter
```

| Method | Description |
|---|---|
| `p.plot_concentrations(save_path=None)` | Line plot of mean concentration vs. time for all species. |
| `p.plot_slice_2d(time_index, channel_name, z_index, save_path=None)` | 2D cross-section image at a given z-plane and time point. |
| `p.plot_slice_3d(time_index, channel_id, save_path=None)` | 3D scatter plot of a volume variable at a time point. |
| `p.plot_averages()` | Envelope plots (min/mean/max) for post-processing statistics. |
| `p.plot_image(image_index, time_index)` | Display a post-processing image channel. |
| `p.animate_channel_3d(channel_id)` | Return a `FuncAnimation` cycling through all time points in 3D. |
| `p.animate_image(image_index)` | Return a `FuncAnimation` of a post-processing image over time. |
