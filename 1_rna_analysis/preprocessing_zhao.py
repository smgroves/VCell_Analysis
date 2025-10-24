# %%
from sklearn.decomposition import PCA
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import seaborn as sns

# %%
# Load RNA-seq data
repo = "/Users/smgroves/Documents/GitHub/VCell_Analysis"
indir = "/Users/smgroves/Library/CloudStorage/Box-Box/CPC_Model_Project/VCell_RNAseq/Zhao_dataset/"
zhao_data = pd.read_csv(
    f"{indir}RQ021672-Zhao_counts.csv", index_col=0, header=0)

zhao_metadata = pd.read_excel(
    f"{indir}/Copy of DEID_TNBC Shavings Annotation.xlsx", sheet_name='Sheet1', index_col=0)

# %%
# TPM normalization from read counts


def tpm_normalization(df, genelengths):
    """
    df: genes x samples (index genes, columns samples)
    genelengths: Series OR DataFrame (index gene IDs) containing gene lengths
    """
    df = df.copy()
    # canonical gene id (remove version)
    df['gene_id'] = df.index.str.split('.').str[0]

    # obtain a Series of lengths
    if isinstance(genelengths, pd.DataFrame):
        # try 'length' column first, else first column
        if 'length' in genelengths.columns:
            length_series = genelengths['length']
        else:
            length_series = genelengths.iloc[:, 0]
    else:
        length_series = genelengths

    # Resolve duplicate index labels by aggregation (mean); you can change to keep='first' if desired
    if length_series.index.duplicated().any():
        # helpful debug message
        dup_count = length_series.index.duplicated().sum()
        print(
            f"Warning: {dup_count} duplicate gene IDs in genelengths; aggregating with mean.")
        length_series = length_series.groupby(level=0).mean()

    # map lengths to df
    df['length_kb'] = df['gene_id'].map(length_series) / 1000.0

    # drop genes with missing lengths
    df = df.dropna(subset=['length_kb'])

    # separate counts and metadata columns
    counts = df.drop(columns=['gene_id', 'length_kb'])

    # reads per kilobase (RPK)
    rpk = counts.div(df['length_kb'], axis=0)

    # per-sample scaling factor and TPM
    per_sample_sum = rpk.sum(axis=0)
    # avoid division by zero
    per_sample_sum[per_sample_sum == 0] = np.nan
    tpm = rpk.div(per_sample_sum, axis=1) * 1e6

    return tpm


genelengths = pd.read_csv(
    f"{repo}/1_rna_analysis/data/ncbi_ensembl_coding_mergedgenelength.csv", index_col=0, header=0, sep='\t')
# Exclude 'genename' column
zhao_tpm = tpm_normalization(zhao_data.iloc[:, 1:], genelengths=genelengths)

zhao_logtpm = np.log2(zhao_tpm + 1)

zhao_logtpm['genename'] = zhao_data['genename']
zhao_logtpm = zhao_logtpm.set_index('genename')
# %%
# get races
races = []
for col in zhao_logtpm.columns:
    match = False
    for casenum in zhao_metadata.index:
        if casenum in col:
            print(zhao_metadata.loc[casenum]['race'])
            match = True
            races.append(zhao_metadata.loc[casenum]['race'])
    if not match:
        print("No match for column:", col)


# %%
# get rows if genename in list
genes_of_interest = [
    'AURKB', 'BIRC5', 'BUB1', 'CASC5', 'CDCA8', 'GSG2', 'INCENP', 'KAT5', 'NDC80', 'PLK1', 'HASPIN', 'KNL1', 'SGO1', 'SGOL1', 'TTK'
]
zhao_subset = zhao_logtpm[zhao_logtpm.index.isin(genes_of_interest)]
zhao_subset = zhao_subset.transpose()
zhao_subset['race'] = races
zhao_logtpm.to_csv(f"{repo}/1_rna_analysis/data/zhao_logTPM_allgenes.csv")
zhao_subset.to_csv(f"{repo}/1_rna_analysis/data/zhao_logTPM_network_genes.csv")
# %%
# z score normalization
data = zhao_subset.drop(columns=['race'])
scaler = StandardScaler()
normalized_data = pd.DataFrame(
    scaler.fit_transform(data.fillna(0)),
    index=data.index,
    columns=data.columns
)
print(normalized_data.head())
normalized_data['race'] = races

normalized_data.to_csv(
    f"{repo}/1_rna_analysis/data/zhao_logTPM_network_genes_zscore.csv")
# %%
pca = PCA(n_components=2)
pca_result = pca.fit_transform(normalized_data.drop(columns=['race']))
print(f'Explained variance ratio: {pca.explained_variance_ratio_}')

# %%
pca_df = pd.DataFrame(
    pca_result, columns=['PC1', 'PC2'], index=normalized_data.index)
pca_df['race'] = zhao_subset['race']
plt.figure(figsize=(10, 8))

sns.scatterplot(x='PC1', y='PC2', hue="race",
                data=pca_df, s=150, edgecolor='k')
# legend next to plot
# plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
# Adjust plot layout to prevent legend overlap
plt.tight_layout()
plt.xlabel("PC1, explained variance: {:.2f}%".format(
    pca.explained_variance_ratio_[0]*100))
plt.ylabel("PC2, explained variance: {:.2f}%".format(
    pca.explained_variance_ratio_[1]*100))
plt.title("PCA of Zhao Data Colored by Race")
plt.tight_layout()
plt.show()

# %%
