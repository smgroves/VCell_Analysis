import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import ListedColormap
sims = ["CPC_all_06_13_26_metacentric_relaxed_MCF10A_chr19_PMP1_25_136x136_",
        "CPC_all_06_13_26_metacentric_transition_tensed_MCF10A_chr19_PMP1_t_0_25_136x136_"]
# "manual_edit_CPC_all_03_21_26_metacentric_transition_MCF10A_chr19_PMP1_Gaussian_X_and_Y_t_transition_20s_17_144x144",
# "manual_edit_CPC_all_03_21_26_metacentric_transition_MCF10A_chr19_PMP1_Gaussian_X_and_Y_t_transition_60s_17_144x144",
#         "manual_edit_CPC_all_03_21_26_metacentric_transition_MCF10A_chr19_PMP1_Gaussian_X_and_Y_t_transition_120s_17_144x144",
#         "manual_edit_CPC_all_02_23_26_metacentric_relaxed_MCF10A_chr19_PMP1_20_144x144"]

# sims= ["manual_edit_CPC_all_03_21_26_metacentric_transition_MCF10A_chr19_PMP1_Gaussian_X_and_Y_Scale_y_scan_0.1_17_144x144_",
#         "manual_edit_CPC_all_02_23_26_metacentric_relaxed_MCF10A_chr19_PMP1_100_144x144"]
for sim in sims:
    x = np.linspace(3.5, 7.5, 100)
    y = np.linspace(9.5, 18.5, 100)
    X, Y = np.meshgrid(x, y)
    Z = ((3-np.sqrt(3))/6)*(Y - X) + X

    # # Create contour plot with light grey grid
    fig, ax = plt.subplots(figsize=(6, 5))
    ax.grid(color='lightgrey', linestyle='--', linewidth=0.5)
    contour = ax.contour(X, Y, Z, levels=10)

    # Add y = x line
    # ax.plot(x, x, 'r--', label='y = x')
    # Add labels to the contours
    plt.clabel(contour, inline=True, fontsize=10)

    # add Z = 4.9  contour line
    contour_Z49 = plt.contour(
        X, Y, Z, levels=[6.2], colors='black', linewidths=2)
    plt.clabel(contour_Z49, fmt={6.2: 'Z = 6.2'}, inline=True, fontsize=10)

    print(f"Processing {sim}...")
    df = pd.read_csv(
        f'/Users/catalinaalvarez/Documents/GitHub/VCell_Analysis/5_vcell_to_ch/generate_plot_pdf/summary_output/{sim}__summary.csv',
        header=0, index_col=0
    )
    # df = df[
    #     # df['min'].isin([4, 4.2, 4.4, 4.6, 4.8, 5, 5.2, 5.4, 5.6, 5.8, 6, 6.2, 6.4, 6.6, 6.8, 7]) &
    #     df['min'].isin([4, 4.5, 5, 5.5, 6, 6.5, 7]) &
    #     df['max'].isin([10, 11, 12, 13, 14, 15, 16, 17, 18])
    # ]

    names = {
        'increasing': 'increasing',
        'decreasing': 'decreasing',
        'stable': 'stable',
        np.nan: 'dissolved',
        "concave_up": "stable",
        "concave_down": "decreasing"
    }

    category_order = ['increasing', 'decreasing', 'stable', 'dissolved']
    color_map = {'increasing': 'green', 'decreasing': 'red',
                 'stable': 'orange', 'dissolved': 'black'}
    cat_to_int = {c: i for i, c in enumerate(category_order)}

    min_vals = sorted(df['min'].unique())
    max_vals = sorted(df['max'].unique())

    # Build a grid: rows = max_vals, cols = min_vals
    grid = np.full((len(max_vals), len(min_vals)), np.nan)

    min_idx = {v: i for i, v in enumerate(min_vals)}
    max_idx = {v: i for i, v in enumerate(max_vals)}

    for _, row in df.iterrows():
        cat = names[row['trend']]
        grid[max_idx[row['max']], min_idx[row['min']]] = cat_to_int[cat]

    # Compute cell edges (midpoints between values, extended at boundaries)

    def edges(vals):
        vals = np.array(vals)
        mids = (vals[:-1] + vals[1:]) / 2
        left = vals[0] - (vals[1] - vals[0]) / 2
        right = vals[-1] + (vals[-1] - vals[-2]) / 2
        return np.concatenate([[left], mids, [right]])

    x_edges = edges(min_vals)
    y_edges = edges(max_vals)

    colors = [color_map[c] for c in category_order]
    cmap = ListedColormap(colors)

    # Mask NaN cells so they show as transparent
    masked_grid = np.ma.masked_invalid(grid)

    ax.pcolormesh(x_edges, y_edges, masked_grid,
                  cmap=cmap, vmin=-0.5, vmax=len(category_order) - 0.5,
                  alpha=0.35)

    # Legend
    # patches = [mpatches.Patch(color=color_map[c], alpha=0.35, label=c)
    #            for c in category_order]
    # ax.legend(handles=patches, loc='center left', bbox_to_anchor=(1, 0.5))

    # ax.set_xlim(3.9, 6.1)
    # ax.set_ylim(9.5, 18.5)
    ax.set_ylabel('Condensate Well Concentration (max)')
    ax.set_xlabel('Soluble Well Concentration (min)')
    # ax.set_title('Spinodal Point with Simulation Results')

    plt.savefig(
        f'/Users/catalinaalvarez/Documents/GitHub/VCell_Analysis/5_vcell_to_ch/spinodal_point_plot/{sim}_filled_small.png',
        dpi=300, bbox_inches='tight', transparent=False
    )
    plt.close()
