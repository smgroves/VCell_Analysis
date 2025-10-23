vcell_table <- function(
    sims, # vector of strings of SimIDs in the form c("SimID_209081149_0__exported","SimID_209081149_0__exported")
    vars,
    tPoints,
    all_species,
    name,
    chromWidth=1.6, #um
    chromHeight=3.5, #um
    dataDim=c(149,68), # rows,columns in concentration matrix; depends on mesh size
    row_1=1,
    row_2=dataDim[1],
    col_1=1,
    col_2=dataDim[2],
    importPath="/Users/sam/Research/JanesLab/vcell_data",
    exportPath="/Users/sam/Research/JanesLab/vcell_plots",
    kt_width = 'Relaxed'
    ){
  
  #######################################  TESTING  #################################################
  # 
  # CPC_species <-c("CPCa", "pH2A_Sgo1_CPCa", "pH3_CPCa", "pH2A_Sgo1_pH3_CPCa", "CPCi", "pH2A_Sgo1_CPCi", "pH3_CPCi", "pH2A_Sgo1_pH3_CPCi")
  # Mps1_species <-c("Mps1a", "pMps1a", "Ndc80_Mps1a", "Ndc80_pMps1a", "pNdc80_Mps1a", "pNdc80_pMps1a", "Mps1i", "pMps1i", "Ndc80_Mps1i", "Ndc80_pMps1i", "pNdc80_Mps1i", "pNdc80_pMps1i")
  # Todd_species <-c("Plk1a", "Plk1i", "Haspina", "Haspini", "pH3", "pH3_CPCa", "pH3_CPCi", "pH2A_Sgo1_CPCi", "pH2A_Sgo1_CPCa")
  # H3_species <- c("H3", "pH3", "pH3_CPCa", "pH3_CPCi", "pH3_CPCa", "pH2A_Sgo1_pH3_CPCa", "pH3_CPCi", "pH2A_Sgo1_pH3_CPCi")
  # H2A_species <- c("H2A", "pH2A", "pH2A_Sgo1", "pH2A_Sgo1_CPCa", "pH2A_Sgo1_CPCi", "pH2A_Sgo1_pH3_CPCi", "pH2A_Sgo1_pH3_CPCa")
  # 
  # 
  # all_species <- c(CPC_species)
  # 
  # sims<-"SimID_258639712_0__exported"
  # 
  # vars <- "base line model KdpNdc80pMps1 start - kpp=0.1 kppKT=0.3 H3d H2Ad"
  # 
  # 
  # # what to name the output graph file, as a string "name"
  # sweep_name<-paste("Relaxed_Base model", var)
  # 
  # exportPath<-"/Users/sam/Research/JanesLab/vcell_plots"
  # 
  # tPoints = c(200, 500)
  # 
  # 
  # sweepName=sweep_name
  # names=names
  # chromWidth=1.6 #um
  # chromHeight=3.5 #um
  # dataDim=c(149,68)
  # row_1=1
  # row_2=dataDim[1]
  # col_1=2
  # col_2=dataDim[2]
  # importPath="/Users/sam/Research/JanesLab/vcell_data"
  # exportPath="/Users/sam/Research/JanesLab/vcell_plots"
  # var=var
  
  ####################################################################################################
  
  name <- name
  
  tb <- data.frame(matrix(ncol = 3, nrow = length(sims)))
  colnames(tb) <- c('Simulation', 'Time = 200 s', 'Time = 500 s')
  
  for(s in 1:length(sims)){
  
    
  SimID = sims[s]
  var = vars[s]
    
  # misc
  folderVar <- 0
  leader <- 10
  offset <- NULL
  
  
  pattern<-paste("[A-Za-z0-9_]*","exported",sep="")
  cond<-grepl(pattern,SimID)
  print(SimID)
  SimID<-ifelse(cond,SimID,paste(SimID,"exported",sep="_"))
  print(SimID)
  
  # initial concentrations (uM) -> Without vol_ratio or fractions multiplications
  # clamped
  Haspini_ic_uM<- 0.55071118
  Plk1_init_uM<-0.23394
  CPCi_init_uM <- 0.07838
  Bub1a_init_uM<-0.02018
  Sgo1_init_uM<-0.02583
  
  kt_species <- vector("list", length(all_species))
  ic_species <- vector("list", length(all_species))
  L <- list()
  
  # Initialize empty vectors for each species
  for (i in 1:length(all_species)) {
    kt_species[[i]] <- vector("numeric", (length(tPoints)))
    ic_species[[i]] <- vector("numeric", (length(tPoints)))
  }
  
  # change working directory
  setwd(importPath)
  
  all_species <- all_species
  
  # data processing
  for(z in 1:length(tPoints)){
    
    t <- tPoints[z] / 10
    
    # convert timepoint to string
    dataPoint<-as.character(round(x=t,digits=0))
    if(nchar(dataPoint)==1){
      dataPoint<-paste("000",dataPoint,sep="")
    }else if(nchar(dataPoint)==2){
      dataPoint<-paste("00",dataPoint,sep="")
    }else if(nchar(dataPoint)==3){
      dataPoint<-paste("0",dataPoint,sep="")
    }
    
    
    
    for(i in 1:length(all_species)){
      pattern<-paste("[A-Za-z0-9_]*_Slice_XY_\\d",
                     all_species[i],
                     dataPoint,
                     sep="_")
      
      
      tryCatch(
        
        expr = {
          # read the csv file to a matrix, M
          L[[i]]<-data.matrix(read.csv(paste(importPath,SimID,grep(pattern, list.files(SimID), value = TRUE),sep="/"),header=FALSE,skip=leader))[row_1:row_2,col_1:col_2]
        },
        error = function(e){
          
          message("Missing species")
          message(all_species[i])
          print(e)
        },
        finally = {
          
        }
      )
    }
    
    
    # set any negative concentration values to zero
    L<-matrixZero(matrixList=L)
    

    for(q in 1:length(all_species)){
      
      if(all(dataDim==c(149,68))){
        y1 = ceiling(1.6 * dataDim[1] / chromHeight)
        y2 = ceiling(1.9 * dataDim[1] / chromHeight)
      }else if(all(dataDim==c(128,64))){
        y1 = ceiling(1.45 * dataDim[1] / chromHeight)
        y2 = ceiling(1.75 * dataDim[1] / chromHeight)
      }
      
      #For relaxed state
      if(kt_width == 'Relaxed'){
        x1 = ceiling(0.425 * dataDim[2] / chromWidth)
        x2 = ceiling(0.500 * dataDim[2] / chromWidth)
        x3 = ceiling(0.700 * dataDim[2] / chromWidth) + 1
        x4 = ceiling(0.900 * dataDim[2] / chromWidth) - 1
        x5 = ceiling(1.100 * dataDim[2] / chromWidth)
        x6 = ceiling(1.175 * dataDim[2] / chromWidth)
      }else if(kt_width == 'Tensed'){
        #For tensed state
        x1 = ceiling(0.125 * dataDim[2] / chromWidth)
        x2 = ceiling(0.200 * dataDim[2] / chromWidth)
        x3 = ceiling(0.700 * dataDim[2] / chromWidth) + 1
        x4 = ceiling(0.900 * dataDim[2] / chromWidth) - 1
        x5 = ceiling(1.400 * dataDim[2] / chromWidth)
        x6 = ceiling(1.475 * dataDim[2] / chromWidth)
      }
      matrix <- L[[q]]
      
      x_indices_LK <- x1:x2
      x_indices_RK <- x5:x6
      x_indices_IC <- x3:x4
      y_indices <- y1:y2
      
      
      left_kinetochore <-matrix[y_indices, x_indices_LK]
      right_kinetochore <-matrix[y_indices, x_indices_RK]
      inner_centromere <-matrix[y_indices, x_indices_IC]
      
      
      lk <- mean(left_kinetochore)
      rk <- mean(right_kinetochore)
      ic <- mean(inner_centromere)
      kt <- mean(lk, rk)
      
      
      kt_species[[q]][z] <- kt
      ic_species[[q]][z] <- ic
      
    }
    
  }
  
  data_ic <- data.frame(
    Time = rep(tPoints, times = length(all_species)), #edited
    Species = rep(all_species, each = (length(tPoints))),
    IC = unlist(ic_species)
  )
  
  data_kt <- data.frame(
    Time = rep(tPoints, times = length(all_species)), #edited
    Species = rep(all_species, each = (length(tPoints))),
    KT = unlist(kt_species)
  )
  
  # Reshape to wide
  data_ic <- reshape(data_ic, idvar = "Time", timevar = "Species", direction = "wide")
  data_kt <- reshape(data_kt, idvar = "Time", timevar = "Species", direction = "wide")
  
  # Rename columns
  colnames(data_ic)[2:ncol(data_ic)] <- gsub("IC.", "", colnames(data_ic)[2:ncol(data_ic)])
  colnames(data_kt)[2:ncol(data_kt)] <- gsub("KT.", "", colnames(data_kt)[2:ncol(data_kt)])
  

  # Add sum columns
  data_ic$Sum <- rowSums(data_ic[, 2:(length(all_species)+1)], na.rm = TRUE)
  data_kt$Sum <- rowSums(data_kt[, 2:(length(all_species)+1)], na.rm = TRUE)
  
  
  tb[s, 1] <- var
  tb[s, 2] <- data_ic['Sum'][1, 1] - data_kt['Sum'][1, 1]
  tb[s, 3] <- data_ic['Sum'][2, 1] - data_kt['Sum'][2, 1]
  
  
  }
  

  
  # tb <- tb[order(tb$`Time = 200 s`, decreasing=TRUE),]

  # grid.table(tb)
  
  setwd(exportPath)
  exportF <- paste(name, "table", sep="_")
  
  write.csv(data_ic, paste("ic_",exportF,".csv", sep=""), row.names = FALSE)
  write.csv(data_kt, paste("kt_",exportF,".csv", sep=""), row.names = FALSE)
  write.csv(tb, paste("sum_",exportF,".csv", sep=""), row.names = FALSE)
  # 
  # png(paste(exportF,"png",sep="."), height = 50*nrow(tb), width = 300*ncol(tb))
  # grid.table(tb)
  # dev.off()
  # 
  setwd(importPath)
  
 
  
  
}
