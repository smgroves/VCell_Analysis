# Code includes functions for building new models from existing models,
# such as building a tensed model from a relaxed model, and building a transition model from a relaxed model.
# Author: Sarah Groves 05/21/2026

import pyvcell.vcml as vc
from .load import *
from .plot import *


def build_tensed_model(relaxed_vcml_file, application="Spatial"):
    """
    Build a tensed model from a relaxed model.

    Parameters:
    relaxed_vcml_file: The path to the relaxed VCell model file.
    field_data_dir: The directory containing the field data for the relaxed model, to be used as IC for the transition model. 
    application: The application name for the relaxed model.

    Returns:
    transition_model: The generated transition model.
    """
    # Load the relaxed model
    relaxed_model = vc.load_vcml_file(relaxed_vcml_file)

    # Generate the transition model from the relaxed model
    tensed_model = relaxed_model.model_copy(deep=True)

    # 1. update global parameters for tensed model
    model = tensed_model.model

    # KK_disSim = 1.15
    # should update L_kin_x1/2 and R_kin_x1/2 (reflected in new geometry)
    model.set_parameter_value("KK_disSim", 1.15)

    # new KdNDC80TTK_MT and KdNDC80pTTK_MT (replaced old NDc80_availability);
    # unlike VCell GUI version, we will directly change the value instead of making new parameters
    model.add_model_parameter("KdNDC80TTK_MT", 1261.5)
    model.add_model_parameter("KdNDC80pTTK_MT", 30.5)

    model.set_parameter_value("KdNDC80TTK", "KdNDC80TTK_MT")
    model.set_parameter_value("KdNDC80pTTK", "KdNDC80pTTK_MT")

    # 2. update geometry to move KT compartments
    app = tensed_model.applications[0]
    geo = app.geometry
    void = geo.subvolumes["name" == 'void']
    # just remove void and update KT compartments to match new geometry
    void.analytic_expr = '0.0'
    plot_2d_geo(
        relaxed_model.applications[0].geometry, title="Relaxed Geometry")

    plot_2d_geo(geo, title="Tensed Geometry")
    compare_models(relaxed_model, tensed_model, name1="Relaxed",
                   name2="Tensed", verbose=1)  # check model differences

    return tensed_model


def build_transition_model(relaxed_vcml_file, field_data_dir, application="Spatial"):
    """
    Build a transition model from a relaxed model.
    Parameters:
    relaxed_vcml_file: The path to the relaxed VCell model file.
    field_data_dir: The directory containing the field data for the relaxed model, to be used as IC for the transition model.
    application: The application name for the relaxed model.
    Returns:
    transition_model: The generated transition model.
    """

    # start with tensed model as the base for the transition model, since we want to keep the updated geometry and parameters
    tensed_model = build_tensed_model(relaxed_vcml_file, application)
    transition_model = tensed_model.model_copy(deep=True)

    # 1. Update parameters
    model = transition_model.model

    # sim params
    model.add_model_parameter("delT", 17.1)
    model.add_model_parameter("t_transition", 100)
    # KT distance from relaxed to tensed
    model.add_model_parameter("max_vel", '0.2875/delT')

    # advection
    model.add_model_parameter("sigma_y", 0.15)
    model.add_model_parameter("sigma_x", 0.2875)
    model.add_model_parameter(
        "norm_x", 'exp(( - ((x_L_L - x_mid) ^ 2.0) / (2.0 * (sigma_x_X ^ 2.0))))')
    model.add_model_parameter("y_mid", '(chrH / 2.0)')
    # model.add_model_parameter("x_L", L_kin_x2)
    # model.add_model_parameter("x_R", R_kin_x1)

    model.add_model_parameter("scale_y", 0.5)

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
