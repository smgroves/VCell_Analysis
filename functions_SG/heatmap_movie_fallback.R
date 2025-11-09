# fallback animation builder: saves PNG frames and builds GIF/MP4 without gganimate
heatmap_movie_fallback <- function(
  SimID,
  names = SimID,
  species,
  speciesName,
  cutoff_color = NULL,
  tInit = 0,
  tSpan,
  tInterval,
  desiredInterval = NULL,   # if NULL -> use tInterval spacing; otherwise frames spaced by desiredInterval (classic behavior)
  frame_interval = 1,       # take every nth frame after spacing selection
  chromWidth = 1.6,
  chromHeight = 3.5,
  dataDim = c(128,64),
  row_1 = 1, row_2 = dataDim[1],
  col_1 = 1, col_2 = dataDim[2],
  xdiv = 3,
  ydiv = 3,
  importPath = ".",
  exportPath = ".",
  export_basename = NULL,   # if NULL defaults to speciesName_heatmap
  cleanup_frames = TRUE,
  png_dpi = 150,
  png_width = 6, png_height = 6
) {
  # ---- dependencies check ----
  if(!requireNamespace("ggplot2", quietly = TRUE)) stop("Please install ggplot2")
  if(!requireNamespace("png", quietly = TRUE)) install.packages("png")
  if(!requireNamespace("grid", quietly = TRUE)) install.packages("grid")
  # renderer preference: gifski then av
  have_gifski <- requireNamespace("gifski", quietly = TRUE)
  have_av     <- requireNamespace("av", quietly = TRUE)
  if(!have_gifski && !have_av) {
    stop("Please install at least one renderer: gifski (for GIF) or av (for MP4).",
         " Install with: install.packages('gifski') or install.packages('av')")
  }

  library(ggplot2)

  # ---- prepare time indices ----
  # If desiredInterval provided then we pick timepoints spaced by desiredInterval (physical units).
  # Otherwise use solver spacing tInterval.
  if (!is.null(desiredInterval)) {
    # compute times (physical units)
    t_seq <- seq(from = tInit, to = tSpan, by = desiredInterval)
  } else {
    t_seq <- seq(from = tInit, to = tSpan, by = tInterval)
  }
  if (length(t_seq) < 1) stop("No timepoints selected; check tInit/tSpan/tInterval/desiredInterval")

  # convert times to the file-index space used in your files:
  # Your original code used integer indices stored as t / tInterval (and padded)
  trange_idx <- round(t_seq / tInterval)  # indices
  # produce file-dataPoint strings like "0000","0050" etc as before
  format_index <- function(idx) {
    s <- as.character(round(x = idx, digits = 0))
    # pad to at least 4 digits like your code did:
    sapply(s, function(ss) {
      if(nchar(ss) == 1) paste0("000", ss)
      else if(nchar(ss) == 2) paste0("00", ss)
      else if(nchar(ss) == 3) paste0("0", ss)
      else ss
    })
  }
  dataPoints <- format_index(trange_idx)

  # ---- read data and stack into data.frame ----
  # We'll loop by SimID and time and build a data.frame for each frame when plotting to reduce memory spike.
  # But to keep it simple we will create frames in order, each frame composed from all SimIDs side-by-side.

  # helper for X,Y coordinates
  row_diff <- row_2
  col_diff <- col_2
  xAxis <- seq(0, chromWidth, length = col_diff)
  yAxis <- seq(0, chromHeight, length = row_diff)
  Xcoords <- rep(xAxis, times = row_diff)
  Ycoords <- rep(yAxis, each = col_diff)

  # set export names
  if (is.null(export_basename)) export_basename <- paste0(gsub("[[:space:]]+","_",speciesName), "_heatmap")
  frames_dir <- file.path(exportPath, paste0(export_basename, "_frames"))
  dir.create(frames_dir, showWarnings = FALSE, recursive = TRUE)

  png_files <- character(0)
  frame_count <- 0

  for (i_dp in seq_along(dataPoints)) {
    dp <- dataPoints[i_dp]
    # apply thinning by frame_interval: we only write the frame if index mod frame_interval == 1
    if (((i_dp - 1) %% frame_interval) != 0) next

    # build combined data for all SimIDs for this dataPoint
    combined_df <- NULL
    for (s in seq_along(SimID)) {
      dataFolder <- SimID[s]
      if (length(dataFolder) > 1) stop("Function doesn't support multiple folders per SimID")
      # read species files and sum
      L <- list()
      for (sp in seq_along(species)) {
        pattern_file <- paste0("[A-Za-z0-9_]*_Slice_XY_\\d_", species[sp], "_", dp)
        files_found <- grep(pattern_file, list.files(path = file.path(importPath, dataFolder)), value = TRUE)
        if (length(files_found) == 0) {
          stop(paste0("No file for pattern: ", pattern_file, " in folder: ", file.path(importPath, dataFolder)))
        }
        # use first match
        file_path <- file.path(importPath, dataFolder, files_found[1])
        mat <- as.matrix(read.csv(file_path, header = FALSE, skip = 10))
        mat <- mat[row_1:row_2, col_1:col_2]
        mat[mat < 0] <- 0
        L[[sp]] <- mat
      }
      if (length(L) > 1) {
        M <- Reduce(`+`, L)
      } else {
        M <- L[[1]]
      }
      # convert to vector in plotting order (same as your original t(M) and as.vector)
      M_vec <- as.vector(t(M))
      df <- data.frame(X = Xcoords, Y = Ycoords, C = M_vec, Sim = names[s], stringsAsFactors = FALSE)
      # position Sim columns side-by-side for faceting by Sim
      df$SimID <- factor(df$Sim, levels = names)
      if (is.null(combined_df)) combined_df <- df else combined_df <- rbind(combined_df, df)
    }

    # create ggplot for this frame (SimIDs faceted horizontally)
    maxColor <- ifelse(is.null(cutoff_color), max(combined_df$C, na.rm = TRUE), cutoff_color)
    xbreaks <- seq(0, chromWidth, chromWidth / (xdiv - 1))
    xlabs <- c(as.character(round(0)), as.character(round(xbreaks[2:length(xbreaks)], digits = 1)))
    ybreaks <- seq(0, chromHeight, chromHeight / (ydiv - 1))
    ylabs <- c(as.character(round(0)), as.character(round(ybreaks[2:length(ybreaks)], digits = 2)))

    p_frame <- ggplot(combined_df, aes(x = X, y = Y, fill = C)) +
      geom_tile() +
      facet_grid(. ~ SimID, labeller = label_value) +
      coord_fixed(ratio = 1) +
      scale_fill_gradientn(name = paste0("[", speciesName, "] (µM)"),
                           limits = c(0, maxColor),
                           colours = c("black","blueviolet","blue","cyan","green","yellow","orange","red"),
                           na.value = "grey100") +
      scale_x_continuous(breaks = xbreaks, labels = xlabs) +
      scale_y_continuous(breaks = ybreaks, labels = ylabs, position = "right") +
      theme_minimal() +
      labs(title = paste0("t (s) = ", t_seq[i_dp]), x = "X (µm)", y = "Y (µm)")

    # write PNG
    frame_count <- frame_count + 1
    png_name <- file.path(frames_dir, sprintf("frame_%04d.png", frame_count))
    ggsave(filename = png_name, plot = p_frame, dpi = png_dpi, width = png_width, height = png_height, units = "in")
    png_files <- c(png_files, png_name)
    message("Wrote frame: ", png_name)
  }

  if (length(png_files) == 0) {
    stop("No frames were generated. Check desiredInterval/frame_interval settings.")
  }

  # ---- build GIF or MP4 ----
  gif_path <- file.path(exportPath, paste0(export_basename, ".gif"))
  mp4_path <- file.path(exportPath, paste0(export_basename, ".mp4"))
  out_path <- NULL

  if (have_gifski) {
    message("Building GIF with gifski...")
    gifski::gifski(png_files, gif_file = gif_path, width = png_width * 150, height = png_height * 150, delay = 0.2)
    out_path <- gif_path
    message("Saved GIF to: ", out_path)
  } else if (have_av) {
    message("Building MP4 with av...")
    av::av_encode_video(png_files, output = mp4_path, framerate = 5)
    out_path <- mp4_path
    message("Saved MP4 to: ", out_path)
  }

  if (cleanup_frames) {
    message("Cleaning up frames directory: ", frames_dir)
    unlink(frames_dir, recursive = TRUE, force = TRUE)
  }

  return(invisible(list(frames = png_files, movie = out_path)))
}
