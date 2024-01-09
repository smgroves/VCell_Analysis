vcell_analyze <- function(
  data, # vector of strings of SimIDs in the form c("SimID_209081149_0__exported","SimID_209081149_0__exported","SimID_209081149_0__exported")
  geometry=c(1.6,3.5),
  model_time=seq(0,500,10),
  desired_time=seq(model_time[1],model_time[2],100),
  species){ 

  # import packages, install if not already
  packages <- c("rhdf5","ggplot2","gridExtra","purrr","latex2exp","stringr","lemon","utils","tictoc","xlsx","tidyverse","tibble","scales")
  install.packages(setdiff(packages, rownames(installed.packages())))
  lapply(packages, require, character.only = TRUE)

  # read raw data from h5 file
  h5_list<-H5Fopen(data)
  raw_data<-sapply(h5_list,FUN=h5read,name="/") # a single species is four levels down from list e.g. raw_data[[1]][[1]][[1]][[1]]

  # geometry (um)
  width<-system_geom[1]
  height<-system_geom[2]

  # input time values (s)
  t_0<-0
  t_end<-500
  t_div<-10
  t_desired<-100

  # recursively parse raw data into dataframe for all simulations
  lapply(raw_data,FUN=analysis_function)

  # concatenate dataframes together
  list.rbind(x)

  # assemble data frame
  # x
  x_val<-seq(0,width,length=x)
  x_axis<-rep(x_val,each=t_len)
  x_axis<-rep(x_axis,times=y)
  # y
  y_val<-seq(0,height,length=y)
  y_axis<-rep(y_val,each=x*t_len)
  # y_axis<-rep(y_axis,times=sim_len*t_len)
  # select only time points you want
  sum_list_desired<-sum_list[t_index,,]
  # transpose & stack matrices
  conc_df<-as.vector(sum_list_desired)
  # extend time points
  t_df<-rep(desired_time,times=x*y)
  # concatenate data from different sim identifiers into one data frame
  master_data<-data.frame(t_df,x_axis,y_axis,conc_df)

  # font sizes
  axis_font_size<-10
  axis_title_font_size<-14
  legend_font_size<-10
  legend_title_font_size<-12
  stripx_font_size<-7
  stripy_font_size<-7

  # axes
  xdiv<-3 # number of divisions desired on x axis of output plot
  xbreaks<-seq(0, width, width/(xdiv-1))
  xlabs<-c(as.character(round(0)),as.character(round(xbreaks[2:length(xbreaks)],digits=1)))
  ydiv<-3 # number of divisions desired on y axis of output plot
  ybreaks<-seq(0,height, height/(ydiv-1))
  ylabs<-c(as.character(round(0)),as.character(round(ybreaks[2:length(ybreaks)],digits=2)))

  # legend
  maxColor<-7
  labelString<-c("0",as.character(maxColor/2),as.character(maxColor))
  legend_name<-paste("\\[","total CPC","\\] ($\\mu$M)",sep="")
  legend_name<-TeX(legend_name)

  # pseudocolor recruitment map
  p<-ggplot(data=master_data,aes(x=x_axis, y=y_axis, fill=conc_df))+
    geom_tile()+
    facet_wrap(t_df,scales="fixed")+
    coord_fixed(ratio = 1, xlim = NULL, ylim = NULL, expand = TRUE, clip = "on")+
    scale_fill_gradientn(name=legend_name,limits=c(0,maxColor),breaks=c(0,round(maxColor/2,digits=0),maxColor),labels=labelString,colors=c("black","blueviolet","blue","cyan","green","yellow","orange","red"),na.value="grey100")+
    scale_x_continuous(breaks=xbreaks,labels=xlabs)+
    scale_y_continuous(breaks=ybreaks,labels=ylabs,position="right")+
    theme_void()+
    # xlab(TeX("$\\geq$10"))+
    xlab(TeX("X ($\\mu$m)"))+
    ylab(TeX("Y ($\\mu$m)"))+
    theme(axis.ticks = element_line(size = 0.025))+
    theme(axis.ticks.length=unit(.1, "cm"))+
    # theme(panel.spacing=unit(0.5,"cm"))+
    theme(axis.text=element_text(size=axis_font_size),
          axis.title=element_text(size=axis_title_font_size))+
    theme(axis.text.x=element_text(angle=45))+
    theme(axis.title.x=element_text(vjust=-0.1,face="bold"))+
    theme(axis.title.y=element_text(vjust=0.5,hjust=0.4,angle=90,face="bold"))+
    theme(legend.key.size = unit(0.4, 'cm'))+
    theme(legend.title=element_text(size=legend_title_font_size,vjust=1,hjust=1))+
    theme(legend.position="bottom")+
    theme(legend.direction="horizontal")+
    theme(legend.text=element_text(size=legend_font_size,angle=45))

  print(p)

}