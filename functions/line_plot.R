line_plot <- function(
    SimID, # vector of strings of SimIDs in the form c("SimID_209081149_0__exported","SimID_209081149_0__exported")
    names,
    all_data,
    all_species,
    species_info_list,
    tInit=0, # in s
    tSpan, # in s
    row_1=1,
    row_2=dataDim[1],
    col_1=1,
    col_2=dataDim[2],
    importPath="/Users/sam/Research/JanesLab/vcell_data",
    exportPath="/Users/sam/Research/JanesLab/vcell_plots",
    linewidth=0.7,
    kt_width = 'Metacentric_relaxed', #can be 'Metacentric_Relaxed' or 'Telomeric_Relaxed',etc "relaxed_metacentric"
    KK_dist_relaxed = 0.575,
    KK_dist_tensed = 1.15,
    KT_width= 0.075,
    KT_height = 0.3,
    cohesin_width = 0.1
    ){
  
  
  ## DEFINE REGIONS
  # pixels per µm in x and center column (pixel coordinates)
  # dataDim = 180, 52; 4.5 x 1.3
  pixels_per_um_x <- dataDim[2] / chromWidth # 40
  center_x <- dataDim[2] / 2 # 26
  
  
  # choose relaxed vs tensed by substring "tensed" presence; default to relaxed
  if (grepl("tensed", kt_width, ignore.case = TRUE)) {
    left_near_um <- KK_dist_tensed/2 #0.575
    left_far_um  <- KK_dist_tensed/2 + KT_width #0.65
    right_near_um <- KK_dist_tensed/2 + 0.025 #0.6
    right_far_um  <- KK_dist_tensed/2 + KT_width #0.65
  } else {
    # relaxed (default)
    # left_far_um   <- KK_dist_relaxed/2 + KT_width #0.3625
    left_far_um   <- KK_dist_relaxed/2 + 0.025 #0.3125
    left_near_um  <- KK_dist_relaxed/2 #0.2875
    right_near_um <- KK_dist_relaxed/2 #0.2875
    right_far_um  <- KK_dist_relaxed/2 + KT_width #0.3625
  }
  center_half_um <- cohesin_width/2   # 0.05
  
  # compute pixel indices (use ceiling/floor to get integer pixel indices)
  x1_calc <- floor(center_x - left_far_um   * pixels_per_um_x) #0 - 13
  x2_calc <- ceiling(center_x - left_near_um  * pixels_per_um_x) #3 - 15
  x3_calc <- ceiling(center_x - center_half_um * pixels_per_um_x) + 1 #25
  x4_calc <- ceiling  (center_x + center_half_um * pixels_per_um_x) #28
  x5_calc <- ceiling(center_x + right_near_um * pixels_per_um_x) #50 - 38 
  x6_calc <- floor(center_x + right_far_um  * pixels_per_um_x)  #52 - 40 
  
  # clamp to valid pixel indices
  x1 <- max(1, min(dataDim[2], x1_calc))
  x2 <- max(1, min(dataDim[2], x2_calc))
  x3 <- max(1, min(dataDim[2], x3_calc))
  x4 <- max(1, min(dataDim[2], x4_calc))
  x5 <- max(1, min(dataDim[2], x5_calc))
  x6 <- max(1, min(dataDim[2], x6_calc))
  
  # ensure ordering (if clamping collapsed ranges, force minimal sensible ranges)
  if (x1 >= x2) x2 <- min(dataDim[2], x1 + kt_width*pixels_per_um_x)
  if (x3 > x4)  { # ensure at least one column in center
    x3 <- max(1, x4 - 1)
    x4 <- min(dataDim[2], x3 + 1)
  }
  if (x5 >= x6) x5 <- min(dataDim[2], x6 - kt_width*pixels_per_um_x)
  
  pixels_per_um <- dataDim[1] / chromHeight
  
  if (grepl("metacentric", kt_width, ignore.case = TRUE)) {
    # 0.3 um tall, centered vertically in the matrix
    half_px <- (KT_height / 2) * pixels_per_um #6
    center_px <- dataDim[1] / 2 #72
    y1_new <- ceiling(center_px - half_px) + 1 #66 --> 67
    y2_new <- floor(center_px + half_px) #78
    
    # clamp to valid indices
    y1 <- max(1, y1_new) # 85
    y2 <- min(dataDim[1], y2_new) # 96
    
  } else if (grepl("telocentric", kt_width, ignore.case = TRUE)) {
    # from 0 um (top) to 0.3 um
    y1_new <- 1  # top pixel (0 um)
    y2_new <- ceiling(KT_height * pixels_per_um) 
    
    # clamp
    y1 <- max(1, y1_new) 
    y2 <- min(dataDim[1], max(1, y2_new)) 
    
  }


  
  # misc
  folderVar <- 0
  leader <- 10
  offset <- NULL
  
  
  pattern<-paste("[A-Za-z0-9_]*","exported",sep="")
  cond<-grepl(pattern,SimID)
  print(SimID)
  SimID<-ifelse(cond,SimID,paste(SimID,"exported",sep="_"))
  print(SimID)

  
  region_check <- check_regions(x1,x2, x3,x4, x5,x6, y1,y2, "HASPINi", "NDC80",
                                simid = SimID, indir = paste(importPath,SimID,sep="/"), verbose = TRUE)
  # show plot
  print(region_check$plot)
  
  kt_species <- vector("list", length(all_species))
  ic_species <- vector("list", length(all_species))
  L <- list()
  
  # Initialize empty vectors for each species
  for (i in 1:length(all_species)) {
    kt_species[[i]] <- vector("numeric", ((tSpan/10) + 1))
    ic_species[[i]] <- vector("numeric", ((tSpan/10) + 1))
  }
  
  
  # change working directory
  setwd(importPath)
  
  custom_colors <- c("#e41a1c",
                     "#377eb8", 
                     "#4daf4a", 
                     "#984ea3", 
                     "#a6761d", 
                     "#e6ab02", 
                     "#ff7f00")
  
  # linewidth <- linewidth
  # 
  # all_data <- all_data
  # all_species <- all_species
  
  
  # data processing
  for(z in 0:(tSpan/10)){
    
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
    
    
    
    for(specie in 1:length(all_species)){
      pattern<-paste("[A-Za-z0-9_]*_Slice_XY_\\d",
                     all_species[specie],
                     dataPoint,
                     sep="_")
      
      
      tryCatch(
        
      expr = {
      # read the csv file to a matrix, M
      L[[specie]]<-data.matrix(read.csv(paste(importPath,SimID,grep(pattern, list.files(SimID), value = TRUE),sep="/"),header=FALSE,skip=leader))[row_1:row_2,col_1:col_2]
      },
      error = function(e){
        
        message("Missing species")
        message(all_species[specie])
        print(e)
      },
      finally = {
        
      }
      )
    }
  
    
    # set any negative concentration values to zero
    L<-matrixZero(matrixList=L)
    
    for(q in 1:length(all_species)){

      
      matrix <- L[[q]]
      
      left_kinetochore <-matrix[y1:y2, x1:x2]
      right_kinetochore <-matrix[y1:y2, x5:x6]
      inner_centromere <-matrix[y1:y2, x3:x4]
      
      
      lk <- mean(left_kinetochore)
      rk <- mean(right_kinetochore)
      ic <- mean(inner_centromere)
      kt <- mean(lk, rk)
      
      
      kt_species[[q]][z+1] <- kt
      ic_species[[q]][z+1] <- ic
      
    }
    
  }
  
  for (sp in 1:length(all_data)){
    
    identity = species_info_list[[sp]][1]
    speciesInactive = species_info_list[[sp]][2]
    speciesActive = species_info_list[[sp]][3]
    speciesFull = species_info_list[[sp]][4]
    sums = species_info_list[[sp]][5]
    total = species_info_list[[sp]][6]
    full = species_info_list[[sp]][7]
    collapsible = species_info_list[[sp]][8]
  
  species <- all_data[[sp]]
  
  if(sp == 1){
    pointer <- 0
  }else{
    pointer <- pointer + length(all_data[[sp - 1]])
  }
  
  data_ic <- data.frame(
    Time = 0:(tSpan/10),
    Species = rep(species, each = ((tSpan/10) + 1)),
    IC = unlist(ic_species[(pointer + 1):(pointer + length(species))])
  )
  
  data_kt <- data.frame(
    Time = 0:(tSpan/10),
    Species = rep(species, each = ((tSpan/10) + 1)),
    KT = unlist(kt_species[(pointer + 1):(pointer + length(species))])
  )
  
  
  # Reshape to wide
  data_ic <- reshape(data_ic, idvar = "Time", timevar = "Species", direction = "wide")
  data_kt <- reshape(data_kt, idvar = "Time", timevar = "Species", direction = "wide")
  
  # Rename columns
  colnames(data_ic)[2:ncol(data_ic)] <- gsub("IC.", "", colnames(data_ic)[2:ncol(data_ic)])
  colnames(data_kt)[2:ncol(data_kt)] <- gsub("KT.", "", colnames(data_kt)[2:ncol(data_kt)])
  
  # Get active and inactive df for IC and KT
  data_inactive_ic <- data_ic %>% select("Time", ends_with('i'))
  data_active_ic <- data_ic %>% select(-c(colnames(data_inactive_ic %>% select(-c('Time')))))
  data_inactive_kt <- data_kt %>% select("Time", ends_with('i'))
  data_active_kt <- data_kt %>% select(-c(colnames(data_inactive_kt %>% select(-c('Time')))))
  
  # Get all active and inactive species
  active_species <- colnames(data_active_ic %>% select(-c('Time')))
  inactive_species <- colnames(data_inactive_ic %>% select(-c('Time')))
  
  if(sums==TRUE){
    # Add in Sum Columns
    
    if (ncol(data_inactive_kt) > 2){
      data_inactive_ic$Sum_Inactive <- rowSums(data_inactive_ic[, 2:(length(inactive_species)+1)], na.rm = TRUE)
      data_inactive_kt$Sum_Inactive <- rowSums(data_inactive_kt[, 2:(length(inactive_species)+1)], na.rm = TRUE)
    }
    
    if (ncol(data_inactive_kt) == 2){
      data_inactive_ic$Sum_Inactive <- data_inactive_ic[, 2:(length(inactive_species)+1)]
      data_inactive_kt$Sum_Inactive <- data_inactive_kt[, 2:(length(inactive_species)+1)]
    }
    
    if (ncol(data_inactive_kt) < 2){
      data_inactive_ic$Sum_Inactive <- 0
      data_inactive_kt$Sum_Inactive <- 0
    }
    
    if (ncol(data_active_kt) > 2){
      data_active_ic$Sum_Active <- rowSums(data_active_ic[, 2:(length(active_species)+1)], na.rm = TRUE)
      data_active_kt$Sum_Active <- rowSums(data_active_kt[, 2:(length(active_species)+1)], na.rm = TRUE)
    }
    
    if (ncol(data_active_kt) == 2){
      data_active_ic$Sum_Active <- data_active_ic[, 2:(length(active_species)+1)]
      data_active_kt$Sum_Active <- data_active_kt[, 2:(length(active_species)+1)]
    }
    
    if (ncol(data_active_kt) < 2){
      data_active_ic$Sum_Active <- 0
      data_active_kt$Sum_Active <- 0
    }
    
  }else if(total==TRUE){
    data_ic$Total <- rowSums(data_ic[, 2:(length(species) + 1)], na.rm = TRUE)
    data_kt$Total <- rowSums(data_kt[, 2:(length(species) + 1)], na.rm = TRUE)
  } 
  
  
  
  if(ncol(data_inactive_kt) > 1){
    
    c_vector <- match(gsub(".$", "", species), gsub(".$", "", inactive_species))
    
    for (n in 1:length(c_vector)){
           if (is.na(c_vector[n])){
             c_vector[n] <- max(c_vector, na.rm = T) + 1
             }
      }
    
    
    species_plot_data <- data.frame(Species = species, 
                                    Linetype = ifelse(species %in% active_species, "solid", "dashed"),
                                    Color = ifelse(species %in% inactive_species, custom_colors[match(species, inactive_species)], custom_colors[c_vector])
    )
    
  }else{
    
    c_vector <- match(gsub(".$", "", species), gsub(".$", "", active_species))
    
    for (n in 1:length(c_vector)){
      if (is.na(c_vector[n])){
        c_vector[n] <- max(c_vector, na.rm = T) + 1
      }
    }
  
  if (ncol(data_active_kt) > 1) {
    species_plot_data <- data.frame(Species = species, 
                                    Linetype = ifelse(species %in% active_species, "solid", "dashed"),
                                    Color = ifelse(species %in% active_species, custom_colors[match(species, active_species)], custom_colors[c_vector])
    )
  }
  }
  
  
  
  
  
  
  if(sums==TRUE){
    sum_active_row <- data.frame(Species = "Sum_Active", Linetype = "solid", Color = "black")
    sum_inactive_row <- data.frame(Species = "Sum_Inactive", Linetype = "dashed", Color = "black")
    
    species_plot_data <- rbind(sum_active_row, sum_inactive_row, species_plot_data)
  }
  
  if(total==TRUE){
    sum_row <- data.frame(Species = "Total", Linetype = "solid", Color = "black")
    
    species_plot_data <- rbind(sum_row, species_plot_data)
  }
  
  # Maybe change
  my_theme <- theme(panel.background = element_rect(fill = "transparent"),
                    legend.background = element_rect(fill = "transparent"),
                    axis.line = element_line(color = "black"),
                    axis.text=element_text(size=12),
                    axis.title=element_text(size=16),
                    plot.title=element_text(size=16),
                    legend.text=element_text(size=12))
  
  if(full==TRUE){ 
    
    #                                                             Active IC
    
    active_ic_long <- data_active_ic %>% gather("Species", "Concentration", -Time)
    
    # Plot the data
    plot_active_ic <- ggplot() +
      geom_line(data = active_ic_long, aes(x = Time, y = Concentration, color = Species, linetype = Species), linewidth = linewidth) +
      labs(x = "Time (s)", y = TeX("Concentration ($\\mu$M)")) +
      ggtitle(paste(speciesActive, "concentration at inner centromere")) +
      scale_x_continuous(breaks = seq(0, (tSpan/10), 10), labels = seq(0, tSpan, 100))+
      scale_color_manual(values = setNames(species_plot_data$Color, species_plot_data$Species)) +
      scale_linetype_manual(values = setNames(species_plot_data$Linetype, species_plot_data$Species)) +
      theme(panel.background = element_rect(fill = "transparent"),
            legend.background = element_rect(fill = "transparent"),
            axis.line = element_line(color = "black"),
            axis.text=element_text(size=12),
            axis.title=element_text(size=14))
    
    
    #                                                             Inactive IC
    
    inactive_ic_long <- data_inactive_ic %>% gather("Species", "Concentration", -Time)
    
    # Plot the data
    plot_inactive_ic <- ggplot() +
      geom_line(data = inactive_ic_long, aes(x = Time, y = Concentration, color = Species, linetype = Species), linewidth = linewidth) +
      labs(x = "Time (s)", y = TeX("Concentration ($\\mu$M)")) +
      ggtitle(paste(speciesInactive, "concentration at inner centromere")) +
      scale_x_continuous(breaks = seq(0, (tSpan/10), 10), labels = seq(0, tSpan, 100))+
      scale_color_manual(values = setNames(species_plot_data$Color, species_plot_data$Species)) +
      scale_linetype_manual(values = setNames(species_plot_data$Linetype, species_plot_data$Species)) +
      theme(panel.background = element_rect(fill = "transparent"),
            legend.background = element_rect(fill = "transparent"),
            axis.line = element_line(color = "black"),
            axis.text=element_text(size=12),
            axis.title=element_text(size=14))
    
    #                                                             Active KT
    
    active_kt_long <- data_active_kt %>% gather("Species", "Concentration", -Time)
    
    # Plot the data
    plot_active_kt <- ggplot() +
      geom_line(data = active_kt_long, aes(x = Time, y = Concentration, color = Species, linetype = Species), linewidth = linewidth) +
      labs(x = "Time (s)", y = TeX("Concentration ($\\mu$M)")) +
      ggtitle(paste(speciesActive, "concentration at kinetochore")) +
      scale_x_continuous(breaks = seq(0, (tSpan/10), 10), labels = seq(0, tSpan, 100))+
      scale_color_manual(values = setNames(species_plot_data$Color, species_plot_data$Species)) +
      scale_linetype_manual(values = setNames(species_plot_data$Linetype, species_plot_data$Species)) +
      theme(panel.background = element_rect(fill = "transparent"),
            legend.background = element_rect(fill = "transparent"),
            axis.line = element_line(color = "black"),
            axis.text=element_text(size=12),
            axis.title=element_text(size=14))
    
    #                                                             Inactive KT
    
    inactive_kt_long <- data_inactive_kt %>% gather("Species", "Concentration", -Time)
    
    # Plot the data
    plot_inactive_kt <- ggplot() +
      geom_line(data = inactive_kt_long, aes(x = Time, y = Concentration, color = Species, linetype = Species), linewidth = linewidth) +
      labs(x = "Time (s)", y = TeX("Concentration ($\\mu$M)")) +
      ggtitle(paste(speciesInactive, "concentration at kinetochore")) +
      scale_x_continuous(breaks = seq(0, (tSpan/10), 10), labels = seq(0, tSpan, 100))+
      scale_color_manual(values = setNames(species_plot_data$Color, species_plot_data$Species)) +
      scale_linetype_manual(values = setNames(species_plot_data$Linetype, species_plot_data$Species)) +
      theme(panel.background = element_rect(fill = "transparent"),
            legend.background = element_rect(fill = "transparent"),
            axis.line = element_line(color = "black"),
            axis.text=element_text(size=12),
            axis.title=element_text(size=14))
    
    
    
    
    #                                                             All IC
    
    if(sums == TRUE){
      data_ic$Sum_Active <- data_active_ic$Sum_Active
      data_ic$Sum_Inactive <- data_inactive_ic$Sum_Inactive
    } else if(total == TRUE){
      data_ic$Total <- data_ic$Total
    }
    
    ic_long <- data_ic %>% gather("Species", "Concentration", -Time)
    
    # Plot the data
    plot_ic <- ggplot() +
      geom_line(data = ic_long, aes(x = Time, y = Concentration, color = Species, linetype = Species), linewidth = linewidth) +
      labs(x = "Time (s)", y = TeX("Concentration ($\\mu$M)")) +
      ggtitle(paste(speciesFull, "at inner centromere")) +
      scale_x_continuous(breaks = seq(0, (tSpan/10), 10), labels = seq(0, tSpan, 100))+
      scale_color_manual(values = setNames(species_plot_data$Color, species_plot_data$Species)) +
      scale_linetype_manual(values = setNames(species_plot_data$Linetype, species_plot_data$Species)) +
      theme(panel.background = element_rect(fill = "transparent"),
            legend.background = element_rect(fill = "transparent"),
            axis.line = element_line(color = "black"),
            axis.text=element_text(size=12),
            axis.title=element_text(size=14))
    
    #                                                             All KT
    
    if(sums == TRUE){
      data_kt$Sum_Active <- data_active_kt$Sum_Active
      data_kt$Sum_Inactive <- data_inactive_kt$Sum_Inactive
    }else if(total == TRUE){
      data_kt$Total <- data_kt$Total
    }
    
    
    kt_long <- data_kt %>% gather("Species", "Concentration", -Time)
    
    # Plot the data
    plot_kt <- ggplot() +
      geom_line(data = kt_long, aes(x = Time, y = Concentration, color = Species, linetype = Species), linewidth = linewidth) +
      labs(x = "Time (s)", y = TeX("Concentration ($\\mu$M)")) +
      ggtitle(paste(speciesFull, "at kinetochore")) +
      scale_x_continuous(breaks = seq(0, (tSpan/10), 10), labels = seq(0, tSpan, 100))+
      scale_color_manual(values = setNames(species_plot_data$Color, species_plot_data$Species)) +
      scale_linetype_manual(values = setNames(species_plot_data$Linetype, species_plot_data$Species)) +
      theme(panel.background = element_rect(fill = "transparent"),
            legend.background = element_rect(fill = "transparent"),
            axis.line = element_line(color = "black"),
            axis.text=element_text(size=12),
            axis.title=element_text(size=14))
    
    
    
  }
  
  else if(collapsible==TRUE){
    
    colMax <- function(data) sapply(data, max, na.rm = TRUE)
    
    n_highlight <- 4
    
    
    #                                                             Active IC
    
    if(sums == TRUE){
      filtered_active_ic <- data_active_ic %>% select(-c('Time', 'Sum_Active'))
    }else{
      filtered_active_ic <- data_active_ic %>% select(-c('Time'))
    }
    active_ic <- which(colSums(filtered_active_ic) > 0)
    
    # Find either the top n_highlight columns or the columns that are != 0
    if(length(active_ic) < n_highlight){
      highlight_active_ic <- filtered_active_ic %>% select(all_of(active_ic))
    }else{
      highlight_active_ic <- filtered_active_ic %>% summarise_if(is.numeric, list(~ max(., na.rm=TRUE)))
      highlight_active_ic <- filtered_active_ic %>% select(all_of(order(highlight_active_ic, decreasing = TRUE))[1:n_highlight])
    }
    
    # Add in Time and Sum
    if(sums == TRUE){
      highlight_active_ic <- cbind(data_active_ic$Time, data_active_ic$Sum_Active, highlight_active_ic)
    }else{
      highlight_active_ic <- cbind(data_active_ic$Time, highlight_active_ic)
    }
    
    # Change names
    names(highlight_active_ic)[names(highlight_active_ic) == 'data_active_ic$Time'] <- 'Time'
    if(sums == TRUE){
      names(highlight_active_ic)[names(highlight_active_ic) == 'data_active_ic$Sum_Active'] <- 'Sum_Active'
    }
    bleached_active_ic <- data_active_ic %>% select(-c(names(highlight_active_ic %>% select(-c("Time")))))
    
    if (ncol(bleached_active_ic) < 2){
      bleached_active_ic$Others <- 0
    }
    
    # Convert to long for plotting
    highlight_active_ic_long <- highlight_active_ic %>% gather("Species", "Concentration", -Time)
    bleached_active_ic_long <- bleached_active_ic %>% gather("Species", "Concentration", -Time)
    
    
    # Plot the data
    plot_active_ic <- ggplot() +
      geom_line(data = bleached_active_ic_long, aes(x = Time, y = Concentration, color = Species, group = Species), linetype = "solid", color = "gray", linewidth = linewidth) +
      geom_line(data = highlight_active_ic_long, aes(x = Time, y = Concentration, color = Species, linetype = Species), linewidth = linewidth) +
      labs(x = "Time (s)", y = TeX("Concentration ($\\mu$M)")) +
      ggtitle(paste(speciesActive, "concentration at inner centromere")) +
      scale_x_continuous(breaks = seq(0, (tSpan/10), 10), labels = seq(0, tSpan, 100))+
      scale_color_manual(values = setNames(species_plot_data$Color, species_plot_data$Species)) +
      scale_linetype_manual(values = setNames(species_plot_data$Linetype, species_plot_data$Species)) +
      theme(panel.background = element_rect(fill = "transparent"),
            legend.background = element_rect(fill = "transparent"),
            axis.line = element_line(color = "black"),
            axis.text=element_text(size=12),
            axis.title=element_text(size=14))
    
    
    
    
    #                                                             Inactive IC
    
    
    if(sums == TRUE){
      filtered_inactive_ic <- data_inactive_ic %>% select(-c('Time', 'Sum_Inactive'))
    }else{
      filtered_inactive_ic <- data_inactive_ic %>% select(-c('Time'))
    }
    active_ic <- which(colSums(filtered_inactive_ic) > 0)
    
    # Find either the top n_highlight columns or the columns that are != 0
    if(length(active_ic) < n_highlight){
      highlight_inactive_ic <- filtered_inactive_ic %>% select(all_of(active_ic))
    }else{
      highlight_inactive_ic <- filtered_inactive_ic %>% summarise_if(is.numeric, list(~ max(., na.rm=TRUE)))
      highlight_inactive_ic <- filtered_inactive_ic %>% select(all_of(order(highlight_inactive_ic, decreasing = TRUE))[1:n_highlight])
    }
    
    # Add in Time and Sum
    if(sums == TRUE){
      highlight_inactive_ic <- cbind(data_inactive_ic$Time, data_inactive_ic$Sum_Inactive, highlight_inactive_ic)
    }else{
      highlight_inactive_ic <- cbind(data_inactive_ic$Time, highlight_inactive_ic)
    }
    
    # Change names
    names(highlight_inactive_ic)[names(highlight_inactive_ic) == 'data_inactive_ic$Time'] <- 'Time'
    if(sums == TRUE){
      names(highlight_inactive_ic)[names(highlight_inactive_ic) == 'data_inactive_ic$Sum_Inactive'] <- 'Sum_Inactive'
    }
    bleached_inactive_ic <- data_inactive_ic %>% select(-c(names(highlight_inactive_ic %>% select(-c("Time")))))
    
    if (ncol(bleached_inactive_ic) < 2){
      bleached_inactive_ic$Others <- 0
    }
    
    # Convert to long for plotting
    highlight_inactive_ic_long <- highlight_inactive_ic %>% gather("Species", "Concentration", -Time)
    bleached_inactive_ic_long <- bleached_inactive_ic %>% gather("Species", "Concentration", -Time)
    
    
    # Plot the data
    plot_inactive_ic <- ggplot() +
      geom_line(data = bleached_inactive_ic_long, aes(x = Time, y = Concentration, color = Species, group = Species), linetype = "solid", color = "gray", linewidth = linewidth) +
      geom_line(data = highlight_inactive_ic_long, aes(x = Time, y = Concentration, color = Species, linetype = Species), linewidth = linewidth) +
      labs(x = "Time (s)", y = TeX("Concentration ($\\mu$M)")) +
      ggtitle(paste(speciesActive, "concentration at inner centromere")) +
      scale_x_continuous(breaks = seq(0, (tSpan/10), 10), labels = seq(0, tSpan, 100))+
      scale_color_manual(values = setNames(species_plot_data$Color, species_plot_data$Species)) +
      scale_linetype_manual(values = setNames(species_plot_data$Linetype, species_plot_data$Species)) +
      theme(panel.background = element_rect(fill = "transparent"),
            legend.background = element_rect(fill = "transparent"),
            axis.line = element_line(color = "black"),
            axis.text=element_text(size=12),
            axis.title=element_text(size=14))
    
    
    
    #                                                             Active KT
    
    
    if(sums == TRUE){
      filtered_active_kt <- data_active_kt %>% select(-c('Time', 'Sum_Active'))
    }else{
      filtered_active_kt <- data_active_kt %>% select(-c('Time'))
    }
    active_kt <- which(colSums(filtered_active_kt) > 0)
    
    # Find either the top n_highlight columns or the columns that are != 0
    if(length(active_kt) < n_highlight){
      highlight_active_kt <- filtered_active_kt %>% select(all_of(active_kt))
    }else{
      highlight_active_kt <- filtered_active_kt %>% summarise_if(is.numeric, list(~ max(., na.rm=TRUE)))
      highlight_active_kt <- filtered_active_kt %>% select(all_of(order(highlight_active_kt, decreasing = TRUE))[1:n_highlight])
    }
    
    # Add in Time and Sum
    if(sums == TRUE){
      highlight_active_kt <- cbind(data_active_kt$Time, data_active_kt$Sum_Active, highlight_active_kt)
    }else{
      highlight_active_kt <- cbind(data_active_kt$Time, highlight_active_kt)
    }
    
    # Change names
    names(highlight_active_kt)[names(highlight_active_kt) == 'data_active_kt$Time'] <- 'Time'
    if(sums == TRUE){
      names(highlight_active_kt)[names(highlight_active_kt) == 'data_active_kt$Sum_Active'] <- 'Sum_Active'
    }
    bleached_active_kt <- data_active_kt %>% select(-c(names(highlight_active_kt %>% select(-c("Time")))))
    
    if (ncol(bleached_active_kt) < 2){
      bleached_active_kt$Others <- 0
    }
    
    # Convert to long for plotting
    highlight_active_kt_long <- highlight_active_kt %>% gather("Species", "Concentration", -Time)
    bleached_active_kt_long <- bleached_active_kt %>% gather("Species", "Concentration", -Time)
    
    
    # Plot the data
    plot_active_kt <- ggplot() +
      geom_line(data = bleached_active_kt_long, aes(x = Time, y = Concentration, color = Species, group = Species), linetype = "solid", color = "gray", linewidth = linewidth) +
      geom_line(data = highlight_active_kt_long, aes(x = Time, y = Concentration, color = Species, linetype = Species), linewidth = linewidth) +
      labs(x = "Time (s)", y = TeX("Concentration ($\\mu$M)")) +
      ggtitle(paste(speciesActive, "concentration at inner centromere")) +
      scale_x_continuous(breaks = seq(0, (tSpan/10), 10), labels = seq(0, tSpan, 100))+
      scale_color_manual(values = setNames(species_plot_data$Color, species_plot_data$Species)) +
      scale_linetype_manual(values = setNames(species_plot_data$Linetype, species_plot_data$Species)) +
      theme(panel.background = element_rect(fill = "transparent"),
            legend.background = element_rect(fill = "transparent"),
            axis.line = element_line(color = "black"),
            axis.text=element_text(size=12),
            axis.title=element_text(size=14))
    
    
    
    #                                                             Inactive KT
    
    
    
    if(sums == TRUE){
      filtered_inactive_kt <- data_inactive_kt %>% select(-c('Time', 'Sum_Inactive'))
    }else{
      filtered_inactive_kt <- data_inactive_kt %>% select(-c('Time'))
    }
    active_kt <- which(colSums(filtered_inactive_kt) > 0)
    
    # Find either the top n_highlight columns or the columns that are != 0
    if(length(active_kt) < n_highlight){
      highlight_inactive_kt <- filtered_inactive_kt %>% select(all_of(active_kt))
    }else{
      highlight_inactive_kt <- filtered_inactive_kt %>% summarise_if(is.numeric, list(~ max(., na.rm=TRUE)))
      highlight_inactive_kt <- filtered_inactive_kt %>% select(all_of(order(highlight_inactive_kt, decreasing = TRUE))[1:n_highlight])
    }
    
    # Add in Time and Sum
    if(sums == TRUE){
      highlight_inactive_kt <- cbind(data_inactive_kt$Time, data_inactive_kt$Sum_Inactive, highlight_inactive_kt)
    }else{
      highlight_inactive_kt <- cbind(data_inactive_kt$Time, highlight_inactive_kt)
    }
    
    # Change names
    names(highlight_inactive_kt)[names(highlight_inactive_kt) == 'data_inactive_kt$Time'] <- 'Time'
    if(sums == TRUE){
      names(highlight_inactive_kt)[names(highlight_inactive_kt) == 'data_inactive_kt$Sum_Inactive'] <- 'Sum_Inactive'
    }
    bleached_inactive_kt <- data_inactive_kt %>% select(-c(names(highlight_inactive_kt %>% select(-c("Time")))))
    
    if (ncol(bleached_inactive_kt) < 2){
      bleached_inactive_kt$Others <- 0
    }
    
    # Convert to long for plotting
    highlight_inactive_kt_long <- highlight_inactive_kt %>% gather("Species", "Concentration", -Time)
    bleached_inactive_kt_long <- bleached_inactive_kt %>% gather("Species", "Concentration", -Time)
    
    
    # Plot the data
    plot_inactive_kt <- ggplot() +
      geom_line(data = bleached_inactive_kt_long, aes(x = Time, y = Concentration, color = Species, group = Species), linetype = "solid", color = "gray", linewidth = linewidth) +
      geom_line(data = highlight_inactive_kt_long, aes(x = Time, y = Concentration, color = Species, linetype = Species), linewidth = linewidth) +
      labs(x = "Time (s)", y = TeX("Concentration ($\\mu$M)")) +
      ggtitle(paste(speciesActive, "concentration at inner centromere")) +
      scale_x_continuous(breaks = seq(0, (tSpan/10), 10), labels = seq(0, tSpan, 100))+
      scale_color_manual(values = setNames(species_plot_data$Color, species_plot_data$Species)) +
      scale_linetype_manual(values = setNames(species_plot_data$Linetype, species_plot_data$Species)) +
      theme(panel.background = element_rect(fill = "transparent"),
            legend.background = element_rect(fill = "transparent"),
            axis.line = element_line(color = "black"),
            axis.text=element_text(size=12),
            axis.title=element_text(size=14))
    
    
    #                                                             All IC
    
    
    filtered_ic <- data_ic %>% select(-c('Time'))
    ic <- which(colSums(filtered_ic) > 0)
    
    # Find either the top n_highlight columns or the columns that are != 0
    if(length(ic) < n_highlight){
      highlight_ic <- filtered_ic %>% select(all_of(ic))
    }else{
      highlight_ic <- filtered_ic %>% summarise_if(is.numeric, list(~ max(., na.rm=TRUE)))
      highlight_ic <- filtered_ic %>% select(all_of(order(highlight_ic, decreasing = TRUE))[1:n_highlight])
    }
    
    # Add in Time and Sum
    if(sums == TRUE){
      highlight_ic <- cbind(data_ic$Time, data_active_ic$Sum_Active, data_inactive_ic$Sum_Inactive, highlight_ic)
    }else if(total == TRUE){
      highlight_ic <- cbind(data_ic$Time, data_ic$Total, highlight_ic)
    }
    else{
      highlight_ic <- cbind(data_ic$Time, highlight_ic)
    }
    
    # Change names
    names(highlight_ic)[names(highlight_ic) == 'data_ic$Time'] <- 'Time'
    if(sums == TRUE){
      names(highlight_ic)[names(highlight_ic) == 'data_active_ic$Sum_Active'] <- 'Sum_Active'
      names(highlight_ic)[names(highlight_ic) == 'data_inactive_ic$Sum_Inactive'] <- 'Sum_Inactive'
      bleached_ic <- data_ic %>% select(-c(names(highlight_ic %>% select(-c("Time", "Sum_Active", "Sum_Inactive")))))
    }else{
      bleached_ic <- data_ic %>% select(-c(names(highlight_ic %>% select(-c("Time")))))
    }
    
    if (ncol(bleached_ic) < 2){
      bleached_ic$Others <- 0
    }
    
    # Convert to long for plotting
    highlight_ic_long <- highlight_ic %>% gather("Species", "Concentration", -Time)
    bleached_ic_long <- bleached_ic %>% gather("Species", "Concentration", -Time)
    
    
    # Plot the data
    plot_ic <- ggplot() +
      geom_line(data = bleached_ic_long, aes(x = Time, y = Concentration, color = Species, group = Species), linetype = "solid", color = "gray", linewidth = linewidth) +
      geom_line(data = highlight_ic_long, aes(x = Time, y = Concentration, color = Species, linetype = Species), linewidth = linewidth) +
      labs(x = "Time (s)", y = TeX("Concentration ($\\mu$M)")) +
      ggtitle(paste(speciesFull, "at inner centromere")) +
      scale_x_continuous(breaks = seq(0, (tSpan/10), 10), labels = seq(0, tSpan, 100))+
      scale_color_manual(values = setNames(species_plot_data$Color, species_plot_data$Species)) +
      scale_linetype_manual(values = setNames(species_plot_data$Linetype, species_plot_data$Species)) +
      theme(panel.background = element_rect(fill = "transparent"),
            legend.background = element_rect(fill = "transparent"),
            axis.line = element_line(color = "black"),
            axis.text=element_text(size=12),
            axis.title=element_text(size=14))
    
    
    #                                                             All KT
    
    
    filtered_kt <- data_kt %>% select(-c('Time'))
    kt <- which(colSums(filtered_kt) > 0)
    
    # Find either the top n_highlight columns or the columns that are != 0
    if(length(kt) < n_highlight){
      highlight_kt <- filtered_kt %>% select(all_of(kt))
    }else{
      highlight_kt <- filtered_kt %>% summarise_if(is.numeric, list(~ max(., na.rm=TRUE)))
      highlight_kt <- filtered_kt %>% select(all_of(order(highlight_kt, decreasing = TRUE))[1:n_highlight])
    }
    
    # Add in Time and Sum
    if(sums == TRUE){
      highlight_kt <- cbind(data_kt$Time, data_active_kt$Sum_Active, data_inactive_kt$Sum_Inactive, highlight_kt)
    }else if(total == TRUE){
      highlight_kt <- cbind(data_kt$Time, data_kt$Total, highlight_kt)
    }else{
      highlight_kt <- cbind(data_kt$Time, highlight_kt)
    }
    
    # Change names
    names(highlight_kt)[names(highlight_kt) == 'data_kt$Time'] <- 'Time'
    if(sums == TRUE){
      names(highlight_kt)[names(highlight_kt) == 'data_active_kt$Sum_Active'] <- 'Sum_Active'
      names(highlight_kt)[names(highlight_kt) == 'data_inactive_kt$Sum_Inactive'] <- 'Sum_Inactive'
      bleached_kt <- data_kt %>% select(-c(names(highlight_kt %>% select(-c("Time", "Sum_Active", "Sum_Inactive")))))
    }else{
      bleached_kt <- data_kt %>% select(-c(names(highlight_kt %>% select(-c("Time")))))
    }
    
    if (ncol(bleached_kt) < 2){
      bleached_kt$Others <- 0
    }
    
    # Convert to long for plotting
    highlight_kt_long <- highlight_kt %>% gather("Species", "Concentration", -Time)
    bleached_kt_long <- bleached_kt %>% gather("Species", "Concentration", -Time)
    
    
    # Plot the data
    plot_kt <- ggplot() +
      geom_line(data = bleached_kt_long, aes(x = Time, y = Concentration, color = Species, group = Species), linetype = "solid", color = "gray", linewidth = linewidth) +
      geom_line(data = highlight_kt_long, aes(x = Time, y = Concentration, color = Species, linetype = Species), linewidth = linewidth) +
      labs(x = "Time (s)", y = TeX("Concentration ($\\mu$M)")) +
      ggtitle(paste(speciesFull, "at kinetochore")) +
      scale_x_continuous(breaks = seq(0, (tSpan/10), 10), labels = seq(0, tSpan, 100))+
      scale_color_manual(values = setNames(species_plot_data$Color, species_plot_data$Species)) +
      scale_linetype_manual(values = setNames(species_plot_data$Linetype, species_plot_data$Species)) +
      theme(panel.background = element_rect(fill = "transparent"),
            legend.background = element_rect(fill = "transparent"),
            axis.line = element_line(color = "black"),
            axis.text=element_text(size=12),
            axis.title=element_text(size=14))
    
    
    
  }
  
  else{
    
    #                                                             All IC
    if(sums == TRUE){
      
      data_ic$Sum_Active <- data_active_ic$Sum_Active
      data_ic$Sum_Inactive <- data_inactive_ic$Sum_Inactive
    }else if(total == TRUE){
      data_ic$Total <- data_ic$Total
    }
    
    ic_long <- data_ic %>% gather("Species", "Concentration", -Time)
    
    # Plot the data
    plot_ic <- ggplot() +
      geom_line(data = ic_long, aes(x = Time, y = Concentration, color = Species, linetype = Species), linewidth = linewidth) +
      labs(x = "Time (s)", y = TeX("Concentration ($\\mu$M)")) +
      ggtitle(paste(speciesFull, "at inner centromere")) +
      scale_x_continuous(breaks = seq(0, (tSpan/10), 10), labels = seq(0, tSpan, 100))+
      scale_color_manual(values = setNames(species_plot_data$Color, species_plot_data$Species)) +
      scale_linetype_manual(values = setNames(species_plot_data$Linetype, species_plot_data$Species)) +
      theme(panel.background = element_rect(fill = "transparent"),
            legend.background = element_rect(fill = "transparent"),
            axis.line = element_line(color = "black"),
            axis.text=element_text(size=12),
            axis.title=element_text(size=14))
    
    #                                                             All KT
    if(sums == TRUE){
      data_kt$Sum_Active <- data_active_kt$Sum_Active
      data_kt$Sum_Inactive <- data_inactive_kt$Sum_Inactive
    }else if(total == TRUE){
      data_kt$Total <- data_kt$Total
    }
    
    kt_long <- data_kt %>% gather("Species", "Concentration", -Time)
    
    # Plot the data
    plot_kt <- ggplot() +
      geom_line(data = kt_long, aes(x = Time, y = Concentration, color = Species, linetype = Species), linewidth = linewidth) +
      labs(x = "Time (s)", y = TeX("Concentration ($\\mu$M)")) +
      ggtitle(paste(speciesFull, "at kinetochore")) +
      scale_x_continuous(breaks = seq(0, (tSpan/10), 10), labels = seq(0, tSpan, 100))+
      scale_color_manual(values = setNames(species_plot_data$Color, species_plot_data$Species)) +
      scale_linetype_manual(values = setNames(species_plot_data$Linetype, species_plot_data$Species)) +
      theme(panel.background = element_rect(fill = "transparent"),
            legend.background = element_rect(fill = "transparent"),
            axis.line = element_line(color = "black"),
            axis.text=element_text(size=12),
            axis.title=element_text(size=14))
    
  }
  
  
  plots <- grid.arrange(plot_ic, plot_kt, ncol=2)

  
  exportF <- paste(identity, "plot", sep="_")
  exportFilename <- paste(exportF,"pdf",sep=".")
  
  
  
  ggsave(
    exportFilename,
    plot = plots,
    device = "pdf",
    path = exportPath,
    scale = 1,
    width = 12,
    height = 7,
    units = "in",
    dpi = 300,
    limitsize = TRUE)
  
    exportP <- paste(exportPath, exportFilename, sep="/")
    setwd(exportPath)
    # pdf_convert(exportP, format = "png")
    
    dir.create(file.path(exportPath, 'data'))
    write.csv(data_active_ic, paste(exportPath,paste0("data/data_active_ic_",identity,".csv"),sep="/"), row.names = FALSE)
    write.csv(data_inactive_ic, paste(exportPath,paste0("data/data_inactive_ic_",identity,".csv"),sep="/"), row.names = FALSE)
    write.csv(data_active_kt, paste(exportPath,paste0("data/data_active_kt_",identity,".csv"),sep="/"), row.names = FALSE)
    write.csv(data_inactive_kt, paste(exportPath,paste0("data/data_inactive_kt_",identity,".csv"),sep="/"), row.names = FALSE)
    write.csv(data_ic, paste(exportPath,paste0("data/data_ic_",identity,".csv"),sep="/"), row.names = FALSE)
    write.csv(data_kt, paste(exportPath,paste0("data/data_kt_",identity,".csv"),sep="/"), row.names = FALSE)
    
    
    setwd(importPath)
    
    
  
  
  
  }
  
  
  
}

