import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import lognorm
from scipy.stats import norm


ic_data = pd.read_csv("/Users/smgroves/Box/CPC_Model_Project/CPC_condensate_images/CPC spots at IC 02_19.csv", header = 0, index_col = 0)
#Name: ID

#get items in excluded ROIs - for 12-18
# exclude_dict = {"T2_image4":[71,72],
#                 "T2_image3":[10033,10034,10035,10036], #28,29,30,31
#                 'T2_image6': [21947.0, 21948.0, 21949.0, 21950.0], #33,34,35,36
#                 'T2_image7':[17082.0, 17084.0, 17085.0], #'82','83','84'
#                 'T2_image5':[25415.0, 25416.0, 25417.0, 25418.0]#65','66','67','68'
#                 }

#for 2-19
exclude_dict = {"T2I4":[71,72],
                "T2I3":[10033,10034,10035,10036], #28,29,30,31
                'T2I6': [21947.0, 21948.0, 21949.0, 21950.0], #33,34,35,36
                'T2I7':[17082.0, 17084.0, 17085.0], #'82','83','84'
                'T2I5':[25415.0, 25416.0, 25417.0, 25418.0]#65','66','67','68'
                }

excluded = []
for key in exclude_dict.keys():
    # print(key)
    tmp = ic_data.loc[ic_data['Item Name']==key]
    # print(set(tmp['Compartment ROIs ID'].dropna().values))
    for roi in exclude_dict[key]:
        # print(len(tmp.loc[tmp['Compartment ROIs ID']==int(roi)]['Name'].values))
        for i in tmp.loc[tmp['Compartment ROIs ID']==int(roi)]['Name'].values:
            excluded.append(i)


# get CPC at IC by removing excluded and ROIs
ic_data = ic_data.loc[~ic_data['Name'].isin(excluded)]
ic_data = ic_data.loc[~ic_data['Compartment ROIs ID'].isna()]
col_1218 =['Item Name', 'Name', 'Population','Surface Area (um2)', 'Volume (um3)','Longest Axis (um)']
col_219 =['Item Name', 'Name', 'Population','Surface Area', 'Voxel Count','Longest Axis']
col_219.append('Compartment ROIs ID')
ic_data = ic_data[col_219]
# ic_data = ic_data[col_1218.append('Compartment ROIs ID')]
ic_data['location'] = 'IC'

#get CPC not at IC by excluding ROIs and removing names in ic_data
all_data = pd.read_csv("/Users/smgroves/Box/CPC_Model_Project/CPC_condensate_images/All CPC spots 02_19.csv", header = 0, index_col = 0)
all_data = all_data.loc[~all_data['Name'].isin(excluded)]
nonIC_data = all_data.loc[~all_data['Name'].isin(ic_data['Name'].values)]
# nonIC_data = nonIC_data[col_1218]
nonIC_data = nonIC_data[col_219]
nonIC_data['location'] = 'nonIC'

combined =(pd.concat([ic_data, nonIC_data]))

# combined = combined.loc[combined['Volume (um3)']>0.01]

print(combined.head())
print(combined.describe())

def plot(type = 'Volume (um3)', plot =True, top = 40):
    g = sns.histplot(data = combined, x = type,hue = 'location', bins = 30)
    plt.axvline(x=combined.loc[combined['location'] == 'nonIC'][type].quantile(0.95), color='C1', linestyle='--')

    plt.title('IC mean: ' + str(round(combined.loc[combined['location'] == 'IC'][type].mean(), 3)) +
              '; nonIC mean: ' + str(round(combined.loc[combined['location'] == 'nonIC'][type].mean(), 3))
              + '\n IC std: ' + str(round(combined.loc[combined['location'] == 'IC'][type].std(), 3)) +
              '; nonIC std: ' + str(round(combined.loc[combined['location'] == 'nonIC'][type].std(), 3))
              + '\n nonIC 95%: ' + str(round(combined.loc[combined['location'] == 'nonIC'][type].quantile(0.95), 3)) )
    # g.set_yscale("log")
    # plt.show()
    plt.tight_layout()
    plt.savefig('all_'+type+'.png', dpi = 300)
    plt.close()
    stats = pd.DataFrame(columns = ['Item Name', 'IC mean', 'IC std', 'nonIC mean', 'nonIC std',
                                    'IC lognorm shape', 'IC lognorm location', 'IC lognorm scale',
                                    'nonIC lognorm shape', 'nonIC lognorm location', 'nonIC lognorm scale',
                                    'IC lognorm 95% CI', 'nonIC lognorm 95% CI',
                                    "IC 95%", "nonIC 95%"])

    for image in sorted(list(set(combined['Item Name'].values))):
        tmp = combined.loc[combined['Item Name']==image]

        print(image)
        shape_IC, loc_IC, scale_IC = lognorm.fit(tmp.loc[tmp['location'] == 'IC'][type].values)
        #if log x is normal with mean mu and variance sigma^2:
        #x is log-normally distributed with shape = sigma and scale = exp(mu)
        print("Lognorm fit of IC condensates: shape (sigma): ", shape_IC, "; location (shift): ", loc_IC, "; scale (e^mu)", scale_IC )

        shape_nonIC, loc_nonIC, scale_nonIC  = lognorm.fit(tmp.loc[tmp['location'] == 'nonIC'][type].values)
        print("Lognorm fit of nonIC condensates: shape (sigma): ", shape_nonIC, "; location (shift): ",
              loc_nonIC, "; scale (e^mu)", scale_nonIC )

        CI_95_IC = lognorm.interval(0.95, shape_IC, loc=loc_IC, scale=scale_IC)[1]
        CI_95_nonIC = lognorm.interval(0.95, shape_nonIC, loc=loc_nonIC, scale=scale_nonIC)[1]

        new_row =pd.Series({"Item Name":image, "IC mean":tmp.loc[tmp['location'] == 'IC'][type].mean(),
                                "IC std":tmp.loc[tmp['location'] == 'IC'][type].std(),
                                "nonIC mean":tmp.loc[tmp['location'] == 'nonIC'][type].mean(),
                                "nonIC std":tmp.loc[tmp['location'] == 'nonIC'][type].std(),
                                "IC lognorm shape":shape_IC,
                                "IC lognorm location":loc_IC,
                                "IC lognorm scale":scale_IC,
                                "nonIC lognorm shape":shape_nonIC,
                                "nonIC lognorm location":loc_nonIC,
                                "nonIC lognorm scale":scale_nonIC,
                                "IC lognorm 95% CI":CI_95_IC,
                                "nonIC lognorm 95% CI":CI_95_nonIC,
                                "IC 95%":tmp.loc[tmp['location'] == 'IC'][type].quantile(0.95),
                                "nonIC 95%":tmp.loc[tmp['location'] == 'nonIC'][type].quantile(0.95)})
        stats =pd.concat([stats,new_row.to_frame().T], ignore_index=True)
        if plot:
            # g = sns.histplot(data = tmp, x = type,hue = 'location', bins = 30)
            # # plt.axvline(x=tmp.loc[tmp['location'] == 'IC'][type].quantile(0.95), color='C0', linestyle='--')
            # plt.axvline(x=tmp.loc[tmp['location'] == 'nonIC'][type].quantile(0.95), color='C1', linestyle='--')
            #
            # plt.title(str(image)+ '\n IC mean: '+ str(round(tmp.loc[tmp['location'] == 'IC'][type].mean(), 3))+
            #           '; nonIC mean: '+ str(round(tmp.loc[tmp['location'] == 'nonIC'][type].mean(), 3))
            #           + '\n IC std: '+ str(round(tmp.loc[tmp['location'] == 'IC'][type].std(), 3))+
            #           '; nonIC std: '+ str(round(tmp.loc[tmp['location'] == 'nonIC'][type].std(), 3))
            #           + "\n nonIC 95%: " + str(round(tmp.loc[tmp['location'] == 'nonIC'][type].quantile(0.95), 3)) )
            # plt.tight_layout()
            # plt.savefig("./plots/"+str(image)+f"_{type}_hist_with_95%.png")
            # plt.close()

            g = sns.histplot(data=tmp, x=type, hue='location', bins=30, log_scale=True)
            plt.title(image)
            plt.savefig(f"./plots/{type}_{image}.png")
            plt.close()
            #
            # x_axis = np.arange(np.min(tmp[type])-0.01, np.max(tmp[type]), 0.01)
            # y_axis0 = lognorm.pdf(x_axis, shape_IC, loc_IC, scale_IC)   # 1st gaussian
            #
            # y_axis1 = lognorm.pdf(x_axis, shape_nonIC, loc_nonIC, scale_nonIC)   # 1st gaussian
            #
            # plt.plot(x_axis, y_axis0, lw=3, c='C0')
            # plt.plot(x_axis, y_axis1, lw=3, c='C1')
            # g = plt.hist(tmp[type], density=True, color='black', bins=30)
            # plt.title(str(image)+ "\n IC scale: " +str(round(scale_IC, 3))+ "; nonIC scale: "+ str(round(scale_nonIC, 3))
            #           + "\n IC shape: " +str(round(shape_IC, 3))+ "; nonIC shape: "+ str(round(shape_nonIC, 3)))
            # plt.xlabel(type)
            # plt.ylabel('Density')
            # plt.ylim(top = top)
            # plt.savefig("./plots/"+str(image)+f"_{type}_lognormfit.png")
            # plt.close()
            # plt.show()
            # x_axis = np.log(np.arange(0, .5, 0.01))
            # y_axis0 = norm.pdf(x_axis,np.log(scale_IC), shape_IC)   # 1st gaussian
            # y_axis1 = norm.pdf(x_axis, np.log(scale_nonIC), shape_nonIC)   # 1st gaussian
            # plt.plot(x_axis, y_axis0, lw=3, c='C0')
            # plt.plot(x_axis, y_axis1, lw=3, c='C1')
            # plt.hist(np.log(tmp[type]), density=True, color='black', bins=30)
            # plt.title(image)
            # plt.xlabel(type)
            # plt.ylabel('Density')
            # plt.show()

    return stats

vox = plot('Voxel Count',plot=True)
sa = plot('Surface Area', top = 4, plot= True)
# plot('Longest Axis')

stats=pd.merge(left = vox, right = sa, on = 'Item Name', suffixes=('_vox', '_sa'))
print(stats)
stats.to_csv('stats.csv', index=False)

long_stats = pd.melt(stats, id_vars=['Item Name'], value_vars = ['IC mean_vox', 'nonIC mean_vox'])
long_std = pd.melt(stats, id_vars=['Item Name'], value_vars = ['IC std_vox', 'nonIC std_vox'])
long_stats = pd.merge(left = long_stats, right = long_std, left_index=True,right_index=True, suffixes=('_mean', '_std'))
print(long_stats)
# sns.pointplot(data = long_stats, x = 'Item Name_mean',errorbar = 'value_std', y = 'value_mean',hue = 'variable_mean')
# plt.show()
sns.pointplot(combined.sort_values("Item Name"), x = 'Item Name', y = 'Voxel Count', errorbar='se',hue = 'location',
              join=False, dodge=.4)
plt.title("Mean +/- SE by Image and Condensate Location")
plt.savefig("./plots/vox_mean_SE.png")
plt.close()

sns.boxplot(combined.sort_values("Item Name"), x = 'Item Name', y = 'Voxel Count',hue = 'location')
plt.title("Distribution of Voxel Count by Image and Condensate Location")
plt.savefig("./plots/vox_boxplot.png")
plt.close()

sns.pointplot(combined.sort_values("Item Name"), x = 'Item Name', y = 'Surface Area', errorbar='se',hue = 'location',
              join=False, dodge=.4)
plt.title("Mean +/- SE by Image and Condensate Location")
plt.savefig("./plots/sa_mean_SE.png")
plt.close()

sns.boxplot(combined.sort_values("Item Name"), x = 'Item Name', y = "Surface Area",hue = 'location')
plt.title("Distribution of Surface Area by Image and Condensate Location")
plt.savefig("./plots/sa_boxplot.png")
plt.close()