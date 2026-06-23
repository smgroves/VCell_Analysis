# Code includes functions for building new models from existing models,
# such as building a tensed model from a relaxed model, and building a transition model from a relaxed model.
# Author: Sarah Groves 05/21/2026

from matplotlib.style import use
from numpy import mean
import pyvcell.vcml as vc
from .load import *
from .plot import *
import pandas as pd
from .utils import *
from .chromosome import *
from colorama import Fore, Style, init
init(autoreset=True) # Automatically resets color after every print


def build_chromosome(relaxed_model, chr='chr19', phase="Metaphase", KT_loc="metacentric"):
    '''
    Adapt a relaxed model to a specific chromosome size by updating the geometry and scaling kinetic parameters accordingly.`
    '''
    chromosome_dict = metaphase_chromosomes()

    #take only first decimal for chr_length
    pmp_lengths = calculate_pmp_length_df(chromosome_dict)
    chr_length = round(pmp_lengths.loc[chr, phase], 1)
    scaling_factor_df = calculate_scaling_factor_df(pmp_lengths)
    chr_scale = scaling_factor_df.loc[chr, phase]

    chr_W = relaxed_model.model.parameter_values['chrW']

    print(
        f"{Fore.BLUE}Building model for {chr} with length {chr_length} um and {chr_W} um width for phase {phase} (scaling factor {chr_scale}){Style.RESET_ALL}"
    )

    ############################################
    # update parameters for chromosome size
    ############################################
    relaxed_model.model.set_parameter_value("chrN_scaling", chr_scale)
    relaxed_model.model.set_parameter_value("chrH", chr_length)
    ############################################
    # update geometry to match chromosome size
    ############################################
    for app in relaxed_model.applications:
        geo = app.geometry
        geo.extent = (chr_W, chr_length, 1)
        print(
            f"Updated geometry extent to {geo.extent} for application '{app.name}'"
        )
        # update chromatin compartment to match new chromosome size
        chromatin = geo.subvolumes["name" == 'chr']
        chromatin.analytic_expr = f'(x >= 0.0) && (x <= {chr_W}) && (y >= 0.0) && (y <= {chr_length})'
        expr = replace_geo_expr_param_to_numeric(chromatin.analytic_expr,
                                                 relaxed_model.model)
        chromatin.analytic_expr = expr

        # update kinetochore compartments to match new geometry
        void = geo.subvolumes["name" == 'void']
        if KT_loc == "metacentric":
            relaxed_model.model.set_parameter_value("kin_y1", "((chrH / 2) - (kinH / 2))")
            relaxed_model.model.set_parameter_value("kin_y2", "((chrH / 2) + (kinH / 2))")
        elif KT_loc == "telocentric":
            relaxed_model.model.set_parameter_value("kin_y1", 0)
            relaxed_model.model.set_parameter_value("kin_y2", "kinH") # keep same kinetochore height as metacentric case, just move to end of chromosome
        else:
            raise ValueError("Invalid KT_loc value. Must be 'metacentric' or 'telocentric'.")
        void.analytic_expr = f'(((x >= 0.0) && (x < L_kin_x1) && (y >= kin_y1) && (y <= kin_y2)) || ((x > R_kin_x2) && (x <= chrW) && (y >=kin_y1) && (y <= kin_y2)))'
        expr = replace_geo_expr_param_to_numeric(void.analytic_expr,
                                                 relaxed_model.model)
        print(expr)
        void.analytic_expr = expr
    plot_2d_geo(geo, title=f"{chr} Geometry\n(length={chr_length} um)")

    ############################################
    #update mesh size for simulations
    ############################################

    for sim in app.simulations:
        sim.mesh_size = (52, int(chr_length / 0.025), 1)
        print(
            f"Updated mesh size to {sim.mesh_size} for simulation '{sim.name}'"
        )
    return relaxed_model



def build_tensed_model(relaxed_model, application="Spatial"):
    """
    Build a tensed model from a relaxed model.

    Parameters:
    relaxed_model: The relaxed VCell model.
    application: The application name for the relaxed model.

    Returns:
    tensed_model: The generated tensed model.
    """
    # Generate the transition model from the relaxed model
    tensed_model = relaxed_model.model_copy(deep=True)

    # 1. update global parameters for tensed model
    model = tensed_model.model

    # KK_disSim = 1.15
    # should update L_kin_x1/2 and R_kin_x1/2 (reflected in new geometry)
    model.set_parameter_value("KK_disSim", 1.15)

    # new KdNDC80TTK_MT and KdNDC80pTTK_MT (replaced old NDc80_availability);
    # unlike VCell GUI version, we will directly change the value instead of making new parameters
    # model.add_model_parameter("KdNDC80TTK_MT", 1261.5)
    # model.add_model_parameter("KdNDC80pTTK_MT", 30.5)
    add_param(model, "KdNDC80TTK_MT", 1261.5)
    add_param(model, "KdNDC80pTTK_MT", 30.5)

    model.set_parameter_value("KdNDC80TTK", "KdNDC80TTK_MT")
    model.set_parameter_value("KdNDC80pTTK", "KdNDC80pTTK_MT")

    # 2. update geometry to move KT compartments
    app = tensed_model.applications[0]
    geo = app.geometry
    void = geo.subvolumes["name" == 'void']
    # just remove void and update KT compartments to match new geometry

    expr_template = f'(((x >= 0.0) && (x < L_kin_x1) && (y >= kin_y1) && (y <= kin_y2)) || ((x > R_kin_x2) && (x <= chrW) && (y >=kin_y1) && (y <= kin_y2)))'

    expr = replace_geo_expr_param_to_numeric(expr_template, model)
    void.analytic_expr = expr
    fig, axes = plt.subplots(figsize=(12, 5), ncols=2)

    plot_2d_geo(relaxed_model.applications[0].geometry,
                ax=axes[0],
                title="Relaxed Geometry")

    plot_2d_geo(geo, ax=axes[1], title="Tensed Geometry")

    plt.tight_layout()
    plt.show()
    compare_models(relaxed_model,
                   tensed_model,
                   name1="Relaxed",
                   name2="Tensed",
                   verbose=1)  # check model differences

    return tensed_model



def build_transition_model(relaxed_model,
                           field_data_dir,
                           application="Spatial",
                           t_transition = 0,
                           high_t_res =False):
    """
    Build a transition model from a relaxed model.
    Parameters:
    relaxed_model: The relaxed VCell model.
    field_data_dir: The directory containing the field data for the relaxed model, to be used as IC for the transition model.
    application: The application name for the relaxed model.
    Returns:
    transition_model: The generated transition model.
    """

    # start with tensed model as the base for the transition model, since we want to keep the updated geometry and parameters
    tensed_model = build_tensed_model(relaxed_model, application)
    #moves KT void and changes KK_disSim to 1.15
    transition_model = tensed_model.model_copy(deep=True)

    # 1. Update parameters
    model = transition_model.model

    # sim params
    delT = 17.1/24
    add_param(model, "delT", delT)
    add_param(model, "t_transition", t_transition)
    # KT distance from relaxed to tensed
    add_param(model, "KT_distance_move", "(KK_disSim-KK_disRef) / 2.0")
    add_param(model, "max_vel", "KT_distance_move/delT")
    add_param(model, "L_kin_x2_relaxed", "x_mid - KK_disRef/2")
    add_param(model, "R_kin_x1_relaxed", "x_mid + KK_disRef/2")
    # advection
    add_param(model, "sigma_y", "kinH/2")
    add_param(model, "sigma_x", "KT_distance_move")
    add_param(model, "scale_y", 0.3)
    add_param(model, "norm_x", 'exp(( - ((L_kin_x2_relaxed - x_mid) ^ 2.0) / (2.0 * (sigma_x ^ 2.0))))')
    add_param(model, "y_mid", "chrH/2")
    x_velocity = "((((x - x_mid) / delT) * exp(( - ((x - x_mid) ^ 2.0) / (2.0 * (sigma_x ^ 2.0)))) / norm_x * exp(( - ((y - y_mid) ^ 2.0) / (2.0 * (sigma_y ^ 2.0)))) * ((x >= L_kin_x2_relaxed) && (x <= R_kin_x1_relaxed))) + ( - max_vel * exp(( - ((y - y_mid) ^ 2.0) / (2.0 * (sigma_y ^ 2.0)))) * (x < L_kin_x2_relaxed)) + (max_vel * exp(( - ((y - y_mid) ^ 2.0) / (2.0 * (sigma_y ^ 2.0)))) * (x > R_kin_x1_relaxed)))* (t <= delT)"
    y_velocity = "( - (y - y_mid) / delT * scale_y * exp(( - ((y - y_mid) ^ 2.0) / (2.0 * (sigma_y ^ 2.0)))))* (t <= delT)"

    # 2. update initial conditions in transition model using field data from relaxed model
    app = transition_model.applications[0]
    for sm in app.species_mappings:
        sm.init_conc = f"vcField('{field_data_dir}', '{sm.species_name}', t_transition, 'Volume')"

    # 3. update velocities for advecting species
    kt_bound_species = ["BUB1a_pknl1","KNL1","NDC80","NDC80_pTTKa","NDC80_pTTKi","NDC80_TTKa","NDC80_TTKi",'pKNL1','pKNL1_bub1a',"pNDC80","pNDC80_pTTKa","pNDC80_pTTKi","pNDC80_TTKa","pNDC80_TTKi"]
    chromatin_bound_species = ["H3","H2A","pH3","pH2A","H3_CPCa","H3_CPCi",'H3S10rep',"I","pH2A_SGO1","pH2A_SGO1_CPCa",'pH2A_SGO1_CPCi','pH3_CPCa','pH3_CPCi','pH3S10rep']
    # placeholder for now -- add velocities for kt and chromatin bound species
    for my_species_name in kt_bound_species:
        app.get_species_mapping(my_species_name).velocity_x = x_velocity
        app.get_species_mapping(my_species_name).velocity_y = y_velocity
    for my_species_name in chromatin_bound_species:
        app.get_species_mapping(my_species_name).velocity_x = x_velocity
        app.get_species_mapping(my_species_name).velocity_y = y_velocity

    # update application sim parameters for transition sim
    sim = app.simulations[0]

    if high_t_res:
        sim.duration = np.ceil(delT)
        sim.output_time_step = np.round(delT / 17.1, 2)


    return transition_model

def build_double_chromosome(relaxed_model, application="Spatial", left = "relaxed", right = "relaxed"):
    """
    Build a double chromosome model from a relaxed model.
    Parameters:
    relaxed_model: The relaxed VCell model.
    application: The application name for the relaxed model.
    Returns:
    double_chromosome_model: The generated double chromosome model.
    """

    double_model = relaxed_model.model_copy(deep=True)
    model = double_model.model
    app = double_model.applications[0]
    geo = app.geometry
    #update geometry to be double width
    geo.extent = [geo.extent[0] * 2, geo.extent[1], geo.extent[2]]

    # update [0-4] void regions and 1 chr region appropriately based on passed left and right
    void = geo.subvolumes["name" == 'void']
    chr = geo.subvolumes["name" == 'chr']
    if left == "relaxed":
        expr_template_L = f'(((x >= 0.0) && (x < L_kin_x1) && (y >= kin_y1) && (y <= kin_y2)) || ((x > R_kin_x2) && (x <= chrW) && (y >=kin_y1) && (y <= kin_y2)))'
    elif left == "tensed":
        expr_template_L = ""
    
    if right == "relaxed":
        expr_template_R = f'(((x >= chrW) && (x < L_kin_x1+chrW) && (y >= kin_y1) && (y <= kin_y2)) || ((x > R_kin_x2+chrW) && (x <= chrW+chrW) && (y >=kin_y1) && (y <= kin_y2)))'
    elif right == "tensed":
        expr_template_R = ""

    if expr_template_L == "":
        expr_template = expr_template_R
    elif expr_template_R == "":
        expr_template = expr_template_L
    else:
        expr_template = f'{expr_template_L} || {expr_template_R}'
    expr = replace_geo_expr_param_to_numeric(expr_template, model)
    void.analytic_expr = expr

    #update localization of initial conditions for each species
    #all diffusible species should have the same concentration as before
    #all localized species should be mapped to the new geometry

    #build dictionary based on left and right parameters
    #H2A, H3, HASPINi, I, KNL1, NDC80
    species_dict = { "KNL1":"", "NDC80":""}
    species_dict["HASPINi"] = "HASPIN_ic*(((x >= L_has_x3) && (x <= R_has_x4))) || (((x >= L_has_x3 +chrW) && (x <= R_has_x4 +chrW)))"

    if (left == "relaxed") and (right == "relaxed"):
        species_dict["KNL1"] ="KNL1_ic * (((x >= R_kin_x1) && (x <= R_kin_x2) && (y >= kin_y1) && (y <= kin_y2)) ||((x >= L_kin_x1) && (x <= L_kin_x2) && (y >= kin_y1) && (y <= kin_y2)) || ((x >= (R_kin_x1 + chrW)) && (x <= (R_kin_x2 + chrW)) && (y >= kin_y1) && (y <= kin_y2)) ||((x >= (L_kin_x1 + chrW)) && (x <= (L_kin_x2 + chrW)) && (y >= kin_y1) && (y <= kin_y2)))"
        species_dict["NDC80"]="NDC80_ic * (((x >= R_kin_x1) && (x <= R_kin_x2) && (y >= kin_y1) && (y <= kin_y2)) ||((x >= L_kin_x1) && (x <= L_kin_x2) && (y >= kin_y1) && (y <= kin_y2)) || ((x >= (R_kin_x1 + chrW)) && (x <= (R_kin_x2 + chrW)) && (y >= kin_y1) && (y <= kin_y2)) ||((x >= (L_kin_x1 + chrW)) && (x <= (L_kin_x2 + chrW)) && (y >= kin_y1) && (y <= kin_y2)))"
    print(species_dict.values())

    #add initial concentrations for each species
    for species in species_dict.keys():
        sm = app.get_species_mapping(species)
        sm.init_conc = species_dict[species]
        print("Updated initial concentrations:")
        print(f"Species: {species}, Initial Concentration: {sm.init_conc}")

    #update mesh size
    sim = app.simulations[0]

    sim.mesh_size = [sim.mesh_size[0] * 2, sim.mesh_size[1], sim.mesh_size[2]]

    
    fig, axes = plt.subplots(figsize=(12, 5), ncols=2)

    plot_2d_geo(relaxed_model.applications[0].geometry,
                ax=axes[0],
                title="Relaxed Geometry")

    plot_2d_geo(geo, ax=axes[1], title=f"Double Geometry for {left} and {right}")

    plt.tight_layout()
    plt.show()

    return double_model

def get_all_numeric_parameters(biomodel):
    """
    Returns a flat dict of all numeric parameters that can be perturbed:
      - global model parameters
      - kinetics parameters (keyed as "reaction.param")
      - species initial conditions per application (keyed as "app/species.init_conc")
    String expressions and vcField references are skipped.
    """
    params = {}

    # # Global model parameters


    # # Kinetics parameters
    # # for rxn in biomodel.model.reactions:
    # #     if rxn.kinetics:
    # #         for p in rxn.kinetics.kinetics_parameters:
    # #             if isinstance(p.value, (int, float)):
    # #                 params[f"{rxn.name}.{p.name}"] = p.value

    # # Initial conditions
    # for app in biomodel.applications:
    #     for sm in app.species_mappings:
    #         if isinstance(sm.init_conc, (int, float)):
    #             params[f"{app.name}/{sm.species_name}.init_conc"] = sm.init_conc
    
        #kinetic params 
    # kinetic = [  'Dapp', 'Dapp_kt', 'alpha_kt',  'KdpNDC80TTK', 'phiNDC80', 'KdpNDC80pTTK']
    
    kinetic = ['Dcyt',"kcatCPC",'KmCPC','KdH3', 'KdpH3','kcatPLK1', 'KmPLK1',"alpha","kcatH2AH3","KmH2AH3","KdSgo1","KdpH2ASgo1",'kcisCPC',   'kcisTTK', 'kcatTTK',  'KmTTK',
               "KdNDC80TTK","KdNDC80pTTK","kpp_ref",'kcatplk1','Kmplk1',"kbind",'kcatCPCsub','KmCPCsub','kppCPC','kcatTTKsub','kmTTKsub','phiNdc80','Da','Da_kt','alpha_kt']


    # ic params
    #if the parameter name includes the word "copiespc" add to ic_list
    ic_list = []
    for p in biomodel.model.model_parameters:
        if "copiespc" in p.name:
            ic_list.append(p.name)

    for p in biomodel.model.model_parameters:
        # if isinstance(p.value, (int, float)):
        if (p.name in kinetic) or (p.name in ic_list):
            params[p.name] = p.value

    if len(params) != len(kinetic) + len(ic_list):
        print("Not all parameters were found.")
        #print missing
        for k in kinetic + ic_list:
            if k not in params:
                print(f"Missing parameter: {k}")
    return params



def perturb_parameters(biomodel, cv = .1, cv_kinetic = None, cv_ic = None, seed: int | None = None) -> tuple:
    """
    Resolve all kinetics parameters to numbers, perturb each by a lognormal
    factor with the given CV, and set them as literal floats in a deep copy.

    Returns (perturbed_biomodel, perturbed_values_dict) so you can record
    exactly what was set.
    """

    rng = np.random.default_rng(seed)
    if cv_kinetic is None:
        cv_kinetic = cv
    if cv_ic is None:
        cv_ic = cv

    sigma_kinetic = np.sqrt(np.log(1 + cv_kinetic**2))
    sigma_ic = np.sqrt(np.log(1 + cv_ic**2))

    perturbed_model = biomodel.model_copy(deep=True)
    perturbed_values = {}


    #kinetic params 
    # kinetic = [  'Dapp', 'Dapp_kt', 'alpha_kt',  'KdpNDC80TTK', 'phiNDC80', 'KdpNDC80pTTK']
    
    kinetic = ['Dcyt',"kcatCPC",'KmCPC','KdH3', 'KdpH3','kcatPLK1', 'KmPLK1',"alpha","kcatH2AH3","KmH2AH3","KdSgo1","KdpH2ASgo1",'kcisCPC',   'kcisTTK', 'kcatTTK',  'KmTTK',
               "KdNDC80TTK","KdNDC80pTTK","kpp_ref",'kcatplk1','Kmplk1',"kbind",'kcatCPCsub','KmCPCsub','kppCPC','kcatTTKsub','kmTTKsub','phiNDC80','Da','Da_kt','alpha_kt']


    # ic params
    #if the parameter name includes the word "copiespc" add to ic_list
    ic_list = []
    for p in perturbed_model.model.model_parameters:
        if "copiespc" in p.name:
            ic_list.append(p.name)

    for p in perturbed_model.model.model_parameters:
        if (p.name in kinetic) or (p.name in ic_list):
            if isinstance(p.value, (int, float)):
                key = f"{p.name}"
                if p.name in kinetic:
                    sigma = sigma_kinetic
                else:
                    sigma = sigma_ic
                new_val = p.value * rng.lognormal(mean=0, sigma=sigma)
                p.value = new_val
                perturbed_values[key] = new_val
            # if its a string, add multiplier to the string
            elif isinstance(p.value, str):
                key = f"{p.name}"
                if p.name in kinetic:
                    sigma = sigma_kinetic
                else:
                    sigma = sigma_ic
                multiplier = rng.lognormal(mean=0, sigma=sigma)
                new_val = f"({p.value})*{multiplier}"
                perturbed_values[key] = new_val



    return perturbed_model, perturbed_values