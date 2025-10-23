# %%
from sklearn.cluster import AgglomerativeClustering
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import sklearn

# %% Load RNA-seq data
TCGA_data = pd.read_csv(
    './data/breast_TCGA_network_proteins_longdata.csv', index_col=0)
print(TCGA_data.head())

CCLE_data = pd.read_csv(
    './data/CCLE_Log_transformed_TPM_MCF10A_longdata.csv', index_col=0)
print(CCLE_data.head())

# %%
# reshape from long to wide
TCGA_wide = TCGA_data.pivot_table(
    index='cell_line', columns='gene', values='rna_counts', aggfunc='first')

TCGA_wide.rename(
    columns={'SGOL1': 'SGO1', "CASC5": "KNL1", "GSG2": "HASPIN"}, inplace=True)
CCLE_wide = CCLE_data.pivot_table(
    index='cell_line_display_name', columns='Protein', values='rna_counts', aggfunc='first')
# %%
# merge dataframes by rows
combined_data = pd.concat([TCGA_wide, CCLE_wide], axis=0, join='outer')

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
pca = sklearn.decomposition.PCA(n_components=2)
pca_result = pca.fit_transform(normalized_data.drop(columns=['tissue_type']))
pca_df = pd.DataFrame(
    pca_result, columns=['PC1', 'PC2'], index=normalized_data.index)
pca_df['tissue_type'] = normalized_data['tissue_type']
sns.scatterplot(x='PC1', y='PC2', hue="tissue_type", data=pca_df)
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0)

# Adjust plot layout to prevent legend overlap
plt.tight_layout()
plt.show()
# %%
# hierarchical clustering and scatterplot with colors by clusters
