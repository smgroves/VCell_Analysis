# %%
from plot_vcml_velocity import compare_custom_velocity
from plot_vcml_velocity import VCMLVelocityPlotter

# %%
plotter = VCMLVelocityPlotter(
    "./models/_02_23_26_CPC_metacentric_transition_MCF10A_chr19_PMP1.vcml")
# plotter.plot_1d("pH3_CPCa", axis="X", slice_val=1.8)    # line plot
plotter.plot_2d("pH3_CPCa")                   # 2D heatmap
# %%
plotter.use_simspec("2_Spatial Gaussian X no cross product")
plotter.overlay_vcell_csv(
    "H2A",
    csv_path="./models/SimID_307011475_0__Slice_XY_0_H2A_velocityX_0000.csv",
    axis="x",
    fixed_coord=1.8,     # y slice through KT band
    # save_path="overlay.png"
)
# %%

CSV = "./models/SimID_307011475_0__Slice_XY_0_H2A_velocityX_0000.csv"
# kin_y1, kin_y2, L_x1, L_x2, R_x1, R_x2
KT = (1.65, 1.95, 0.0, 0.075, 1.225, 1.3)
# %%
# # 1. VCell-style string (&&, ^) with named params
compare_custom_velocity(
    CSV,
    "(((x - x_mid) / delT * exp(( - ((x - x_mid) ^ 2.0) / (2.0 * (sigma_x_X ^ 2.0)))) / (exp((( - (x_L_L - x_mid) ^ 2.0) / (2.0 * (sigma_x_X ^ 2.0))))) * ((y >= kin_y1) && (y <= kin_y2) && (x >= 0.3625) && (x <= 0.9375))) + ( - max_vel * ((y >= kin_y1) && (y <= kin_y2) && (x < 0.3625))) + (max_vel * ((y >= kin_y1) && (y <= kin_y2) && (x > 0.9375))))",
    # "(((x - x_mid) / delT * exp(( - ((x - x_mid) ^ 2.0) / (2.0 * (sigma_x_X ^ 2.0)))) *((y >= kin_y1) && (y <= kin_y2) && (x >= 0.3625) && (x <= 0.9375))) + ( - max_vel * ((y >= kin_y1) && (y <= kin_y2) && (x < 0.3625))) + (max_vel * ((y >= kin_y1) && (y <= kin_y2) && (x > 0.9375))))",
    # "(((x - x_mid) / delT * exp(( - ((x - x_mid) ^ 2.0) / (2.0 * (sigma_x_X ^ 2.0)))) *((y >= kin_y1) && (y <= kin_y2) && (x >= 0.3625) && (x <= 0.9375))) + ( - max_vel * ((y >= kin_y1) && (y <= kin_y2) && (x < 0.3625))) + (max_vel * ((y >= kin_y1) && (y <= kin_y2) && (x > 0.9375))))",

    extra_params={"x_mid": 0.65, "delT": 17.1, "kin_y1": 1.65, "kin_y2": 1.95,
                  "sigma_x_X": 0.2875, "x_L_L": 0.3625, "max_vel": 0.0167},
    axis="x", fixed_coord=1.8, kt_bounds=KT,
)

# # 2. Python/numpy string (np., **, standard comparisons)
# compare_custom_velocity(
#     CSV,
#     "(x - 0.65) / 17.1 * (y >= 1.65) * (y <= 1.95)",
#     axis="x", fixed_coord=1.8, kt_bounds=KT,
# )

# x_mid = 0.65
# # 3. Python callable
# compare_custom_velocity(
#     CSV,
#     lambda x, y: (x - x_mid) / 17.1 * (y >= 1.65) * (y <= 1.95),
#     axis="x", fixed_coord=1.8, kt_bounds=KT,
# )
# %%
# SimID_307973160_0__Slice_XY_0_H2A_velocityY_0000
plotter = VCMLVelocityPlotter(
    "./models/_02_23_26_CPC_metacentric_transition_MCF10A_chr19_PMP1.vcml")
plotter.use_simspec("6_Spatial Gaussian X and Y_KT_Bar_pull")
plotter.plot_2d("pH3_CPCa", component="Y")                   # 2D heatmap
# %%
plotter.use_simspec("6_Spatial Gaussian X and Y_KT_Bar_pull")

plotter.overlay_vcell_csv(
    "H2A",
    csv_path="./models/SimID_307973160_0__Slice_XY_0_H2A_velocityY_0000.csv",
    axis="y",
    component="Y",
    # save_path="overlay.png"
)

# %%
plotter.use_simspec("6_Spatial Gaussian X and Y_KT_Bar_pull")
plotter.plot_1d("pH3_CPCa", component="Y", axis="y")

plotter.use_simspec("5_Spatial Gaussian X and Y")
plotter.plot_1d("pH3_CPCa", component="Y", axis="y")

# %%
CSV = "./models/SimID_307973160_0__Slice_XY_0_H2A_velocityY_0000.csv"

# # 1. VCell-style string (&&, ^) with named params
compare_custom_velocity(
    CSV,
    "(((-(y - kin_y1) * nu * exp((-((y - kin_y1)^2.0)) / (2.0 * (sigma_y_y^2.0))) / (sigma_y_y * delT)) * (y < kin_y1))+((-(y - kin_y2) * nu * exp((-((y - kin_y2)^2.0)) / (2.0 * (sigma_y_y^2.0))) / (sigma_y_y * delT)) * (y > kin_y2)))",
    extra_params={"y_mid": 1.8, "delT": 17.1, "kin_y1": 1.65, "kin_y2": 1.95,
                  "nu": 0.1, "sigma_y_y": 0.5},
    axis="y", fixed_coord=1.8, kt_bounds=KT,
)

# %%
plotter.use_simspec("5_Spatial Gaussian X and Y")
plotter.plot_1d("pH3_CPCa", component="X", axis="x")
# %%
#['1_Spatial', '3_Spatial Gaussian X', '2_Spatial Gaussian X no cross product', '5_Spatial Gaussian X and Y', '4_Spatial Gaussian X and Y no cross product', '6_Spatial Gaussian X and Y_KT_Bar_pull']
