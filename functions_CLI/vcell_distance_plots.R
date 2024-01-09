vcell_distance_plots <- function(
    SimID, # vector of strings of SimIDs in the form c("SimID_209081149_0__exported","SimID_209081149_0__exported")
    sweepName=NULL,
    speciesDesired="inactive CPC",
    tInit=0, # in s
    tSpan, # in s
    chromWidth=1.6, #um
    chromHeight=3.5, #um
    dataDim=c(149,68), # rows,columns in concentration matrix; depends on mesh size
    row_1=1,
    row_2=dataDim[1],
    col_1=1,
    col_2=dataDim[2],
    importPath="/Users/sam/Research/JanesLab/vcell_data",
    exportPath="/Users/sam/Research/JanesLab/vcell_plots",
    relaxed=TRUE
){
  
  
  
    
    #######################################  TESTING  #################################################
  
  # sims<-c("SimID_258078189_0__exported") #pre
  # names<-c("Relaxed model")
  # 
  # var <-"both - MBP - Mod2 - HA2 mod —"
  # 
  # # what to name the output graph file, as a string "name"
  # sweep_name<-paste("Relaxed_Base model", var)
  # 
  # exportPath<-"/Users/sam/Research/JanesLab/vcell_plots"
  # 
  # 
  # 
  #   SimID=sims
  #   sweepName=sweep_name
  #   names=names
  #   speciesDesired=c("pH2A_Sgo1_CPCa",
  #                    "pH2A_Sgo1_pH3_CPCa")
  #   speciesName=
  #   tInit=0
  #   tSpan=500
  #   chromWidth=1.6 #um
  #   chromHeight=3.5 #um
  #   dataDim=c(149,68)
  #   row_1=1
  #   row_2=dataDim[1]
  #   col_1=2
  #   col_2=dataDim[2]
  #   importPath="/Users/sam/Research/JanesLab/vcell_data"
  #   exportPath="/Users/sam/Research/JanesLab/vcell_plots"
  #   full=TRUE
  #   collapsible=FALSE
  #   save=FALSE
  #   var=var
  #   sums=TRUE
  #   linewidth <- 0.7
  #   relaxed=TRUE
  

    ####################################################################################################
    
    # 0.6 relaxed state
    # 1.2 tensed state
  
  linewidth <- 0.7
    
    # misc
    folderVar <- 0
    leader <- 10
    offset <- NULL
    
    
    pattern<-paste("[A-Za-z0-9_]*","exported",sep="")
    cond<-grepl(pattern,SimID)
    print(SimID)
    SimID<-ifelse(cond,SimID,paste(SimID,"exported",sep="_"))
    print(SimID)
    
    
    #All the following data is updated until the vcell version 03-27-23
    #All species
    all_species<-c("Plk1a",
                   "Plk1i",
                   "Haspini",
                   "Haspina",
                   "Knl1",
                   "pKnl1",
                   "pKnl1_Bub1a",
                   "Bub1a",
                   "Bub1a_his",
                   "Sgo1",
                   "H2A",
                   "pH2A",
                   "H3",
                   "pH3",
                   "pH2A_Sgo1",
                   "CPCi",
                   "pH2A_Sgo1_CPCi",
                   "pH2A_Sgo1_CPCa",
                   "pH3_CPCi",
                   "pH2A_Sgo1_pH3_CPCi", 
                   "CPCa",
                   "pH3_CPCa",
                   "pH2A_Sgo1_CPCa",
                   "pH2A_Sgo1_pH3_CPCa", "Mps1a", "pMps1a", "Ndc80_Mps1a", "Ndc80_pMps1a", "pNdc80_Mps1a", "pNdc80_pMps1a",
                   "Mps1i", "pMps1i", "Ndc80_Mps1i", "Ndc80_pMps1i", "pNdc80_Mps1i", "pNdc80_pMps1i")
    
    # initial concentrations (uM) -> Without vol_ratio or fractions multiplications
    # clamped
    Haspini_ic_uM<- 0.55071118
    Plk1_init_uM<-0.23394
    CPCi_init_uM <- 0.07838
    Bub1a_init_uM<-0.02018
    Sgo1_init_uM<-0.02583
    
    species <- speciesDesired
    concentration <- vector("list", length(species))
    
    
    for (i in 1:length(species)){
      concentration[[i]] <- vector("numeric", dataDim[2])
    }
    
    
    # change working directory
    setwd(importPath)
    
    t <- tInit / 10
    
    # convert timepoint to string
    dataPoint<-as.character(round(x=t,digits=0))
    if(nchar(dataPoint)==1){
      dataPoint<-paste("000",dataPoint,sep="")
    }else if(nchar(dataPoint)==2){
      dataPoint<-paste("00",dataPoint,sep="")
    }else if(nchar(dataPoint)==3){
      dataPoint<-paste("0",dataPoint,sep="")
    }
    
    L <- list()
    
    
    for(i in 1:length(species)){
      pattern<-paste("[A-Za-z0-9_]*_Slice_XY_\\d",
                     species[i],
                     dataPoint,
                     sep="_")
      
      
      
      # read the csv file to a matrix, M
      L[[i]]<-data.matrix(read.csv(paste(importPath,SimID,grep(pattern, list.files(SimID), value = TRUE),sep="/"),header=FALSE,skip=leader))[row_1:row_2,col_1:col_2]
    }
    
    # set any negative concentration values to zero
    L<-matrixZero(matrixList=L)
    
    
    
    for(i in 1:length(species)){
      
      
      y1 = ceiling(1.6 * dataDim[1] / 3.5)
      y2 = ceiling(1.9 * dataDim[1] / 3.5)
      
      x1 = ceiling(0.425 * dataDim[2] / 1.6) - 1
      x6 = ceiling(1.175 * dataDim[2] / 1.6) - 1
      
      
      matrix <- L[[i]]
      
      x_indices_horizontal <- x1:x6
      y_indices <- y1:y2
      
      horizontal_strip <- matrix[y_indices, x_indices_horizontal]
      
      hs <- colMeans(horizontal_strip)
      
      
      concentration[[i]] <- hs
      
    }
    
    
    if(relaxed){
      d_kinetichores = 0.6
    }else{
      d_kinetichores = 1.2
    }
    
    distance = seq(-1 * d_kinetichores/2, d_kinetichores/2, by=d_kinetichores/(length(x_indices_horizontal) - 1))
    
    
    data <- data.frame(
      Distance = rep(distance, length(species)),
      Species = rep(species, each = length(distance)),
      Concentration = unlist(concentration)
    )
    
    data_wide <- reshape(data, idvar = "Distance", timevar = "Species", direction = "wide")
    
    # Rename columns
    colnames(data_wide)[2:ncol(data_wide)] <- gsub("Concentration.", "", colnames(data_wide)[2:ncol(data_wide)])
    
    # Get active and inactive df for IC and KT
    data_active <- data_wide %>% select("Distance", ends_with('a'))
    data_inactive <- data_wide %>% select("Distance", ends_with('i'))
    
    # Get all active and inactive species
    active_species <- colnames(data_active %>% select(-c('Distance')))
    inactive_species <- colnames(data_inactive %>% select(-c('Distance')))
    
    
    data_long <-data_wide %>% gather("Species", "Concentration", -Distance)
    
    plot_data_start <- ggplot() +
      geom_line(data = data_long, aes(x = Distance, y = Concentration, color = Species), linewidth = linewidth) +
      labs(x = TeX("Distance ($\\mu$m)"), y = TeX("Concentration ($\\mu$M)")) +
      theme(panel.background = element_rect(fill = "transparent"),
            legend.background = element_rect(fill = "transparent"),
            axis.line = element_line(color = "black"))
    
    
    
    
    
    t <- tSpan / 10
    
    # convert timepoint to string
    dataPoint<-as.character(round(x=t,digits=0))
    if(nchar(dataPoint)==1){
      dataPoint<-paste("000",dataPoint,sep="")
    }else if(nchar(dataPoint)==2){
      dataPoint<-paste("00",dataPoint,sep="")
    }else if(nchar(dataPoint)==3){
      dataPoint<-paste("0",dataPoint,sep="")
    }
      
      L <- list()
      
      
      for(i in 1:length(species)){
        pattern<-paste("[A-Za-z0-9_]*_Slice_XY_\\d",
                       species[i],
                       dataPoint,
                       sep="_")
        
        
        
        # read the csv file to a matrix, M
        L[[i]]<-data.matrix(read.csv(paste(importPath,SimID,grep(pattern, list.files(SimID), value = TRUE),sep="/"),header=FALSE,skip=leader))[row_1:row_2,col_1:col_2]
      }
      
      # set any negative concentration values to zero
      L<-matrixZero(matrixList=L)
      
      
      
      for(i in 1:length(species)){
        
        
        y1 = ceiling(1.6 * dataDim[1] / 3.5)
        y2 = ceiling(1.9 * dataDim[1] / 3.5)
        
        x1 = ceiling(0.425 * dataDim[2] / 1.6) - 1
        x6 = ceiling(1.175 * dataDim[2] / 1.6) - 1
        
        
        matrix <- L[[i]]
        
        x_indices_horizontal <- x1:x6
        y_indices <- y1:y2

        horizontal_strip <- matrix[y_indices, x_indices_horizontal]
        
        hs <- colMeans(horizontal_strip)
        

        concentration[[i]] <- hs
        
      }
    
    if(relaxed){
    d_kinetichores = 0.6
    }else{
      d_kinetichores = 1.2
    }

    distance = seq(-1 * d_kinetichores/2, d_kinetichores/2, by=d_kinetichores/(length(x_indices_horizontal) - 1))

      
    data <- data.frame(
      Distance = rep(distance, length(species)),
      Species = rep(species, each = length(distance)),
      Concentration = unlist(concentration)
    )
    
    data_wide <- reshape(data, idvar = "Distance", timevar = "Species", direction = "wide")
    
    # Rename columns
    colnames(data_wide)[2:ncol(data_wide)] <- gsub("Concentration.", "", colnames(data_wide)[2:ncol(data_wide)])
    
    # Get active and inactive df for IC and KT
    data_active <- data_wide %>% select("Distance", ends_with('a'))
    data_inactive <- data_wide %>% select("Distance", ends_with('i'))

    # Get all active and inactive species
    active_species <- colnames(data_active %>% select(-c('Distance')))
    inactive_species <- colnames(data_inactive %>% select(-c('Distance')))
    
    
    data_long <- data_wide %>% gather("Species", "Concentration", -Distance)
    
    plot_data_final <- ggplot() +
      geom_line(data = data_long, aes(x = Distance, y = Concentration, color = Species), linewidth = linewidth) +
      labs(x = TeX("Distance ($\\mu$m)"), y = TeX("Concentration ($\\mu$M)")) +
      theme(panel.background = element_rect(fill = "transparent"),
            legend.background = element_rect(fill = "transparent"),
            axis.line = element_line(color = "black"))
  
    
    all_plots <- list(plot_data_start, plot_data_final)
    
    return(all_plots)
    
  
  
}