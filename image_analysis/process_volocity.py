import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import norm
import statistics
from sklearn.mixture import GaussianMixture as GMM

data = pd.read_csv("./CPC prophase cells sep cells.csv", header = 0, index_col = 0)

data = data.loc[["Population" in x for x in data['Population']]]
data_i4 = data.loc[data["Item Name"] =='T2_image4']

data_i4['Cell Stage'] = [{1165.0:"Early Prophase", 1166.0:"Prometaphase"}[x] for x in data_i4['Compartment ROIs ID']]
#
# sns.violinplot(data = data_i4, x ="Cell Stage", y = "Volume (�m3)")
# plt.ylabel("Volume (um^3)")
# plt.title("Volume of CPC Condensates in Early Prophase and Prometaphase \n"
#           f"Min: {np.min(data_i4['Volume (�m3)'])}, Max: {np.max(data_i4['Volume (�m3)'])}, Mean: {np.mean(data_i4['Volume (�m3)'])}")
# plt.ylim(0, None)
#
# plt.show()
#
# sns.violinplot(data = data_i4, x ="Cell Stage", y = "Longest Axis (�m)")
# plt.ylabel("Longest Axis (um)")
# plt.title("Longest Axis of CPC Condensates in Early Prophase and Prometaphase \n"
#           f"Min: {np.min(data_i4['Longest Axis (�m)'])}, Max: {np.max(data_i4['Longest Axis (�m)'])}, Mean: {np.mean(data_i4['Longest Axis (�m)'])}")
# #set yaxis min to 0
# plt.ylim(0, None)
# plt.show()
#
# sns.violinplot(data = data_i4, x ="Cell Stage", y = "Surface Area (�m2)")
# plt.ylabel("Surface Area (um2)")
# plt.title(f"Surface Area of CPC Condensates in Early Prophase and Prometaphase \n"
#           f"Min: {np.min(data_i4['Surface Area (�m2)'])}, Max: {np.max(data_i4['Surface Area (�m2)'])}, Mean: {np.mean(data_i4['Surface Area (�m2)'])}")
# plt.ylim(0, None)
#
# plt.show()

sns.histplot(data = data_i4.loc[data_i4['Cell Stage']=='Prometaphase'], x ="Volume (�m3)", hue = "Cell Stage", bins = 50)
plt.show()

X = data_i4.loc[data_i4['Cell Stage']=='Prometaphase']["Volume (�m3)"].to_numpy().reshape(-1, 1)
gmm = GMM(n_components=2)
labels = gmm.fit_predict(X)
print(labels)

new_data = data_i4.loc[data_i4['Cell Stage']=='Prometaphase']
new_data['labels'] = labels

# Plot between -10 and 10 with .001 steps.
x_axis = np.arange(0, .5, 0.01)
mean = gmm.fit(X).means_
covs  = gmm.fit(X).covariances_
weights = gmm.fit(X).weights_
y_axis0 = norm.pdf(x_axis, float(mean[0][0]), np.sqrt(float(covs[0][0][0])))*weights[0] # 1st gaussian
y_axis1 = norm.pdf(x_axis, float(mean[1][0]), np.sqrt(float(covs[1][0][0])))*weights[1] # 2nd gaussian

plt.plot(x_axis, y_axis0, lw=3, c='C0')
plt.plot(x_axis, y_axis1, lw=3, c='C1')
plt.plot(x_axis, y_axis0+y_axis1, lw=3, c='C2', ls='dashed')
plt.hist(new_data["Volume (�m3)"], density=True, color='black', bins = 30)

# sns.histplot(data = new_data, x ="Surface Area (�m2)", hue = "labels", bins = 50)
plt.show()