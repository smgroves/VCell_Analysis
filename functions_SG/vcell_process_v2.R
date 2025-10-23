# # Install all needed packages
# # install.packages("BiocManager")
# 
# packages <- c("ggplot2","gridExtra","purrr","latex2exp","stringr","lemon","utils","tictoc","tidyverse","tibble","scales")
# install.packages(setdiff(packages, rownames(installed.packages())))
# lapply(packages, require, character.only = TRUE)
# install.packages(pkgs = "xlsx")
# BiocManager::install("rhdf5")
# 
# # h5_path<-"C:/Users/jasra/Desktop/SimID_212440868_0__exported.hdf5"
# # t_des<-seq(0,500,100)
# t_des<-500
# h5_path<-"C:/Users/jasra/Desktop/SimID_212441030_0__exported.hdf5"
# h5_path_vec<-c("C:/Users/jasra/Desktop/SimID_212440934_0__exported.hdf5",
#                "C:/Users/jasra/Desktop/SimID_212441030_0__exported.hdf5")
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
# 
# other_spec<-c("Plk1",
#               "pPlk1",
#               "Haspin",
#               "pHaspin",
#               "H3",
#               "pH3",
#               "Mps1",
#               "pMps1",
#               "ppMps1",
#               "Ndc80",
#               "pNdc80",
#               "Knl1",
#               "pKnl1",
#               "Bub1",
#               "pBub1",
#               "Sgo1",
#               "H2A",
#               "pH2A",
#               "pH2A_Sgo1")
# 
# CPC_spec<-c("CPC",
#             "pH2A_CPC",
#             "CPC_pH3",
#             "pH2A_CPC_pH3",
#             "CPCa",
#             "pH2A_CPCa",
#             "CPCa_pH3",
#             "pH2A_CPCa_pH3")
# 
# all_spec<-c(other_spec,CPC_spec)
# 
# # define group names from HDF5 file
# # group_names<-paste("VCSimulationIdentifier[212440868,0,mgrahn(208009576)]",CPC_spec,"DataValues (XYT)",sep="/")
# group_names<-paste("VCSimulationIdentifier[212441030,0,mgrahn(208009576)]",CPC_spec,"DataValues (XYT)",sep="/")
# 
# # get list of 3D matrices for CPC species; each 3D matrix is in format (t,x,y) 
# #all_data<-lapply(group_names,FUN=h5read,file=h5_path)
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
# # all_t_points<-seq(from=t_0,to=t_end,by=t_div)
# # desired_t_points<-seq(from=t_0,to=t_end,by=t_desired)
# t_index<-match(t_des,seq(t_0,t_end,t_div))
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
# t_df<-rep(t_des,times=x*y)
# 
# # concatenate data from different sim identifiers into one data frame
# master_data<-data.frame(t_df,x_axis,y_axis,conc_df)
# 
# # font sizes
# axis_font_size<-10
# axis_title_font_size<-14
# legend_font_size<-10
# legend_title_font_size<-12
# stripx_font_size<-7
# stripy_font_size<-7
# 
# # axes
# xdiv<-3 # number of divisions desired on x axis of output plot
# xbreaks<-seq(0, width, width/(xdiv-1))
# xlabs<-c(as.character(round(0)),as.character(round(xbreaks[2:length(xbreaks)],digits=1)))
# ydiv<-3 # number of divisions desired on y axis of output plot
# ybreaks<-seq(0,height, height/(ydiv-1))
# ylabs<-c(as.character(round(0)),as.character(round(ybreaks[2:length(ybreaks)],digits=2)))
# 
# # legend
# maxColor<-7
# labelString<-c("0",as.character(maxColor/2),as.character(maxColor))
# legend_name<-paste("\\[","total CPC","\\] ($\\mu$M)",sep="")
# legend_name<-TeX(legend_name)
# 
# # heatmap
# p<-ggplot(data=master_data,aes(x=x_axis, y=y_axis, fill=conc_df))+
#   geom_tile()+
#   facet_wrap(t_df,scales="fixed")+
#   coord_fixed(ratio = 1, xlim = NULL, ylim = NULL, expand = TRUE, clip = "on")+
#   scale_fill_gradientn(name=legend_name,limits=c(0,maxColor),breaks=c(0,round(maxColor/2,digits=0),maxColor),labels=labelString,colors=c("black","blueviolet","blue","cyan","green","yellow","orange","red"),na.value="grey100")+
#   scale_x_continuous(breaks=xbreaks,labels=xlabs)+
#   scale_y_continuous(breaks=ybreaks,labels=ylabs,position="right")+
#   theme_void()+
#   # xlab(TeX("$\\geq$10"))+
#   xlab(TeX("X ($\\mu$m)"))+
#   ylab(TeX("Y ($\\mu$m)"))+
#   theme(axis.ticks = element_line(size = 0.025))+
#   theme(axis.ticks.length=unit(.1, "cm"))+
#   # theme(panel.spacing=unit(0.5,"cm"))+
#   theme(axis.text=element_text(size=axis_font_size),
#         axis.title=element_text(size=axis_title_font_size))+
#   theme(axis.text.x=element_text(angle=45))+
#   theme(axis.title.x=element_text(vjust=-0.1,face="bold"))+
#   theme(axis.title.y=element_text(vjust=0.5,hjust=0.4,angle=90,face="bold"))+
#   theme(legend.key.size = unit(0.4, 'cm'))+
#   theme(legend.title=element_text(size=legend_title_font_size,vjust=1,hjust=1))+
#   theme(legend.position="bottom")+
#   theme(legend.direction="horizontal")+
#   theme(legend.text=element_text(size=legend_font_size,angle=45))
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