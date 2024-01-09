 new_vcell_timecourse <- function(
  SimID, # vector of strings of SimIDs in the form c("SimID_209081149_0__exported","SimID_209081149_0__exported","SimID_209081149_0__exported")
  sweepName=NULL,
  names=SimID,
  criticalConc=3,
  op="fold_enrich",
  # clamped=NULL,
  phase=1, # 1 (pre-coac) or 2 (post-coac)
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
  importPath="C:/Users/jasra/Desktop/vcell_data",
  exportPath="C:/Users/jasra/Desktop/vcell_plots"){ 

  # add "exported" onto filename if not already present
  SimID<-as.character(SimID)
  pattern<-paste("[A-Za-z0-9_]*","exported",sep="")
  cond<-grepl(pattern,SimID)
  SimID<-ifelse(cond,SimID,paste(SimID,"exported",sep="_"))

  # misc
  folderVar <- 0
  leader <- 10
  offset <- NULL

  # initialize variables
  n_SimID<-length(SimID)
  n_t<-(tSpan-tInit)/desiredInterval+1
  trange<-seq(from=tInit/tInterval,to=tSpan/tInterval,length.out=n_t)
  tpoints<-seq(from=tInit,to=tSpan,desiredInterval)
  graphType<-"timecourse"
  Cc<-criticalConc
  kinProt<-c("Ndc80","Knl1")
  plist<-list()
  L <- list()
  Clist<-list()
  nlist<-list()
  rlist<-list()
  matrix_list<-list()
  master_data<-data.frame()
  t_labs<-vector()
  count_species<-1
  count<-1

  # constants
  N_A<-6.02e23
  Cexp <- 10 #10 uM

  total_Plk1<-c("Plk1","pPlk1")
  total_Haspin<-c("Haspin","pHaspin")
  total_H3<-c("H3","pH3")
  total_Mps1<-c("Mps1","pMps1","ppMps1")
  total_Ndc80<-c("Ndc80","pNdc80")
  total_Knl1<-c("Knl1","pKnl1")
  total_Bub1<-c("Bub1","pBub1")
  total_H2A<-c("H2A","pH2A")


  # define species
  other_species<-c("Plk1",
    "pPlk1",
    "Haspin",
    "pHaspin",
    "H3",
    "pH3",
    "Mps1",
    "pMps1",
    "ppMps1",
    "Ndc80",
    "pNdc80",
    "Knl1",
    "pKnl1",
    "Bub1",
    "pBub1",
    "Sgo1",
    "H2A",
    "pH2A",
    "pH2A_Sgo1")#,
    # "CENP",
    # "pCENP",
    # "Sgo1_pCENP")

  CPC_species<-c("CPC",
    "pH2A_CPC",
    "CPC_pH3",
    "pH2A_CPC_pH3",
    "CPCa",
    "pH2A_CPCa",
    "CPCa_pH3",
    "pH2A_CPCa_pH3")

  other_spec_pat<-c("Plk1","Haspin","Mps1","Ndc80","Knl1","Bub1","Sgo1")
  inact_pat<-"(CPC[^a])|(CPC$)"
  act_pat<-"CPCa"
  tot_pat<-"CPC"
  totals<-c(other_spec_pat,inact_pat,act_pat,tot_pat)

  spec<-c(other_species,CPC_species)
  # if(clamped!=NULL){
  #   clamp_ind<-match(clamped,spec)
  #   spec<-spec[-clamp_ind]
  # }
  
  # print("HELLO")
  # change working directory
  setwd(importPath)
  
  n_spec<-length(spec)
  n_CPC_spec<-length(CPC_species)
  n_trange<-length(trange)
  n_sim<-length(SimID)

  #species
  spec_rep<-rep(spec,each=n_trange,times=n_sim)
  CPC_spec_rep<-rep(CPC_species,times=n_sim)

  #time points
  t <- trange
  # convert timepoint to string
  dataPoint<-as.character(round(x=t,digits=0))
  dataPoint<-ifelse(nchar(dataPoint)==1,paste("000",dataPoint,sep=""),dataPoint)
  dataPoint<-ifelse(nchar(dataPoint)==2,paste("00",dataPoint,sep=""),dataPoint)
  dataPoint<-ifelse(nchar(dataPoint)==3,paste("0",dataPoint,sep=""),dataPoint)
  t_rep<-rep(dataPoint,times=n_spec*n_sim)
  tpoints_rep<-rep(tpoints,times=n_spec*n_sim)

  # Simulation IDs
  sim_rep<-rep(SimID,each=n_spec*n_trange)
  name_rep<-rep(names,each=n_spec*n_trange)

  # print(paste("sim_rep",length(sim_rep)))
  # print(paste("name_rep",length(name_rep)))
  # print(paste("spec_rep",length(spec_rep)))
  # print(paste("t_rep",length(t_rep)))
  # print(paste("tpoints_rep",length(tpoints_rep)))
  # print(paste("trange",length(trange)))
  # print(paste("n_trange*n_sim*n_spec",n_trange*n_sim*n_spec))

  # fold enrichment
  if(op=="fold_enrich"){
    t_end<-t[length(t)]
    dataPoint<-as.character(round(x=t_end,digits=0))
    dataPoint<-ifelse(nchar(dataPoint)==1,paste("000",dataPoint,sep=""),dataPoint)
    dataPoint<-ifelse(nchar(dataPoint)==2,paste("00",dataPoint,sep=""),dataPoint)
    dataPoint<-ifelse(nchar(dataPoint)==3,paste("0",dataPoint,sep=""),dataPoint)
    t_end_rep<-rep(dataPoint,each=n_sim)
    t_end_rep<-rep(t_end_rep,times=n_CPC_spec)
    sim_rep2<-rep(SimID,each=length(CPC_species))
    sim<-gsub(pattern="_exported",replacement="",x=sim_rep2)
    pattern<-paste(sim,
                          "Slice_XY_0",
                           CPC_spec_rep,
                           t_end_rep,
                           sep="_")
    pattern<-paste(pattern,"csv",sep=".")
    path<-rep(getwd(),length(pattern))
    file_path<-file.path(path,sim_rep2,pattern)
    # print(file_path)
    # CPC_init_uM <- 0.116245
    # return(file_path)
    mat_list<-lapply(file_path,FUN=read.csv,skip=leader)
    print("WE MADE IT!")
    mat_list<-lapply(mat_list,FUN=function(x){x<-x[,(1:ncol(x)-1)]})
    mat_list<-lapply(mat_list,FUN=as.matrix)
    # mat_list<-lapply(mat_list,FUN=function(x){x+CPC_init_uM})
    split_list<-split(mat_list, ceiling(seq_along(mat_list)/n_CPC_spec))
    sum_list<-lapply(split_list,FUN=reduce,.f=`+`)
    fe_list<-lapply(sum_list,FUN=fold_enrich)
    fe_df<-t(data.frame(fe_list))
    fe_df<-data.frame(names,fe_df)
    rownames(fe_df)<-c()
    colnames(fe_df)<-c("TCGA_ID",
    "C_max",
    "C_min",
    "C_ic",
    "ic_enrich",
    "max_enrich",
    "y_enrich",
    "y_enrich_ratio",
    "x_enrich",
    "x_enrich_ratio")
    return(fe_df)
  }

  # if(op=="heatmap"){

    # time labels
    t_short<-seq(from=tInit,to=tSpan,length.out=n_t)
    t_equal_str<-"t (s) ="
    t_labs[1] <- paste(t_equal_str,t_short[1])
    t_labs[2:length(t_short)]<-t_short[2:length(t_short)]
    names(t_labs) <- as.character(t_short)
    t_long<-as.character(rep(t_short,each=dataDim[1]*dataDim[2],times=n_SimID))
    t_lev<-levels(factor(as.numeric(t_short)))
    
    # SimID labels
    ID_short<-seq(from=1,to=n_SimID)
    ID_labs <- names
    names(ID_labs) <- as.character(ID_short)
    ID_long<-name_rep
    ID_lev<-levels(factor(as.numeric(ID_short)))

  # }

  if(op=="timecourse"){
    # generate path for all files
    sim<-gsub(pattern="_exported",replacement="",x=sim_rep)
    pattern<-paste(sim,
                          "Slice_XY_0",
                           spec_rep,
                           t_rep,
                           sep="_")
    pattern<-paste(pattern,"csv",sep=".")
    file_path<-file.path(sim_rep,pattern)
    # get csv file
    mat_list<-lapply(file_path,FUN=read.csv,skip=leader)
    mat_list<-lapply(mat_list,FUN=function(x){x<-x[,(1:ncol(x)-1)]})
    mat_list<-lapply(mat_list,FUN=as.matrix)
    # perform integration to get copy number
    mat_list_um3<-lapply(mat_list,FUN=function(x){x*1e-15})
    umol<-sapply(mat_list_um3,FUN=massInt,chrWidth=chromWidth, chrHeight=chromHeight, Cc=0)
    umol_1<-massInt(mat_list_um3[[1]],chrWidth=chromWidth, chrHeight=chromHeight, Cc=0)
    copy_num<-sapply(umol,FUN=function(x){x*1e-6*N_A})
    copy_num_round<-sapply(copy_num,FUN=round,digits=1)
    # assemble data frame
    master_data<-data.frame(name_rep,spec_rep,tpoints_rep,copy_num_round)
    colnames(master_data)<-c("sim","spec","t","copy")
    
    # summed species
    totals<- c("total Plk1","total Haspin","total Mps1","total Ndc80","total Knl1","total Bub1","total Sgo1","total CPC")
    acts<-c("active CPC","inactive CPC")

    # # lapply(master_data$spec,FUN=grepl,pattern=totals)

    # print(master_data$spec)
    # Plk1_b<-grepl(x=master_data$spec,pattern="Plk1")
    # Haspin_b<-grepl(x=master_data$spec,pattern="Haspin")
    # Mps1_b<-grepl(x=master_data$spec,pattern="Mps1")
    # Ndc80_b<-grepl(x=master_data$spec,pattern="Ndc80")
    # Knl1_b<-grepl(x=master_data$spec,pattern="Knl1")
    # Bub1_b<-grepl(x=master_data$spec,pattern="Bub1")
    # Sgo1_b<-grepl(x=master_data$spec,pattern="Sgo1")
    # act_b<-grepl(x=master_data$spec,pattern=act_pat)
    # inact_b<-grepl(x=master_data$spec,pattern=inact_pat)
    # tot_b<-grepl(x=master_data$spec,pattern=tot_pat)

    Plk1_b<-grepl(x=master_data$spec,pattern="pPlk1")
    Haspin_b<-grepl(x=master_data$spec,pattern="pHaspin")
    Mps1_b<-grepl(x=master_data$spec,pattern="(pMps1)|(ppMps1)")
    Ndc80_b<-grepl(x=master_data$spec,pattern="(pNdc80)|(ppMps1)")
    Knl1_b<-grepl(x=master_data$spec,pattern="pKnl1")
    Bub1_b<-grepl(x=master_data$spec,pattern="pBub1")
    Sgo1_b<-grepl(x=master_data$spec,pattern="pH2A_Sgo1")
    act_b<-grepl(x=master_data$spec,pattern=act_pat)
    inact_b<-grepl(x=master_data$spec,pattern=inact_pat)
    tot_b<-grepl(x=master_data$spec,pattern="(pH2A_CPC)|(CPC_pH3)|(pH2A_CPC_pH3)|(CPCa)|(pH2A_CPCa)|(CPCa_pH3)|(pH2A_CPCa_pH3)")

    # "pH2A_CPC",
    # "CPC_pH3",
    # "pH2A_CPC_pH3",
    # "CPCa",
    # "pH2A_CPCa",
    # "CPCa_pH3",
    # "pH2A_CPCa_pH3"

    bool_tot<-list(Plk1_b,Haspin_b,Mps1_b,Ndc80_b,Knl1_b,Bub1_b,Sgo1_b,tot_b)
    bool_act<-list(act_b,inact_b)
    act_list<-list()
    tot_list<-list()

    bar_df<-data.frame()
    empty<-data.frame()

    View(filter(master_data,Sgo1_b))

    for(i in 1:length(acts)){
      prot<-filter(master_data,bool_act[[i]])
      prot<-prot %>%
        dplyr::group_by(sim,t) %>%
        dplyr::summarise(copy = sum(copy), n = dplyr::n())
    prot<-prot %>% select(sim,t,copy)
    prot<-add_column(prot, spec = rep(acts[i],times=nrow(prot)), .before = "t")
    act_list[[i]]<-prot
    prot<-as.data.frame(prot)
    # master_data<-rbind(master_data,prot)
    # master_data<-bind_rows(empty,master_data)
    # master_data<-bind_rows(master_data,prot)
    # View(prot)
    }

    View(master_data)
    
    for(i in 1:length(totals)){
      prot<-filter(master_data,bool_tot[[i]])
      prot<-prot %>%
        dplyr::group_by(sim,t) %>%
        dplyr::summarise(copy = sum(copy), n = dplyr::n())
    prot<-prot %>% select(sim,t,copy)
    prot<-add_column(prot, spec = rep(totals[i],times=nrow(prot)), .before = "t")
    tot_list[[i]]<-prot
    prot<-as.data.frame(prot)
    bar_df<-bind_rows(bar_df,prot)
    }
    
    View(bar_df)
    bar_df<-bar_df %>%
        dplyr::group_by(sim,spec) %>%
        dplyr::summarise(copy = mean(copy), n = dplyr::n())



    # bar_df<-bar_df %>%
    #     dplyr::group_by(sim,spec) %>%
    #     dplyr::summarise(copy = mean(copy), n = dplyr::n())
    # return(list(master_data,bar_df))
    

    # return(list(act_list,tot_list))


    # 10% from before
    # HeLa<-c(1133.1545,NA,141.9737,NA,NA,NA,666.833942353)
    # A549<-c(1568.047474538,NA,95.783003474,239.899110599,628.606494521,NA,756.575938897)
    # Hep_G2<-c(1133.154503478,NA,NA,440.301071503,53.741063767,NA,775.897642370)
    # PC_3<-c(774.517713637,NA,453.813992609,2103.154258650,2190.285698500,NA,1219.782025918)
    # U87_MG<-c(715.573562301,NA,34.098679708,763.564974914,2658.231713329,NA,764.522855220)
    # PrEST_SILAC<-c(1133.154503826,NA,489.370879447,1050.305355066,1070.519627216,63.011300696,2375.447793805)

    # totals<- c("total Plk1","total Haspin","total Mps1","total Ndc80","total Knl1","total Bub1","total CPC")
    HeLa<-c(10204.171583240,202.303970220,1278.487766358,NA,NA,NA,3290.347927611)
    A549<-c(16818.602406575,29.235683731,1027.351708980,2573.115817196,6742.323094941,NA,3796.556808696)
    Hep_G2<-c(12999.416412579,13.202722606,NA,5051.082582127,616.511220863,NA,4320.420361233)
    PC_3<-c(9077.900864803,23.938682721,5319.024166173,24650.470256859,25671.712972482,NA,4851.344383831)
    U87_MG<-c(8165.354162392,5.590408363,389.097377204,8712.980432256,30332.874953113,NA,3821.316878943)
    PrEST_SILAC<-c(10919.879283770,124.721826196,4715.924360277,10121.486213657,10316.285255569,607.221517269,4443.207716872)

    # cell_data<-list(HeLa,A549,Hep_G2,PC_3,U87_MG,PrEST_SILAC)
    # cell_data_rep<-lapply(cell_data,FUN=rep,times=n_trange)
    # cell_data_lin<-t(as.data.frame(lapply(cell_data_rep,FUN=rbind)))

    limits<-c(HeLa,A549,Hep_G2,PC_3,U87_MG,PrEST_SILAC)
    cell_type<-c("HeLa","A549","Hep_G2","PC_3","U87_MG","PrEST_SILAC")
    cell<-rep(cell_type,each=length(totals))
    totals_rep<-rep(totals,times=length(cell_type))

    limit_data<-data.frame(cell,totals_rep,limits)
    colnames(limit_data)<-c("sim","spec","copy")
    limit_data<-rbind(bar_df,limit_data)
    limit_data <- limit_data %>% select(sim,spec,copy)

    View(limit_data)
    # cell_data_rep<-rep(cell_data,each=n_trange)
    # cell_type_rep<-rep(cell_type,each=length(totals)*n_trange)
    # totals_rep<-rep(totals,each=n_trange,times=length(cell_type))
    # rep(tpoints,times=length(totals)*length(cell_type))

    # facet names
    # species_labs<-totals
    # species_labs<-gsub("[_]+","- ",species_labs)
    # species_labs<-str_wrap(species_labs,width=5)
    facet_var<-factor(limit_data$spec,levels=totals,labels=totals)


    bar<-ggplot(data=limit_data,aes(x=sim, y=copy,fill=sim))+geom_bar(stat="identity")+
      facet_wrap(facet_var,scales="free")+
      scale_y_continuous(limits = c(0,NA))+
      theme_void()+
      xlab("model condition or cell type")+
      ylab("copies / chromosome")+
      theme(axis.ticks = element_line(size = 0.5))+
      theme(axis.ticks.length=unit(.2, "cm"))+
      theme(panel.spacing=unit(.5,"cm"))+
      theme(axis.text=element_text(size=10),
            axis.title=element_text(size=14,face="bold"))+
      theme(axis.title.y=element_text(angle=90,vjust=1))+
      theme(axis.text.x=element_text(angle=90))+
      theme(axis.line=element_line(size=1))+
      theme(strip.text=element_text(size=12,face="bold"))+
      theme(legend.title = element_blank())+
      theme(legend.text=element_text(size=14))


    # Plk1<-filter(master_data,Plk1_b)
    # Plk1<-Plk1 %>%
    #   dplyr::group_by(sim,t) %>%
    #   dplyr::summarise(copy = sum(copy), n = dplyr::n())
    # Plk1<-Plk1 %>% select(sim,t,copy)
    # Plk1<-add_column(Plk1, spec = rep("total Plk1",times=nrow(Plk1)), .before = "t")
    # View(Plk1)

    # Haspin<-filter(master_data,Haspin_b)
    # Haspin<-Haspin %>%
    #   group_by(t) %>%
    #   summarise(sum = sum(copy_num))
    # # View(Haspin)

    # Mps1<-filter(master_data,Mps1_b)
    # Mps1<-Mps1 %>%
    #   group_by(t) %>%
    #   summarise(sum = sum(copy_num))
    # # View(Mps1)

    # Ndc80<-filter(master_data,Ndc80_b)
    # Ndc80<-Ndc80 %>%
    #   group_by(t) %>%
    #   summarise(sum = sum(copy_num))
    # # View(Ndc80)

    # Knl1<-filter(master_data,Knl1_b)
    # Knl1<-Knl1 %>%
    #   group_by(t) %>%
    #   summarise(sum = sum(copy_num))
    # # View(Knl1)

    # Bub1<-filter(master_data,Bub1_b)
    # Bub1<-Bub1 %>%
    #   group_by(t) %>%
    #   summarise(sum = sum(copy_num))
    # # View(Bub1)

    # Sgo1<-filter(master_data,Sgo1_b)
    # Sgo1<-Sgo1 %>%
    #   group_by(t) %>%
    #   summarise(sum = sum(copy_num))
    # # View(Sgo1)
    
    # act<-filter(master_data,act_b)
    # act<-act %>%
    #   group_by(t) %>%
    #   summarise(sum = sum(copy_num))
    # # View(act)

    # inact<-filter(master_data,inact_b)
    # inact<-inact %>%
    #   group_by(t) %>%
    #   summarise(sum = sum(copy_num))
    # # View(inact)

    # tot<-filter(master_data,tot_b)
    # tot<-tot %>%
    #   group_by(t) %>%
    #   summarise(sum = sum(copy_num))
    # # View(tot)


    # axes limits
    xbreaks<-seq(0, tSpan, tSpan/(xdiv-1))
    xlabs<-c(as.character(round(0)),as.character(round(xbreaks[2:length(xbreaks)],digits=0)))

    # facet names
    species_labs<-spec
    species_labs<-gsub("[_]+","- ",species_labs)
    species_labs<-str_wrap(species_labs,width=5)
    facet_var<-factor(master_data$spec,levels=spec,labels=species_labs)

    # plot timecourse
    p2<-ggplot(data=master_data,aes(x=t, y=copy, color=sim))+geom_line(size=1,position=position_dodge(width=40))+
      facet_wrap(facet_var,scales="free")+
      scale_x_continuous(breaks=xbreaks,labels=xlabs)+
      scale_y_continuous(limits = c(0,NA))+
      theme_void()+
      xlab("t (s)")+
      ylab("copies / chromosome")+
      theme(axis.ticks = element_line(size = 0.5))+
      theme(axis.ticks.length=unit(.2, "cm"))+
      theme(panel.spacing=unit(.5,"cm"))+
      theme(axis.text=element_text(size=10),
            axis.title=element_text(size=14,face="bold"))+
      theme(axis.title.y=element_text(angle=90,vjust=1))+
      theme(axis.text.x=element_text(angle=45))+
      theme(axis.line=element_line(size=1))+
      theme(strip.text=element_text(size=12,face="bold"))+
      theme(legend.title = element_blank())+
      theme(legend.text=element_text(size=14))


    # exporting graph as file
    phaseString<-paste("phase",as.character(phase),sep="")
    exportFilename<-paste(graphType,sweepName,phaseString,sep="_")
    exportFilename <- paste(exportFilename,"png",sep=".")

    # save graph to png file
    ggsave(
      exportFilename,
      plot = p2,
      device = "png",
      path = exportPath,
      scale = 1,
      width = 16,
      height = 10,
      units = "in",
      dpi = 300,
      limitsize = TRUE)

    # exporting graph as file
    phaseString<-paste("phase",as.character(phase),sep="")
    exportFilename<-paste("bar",sweepName,phaseString,sep="_")
    exportFilename <- paste(exportFilename,"png",sep=".")

    # save graph to png file
    ggsave(
      exportFilename,
      plot = bar,
      device = "png",
      path = exportPath,
      scale = 1,
      width = 16,
      height = 10,
      units = "in",
      dpi = 300,
      limitsize = TRUE)

    print(bar)
    print(p2)
    return(master_data)
  }
}