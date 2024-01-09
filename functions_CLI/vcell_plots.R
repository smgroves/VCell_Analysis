vcell_plots <- function(
    SimID, # vector of strings of SimIDs in the form c("SimID_209081149_0__exported","SimID_209081149_0__exported")
    sweepName=NULL,
    names=SimID,
    speciesDesired="inactive CPC",
    speciesName=speciesDesired,
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
    full=FALSE,
    collapsible=FALSE,
    single=TRUE,
    save=FALSE,
    var){
  
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
                 "Haspini",
                 "Haspina",
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
  
  
  # special species commands
  if(speciesDesired=="inactive CPC"){ 

      species<-c("CPCi", "pH2A_Sgo1_CPCi", "pH3_CPCi", "pH2A_Sgo1_pH3_CPCi")
    
  }else if(speciesDesired=="total Haspin"){

      species<-c("Haspini","Haspina")


  }else if(speciesDesired=="inactive Trimolecular CPC"){

      species<-c("pH2A_Sgo1_pH3_CPCi")

  }else if(speciesDesired=="active CPC"){

      species<-c("CPCa", "pH2A_Sgo1_CPCa", "pH3_CPCa", "pH2A_Sgo1_pH3_CPCa")

  }else if(speciesDesired=="all CPC"){

      species<-c("CPCa", "pH2A_Sgo1_CPCa", "pH3_CPCa", "pH2A_Sgo1_pH3_CPCa", "CPCi", "pH2A_Sgo1_CPCi", "pH3_CPCi", "pH2A_Sgo1_pH3_CPCi")
      name <- "CPC"
  }else if(speciesDesired=="all Mps1a"){

      species<-c("Mps1a", "pMps1a", "Ndc80_Mps1a", "Ndc80_pMps1a", "pNdc80_Mps1a", "pNdc80_pMps1a")

  }else if(speciesDesired=="all Mps1i"){

      species<-c("Mps1i", "pMps1i", "Ndc80_Mps1i", "Ndc80_pMps1i", "pNdc80_Mps1i", "pNdc80_pMps1i")
 
  }else if(speciesDesired=="all Mps1"){
    species<-c("Mps1a", "pMps1a", "Ndc80_Mps1a", "Ndc80_pMps1a", "pNdc80_Mps1a", "pNdc80_pMps1a", "Mps1i", "pMps1i", "Ndc80_Mps1i", "Ndc80_pMps1i", "pNdc80_Mps1i", "pNdc80_pMps1i")
    name <- "Mps1"
    }
  
  kt_species <- vector("list", length(species))
  ic_species <- vector("list", length(species))
  L <- list()
  
  # Initialize empty vectors for each species
  for (i in 1:length(species)) {
    kt_species[[i]] <- vector("numeric", 51)
    ic_species[[i]] <- vector("numeric", 51)
  }
  
  
  # change working directory
  setwd(importPath)
  

  # data processing
  for(z in 0:50){
      
      t <- z
      
      # convert timepoint to string
      dataPoint<-as.character(round(x=t,digits=0))
      if(nchar(dataPoint)==1){
        dataPoint<-paste("000",dataPoint,sep="")
      }else if(nchar(dataPoint)==2){
        dataPoint<-paste("00",dataPoint,sep="")
      }else if(nchar(dataPoint)==3){
        dataPoint<-paste("0",dataPoint,sep="")
      }
      

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
          
          x1 = ceiling(0.425 * dataDim[2] / 1.6)
          x2 = ceiling(0.500 * dataDim[2] / 1.6)
          x3 = ceiling(0.700 * dataDim[2] / 1.6) + 1
          x4 = ceiling(0.900 * dataDim[2] / 1.6) - 1
          x5 = ceiling(1.100 * dataDim[2] / 1.6)
          x6 = ceiling(1.175 * dataDim[2] / 1.6)
          
          
          matrix <- L[[i]]
          
          x_indices_LK <- x1:x2
          x_indices_RK <- x5:x6
          x_indices_IC <- x3:x4
          y_indices <- y1:y2
          
          
          left_kinetichore <-matrix[y_indices, x_indices_LK]
          right_kinetichore <-matrix[y_indices, x_indices_RK]
          inner_centromere <-matrix[y_indices, x_indices_IC]
          
          lk <- mean(left_kinetichore)
          rk <- mean(right_kinetichore)
          ic <- mean(inner_centromere)
          kt <- mean(lk, rk)
          
          
          kt_species[[i]][z+1] <- kt
          ic_species[[i]][z+1] <- ic
          
          
          
          # if(z == 49){
          #   print(inner_centromere)
          # }
          
        
        
        
      }
      
    }
  
    
    
    

    data <- data.frame(
      Time = 0:50,
      Species = rep(species, each = 51),
      KT = unlist(kt_species),
      IC = unlist(ic_species)
    )
    
    line_width <- 0.7
    
    active_species <- species[grep("a$", species)]
    inactive_species <- species[grep("i$", species)]
    
    
    data_active <- data.frame(
      Time = 0:50,
      Species = rep(active_species, each = 51),
      KT = unlist(kt_species[1:length(active_species)]),
      IC = unlist(ic_species[1:length(active_species)])
    )
    
    data_inactive <- data.frame(
      Time = 0:50,
      Species = rep(inactive_species, each = 51),
      KT = unlist(kt_species[length(active_species)+1:length(species)]),
      IC = unlist(ic_species[length(active_species)+1:length(species)])
    )
    
    
    data_active$Species <- factor(data_active$Species, levels = active_species)
    data_inactive$Species <- factor(data_inactive$Species, levels = inactive_species)
    
    # Combine active and inactive data frames
    
    
    sum_ic_inactive <- aggregate(IC ~ Time, data = data_inactive, FUN = sum)
    sum_ic_active <- aggregate(IC ~ Time, data = data_active, FUN = sum)
    sum_kt_inactive <- aggregate(KT ~ Time, data = data_inactive, FUN = sum)
    sum_kt_active <- aggregate(KT ~ Time, data = data_active, FUN = sum)
    
    
    
    # Create a data frame for active species with Sum IC Active
    data_active_ic <- data_active[data_active$Species != "Sum KT Active", ]
    
    # Create a data frame for active species with Sum KT Active
    data_active_kt <- data_active[data_active$Species != "Sum IC Active", ]
    
    # Create a new row for the sum values
    sum_row_ic <- data.frame(Time = sum_ic_active$Time, Species = "Sum IC Active", IC = sum_ic_active$IC, KT = 0)
    
    # Append the sum row to the data_active_ic dataframe
    data_active_ic <- rbind(sum_row_ic, data_active_ic)
    
    # Create a new row for the sum values
    sum_row_kt <- data.frame(Time = sum_kt_active$Time, Species = "Sum KT Active", KT = sum_kt_active$KT, IC = 0)
    
    # Append the sum row to the data_active_kt dataframe
    data_active_kt <- rbind(sum_row_kt, data_active_kt)
    

    
    # Create a data frame for active species with Sum IC Active
    data_inactive_ic <- data_inactive[data_inactive$Species != "Sum KT Inactive", ]
    
    # Create a data frame for active species with Sum KT Active
    data_inactive_kt <- data_inactive[data_inactive$Species != "Sum IC Inactive", ]
    
    # Create a new row for the sum values
    sum_row_ic <- data.frame(Time = sum_ic_inactive$Time, Species = "Sum IC Inactive", IC = sum_ic_inactive$IC, KT = 0)
    
    # Append the sum row to the data_active_ic dataframe
    data_inactive_ic <- rbind(sum_row_ic, data_inactive_ic)
    
    # Create a new row for the sum values
    sum_row_kt <- data.frame(Time = sum_kt_inactive$Time, Species = "Sum KT Inactive", KT = sum_kt_inactive$KT, IC = 0)
    
    # Append the sum row to the data_active_kt dataframe
    data_inactive_kt <- rbind(sum_row_kt, data_inactive_kt)
    
  
    
    if(full==TRUE){ 

      # Assuming a maximum of 8 species
      # custom_colors <- c("#e41a1c", "#377eb8", "#4daf4a", "#984ea3", "#ff7f00", "#ffff33", "#a65628", "#f781bf")
      custom_colors <- c("black", "#1b9e77", "#d95f02", "#7570b3", "#e7298a", "#66a61e", "#e6ab02", "#e41a1c", "#666666")
      len <- max(c(length(active_species) + 1, length(inactive_species) + 1))
      custom_colors <- custom_colors[1:len]
      
      
      
      if(speciesDesired=="all Mps1"){
        speciesInactive = "Inactive Mps1"
        speciesActive = "Active Mps1"
        speciesFull = "Mps1 Activation"
      }
      
      if(speciesDesired=="all CPC"){
        speciesInactive = "Inactive CPC"
        speciesActive = "Active CPC"
        speciesFull = "CPC Activation"
      }
      
      data_inactive_ic$Species <- factor(data_inactive_ic$Species, levels = unique(data_inactive_ic$Species))
      
      # Inactive IC
      plot_inactive_ic <- ggplot(data_inactive_ic, aes(x = Time, y = IC, color = Species)) +
        theme(panel.background = element_rect(fill='white')) +
        theme(legend.background = element_rect(fill = "white"))+
        geom_line(linetype = "dashed", size=line_width)+
        # geom_line(data = sum_ic_inactive, aes(y = IC), color = "black", size=line_width, linetype="dashed") +
        labs(x = "Time (s)", y = TeX("Concentration ($\\mu$M)")) +
        ggtitle(paste(speciesInactive, "concentration at inner centromere")) +
        # theme(plot.margin = unit(scaling, "cm"))+
        scale_x_continuous(breaks = seq(0, 50, 10), labels = seq(0, 500, 100))+
        # theme(legend.key.size = unit(0.5, "cm"))+  # Adjust the size as needed
        scale_color_manual(values = custom_colors)+
        theme(axis.line = element_line(color = "black"))
      
      
      # # Active IC
      # plot_active_ic <- ggplot(data_active, aes(x = Time, y = IC, color = Species)) + 
      #   theme(panel.background = element_rect(fill='white')) +
      #   theme(legend.background = element_rect(fill = "white"))+
      #   geom_line(linetype = "solid", size=line_width)+
      #   geom_line(data = sum_ic_active, aes(y = IC), color = "black", size=line_width) +
      #   labs(x = "Time (s)", y = TeX("Concentration ($\\mu$M)")) +
      #   ggtitle(paste(speciesActive, "concentration at inner centromere")) +
      #   # theme(plot.margin = unit(scaling, "cm"))+
      #   scale_x_continuous(breaks = seq(0, 50, 10), labels = seq(0, 500, 100))+
      #   # theme(legend.key.size = unit(0.5, "cm"))+  # Adjust the size as needed
      #   scale_color_manual(values = custom_colors)+
      #   theme(axis.line = element_line(color = "black"))
      
      data_active_ic$Species <- factor(data_active_ic$Species, levels = unique(data_active_ic$Species))
      
      plot_active_ic <- ggplot(data_active_ic, aes(x = Time, y = IC, color = Species)) + 
        theme(panel.background = element_rect(fill='white')) +
        theme(legend.background = element_rect(fill = "white"))+
        geom_line(linetype = "solid", size=line_width)+
        # geom_line(data = sum_ic_active, aes(y = IC), color = "black", size=line_width) +
        labs(x = "Time (s)", y = TeX("Concentration ($\\mu$M)")) +
        ggtitle(paste(speciesActive, "concentration at inner centromere")) +
        # theme(plot.margin = unit(scaling, "cm"))+
        scale_x_continuous(breaks = seq(0, 50, 10), labels = seq(0, 500, 100))+
        # theme(legend.key.size = unit(0.5, "cm"))+  # Adjust the size as needed
        scale_color_manual(values = custom_colors)+
        theme(axis.line = element_line(color = "black"))
      
      
      data_inactive_kt$Species <- factor(data_inactive_kt$Species, levels = unique(data_inactive_kt$Species))
      
      # Inactive KT
      plot_inactive_kt <- ggplot(data_inactive_kt, aes(x = Time, y = KT, color = Species)) + 
        theme(panel.background = element_rect(fill='white')) +
        theme(legend.background = element_rect(fill = "white"))+
        geom_line(linetype = "dashed", size=line_width)+
        # geom_line(data = sum_kt_inactive, aes(y = KT), color = "black", size=line_width, linetype="dashed") +
        labs(x = "Time (s)", y = TeX("Concentration ($\\mu$M)")) +
        ggtitle(paste(speciesInactive, "concentration at kinetochores")) +
        # theme(plot.margin = unit(scaling, "cm"))+
        scale_x_continuous(breaks = seq(0, 50, 10), labels = seq(0, 500, 100))+
        # theme(legend.key.size = unit(0.5, "cm"))+  # Adjust the size as needed
        scale_color_manual(values = custom_colors)+
        theme(axis.line = element_line(color = "black"))
      
      
      data_active_kt$Species <- factor(data_active_kt$Species, levels = unique(data_active_kt$Species))
      
      # Active KT
      plot_active_kt <- ggplot(data_active_kt, aes(x = Time, y = KT, color = Species)) + 
        theme(panel.background = element_rect(fill='white')) +
        theme(legend.background = element_rect(fill = "white"))+
        geom_line(linetype = "solid", size=line_width)+
        # geom_line(data = sum_kt_active, aes(y = KT), color = "black", size=line_width) +
        labs(x = "Time (s)", y = TeX("Concentration ($\\mu$M)")) +
        ggtitle(paste(speciesActive, "concentration at kinetochores")) +
        # theme(plot.margin = unit(scaling, "cm"))+
        scale_x_continuous(breaks = seq(0, 50, 10), labels = seq(0, 500, 100))+
        # theme(legend.key.size = unit(0.5, "cm"))+  # Adjust the size as needed
        scale_color_manual(values = custom_colors)+
        theme(axis.line = element_line(color = "black"))
      
      data_combined <- rbind(data_active, data_inactive)
      data_combined$Species <- factor(data_combined$Species, levels = c(active_species, inactive_species))
      
      data_combined_ic <- rbind(data_active_ic, data_inactive_ic)
      data_combined_ic$Species <- factor(data_combined_ic$Species, levels = unique(c(levels(data_active_ic$Species), levels(data_inactive_ic$Species))))
      
      
      data_combined_kt <- rbind(data_active_kt, data_inactive_kt)
      data_combined_kt$Species <- factor(data_combined_kt$Species, levels = unique(c(levels(data_active_kt$Species), levels(data_inactive_kt$Species))))
      
      

      # print(data_combined)
      # 
      # sum_ic_data <- aggregate(IC ~ Time, data = data_combined, FUN = sum)
      # sum_kt_data <- aggregate(KT ~ Time, data = data_combined, FUN = sum)
      
      # Assuming a maximum of 8 species
      # custom_colors <- c("#e41a1c", "#377eb8", "#4daf4a", "#984ea3", "#ff7f00", "#ffff33", "#a65628", "#f781bf")
      # custom_colors <- c("#1b9e77", "#d95f02", "#7570b3", "#e7298a", "#66a61e", "#e6ab02", "#e41a1c", "#666666")

      # len <- unique(length(active_species))
      # custom_colors <- custom_colors[1:len]
      
      c_colors <- c(custom_colors, custom_colors)
      
      
     
      
      # Active and Inactive KT on the same plot
      plot_kt <- ggplot() + theme(panel.background = element_rect(fill='white')) +
        theme(legend.background = element_rect(fill = "white"))+
        geom_line(data = data_combined_kt, aes(x = Time, y = KT, color = Species, linetype = Species), size=line_width) +
        # geom_line(data = sum_kt_active, aes(x = Time, y = KT), color = "black", size=line_width) +
        # geom_line(data = sum_kt_inactive, aes(x = Time, y = KT), color = "black", linetype = "dashed", size=line_width) +
        labs(x = "Time (s)", y = TeX("Concentration ($\\mu$M)")) +
        ggtitle(paste(speciesFull, "at kinetochores")) +
        # theme(plot.margin = unit(scaling, "cm"))+
        scale_x_continuous(breaks = seq(0, 50, 10), labels = seq(0, 500, 100))+
        scale_color_manual(values = c_colors) +
        scale_linetype_manual(values = c(rep("solid", length(unique(data_active_kt$Species))), rep("dashed", length(unique(data_inactive_kt$Species)))))+
        theme(axis.line = element_line(color = "black"))
      # theme_bw()+
      # theme(plot.background = element_rect(fill = "lightgray"))
      
      
      # Active and Inactive IC on the same plot
      plot_ic <- ggplot() + theme(panel.background = element_rect(fill='white')) +
        theme(legend.background = element_rect(fill = "white"))+
        geom_line(data = data_combined_ic, aes(x = Time, y = IC, color = Species, linetype = Species), size=line_width) +
        # geom_line(data = sum_ic_active, aes(x = Time, y = IC), color = "black", size=line_width) +
        # geom_line(data = sum_ic_inactive, aes(x = Time, y = IC), color = "black", linetype = "dashed", size=line_width) +
        labs(x = "Time (s)", y = TeX("Concentration ($\\mu$M)")) +
        ggtitle(paste(speciesFull, "at inner centromere")) +
        # theme(plot.margin = unit(scaling, "cm"))+
        scale_x_continuous(breaks = seq(0, 50, 10), labels = seq(0, 500, 100))+
        scale_color_manual(values = c_colors) +
        scale_linetype_manual(values = c(rep("solid", length(unique(data_active_ic$Species))), rep("dashed", length(unique(data_inactive_ic$Species)))))+
        theme(axis.line = element_line(color = "black"))

      
    }
    
    else if(collapsible==TRUE){
      
      custom_colors <- c("black", "#1b9e77", "#d95f02", "#7570b3", "#e7298a", "#66a61e", "#e6ab02", "#e41a1c", "#666666")
      len <- max(c(length(active_species) + 1, length(inactive_species) + 1))
      custom_colors <- custom_colors[1:len]
      
      c_colors <- c(custom_colors, custom_colors)
      
      
      data_inactive_ic$Species <- factor(data_inactive_ic$Species, levels = unique(data_inactive_ic$Species))
      data_active_ic$Species <- factor(data_active_ic$Species, levels = unique(data_active_ic$Species))
      data_inactive_kt$Species <- factor(data_inactive_kt$Species, levels = unique(data_inactive_kt$Species))
      data_active_kt$Species <- factor(data_active_kt$Species, levels = unique(data_active_kt$Species))
      
      
      
      data_combined_ic <- rbind(data_active_ic, data_inactive_ic)
      data_combined_ic$Species <- factor(data_combined_ic$Species, levels = unique(c(levels(data_active_ic$Species), levels(data_inactive_ic$Species))))
      
      
      data_combined_kt <- rbind(data_active_kt, data_inactive_kt)
      data_combined_kt$Species <- factor(data_combined_kt$Species, levels = unique(c(levels(data_active_kt$Species), levels(data_inactive_kt$Species))))
      
      
      # Filter out species with "Sum" in their name from data_combined_ic
      filtered_data_ic <- data_combined_ic[!grepl("Sum", data_combined_ic$Species), ]
      
      # Get top 4 species with highest concentrations from filtered_data_ic
      top_species_ic <- filtered_data_ic %>%
        group_by(Species) %>%
        summarize(max_concentration = max(IC)) %>%
        top_n(4, max_concentration) %>%
        select(Species)
      
      
      top_species <- top_species_ic$Species
      
      filtered_data <- filtered_data_ic %>% filter(Species %in% top_species)
      
      bleach <- filtered_data_ic %>% filter(!Species %in% top_species)
      

      # Create a new row for the sum values
      sum_row_active_ic <- data.frame(Time = sum_ic_active$Time, Species = "Sum IC Active", IC = sum_ic_active$IC, KT = 0)
      sum_row_inactive_ic <- data.frame(Time = sum_ic_inactive$Time, Species = "Sum IC Inactive", IC = sum_ic_inactive$IC, KT = 0)
      
      filtered_data_ic <- rbind(sum_row_active_ic, sum_row_inactive_ic, filtered_data)
      
      
      custom_colors_comp <- c("black", "#1b9e77", "#d95f02", "#7570b3", "#e7298a")
      
      bleached_layer <- geom_line(data = bleach, aes(x=Time, y=IC, color=Species, linetype=Species),colour = "grey", size=line_width)
      
      highlight_layer <- geom_line(data = filtered_data, aes(x=Time, y=IC, color=Species, linetype=Species), size=line_width)
      
      plot1 <- ggplot() +
              bleached_layer
              # highlight_layer
  
      print(plot1)
      
    }
    
    
    else{
      
      
      
      sum_ic_data <- aggregate(IC ~ Time, data = data, FUN = sum)
      sum_kt_data <- aggregate(KT ~ Time, data = data, FUN = sum)
      
      
      max_sum_ic_value <- max(sum_ic_data$IC, na.rm = TRUE)
      max_sum_kt_value <- max(sum_kt_data$KT, na.rm = TRUE)
      
      # Add maximum y-axis value as label for plot_ic_nosum
      max_ic_nosum <- max(data$IC, na.rm = TRUE)
      max_kt_nosum <- max(data$KT, na.rm = TRUE)
      
      print("Max IC Value (Summed):")
      print(max_sum_ic_value)
      print("Max KT Value (Summed):")
      print(max_sum_kt_value)
      print("Max IC Value (Not Summed):")
      print(max_ic_nosum)
      print("Max KT Value (Not Summed):")
      print(max_kt_nosum)
      
      # Plot IC vs. time
      plot_ic <- ggplot(data, aes(x = Time, y = IC, color = Species)) + 
        theme(panel.background = element_rect(fill='white')) +
        theme(legend.background = element_rect(fill = "white"))+
        geom_line(linetype = "solid", size=1.1)+
        geom_line(data = sum_ic_data, aes(y = IC), color = "black", size=1.1) +
        labs(x = "Time (s)", y = TeX("Concentration at Inner Centromere ($\\mu$M)")) +
        ggtitle(paste(speciesDesired, "Concentration at Inner Centromere vs. Time")) +
        # theme(plot.margin = unit(scaling, "cm"))+
        scale_x_continuous(breaks = seq(0, 50, 10), labels = seq(0, 500, 100))+
        theme(legend.key.size = unit(0.5, "cm"))+  # Adjust the size as needed
        scale_color_manual(values = custom_colors)+
        theme(axis.line = element_line(color = "black"))
        
      
      plot_ic_nosum <- ggplot(data, aes(x = Time, y = IC, color = Species))+
        geom_line()+
        labs(x = "Time (s)", y = TeX("Concentration at Inner Centromere ($\\mu$M)"))+
        ggtitle(paste(speciesDesired, "Concentration at Inner Centromere vs. Time")) + 
        theme_minimal()+
        scale_x_continuous(breaks = seq(0, 50, 10), labels = seq(0, 500, 100))+
        theme(legend.key.size = unit(0.5, "cm"))+  # Adjust the size as needed
        scale_color_manual(values = custom_colors)+
        theme(plot.background = element_rect(fill = "white", colour = "black"))+
        theme(legend.background = element_rect(fill = "white"))+
        theme(axis.line = element_line(color = "black"))
      
      
      plot_kt <- ggplot(data, aes(x = Time, y = KT, color = Species)) + 
        theme(panel.background = element_rect(fill='white')) +
        theme(legend.background = element_rect(fill = "white"))+
        geom_line(linetype = "solid", size=1.1)+
        geom_line(data = sum_kt_data, aes(y = KT), color = "black", size=1.1) +
        labs(x = "Time (s)", y = TeX("Concentration at Kinetochores ($\\mu$M)")) +
        ggtitle(paste(speciesDesired, "Concentration at Kinetochores vs. Time")) +
        # theme(plot.margin = unit(scaling, "cm"))+
        scale_x_continuous(breaks = seq(0, 50, 10), labels = seq(0, 500, 100))+
        # theme(legend.key.size = unit(0.5, "cm"))+  # Adjust the size as needed
        scale_color_manual(values = custom_colors)+
        theme(axis.line = element_line(color = "black"))
        
      
      
      plot_kt_nosum <- ggplot(data, aes(x = Time, y = KT, color = Species))+
        geom_line()+
        labs(x = "Time (s)", y = TeX("Concentration at Kinetochores ($\\mu$M)"))+
        ggtitle(paste(speciesDesired, "Concentration at Kinetochores vs. Time"))+
        theme_minimal()+
        scale_x_continuous(breaks = seq(0, 50, 10), labels = seq(0, 500, 100))+
        theme(legend.key.size = unit(0.5, "cm"))+ # Adjust the size as needed
        scale_color_manual(values = custom_colors)+
        theme(panel.background = element_rect(fill='white'))+
        theme(legend.background = element_rect(fill = "white"))+
        theme(axis.line = element_line(color = "black"))
      
      
      # p <- grid.arrange(p1, p2, ncol=2)
      # q <- grid.arrange(plot_ic, plot_kt, ncol=2)
      # q_nosum <- grid.arrange(plot_ic_nosum, plot_kt_nosum, ncol=2)
      # combined_plot <- grid.arrange(full_p, q, ncol = 2)
      # combined_plot <- combined_plot +theme(plot.margin = unit(c(0, -5, 0, -5), "null"))
      
      
    }
    
    
    

    
    if(save == TRUE & speciesDesired == "all CPC"){
      
      ic_name <- paste(name, "IC", sep="_")
      kt_name <- paste(name, "KT", sep="_")
      
      
      exportFilename_ic<-paste(ic_name,var,sep="_")
      exportFilename_ic <- paste(exportFilename_ic,"pdf",sep=".")
      
      exportFilename_kt<-paste(kt_name,var,sep="_")
      exportFilename_kt <- paste(exportFilename_kt,"pdf",sep=".")
      
      # save graph to png file
      ggsave(
        exportFilename_ic,
        plot = plot_ic,
        device = "pdf",
        path = exportPath,
        scale = 1,
        width = 5,
        height = 5,
        units = "in",
        dpi = 300,
        limitsize = TRUE)
      
      ggsave(
        exportFilename_kt,
        plot = plot_kt,
        device = "pdf",
        path = exportPath,
        scale = 1,
        width = 5,
        height = 5,
        units = "in",
        dpi = 300,
        limitsize = TRUE)
      
    }
    
    if(save == TRUE & speciesDesired == "all Mps1"){
      
      ic_name_active <- paste(name, "IC", "active", sep="_")
      ic_name_inactive <- paste(name, "IC", "inactive", sep="_")
      kt_name_active <- paste(name, "KT", "active", sep="_")
      kt_name_inactive <- paste(name, "KT", "inactive", sep="_")
      
      
      exportFilename_ic_active<-paste(ic_name_active,var,sep="_")
      exportFilename_ic_active <- paste(exportFilename_ic_active,"pdf",sep=".")
      
      exportFilename_ic_inactive<-paste(ic_name_inactive,var,sep="_")
      exportFilename_ic_inactive <- paste(exportFilename_ic_inactive,"pdf",sep=".")
      
      exportFilename_kt_active<-paste(kt_name_active,var,sep="_")
      exportFilename_kt_active <- paste(exportFilename_kt_active,"pdf",sep=".")
      
      exportFilename_kt_inactive<-paste(kt_name_inactive,var,sep="_")
      exportFilename_kt_inactive <- paste(exportFilename_kt_inactive,"pdf",sep=".")
      
      KT_side <- grid.arrange(plot_active_ic, plot_inactive_ic, ncol=2)
      IC_side <- grid.arrange(plot_active_kt, plot_inactive_kt, ncol=2)
      
      # save graph to png file
      ggsave(
        exportFilename_ic_active,
        plot = plot_active_ic,
        device = "pdf",
        path = exportPath,
        scale = 1,
        width = 5,
        height = 5,
        units = "in",
        dpi = 300,
        limitsize = TRUE)
      
      ggsave(
        exportFilename_ic_inactive,
        plot = plot_inactive_ic,
        device = "pdf",
        path = exportPath,
        scale = 1,
        width = 5,
        height = 5,
        units = "in",
        dpi = 300,
        limitsize = TRUE)
      
      ggsave(
        exportFilename_kt_active,
        plot = plot_active_kt,
        device = "pdf",
        path = exportPath,
        scale = 1,
        width = 5,
        height = 5,
        units = "in",
        dpi = 300,
        limitsize = TRUE)
      
      ggsave(
        exportFilename_kt_inactive,
        plot = plot_inactive_kt,
        device = "pdf",
        path = exportPath,
        scale = 1,
        width = 5,
        height = 5,
        units = "in",
        dpi = 300,
        limitsize = TRUE)
      
    }
    
    
    all_plots <- list(plot_ic, plot_kt)
    
    if(full==TRUE){
      all_plots <- list(plot_ic, plot_kt, plot_active_ic, plot_inactive_ic, plot_active_kt, plot_inactive_kt)
    }
    
    return(all_plots)
  
   
}