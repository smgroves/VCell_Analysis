#includes functions for loading and comparing VCell models using pyvcell
# Author: Sarah Groves 05/21/2026

import pyvcell.vcml as vc

import re
def load_model(vcml_file):
    """
    Load a VCell model from a .vcml file.

    Parameters:
    vcml_file (str): The path to the .vcml file.

    Returns:
    bio_model: The loaded VCell model.
    """
    bio_model = vc.load_vcml_file(vcml_file)
    #print details about the loaded model
    print(f"Model '{bio_model.name}' loaded successfully.")
    print(f"Compartments: {[c.name for c in bio_model.model.compartments]}")
    print(f"Number of species: {len(bio_model.model.species)}")
    print(f"Number of reactions: {len(bio_model.model.reactions)}")
    print(f"Applications: {sorted([app.name for app in bio_model.applications])}")
    return bio_model




def compare_reactions(model1, model2, name1, name2):
    names1 = set(model1.reaction_names)
    names2 = set(model2.reaction_names)

    only_in_1 = names1 - names2
    only_in_2 = names2 - names1
    shared = names1 & names2

    report = []

    for name in sorted(only_in_1):
        report.append(f"  [{name}] present in {name1} only")
    for name in sorted(only_in_2):
        report.append(f"  [{name}] present in {name2} only")

    for name in sorted(shared):
        r1 = model1.get_reaction(name).model_dump()
        r2 = model2.get_reaction(name).model_dump()
        if r1 != r2:
            diffs = _dict_diff(r1, r2)
            report.append(f"  [{name}] differs:")
            for path, v1, v2 in diffs:
                report.append(f"    {path}: {name1}={v1!r}  {name2}={v2!r}")

    if report:
        print("Reaction differences:")
        print("\n".join(report))
    else:
        print("Reactions are identical.")


def _dict_diff(d1, d2, path=""):
    diffs = []
    all_keys = set(d1) | set(d2)
    for k in all_keys:
        current_path = f"{path}.{k}" if path else k
        if k not in d1:
            diffs.append((current_path, "<missing>", d2[k]))
        elif k not in d2:
            diffs.append((current_path, d1[k], "<missing>"))
        elif isinstance(d1[k], dict) and isinstance(d2[k], dict):
            diffs.extend(_dict_diff(d1[k], d2[k], current_path))
        elif isinstance(d1[k], list) and isinstance(d2[k], list):
            diffs.extend(_list_diff(d1[k], d2[k], current_path))
        elif d1[k] != d2[k]:
            diffs.append((current_path, d1[k], d2[k]))
    return diffs


def _list_diff(l1, l2, path=""):
    diffs = []
    for i, (v1, v2) in enumerate(zip(l1, l2)):
        item_path = f"{path}[{i}]"
        if isinstance(v1, dict) and isinstance(v2, dict):
            diffs.extend(_dict_diff(v1, v2, item_path))
        elif v1 != v2:
            diffs.append((item_path, v1, v2))
    if len(l1) != len(l2):
        diffs.append((f"{path}.length", len(l1), len(l2)))
    return diffs


def count_parameter_usage(biomodel, param_name: str) -> dict[str, list[str]]:
    """Find everywhere a global parameter name is referenced across a biomodel."""
    model = biomodel.model
    hits: dict[str, list[str]] = {
         "model_parameters": [],
        "reactions": [],
        "species_mappings": [],
        "compartment_mappings": [],
        "application_parameters": [],
    }

    def _matches(expr) -> bool:
        # whole-word match to avoid "kon" matching inside "konrate"
        return bool(re.search(rf"\b{re.escape(param_name)}\b", str(expr)))

    # 1. Other global model parameters whose value references this parameter
    for p in model.model_parameters:
        if p.name != param_name and isinstance(p.value, str) and _matches(p.value):
            hits["model_parameters"].append(p.name)

    # 2. Kinetics parameter values (e.g. Kf = "kbind", J = "(Kf * A) - ...")
    for rxn in model.reactions:
        if rxn.kinetics:
            if any(_matches(p.value) for p in rxn.kinetics.kinetics_parameters):
                hits["reactions"].append(rxn.name)

    # 3. Species initial conditions, diffusion coefficients, boundary values
    for app in biomodel.applications:
        for sm in app.species_mappings:
            exprs = [sm.init_conc, sm.diff_coef] + list(sm.boundary_values)
            if any(_matches(e) for e in exprs if isinstance(e, str)):
                hits["species_mappings"].append(f"{app.name} / {sm.species_name}")

        # 4. Compartment size expressions
        for cm in app.compartment_mappings:
            if _matches(cm.size_exp):
                hits["compartment_mappings"].append(f"{app.name} / {cm.compartment_name}")

        # 5. Application-level parameter overrides
        for ap in app.application_parameters:
            if _matches(ap.value):
                hits["application_parameters"].append(f"{app.name} / {ap.name}")
    

    return hits

def compare_models(biomodel1, biomodel2, name1= None, name2=None, verbose = 1):
    """
    Compare two VCell models and identify differences in their structure and parameters.

    Parameters:
    model1: The first VCell model to compare.
    model2: The second VCell model to compare.
    verbose: Whether to print detailed comparison information; can be 0 (basic output), 1 (detailed output), or 2 (advanced output).

    Returns:
    differences: A list of differences between the two models, including differences in compartments, species, reactions, and parameters.
    """
    #grab names of each model for reporting
    if name1 is None:
        name1 = biomodel1.name
    
    if name2 is None:
        name2 = biomodel2.name

    # at the model level, the following are defined and can be compared:
    # - compartments (name, dim)
    # - species (name, compartment_name)
    # - reactions (name, compartment_name, reversible, is_flux, kinetics, kinetics_parameters)
    # - parameter_values (name, value)

    # at the application level, the following are defined and can be compared:

    # Compare compartments
    comp_differences = []
    compartments1 = set([comp.name for comp in biomodel1.model.compartments])
    compartments2 = set([comp.name for comp in biomodel2.model.compartments])
    if compartments1 != compartments2:
        for comp in compartments1.symmetric_difference(compartments2):
            if comp in compartments1:
                comp_differences.append(f"Compartment '{comp}' is present in {name1} but not in {name2}.")
            else:
                comp_differences.append(f"Compartment '{comp}' is present in {name2} but not in {name1}.")
    if verbose>0: 
        for comp in compartments1.intersection(compartments2):
            if biomodel1.model.get_compartment(comp).dim != biomodel2.model.get_compartment(comp).dim:
                comp_differences.append(f"Compartment '{comp}' dimensions differ: \n\t {name1}={biomodel1.model.get_compartment(comp).dim} \n\t {name2}={biomodel2.model.get_compartment(comp).dim}).")
    if len(comp_differences) == 0:
        comp_differences.append("Compartments are identical.")
    else:   
        print("Compartment differences:")
        for i in comp_differences:
            print("..." + i)

    # Compare species
    spec_differences = []
    species1 = set([sp.name for sp in biomodel1.model.species])
    species2 = set([sp.name for sp in biomodel2.model.species])
    if species1 != species2:
        for sp in species1.symmetric_difference(species2):
            if sp in species1:
                spec_differences.append(f"Species '{sp}' is present in {name1} but not in {name2}.")
            else:
                spec_differences.append(f"Species '{sp}' is present in {name2} but not in {name1}.")
    if len(spec_differences) == 0:
        spec_differences.append("Species are identical.")
    else:
        print("Species differences:")
        for i in spec_differences:
            print("..." + i)

    # Compare reactions
    compare_reactions(biomodel1.model, biomodel2.model, name1, name2)
        

    # Compare parameters
    print("Parameter differences:")

    parameters1 = set([param for param in biomodel1.model.parameter_values])
    parameters2 = set([param for param in biomodel2.model.parameter_values])
    if parameters1 != parameters2:
        for param in parameters1.symmetric_difference(parameters2):
            if param in parameters1:
                usage = count_parameter_usage(biomodel1, param)
                len_usage = sum(len(locations) for locations in usage.values())
                if ((len_usage> 0) and (verbose == 0)) or (verbose >0):
                    print(f"...Parameter '{param}' is present in {name1} but not in {name2} (used in {len_usage} places)" ) 
                if verbose>0:
                    for location, names in usage.items():
                        if len(names) > 0:
                            print(f"\t{location}: {len(names)}")
                        else:
                            if verbose > 1:
                                print(f"\t{location}: 0")
                        if verbose > 1: 
                            for n in names:
                                print(f"\t{n}")
            else:

                usage = count_parameter_usage(biomodel2, param)
                len_usage = sum(len(locations) for locations in usage.values())
                if ((len_usage > 0) and (verbose == 0)) or (verbose >0):
                    print(f"...Parameter '{param}' is present in {name2} but not in {name1} (used in {len_usage} places)" )
                if verbose>0:
                    for location, names in usage.items():
                        if len(names) > 0:
                            print(f"\t{location}: {len(names)}")
                        else:
                            if verbose > 1:
                                print(f"\t{location}: 0")
                        if verbose > 1: 
                            for n in names:
                                print(f"\t{n}")
    for param in parameters1.intersection(parameters2):
        if biomodel1.model.parameter_values[param] != biomodel2.model.parameter_values[param]:
            usage = count_parameter_usage(biomodel2, param)
            len_usage = sum(len(locations) for locations in usage.values())
            if ((len_usage > 0) and (verbose == 0)) or (verbose >0):
                print(f"...Parameter '{param}' differs in value: \n\t {name1}={biomodel1.model.parameter_values[param]} \n\t {name2}= {biomodel2.model.parameter_values[param]}")
                if verbose >1:
                    print(f"\t used in {len_usage} place(s)" )
            if verbose>0:
                for location, names in usage.items():
                    if len(names) > 0:
                        print(f"\t{location}: {len(names)}")
                    else:
                        if verbose > 1:
                            print(f"\t{location}: 0")
                    if verbose > 1: 
                        for n in names:
                            print(f"\t{n}")

