import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
# Define your grid and function
x = np.linspace(3.5, 5.2 , 100)
y = np.linspace(5.5, 20, 100)
X, Y = np.meshgrid(x, y)
Z = ((3-np.sqrt(3))/6)*(Y - X) + X

# Create contour plot with light grey grid
plt.figure(figsize=(8, 5))
plt.grid(color='lightgrey', linestyle='--', linewidth=0.5)
contour = plt.contour(X, Y, Z, levels=10)

#Add y = x line
plt.plot(x, x, 'r--', label='y = x')
# Add labels to the contours
plt.clabel(contour, inline=True, fontsize=10)

# add Z = 4.9  contour line
contour_Z49 = plt.contour(X, Y, Z, levels=[4.9], colors='black', linewidths=2)
plt.clabel(contour_Z49, fmt={4.9: 'Z = 4.9'}, inline=True, fontsize=10)
# add points from simulations with color corresponding to whether droplet is increasing, decreasing, or dissolved
for state, shape,size in zip(['relaxed','tensed'], ['o', 'X'],[200,70]):
    try:
        sim = f"CPC_all_02_23_26_metacentric_{state}_MCF10A_chr19_PMP1_100_144x144"

        df = pd.read_csv(f'/Users/smgroves/Documents/GitHub/VCell_Analysis/5_vcell_to_ch/generate_plot_pdf/summary_output/{sim}_summary.csv',header = 0, index_col=0)
        names = {'increasing':'increasing', 'decreasing':'decreasing','stable':'stable', np.nan:'dissolved'}
        sns.scatterplot(x=df['min'], y=df['max'],
                        hue=[names[i] for i in df['trend']], hue_order=['increasing', 'decreasing', "stable", "dissolved"], palette=['green','red','orange','black'], alpha=0.7,
                        marker=shape, s=size, edgecolor='black', legend='full')
    except FileNotFoundError:
        print(f"File for {sim} not found. Skipping this simulation.")

plt.colorbar(contour)
plt.xlim(3.7, 5.2)
plt.ylim(5.5, 19)
plt.ylabel('Condensate Well Concentration (max)')
plt.xlabel('Soluble Well Concentration (min)')
plt.title('Spinodal Point with Simulation Results (o = relaxed, x = tensed)')
plt.savefig(f'/Users/smgroves/Documents/GitHub/VCell_Analysis/5_vcell_to_ch/spinodal_point_plot/{sim}.png', dpi=300, bbox_inches='tight')
plt.show()