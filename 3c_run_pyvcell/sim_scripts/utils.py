# Author: Sarah Groves 05/21/2026
import pyvcell

#patch for problem with add_model_parameter function
def add_param(model, param_name, value):
    """Add a parameter to the model with the given name, value, and optional role."""
    model.add_model_parameter(param_name, value)
    assert param_name == model.model_parameters[-1].name
    model.model_parameters[-1].role = "user defined"


def inspect_parameters(model):
    # Inspect all parameters to find the problematic one
    print("\n=== Checking all model parameters ===")
    print(model.parameter_values)
    for name, value in model.parameter_values.items():
        print(f"Parameter: {name}")
        print(f"  Value: {value}")
        print(f"  Type: {type(value)}")

        # Check if it's actually a parameter object with more attributes
        if hasattr(model, 'parameters'):
            for p in model.parameters:
                if p.name == name:
                    print(f"  Parameter object type: {type(p)}")
                    print(f"  Attributes: {dir(p)}")
                    if hasattr(p, 'role'):
                        print(f"  Role: {p.role}")
                    break

    # # Try to serialize to VCML to trigger the error with diagnostics
    # try:
    #     vcml_str = model.to_vcml()  # or whatever method triggers the conversion
    # except Exception as e:
    #     print(f"\n!!! Error occurred: {e}")
    #     print("Last parameter checked above is likely the culprit")
def check_geometry_expressions(model):
    '''
    Check that all geometry expressions in the model are valid and can be evaluated without errors. This can help identify any parameters that are causing issues in the geometry definitions.
    '''
    for app in model.applications:
        geo = app.geometry
        for compartment in geo.subvolumes:
            try:
                # Attempt to evaluate the analytic expression for the compartment
                expr = compartment.analytic_expr
                # Here we would need to implement a method to evaluate the expression, which may involve parsing it and substituting parameter values
                # This is a placeholder for the actual evaluation logic
                print(expr)
            except Exception as e:
                print(f"Error evaluating geometry expression for compartment '{compartment.name}': {e}")
                print(f"Expression: {expr}")
                # Optionally, you could raise an error here or continue checking other compartments


def replace_geo_expr_param_to_numeric(expr_template, model):
    # get all parameter names to replace
    replace_list = model.parameter_values.keys()
    # Replace all parameter names with their values
    expr = expr_template
    # while any parameter names remain in the expression, replace them with their values
    while any(param_name in expr for param_name in replace_list):
        shrotlist = [
            param_name for param_name in replace_list if param_name in expr]
        for param_name in shrotlist:
            param_value = model.parameter_values[param_name]
            expr = expr.replace(param_name, str(param_value))

    return expr
