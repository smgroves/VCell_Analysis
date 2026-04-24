import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
# Define your grid and function
x = np.linspace(3.5, 7.5 , 100)
y = np.linspace(7, 17, 100)
X, Y = np.meshgrid(x, y)
Z = ((3-np.sqrt(3))/6)*(Y - X) + X

# # Create contour plot with light grey grid
plt.figure(figsize=(12, 7))
plt.grid(color='lightgrey', linestyle='--', linewidth=0.5)
contour = plt.contour(X, Y, Z, levels=10)

#Add y = x line
# plt.plot(x, x, 'r--', label='y = x')
# Add labels to the contours
plt.clabel(contour, inline=True, fontsize=10)

# add Z = 4.9  contour line
contour_Z49 = plt.contour(X, Y, Z, levels=[6.2], colors='black', linewidths=2)
plt.clabel(contour_Z49, fmt={6.2: 'Z = 6.2'}, inline=True, fontsize=10)
# add points from simulations with color corresponding to whether droplet is increasing, decreasing, or dissolved


# for state, shape,size in zip(['relaxed','tensed'], ['o', 'X'],[200,70]):
#     try:
#         if state == 'relaxed':
#             sim = f"manual_edit_CPC_all_02_23_26_metacentric_{state}_MCF10A_chr19_PMP1_100_144x144"

#             df = pd.read_csv(f'/Users/smgroves/Documents/GitHub/VCell_Analysis/5_vcell_to_ch/generate_plot_pdf/summary_output/{sim}_summary.csv',header = 0, index_col=0)
#             names = {'increasing':'increasing', 'decreasing':'decreasing','stable':'stable', np.nan:'dissolved'}
#             #subset to x and y
#                 # only use regularly spaced points where x = 4, 4.2, 4.4, 4.6, 4.8, 5, 5.2, 5.4, 5.6, 5.8, 6, 6.2, 6.4, 6.6, 6.8, 7
#                 # y = 8, 9, 10, 11, 12, 13, 14, 15, 16
#             df = df[df['min'].isin([4, 4.2, 4.4, 4.6, 4.8, 5, 5.2, 5.4, 5.6, 5.8, 6, 6.2, 6.4, 6.6, 6.8, 7]) & df['max'].isin([8, 9, 10, 11, 12, 13, 14, 15, 16])]
#             sns.scatterplot(x=df['min'], y=df['max'],
#                             hue=[names[i] for i in df['trend']], hue_order=['increasing', 'decreasing', "stable", "dissolved"], palette=['green','red','orange','black'], alpha=0.7,
#                             marker=shape, s=size, edgecolor='black')
#     except FileNotFoundError:
#         print(f"File for {sim} not found. Skipping this simulation.")

# sim = f"CPC_all_03_30_26_metacentric_transition_MCF10A_chr19_PMP1_Gaussian_X_and_Y_KT_Bar_pull_simplified_17_144x144_"
sim = f"CPC_all_04_13_26_metacentric_relaxed_MCF10A_chr19_PMP1_100_144x144_"
# sim = f"manual_edit_CPC_all_03_21_26_metacentric_transition_MCF10A_chr19_PMP1_Gaussian_X_and_Y_Scale_y_scan_0.3_17_144x144_"
df = pd.read_csv(f'/Users/smgroves/Documents/GitHub/VCell_Analysis/5_vcell_to_ch/generate_plot_pdf/summary_output/{sim}_summary.csv',header = 0, index_col=0)
df = df[df['min'].isin([4, 4.2, 4.5, 4.4, 4.6, 4.8, 5, 5.2, 5.4,5.5, 5.6, 5.8, 6, 6.2, 6.4, 6.6,6.6, 6.8, 7]) & df['max'].isin([8, 9, 10, 11, 12, 13, 14, 15, 16])]

names = {'increasing':'increasing', 'decreasing':'decreasing','stable':'stable', np.nan:'dissolved', "concave_up":"stable", "concave_down":"decreasing"}
sns.scatterplot(x=df['min'], y=df['max'],
                hue=[names[i] for i in df['trend']], hue_order=['increasing', 'decreasing', "stable", "dissolved"], palette=['green','red','orange','black'], alpha=1,
                marker='^', s=300, edgecolor='black')

# plt.colorbar(contour)
#put legend outside of plot
plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
plt.xlim(3.7, 7.2)
plt.ylim(7, 17) 
plt.ylabel('Condensate Well Concentration (max)')
plt.xlabel('Soluble Well Concentration (min)')
# plt.title('Spinodal Point with Simulation Results (o = relaxed, x = tensed, ^ = transition)')
plt.savefig(f'/Users/smgroves/Documents/GitHub/VCell_Analysis/5_vcell_to_ch/spinodal_point_plot/{sim}_full.png', dpi=300, bbox_inches='tight', transparent = True)
plt.show()