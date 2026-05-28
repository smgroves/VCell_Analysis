# Code includes functions for building new models from existing models,
# such as building a tensed model from a relaxed model, and building a transition model from a relaxed model.
# Author: Sarah Groves 05/21/2026

from matplotlib.style import use
import pyvcell.vcml as vc
from .load import *
from .plot import *
import pandas as pd
from .utils import *
from .chromosome import *
from colorama import Fore, Style, init
init(autoreset=True) # Automatically resets color after every print


def build_chromosome(relaxed_model, chr='chr19', phase="Metaphase"):
    '''
    Adapt a relaxed model to a specific chromosome size by updating the geometry and scaling kinetic parameters accordingly.`
    '''
    chromosome_dict = MCF10A_metaphase_chromosomes()

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
                           t_transition = 100):
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
    transition_model = tensed_model.model_copy(deep=True)

    # 1. Update parameters
    model = transition_model.model

    # sim params
    add_param(model, "delT", 17.1)
    add_param(model, "t_transition", t_transition)
    # KT distance from relaxed to tensed
    add_param(model, "max_vel", 0.2875 / 17.1)
    # advection
    add_param(model, "sigma_y", 0.15)
    add_param(model, "sigma_x", 0.2875)
    add_param(model, "norm_x", 'exp(( - ((L_kin_x2 - x_mid) ^ 2.0) / (2.0 * (sigma_x ^ 2.0))))')
    add_param(model, "y_mid", '(chrH / 2.0)')
    # model.add_model_parameter("x_L", L_kin_x2)
    # model.add_model_parameter("x_R", R_kin_x1)

    add_param(model, "scale_y", 0.5)

    # 2. update initial conditions in transition model using field data from relaxed model
    app = transition_model.applications[0]
    for sm in app.species_mappings:
        sm.init_conc = f"vcField('{field_data_dir}', '{sm.species_name}', t_transition, 'Volume')"

    # 3. update velocities for advecting species
    kt_bound_species = []
    chromatin_bound_species = []
    # placeholder for now -- add velocities for kt and chromatin bound species

    # update application sim parameters for transition sim
    sim = app.simulations[0]

    sim.duration = 20.0
    sim.output_time_step = 1.0

    return transition_model
