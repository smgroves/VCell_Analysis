import numpy as np
import pyvcell.vcml as vc

print("Loading model...")
biomodel = vc.load_vcml_url(
    "https://raw.githubusercontent.com/virtualcell/pyvcell/refs/heads/main/examples/models/Tutorial_MultiApp_PDE.vcml")
model = biomodel.model
model.set_parameter_value(name="r0.Kf", value=20.0)
print("✓ Model loaded")

print("\nSetting up simulation...")
sim = biomodel.applications[0].simulations[0]
sim.mesh_size = (50, 50, 18)
print("✓ Simulation configured")

print("\nRunning single simulation...")
print("(This may take a minute...)")
result = vc.simulate(biomodel, sim.name)
print("✓ Simulation COMPLETED")

print("\nGenerating plot...")
result.plotter.plot_concentrations()
print("✓ ALL DONE")