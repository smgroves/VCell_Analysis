# %%
import matplotlib.colors as mcolors
from sklearn.datasets import load_iris
from pca import pca as pc
from scipy.cluster.hierarchy import dendrogram
from matplotlib import pyplot as plt
from sklearn.cluster import AgglomerativeClustering
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.cluster import hierarchy

# %% Load RNA-seq data
TCGA_data = pd.read_csv(
    './data/breast_TCGA_network_proteins_longdata.csv', index_col=0)
print(TCGA_data.head())

CCLE_data = pd.read_csv(
    './data/CCLE_Log_transformed_TPM_MCF10A_longdata.csv', index_col=0)
print(CCLE_data.head())

MCF10A_1_data = pd.read_csv(
    './data/Kang_etal_2013_GSM1100206_SL27418_network_longdata.csv', index_col=0)
print(MCF10A_1_data.head())

MCF10A_2_data = pd.read_csv(
    './data/Kang_etal_2013_GSM1100205_SL27417_network_longdata.csv', index_col=0)
print(MCF10A_2_data.head())


# %%
# reshape from long to wide
TCGA_wide = TCGA_data.pivot_table(
    index='cell_line', columns='gene', values='rna_counts', aggfunc='first')

TCGA_wide.rename(
    columns={'SGOL1': 'SGO1', "CASC5": "KNL1", "GSG2": "HASPIN"}, inplace=True)

CCLE_wide = CCLE_data.pivot_table(
    index='cell_line_display_name', columns='Protein', values='rna_counts', aggfunc='first')

MCF10A_1_wide = MCF10A_1_data.pivot_table(
    index='cell_line', columns='gene', values='rna_counts', aggfunc='first')
MCF10A_2_wide = MCF10A_2_data.pivot_table(
    index='cell_line', columns='gene', values='rna_counts', aggfunc='first')
MCF10A_1_wide.rename(
    columns={'SGOL1': 'SGO1', "CASC5": "KNL1", "GSG2": "HASPIN"}, inplace=True)
MCF10A_1_wide.index = ['MCF10A_cellline_1']
MCF10A_2_wide.rename(
    columns={'SGOL1': 'SGO1', "CASC5": "KNL1", "GSG2": "HASPIN"}, inplace=True)
MCF10A_2_wide.index = ['MCF10A_cellline_2']

# %%
# merge dataframes by rows
combined_data = pd.concat(
    [TCGA_wide, CCLE_wide, MCF10A_1_wide, MCF10A_2_wide], axis=0, join='outer')

# %%
# z score normalization
scaler = StandardScaler()
normalized_data = pd.DataFrame(
    scaler.fit_transform(combined_data.fillna(0)),
    index=combined_data.index,
    columns=combined_data.columns
)
print(normalized_data.head())

# %%
# add a column to normalized data about tissue type


def get_tissue_type(cell_line):
    if cell_line in TCGA_wide.index:
        return 'TCGA_Breast'
    elif 'MCF10A' in cell_line:
        if "cellline" in cell_line:
            return 'MCF10A_cellline'
        else:
            return 'MCF10A_organoid'
    else:
        if cell_line in ["HELA", "U2OS"]:
            return cell_line
        elif "RPE" in cell_line:
            return 'RPE'
        elif cell_line == "HMEL":
            return 'HMEL'
        else:
            return 'CCLE'


normalized_data['tissue_type'] = normalized_data.index.map(get_tissue_type)

# %%
# PCA analysis
pca = PCA(n_components=2)
pca_result = pca.fit_transform(normalized_data.drop(columns=['tissue_type']))
print(f'Explained variance ratio: {pca.explained_variance_ratio_}')

# %%
pca_df = pd.DataFrame(
    pca_result, columns=['PC1', 'PC2'], index=normalized_data.index)
pca_df['tissue_type'] = normalized_data['tissue_type']
plt.figure(figsize=(10, 8))

sns.scatterplot(x='PC1', y='PC2', hue="tissue_type",
                data=pca_df, s=150, edgecolor='k')
# legend next to plot
# plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
# Adjust plot layout to prevent legend overlap
plt.tight_layout()
plt.xlabel("PC1, explained variance: {:.2f}%".format(
    pca.explained_variance_ratio_[0]*100))
plt.ylabel("PC2, explained variance: {:.2f}%".format(
    pca.explained_variance_ratio_[1]*100))
plt.title("PCA of RNA-seq Data Colored by Source/Cell Line")
plt.tight_layout()
plt.show()
# plt.savefig('./figures/rnaseq_pca_plot.png')
# %%
# list most important genes for each component
for c in pca.components_:
    component_genes = pd.Series(c, index=normalized_data.columns[:-1])
    sorted_genes = component_genes.abs().sort_values(ascending=False)
    print("Top genes for component:")
    print(sorted_genes.head(10))
# pca.components_
# pca.feature_names_in_
# %%
# hierarchical clustering and dendrogram


def plot_dendrogram(model, **kwargs):
    # Create linkage matrix and then plot the dendrogram

    # create the counts of samples under each node
    counts = np.zeros(model.children_.shape[0])
    n_samples = len(model.labels_)
    for i, merge in enumerate(model.children_):
        current_count = 0
        for child_idx in merge:
            if child_idx < n_samples:
                current_count += 1  # leaf node
            else:
                current_count += counts[child_idx - n_samples]
        counts[i] = current_count

    linkage_matrix = np.column_stack(
        [model.children_, model.distances_, counts]).astype(float)

    # Plot the corresponding dendrogram
    R = dendrogram(linkage_matrix, **kwargs)
    return R


# setting distance_threshold=0 ensures we compute the full tree.
# model = AgglomerativeClustering(
#     distance_threshold=0, n_clusters=None, linkage='ward')
model = AgglomerativeClustering(
    n_clusters=4, compute_distances=True, linkage='ward')
model = model.fit(normalized_data.drop(columns=['tissue_type']))


plt.figure(figsize=(10, 5))
plt.title("Hierarchical Clustering Dendrogram of Network RNA-seq Data")
# plot the top three levels of the dendrogram
R = plot_dendrogram(
    model,
    color_threshold=10,
    labels=normalized_data.index.tolist(),
    leaf_rotation=90.,
)
plt.axhline(y=10, color='lightgrey', linestyle='--')
plt.ylabel("Distance")
plt.xlabel("Sample")
plt.tight_layout()
# plt.show()
plt.savefig('./figures/rnaseq_hierarchicalclustering_plot.pdf')


# %%
# colors dictionary for dendrogram
colors_dict = {}
for i, d in enumerate(sorted(list(set(R['leaves_color_list'])))):
    colors_dict[d] = sns.color_palette("tab10")[1:][i]
# add hierarchical clustering results to PCA plot
pca_df['HC_cluster'] = model.labels_

# add dendrogram colors
# sort leaves_colors_list by leaves
leaves_colors = {}
for i, d in zip(R['leaves'], R['leaves_color_list']):
    leaves_colors[i] = d
pca_df['HC_cluster_color'] = [leaves_colors[i] for i in range(len(pca_df))]
plt.figure(figsize=(8, 6))
sns.scatterplot(x='PC1',
                y='PC2',
                hue="HC_cluster_color",
                palette=colors_dict,
                data=pca_df)
plt.tight_layout()
plt.savefig('./figures/rnaseq_pca_plot_HC_clusters.pdf')

# %%
# Prepare data for pca package
color_dict = {}
for i, tissue in enumerate(normalized_data['tissue_type'].unique()):
    color_dict[tissue] = i
color = np.array([np.array(sns.color_palette()[color_dict[i]])
                  for i in normalized_data['tissue_type']])

# cmap = plt.get_cmap('tab10', len(set(normalized_data['tissue_type'])))
# color_dict = {}
# for i, tissue in enumerate(sorted(set(normalized_data['tissue_type']))):
#     color_dict[tissue] = i
# color = cmap.colors[[color_dict[i]
#                      for i in normalized_data['tissue_type']], 0:3]
###########################################################
# COMPUTE AND VISUALIZE PCA
###########################################################
# Initialize the PCA, either reduce the data to the number of
# principal components that explain 95% of the total variance...
pc_model = pc(n_components=0.95)
# ... or explicitly specify the number of PCs

# Fit and transform
results = pc_model.fit_transform(X=normalized_data.drop(
    columns=["tissue_type"]), row_labels=normalized_data.index)

# Plot the explained variance
fig, ax = pc_model.plot()
plt.savefig('./figures/rnaseq_pca_explained_variance.png')
# Create a biplot
# %%
pc_model.biplot(
    n_feat=6,  # labels=normalized_data['tissue_type'],
    c=color,
    s=100,
    figsize=(10, 8))
plt.tight_layout()
plt.savefig('./figures/rnaseq_pca_biplot.png')

# %%
# adding in zhao data
zhao_normalized = pd.read_csv(
    './data/zhao_logTPM_network_genes_zscore.csv', index_col=0)

zhao_normalized['tissue_type'] = ["Zhao_" + i for i in zhao_normalized['race']]
zhao_normalized = zhao_normalized.drop(columns=['race'])
combined_with_zhao = pd.concat(
    [normalized_data, zhao_normalized], axis=0, join='outer')

# %%
# use prior PCA to transform zhao data
pca_zhao = pca.transform(zhao_normalized.drop(
    columns=['tissue_type'])[normalized_data.columns[:-1]])
pca_zhao_df = pd.DataFrame(pca_zhao,
                           columns=['PC1', 'PC2'],
                           index=zhao_normalized.index)
pca_zhao_df['tissue_type'] = zhao_normalized['tissue_type']
combined_pca_df = pd.concat([pca_df, pca_zhao_df], axis=0, join='outer')

# Define partial color overrides
custom_colors = {
    "Zhao_WHITE": "white",  # custom color
    "Zhao_BLACK OR AFRICAN AMERICAN": "black",  # custom color
    # leave others to use the normal palette
}

# Get all hue levels
hue_levels = combined_pca_df["tissue_type"].unique()

# Get the default Seaborn palette for all levels
default_palette = sns.color_palette(n_colors=len(hue_levels))
default_mapping = dict(zip(hue_levels, default_palette))

# Merge custom overrides
palette = {**default_mapping, **custom_colors}


plt.figure(figsize=(15, 8))
sns.scatterplot(x='PC1',
                y='PC2',
                hue="tissue_type",
                data=combined_pca_df,
                palette=palette,
                s=150,
                edgecolor='k')
# legend next to plot
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
# Adjust plot layout to prevent legend overlap
plt.xlabel("PC1, explained variance: {:.2f}%".format(
    pca.explained_variance_ratio_[0] * 100))
plt.ylabel("PC2, explained variance: {:.2f}%".format(
    pca.explained_variance_ratio_[1] * 100))
plt.title("PCA of RNA-seq Data with Zhao Data Colored by Source/Cell Line")
plt.tight_layout()
plt.savefig("./figures/rnaseq_pca_with_zhao_plot.png")
# %%
