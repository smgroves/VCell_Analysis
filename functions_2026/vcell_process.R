# # install.packages("BiocManager")
# # BiocManager::install("rhdf5")
# packages <- c("rhdf5","ggplot2","gridExtra","purrr","latex2exp","stringr","lemon","utils","tictoc","xlsx","tidyverse","tibble","scales")
# install.packages(setdiff(packages, rownames(installed.packages())))
# lapply(packages, require, character.only = TRUE)
# 
# h5_path<-"C:/Users/sam/Research/JanesLab/vcell_data/SimID_256738913_0__exported"
# # h5_path<-"C:/Users/jasra/Desktop/SimID_212441030_0__exported.hdf5"
# sim_len<-1
# # sim_paths<-c("")
# # sim_len<-length(sim_paths)
# # sim_names<-c("")
# # sweep_name<-c("")
# 
# # geometry (um)
# width<-1.6
# height<-3.5
# 
# # input time values (s)
# t_0<-0
# t_end<-500
# t_div<-10
# t_desired<-100
# 
# other_spec<-c("Plk1",
#                  "pPlk1",
#                  "Haspin",
#                  "pHaspin",
#                  "H3",
#                  "pH3",
#                  "Mps1",
#                  "pMps1",
#                  "ppMps1",
#                  "Ndc80",
#                  "pNdc80",
#                  "Knl1",
#                  "pKnl1",
#                  "Bub1",
#                  "pBub1",
#                  "Sgo1",
#                  "H2A",
#                  "pH2A",
#                  "pH2A_Sgo1")
# 
# CPC_spec<-c("CPC",
#                "pH2A_CPC",
#                "CPC_pH3",
#                "pH2A_CPC_pH3",
#                "CPCa",
#                "pH2A_CPCa",
#                "CPCa_pH3",
#                "pH2A_CPCa_pH3")
# 
# all_spec<-c(other_spec,CPC_spec)
# 
# # define group names from HDF5 file
# # group_names<-paste("VCSimulationIdentifier[212440868,0,mgrahn(208009576)]",CPC_spec,"DataValues (XYT)",sep="/")
# group_names<-paste("VCSimulationIdentifier[212441030,0,mgrahn(208009576)]",CPC_spec,"DataValues (XYT)",sep="/")
# 
# # get list of 3D matrices for CPC species; each 3D matrix is in format (t,x,y) 
# all_data<-lapply(group_names,FUN=h5read,file=h5_path)
# 
# # sum up all the CPC species
# sum_list<-reduce(all_data,`+`)
# 
# ## dimensional setup
# 
# # get dimensions of summed array
# t<-dim(sum_list)[1]
# x<-dim(sum_list)[2]
# y<-dim(sum_list)[3]
# 
# # t
# all_t_points<-seq(from=t_0,to=t_end,by=t_div)
# desired_t_points<-seq(from=t_0,to=t_end,by=t_desired)
# t_index<-match(desired_t_points,all_t_points)
# t_len<-length(t_index)
# 
# # x
# x_val<-seq(0,width,length=x)
# x_axis<-rep(x_val,each=t_len)
# x_axis<-rep(x_axis,times=y)
# 
# # y
# y_val<-seq(0,height,length=y)
# y_axis<-rep(y_val,each=x*t_len)
# # y_axis<-rep(y_axis,times=sim_len*t_len)
# 
# 
# # select only time points you want
# sum_list_desired<-sum_list[t_index,,]
# 
# # transpose & stack matrices
# conc_df<-as.vector(sum_list_desired)
# 
# # extend time points
# t_df<-rep(desired_t_points,times=x*y)
# 
# # concatenate data from different sim identifiers into one data frame
# master_data<-data.frame(t_df,x_axis,y_axis,conc_df)
# 
# # heatmap
# p<-ggplot(data=master_data,aes(x=x_axis, y=y_axis, fill=conc_df))+
#   geom_tile()+
#   facet_wrap(t_df,scales="free")
# 
# print(p)
# 
# 
# # extend simulation identifiers (note: done by index to preserve order)
# # sim_index<-seq(from=1,to=sim_len,length.out=sim_len)
# # sim_df<-rep(sim_index,each=t*x*y)
# 
# # turn array into list of length, t
# 
# 
# # turn list of x*y matrices into list of data frames