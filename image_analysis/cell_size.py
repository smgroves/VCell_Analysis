import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm
import matplotlib.mlab as mlab

import seaborn as sns
indir = "/Users/smgroves/Box/CPC_Model_Project/Cell size images/Segmentation"

#pixel dictionary
pixels = {"2X":2.02, "4X":1.01,'10X':.505, "20X":.252, "40X":.126}

volume_to_pixel = lambda vol: np.cbrt((3/(4*np.pi))*vol)/.505
def plot_hist_sizes(indir, celltype, threshold = 10000, save = False, filter_formfactor = True, suffix = ""):
    print(celltype)
    df = pd.read_csv(f"{indir}/{celltype}_Cells.csv",index_col=None, header=0)
    if filter_formfactor:
        df = df.loc[df["AreaShape_FormFactor"]>=0.8]
    df['Radius'] = np.sqrt(df["AreaShape_Area"]/np.pi)
    df['Radius_um'] = df['Radius']*.505
    df['Volume_um'] = (4/3)*(np.pi*df['Radius_um']**3)
    df['under_threshold'] = df['Volume_um']<threshold
    data_max = df['Volume_um'].max()

    subset = df.loc[df['Volume_um']<threshold].copy()
    (mu, sigma) = norm.fit(subset['Volume_um'])
    print(mu)
    # the histogram of the data

    n, bins, patches = plt.hist(df['Volume_um'], 60,  alpha=0.75, density = True)
    plt.close()
    f, ax = plt.subplots()
    # add a 'best fit' line
    y = norm.pdf(bins, mu, sigma)
    plt.plot(bins, y, 'r--', linewidth=2)
    g = sns.histplot(data = df, x = 'Volume_um', hue = 'under_threshold',
                     palette=['blue','red'],
                     stat = 'density',
                     bins = 60, common_norm=True)
    g.legend([],[], frameon=False)

    plt.axvline(x = mu, linestyle = '--', c = 'gray')
    plt.title(f"{celltype} Cell Sizes")
    plt.ylabel("Density")
    plt.xlabel("Cell Volume (um^3)")
    plt.text(.99, .99, f'mu = {round(mu,3)} '
                       f'\n diameter = {round(2*volume_to_pixel(mu)*.505,3)} (px: {round(2*volume_to_pixel(mu),3)})'
                       f'\n sigma ={round(sigma,3)}'
                       f'\n data max = {round(data_max,3)}'
                       f'\n threshold = {threshold}'
                       f'\n Filter Form Factor = {filter_formfactor}', ha='right', va='top', transform=ax.transAxes)
    plt.tight_layout()
    if save:
        plt.savefig(f"{indir}/{celltype}_threshold{threshold}_size_histogram{suffix}.pdf")
        plt.close()
    else:
        plt.show()

plot_hist_sizes(indir, celltype="HCC1806", threshold = 6000, save = True)
