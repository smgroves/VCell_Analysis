heatmap_movie <- function(
    SimID,
    names = SimID,
    species,
    speciesName,
    cutoff_color = NULL,
    tInit = 0,
    tSpan,
    tInterval,
    frame_interval = 1,          # NEW: take every nth frame (default 1)
    movie_format = c("gif","mp4"), # choose output format, gif by default
    # dataDim = c(149,68),
    row_1 = 1,
    row_2 = dataDim[1],
    col_1 = 1,
    col_2 = dataDim[2],
    xdiv = 3,
    ydiv = 3,
    fps_chosen = 5, #default frames per second
    importPath = "/Users/catalinaalvarez/Google Drive/My Drive/UVA/Research/JanesLab/CPC_project/Manuscript/Paper_simulations/vcell_data",
    exportPath = "/Users/catalinaalvarez/Desktop/"
) {

  ## Required packages
  if (!requireNamespace("ggplot2", quietly = TRUE)) stop("ggplot2 required")
  if (!requireNamespace("gganimate", quietly = TRUE)) stop("gganimate required")
  if (!requireNamespace("gifski", quietly = TRUE) && !requireNamespace("av", quietly = TRUE)) {
    stop("Either gifski (for GIF) or av (for MP4) is required by gganimate")
  }
  library(ggplot2)
  library(gganimate)

  movie_format <- match.arg(movie_format)

  # --- keep most of your original preprocessing logic unchanged ---
  pattern <- paste("[A-Za-z0-9_]*","exported",sep="")
  cond <- grepl(pattern,SimID)
  SimID <- ifelse(cond,SimID,paste(SimID,"exported",sep="_"))

  clamped <- FALSE
  clampConc <- 0
  criticalConc <- 0

  n_SimID <- length(SimID)
  n_t <- (tSpan - tInit) / tInterval + 1
  trange <- seq(from = tInit / tInterval, to = tSpan / tInterval, length.out = n_t)

  Clist <- list()
  count <- 1

  setwd(importPath)

  for (s in 1:n_SimID) {
    dataFolder <- SimID[s]

    row_diff <- row_2
    col_diff <- col_2

    xAxis <- seq(0, chromWidth, length = col_diff)
    yAxis <- seq(0, chromHeight, length = row_diff)

    for (z in 1:length(trange)) {
      t <- trange[z]
      dataPoint <- as.character(round(x=t, digits=0))
      if (nchar(dataPoint) == 1) {
        dataPoint <- paste("000",dataPoint,sep="")
      } else if (nchar(dataPoint) == 2) {
        dataPoint <- paste("00",dataPoint,sep="")
      } else if (nchar(dataPoint) == 3) {
        dataPoint <- paste("0",dataPoint,sep="")
      }

      if (length(dataFolder) > 1) {
        stop("ERROR: This function does not have the capability to read data in different folders yet.")
      } else {
        if (clamped == FALSE) {
          # read species matrices into L list (kept minimal)
          L <- list()
          for (i in 1:length(species)) {
            pattern_file <- paste("[A-Za-z0-9_]*_Slice_XY_\\d",
                                  species[i],
                                  dataPoint,
                                  sep="_")
            file_match <- grep(pattern_file, list.files(dataFolder), value = TRUE)
            if (length(file_match) == 0) {
              stop(paste("No file matching", pattern_file, "in", dataFolder))
            }
            L[[i]] <- data.matrix(read.csv(paste(importPath, dataFolder, file_match, sep="/"),
                                           header = FALSE, skip = 10))[row_1:row_2, col_1:col_2]
          }
          # replace negatives with zero 
          # If matrixZero() exists in your environment, keep it. Otherwise do simple clamp:
          if (exists("matrixZero")) {
            L <- matrixZero(matrixList = L)
          } else {
            L <- lapply(L, function(mat) { mat[mat < 0] <- 0; mat })
          }
        }

        if (length(species) > 1) {
          if (speciesName == "inactive CPC") {
            M <- Reduce(`+`, L) + clampConc
          } else {
            M <- Reduce(`+`, L)
          }
        } else if (clamped == TRUE) {
          M <- matrix(0, nrow = dataDim[1], ncol = dataDim[2]) + clampConc
        } else {
          M <- L[[1]] + clampConc
        }

        M_transform <- as.vector(t(M))
        Clist[[count]] <- M_transform
        count <- count + 1
      }
    }
  }

  # build time and ID vectors for the full stacked data
  t_short <- seq(from = tInit, to = tSpan, length.out = n_t)
  t_labs <- as.character(t_short)
  t_long <- as.character(rep(t_short, each = dataDim[1] * dataDim[2], times = n_SimID))

  ID_short <- seq(from = 1, to = n_SimID)
  ID_labs <- names
  names(ID_labs) <- as.character(ID_short)
  ID_long <- as.character(rep(ID_short, each = dataDim[1] * dataDim[2] * n_t))

  X <- rep(seq(0, chromWidth, length = col_diff), times = row_diff)
  # X replicated to full length:
  X_all <- rep(X, times = n_SimID * n_t)
  Y <- rep(seq(0, chromHeight, length = row_diff), each = col_diff)
  Y_all <- rep(Y, times = n_SimID * n_t)

  C <- as.vector(sapply(Clist, as.vector))
  dataMat <- data.frame(X = X_all, Y = Y_all, C = C, ID = ID_long, t = t_long, stringsAsFactors = FALSE)

  # select frames according to frame_interval
  # unique times in order
  unique_times <- (unique(dataMat$t))
  chosen_times <- unique_times[seq(1, length(unique_times), by = frame_interval)]
  dataMat_sub <- dataMat[dataMat$t %in% chosen_times, ]

  # plotting constants
  #define our own maxcolor
  if (is.null(cutoff_color)){
    if(max(C)>=10){
      maxColor=10*ceiling(max(C)/10)
    }else{
      maxColor=ceiling(max(C))}
  }else{
    maxColor<-cutoff_color}
  
  xbreaks <- seq(0, chromWidth, chromWidth / (xdiv - 1))
  xlabs <- c(as.character(round(0)), as.character(round(xbreaks[2:length(xbreaks)], digits = 1)))
  ybreaks <- seq(0, chromHeight, chromHeight / (ydiv - 1))
  ylabs <- c(as.character(round(0)), as.character(round(ybreaks[2:length(ybreaks)], digits = 2)))

  legend_name <- paste("[", speciesName, "] (µM)", sep = "")
  labelString<-c("0",as.character(maxColor/4),as.character(maxColor/2),as.character(3*maxColor/4),as.character(maxColor))
  
  axis_font_size <- 12 
  axis_title_font_size <- 14 
  legend_font_size <- 12 
  legend_title_font_size <- 12
  stripx_font_size <- 12 
  stripy_font_size <- 12 

  # ggplot: SimIDs as columns, time will be animated
  p <- ggplot(data = dataMat_sub, aes(x = X, y = Y, fill = C)) +
    geom_tile() +
    facet_grid(. ~ factor(ID, levels = sort(unique(as.numeric(ID))), labels = ID_labs), switch = "y") +
    coord_fixed(ratio = 1) +
    # scale_fill_gradientn(name = legend_name, limits = c(0, maxColor),
    #                      breaks = c(0, round(maxColor / 2, digits = 0), maxColor),
    #                      labels = labelString,
    #                      colors = c("black","blueviolet","blue","cyan","green","yellow","orange","red"),
    #                      na.value = "grey100") +
    # scale_fill_gradientn(colours = cet_pal(5, name = "r3"))+
    scale_fill_viridis_c(name = legend_name,limits = c(0, maxColor), breaks = c(0, round(maxColor/4, digits=2),round(maxColor/2, digits=2), round(3*maxColor/4, digits=2),maxColor),labels = labelString,na.value = "grey100")+
    scale_x_continuous(breaks = xbreaks, labels = xlabs) +
    scale_y_continuous(breaks = ybreaks, labels = ylabs, position = "right") +
    xlab("X (µm)") + ylab("Y (µm)") +
    theme_void() +
    theme(axis.text = element_text(size = axis_font_size),
          axis.title = element_text(size = axis_title_font_size),
          axis.text.x = element_text(angle = 45),
          axis.title.x = element_text(vjust = -0.1, face = "bold"),
          axis.title.y = element_text(vjust = 0.5, hjust = 0.4, angle = 90, face = "bold"),
          legend.key.size = unit(0.4, 'cm'),
          legend.title = element_text(size = legend_title_font_size, vjust = 1, hjust = 1),
          legend.position = "bottom",
          legend.direction = "horizontal",
          legend.text = element_text(size = legend_font_size, angle = 45),
          strip.text.x = element_text(size = stripx_font_size),
          strip.text.y = element_text(size = stripy_font_size, vjust = 0.5)
    ) +
    labs(title = "t (s) = {current_frame}")

  # gganimate: animate by time; current_frame will show the current time label (we use chosen_times as frames)
  anim <- p + transition_manual(frames = factor(dataMat_sub$t, levels = chosen_times)) +
    ease_aes('linear')

  # output filename
  exportFilename_base <- paste0(gsub("[[:space:]]+", "_", speciesName), "_heatmap")
  if (movie_format == "gif") {
    out_file <- file.path(exportPath, paste0(exportFilename_base, ".gif"))
    # use gifski renderer
    animate(anim, renderer = gifski_renderer(out_file), nframes = length(chosen_times), fps = max(fps_chosen, 1 / max(1, frame_interval)), width = 800, height = 800)
  } else {
    out_file <- file.path(exportPath, paste0(exportFilename_base, ".mp4"))
    # use av renderer
    animate(anim, renderer = av_renderer(out_file), nframes = length(chosen_times), fps = max(fps_chosen, 1 / max(1, frame_interval)), width = 800, height = 800)
  }

  message("Saved animation to: ", out_file)
  return(invisible(list(data = dataMat_sub, movie = out_file)))
}
