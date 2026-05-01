# Module 3a: VCell Model Validation (Mass Conservation)

**Location:** `3a_VCell_GUI/`

## Purpose

Before investing compute time running long simulations, it is essential to verify that the biochemical reaction network encoded in the VCell model is **internally consistent**. The most fundamental check is **mass conservation**: in a closed system (no production or degradation of total protein), the total amount of each protein should remain constant over time regardless of how it partitions between molecular forms.

For example, if the model has species `CPCa`, `CPCi`, and `CPCa_pH3`, then:
$$[\text{CPCa}] + [\text{CPCi}] + [\text{CPCa\_pH3}] = \text{const}$$

at all timepoints. A violation indicates a stoichiometry error in a reaction, a missing reaction, or an incorrectly defined conserved moiety.

---

## Script: `mass_conservation.py`

### What it does

`3a_VCell_GUI/mass_conservation.py` reads simulation output (typically a short test run from the VCell GUI) and:

1. Groups species by conserved protein (CPC, H2A, H3, Knl1, Mps1, Ndc80)
2. Sums their concentrations at each timepoint across the spatial domain
3. Plots the total as a function of time
4. A flat horizontal line = conservation satisfied; drift = error in the model

### Output figures

The script produces one PNG per protein group (already present in `3a_VCell_GUI/`):

| File | Protein checked |
|------|----------------|
| `mass_conservation_CPC_models.png` | CPC and all CPC-bound complexes |
| `mass_conservation_H2A_models.png` | H2A, pH2A, pH2A_SGO1 and complexes |
| `mass_conservation_H3_models.png` | H3, pH3 and all pH3-bound complexes |
| `mass_conservation_Knl1_models.png` | KNL1, pKNL1, BUB1a_pKNL1 |
| `mass_conservation_Mps1_models.png` | TTKa, TTKi, NDC80-TTK complexes |
| `mass_conservation_Ndc80_models.png` | NDC80 and all NDC80 phosphoforms |

### Running the check

```bash
cd 3a_VCell_GUI/
python mass_conservation.py
```

You will need to update the path to your simulation CSV output at the top of the script.

---

## Workflow: Running a Validation Simulation in the VCell GUI

Before running `mass_conservation.py`, you need a short test simulation. The recommended approach is:

1. **Open the VCell GUI** (download from `vcell.org` or use the web client)
2. **Load the VCML model** from `vcell_models/vcml/`
   - Use `_09_16_25_CPC_metacentric_relaxed_model_v2.vcml` for the relaxed state
3. **Set a short duration** (e.g., 10–20 seconds) — enough to see if conserved quantities drift
4. **Run the simulation** locally or submit to the VCell server
5. **Export the HDF5** output (File > Export > HDF5)
6. **Convert to CSV** using `hdf5_converter.py` (see Module 4)
7. Run `mass_conservation.py` on the CSV output

---

## What to look for

**Good (conservation holds):**
```
Total CPC: 10.0  10.0  10.0  10.0  10.0  ...  (flat)
```

**Bad (conservation violated):**
```
Total CPC: 10.0  9.8   8.1   5.3   2.0  ...  (drifting — missing a reaction)
Total CPC: 10.0  10.0  12.5  14.2  15.0 ...  (growing — duplicate production term)
```

If mass is not conserved, check:
- Are all complexes and their dissociation reactions included symmetrically?
- Is each species counted in exactly one conservation group?
- Are boundary conditions (flux terms) intentionally allowing mass in/out?

---

## Conserved moiety groups in the CPC model

The CPC model tracks the following conserved protein pools:

| Pool | Species included |
|------|-----------------|
| **CPC total** | CPCa, CPCi, H3_CPCa, H3_CPCi, pH3_CPCa, pH3_CPCi, SGO1_CPCa, SGO1_CPCi, pH2A_SGO1_CPCa, pH2A_SGO1_CPCi, SGO1_CPCi_pH3, SGO1_CPCa_pH3 |
| **H2A total** | H2A, pH2A, pH2A_SGO1, pH2A_SGO1_CPCa, pH2A_SGO1_CPCi |
| **H3 total** | H3, pH3, pH3_CPCa, pH3_CPCi, H3_CPCa, H3_CPCi, SGO1_CPCi_pH3, SGO1_CPCa_pH3 |
| **SGO1 total** | SGO1, SGO1_CPCa, SGO1_CPCi, pH2A_SGO1, pH2A_SGO1_CPCa, pH2A_SGO1_CPCi, SGO1_CPCi_pH3, SGO1_CPCa_pH3 |
| **KNL1 total** | KNL1, pKNL1, BUB1a_pKNL1 |
| **NDC80 total** | NDC80, pNDC80, NDC80_TTKa, NDC80_TTKi, NDC80_pTTKa, NDC80_pTTKi, pNDC80_TTKa, pNDC80_TTKi, pNDC80_pTTKa, pNDC80_pTTKi |
| **TTK/Mps1 total** | TTKa, TTKi, NDC80_TTKa, NDC80_TTKi, NDC80_pTTKa, NDC80_pTTKi, pNDC80_TTKa, pNDC80_TTKi, pNDC80_pTTKa, pNDC80_pTTKi |
