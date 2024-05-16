vcell_heatmap <- function(
    SimID, # vector of strings of SimIDs in the form c("SimID_209081149_0__exported","SimID_209081149_0__exported")
    names=SimID,
    species,
    speciesName,
    cutoff_color=NULL,
    tInit=0, # in s
    tSpan, # in s
    tInterval, # in s, what set in VCell
    desiredInterval, # in s, what you want the data to be spaced by
    chromWidth=1.6, #um
    chromHeight=3.5, #um
    dataDim=c(149,68), # rows,columns in concentration matrix; depends on mesh size
    row_1=1,
    row_2=dataDim[1],
    col_1=1,
    col_2=dataDim[2],
    xdiv=3, # number of divisions desired on x axis of output plot
    ydiv=3, # number of divisions desired on y axis of output plot
    importPath="/Users/catalinaalvarez/Google\ Drive/My\ Drive/UVA/Research/JanesLab/CPC_project/Manuscript/Paper_simulations/vcell_data",
    exportPath="/Users/catalinaalvarez/Desktop/"){ 
  
  
  # misc
  folderVar <- 0
  leader <- 10
  offset <- NULL
  
  # pattern<-paste("[A-Za-z0-9_]*","exported",sep="")
  # cond<-grepl(pattern,SimID)
  # print(SimID)
  # SimID<-ifelse(cond,SimID,paste(SimID,"exported",sep="_"))
  # print(SimID)
  
  # initial concentrations (uM) -> Without vol_ratio or fractions multiplications
  # clamped
  # Haspini_ic_uM<- 0.55071118
  # Plk1_init_uM<-0.23394
  # CPCi_init_uM <- 0.07838
  # Bub1a_init_uM<-0.02018
  # Sgo1_init_uM<-0.02583
  # 
  clamped = FALSE
  clampConc<-0
  
  # speciesName <- speciesName
  
  criticalConc=0
  phase=1 # 1 (pre-coac) or 2 (post-coac)
  
  # initialize variables
  n_SimID<-1 #length(SimID)
  n_t<-(tSpan-tInit)/desiredInterval+1
  trange<-seq(from=tInit/tInterval,to=tSpan/tInterval,length.out=n_t)
  
  plist<-list()
  L <- list()
  Clist<-list()
  nlist<-list()
  rlist<-list()
  t_labs<-vector()
  
  count<-1
  
  # constants
  N_A<-6.02e23
  
  # change working directory
  setwd(importPath)
  
  # loop through simulations and time points to make desired plot
  for(s in 1:n_SimID){
    dataFolder<-'data'
    
    
    # dim_data<-dataFolder
    
    # dataDim<-c(row_diff,col_diff)
    # dataDim<-c(149,68)
    row_diff<-row_2
    col_diff<-col_2
    
    # model geometry
    # set X and Y coordinates using system dimensions
    xAxis<-seq(0,chromWidth,length=col_diff)
    yAxis<-seq(0,chromHeight,length=row_diff)
    X<-rep(xAxis,times=row_diff)
    X<-rep(X,times=n_SimID*n_t)
    Y<-rep(yAxis,each=col_diff)
    Y<-rep(Y,times=n_SimID*n_t)
    
    # data processing
    for(z in 1:length(trange)){
      
      t <- trange[z]
      
      # convert timepoint to string
      dataPoint<-as.character(round(x=t,digits=0))
      if(nchar(dataPoint)==1){
        dataPoint<-paste("000",dataPoint,sep="")
      }else if(nchar(dataPoint)==2){
        dataPoint<-paste("00",dataPoint,sep="")
      }else if(nchar(dataPoint)==3){
        dataPoint<-paste("0",dataPoint,sep="")
      }
      
      # match the correct data files in the dataFolder
      if(length(dataFolder)>1){
        return("ERROR: This function does not have the capability to read data in different folders yet.")
      }else{
        if(clamped==FALSE){
          # print(dataPoint)
          for(i in 1:length(species)){
            # print(species[i])
            pattern<-paste("[A-Za-z0-9_]*_Slice_XY_\\d",
                           species[i],
                           dataPoint,
                           sep="_")
            # read the csv file to a matrix, M
            L[[i]]<-data.matrix(read.csv(paste(importPath,dataFolder,grep(pattern, list.files(dataFolder), value = TRUE),sep="/"),header=FALSE,skip=leader))[row_1:row_2,col_1:col_2]
          }
          
          # set any negative concentration values to zero
          L<-matrixZero(matrixList=L)
        }
        
        speciesDesired <- speciesName
        
        # sum matrices
        if(length(species)>1 && speciesDesired=="inactive CPC"){
          M <- reduce(L,`+`)+clampConc
        }else if(length(species)>1 && speciesDesired!="inactive CPC"){
          M <- reduce(L,`+`)
        }else if(clamped==TRUE){
          M<-matrix(0,nrow=dataDim[1],ncol=dataDim[2])+clampConc
        }else if(clamped==FALSE){
          M<-L[[1]]+clampConc
        }
        
        # Mass integration 
        # total CPC
        # View(M)
        Mum<-M*1e-15 # umol/L (uM) --> umol/um^3
        Mum_avg<-mean(Mum)
        # nlist[[count]] <- 1e-6*N_A*massInt(C=Mum, chrWidth=chromWidth, chrHeight=chromHeight, Cc=criticalConc*1e-15) #umol/um --> molecules/um
        nlist[[count]] <- massInt(C=Mum, chrWidth=chromWidth, chrHeight=chromHeight, Cc=criticalConc*1e-15) #umol/um --> molecules/um
        
        # assume C = 10 uM, calculate r (preferred)
        Cexp <- 10 #10 uM
        rlist <- sqrt(nlist[[count]]/(Cexp*1e-15*pi))
        
        # transform M to format it for the heatmap function geomtile()
        M_transform<-as.vector(t(M))
        # print(paste("Max (uM):",max(M_transform)))
        Clist[[count]]<-M_transform
        
        count<-count+1
      }
    }
  }
  
  
  t_short<-seq(from=tInit,to=tSpan,length.out=n_t)
  t_equal_str<-"t (s) ="
  
  t_labs[1] <- paste(t_equal_str,t_short[1])
  t_labs[2:length(t_short)]<-t_short[2:length(t_short)]
  names(t_labs) <- as.character(t_short)
  
  t_long<-as.character(rep(t_short,each=dataDim[1]*dataDim[2],times=n_SimID))
  
  # SimIDs
  ID_short<-seq(from=1,to=n_SimID)
  ID_labs <- names
  names(ID_labs) <- as.character(ID_short)
  ID_long<-as.character(rep(ID_short,each=dataDim[1]*dataDim[2]*n_t))
  
  # concentration
  C<-as.vector(sapply(Clist,as.vector))
  dataMat<-data.frame(cbind(X,Y,C))
  dataMat2<-cbind(ID_long,t_long,dataMat)
  
  ID_lev<-levels(factor(as.numeric(ID_short)))
  t_lev<-levels(factor(as.numeric(t_short)))
  # t_labs<-paste(t_equal_str,t_short,t_unit_str)
  # print(t_labs)
  
  #define our own maxcolor
  maxColor<-cutoff_color
  
  xbreaks<-seq(0, chromWidth, chromWidth/(xdiv-1))
  xlabs<-c(as.character(round(0)),as.character(round(xbreaks[2:length(xbreaks)],digits=1)))
  
  ybreaks<-seq(0,chromHeight, chromHeight/(ydiv-1))
  ylabs<-c(as.character(round(0)),as.character(round(ybreaks[2:length(ybreaks)],digits=2)))
  
  legend_name<-paste("\\[",speciesName,"\\] ($\\mu$M)",sep="")
  legend_name<-TeX(legend_name)
  
  labelString<-c("0",as.character(maxColor/2),as.character(maxColor))
  
  font_size_scaling_factor<-0.5
  
  axis_font_size<-10-0.6*n_SimID
  axis_title_font_size<-14-font_size_scaling_factor*n_SimID
  legend_font_size<-10-font_size_scaling_factor*n_SimID
  legend_title_font_size<-12-font_size_scaling_factor*n_SimID
  stripx_font_size<-7-0.25*n_SimID
  stripy_font_size<-7-0.25*n_SimID
  
  ##heatmap
  
  p<-ggplot(data=dataMat2,aes(x=X, y=Y, fill=C))+geom_tile()+
    facet_grid(factor(ID_long,levels=ID_lev,labels=ID_labs) ~ factor(t_long,levels=t_lev,labels=t_labs), switch="y",labeller = label_wrap_gen(width = 10, multi_line = TRUE))+
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
    theme(legend.text=element_text(size=legend_font_size,angle=45))+
    theme(strip.text.x=element_text(size=stripx_font_size))+
    theme(strip.text.y=element_text(size=stripy_font_size,vjust=0.5))
  
  
  
  
  # create string for export filename
  
  exportFilename<-paste(speciesName, "heatmap", sep="_")
  exportFilename <- paste(exportFilename,"png",sep=".")
  
  # save graph to png file
  ggsave(
    exportFilename,
    plot = p,
    device = "png",
    path = exportPath,
    scale = 1,
    width = 5,
    height = 5,
    units = "in",
    dpi = 300
    # limitsize = TRUE
    )
  
  print(p)
  return(list(nlist,M))
}

