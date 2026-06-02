# requires ggplot2
if(!requireNamespace("ggplot2", quietly = TRUE)) install.packages("ggplot2")
library(ggplot2)

# check_regions function
check_regions <- function(x1, x2, x3, x4, x5, x6,
                          y1, y2,
                          channelA, channelB,
                          simid = NULL,                 # optional SimID string (e.g. "299564396_0")
                          slice = "Slice_XY_0",          # optional, default to the pattern you used
                          indir = "",
                          verbose = TRUE) {
  
  # helper to locate file for a channel
  find_file_for_channel <- function(channel) {
    if (!is.null(simid)) {
      # try exact filename pattern used in your examples
      # fname <- sprintf("%s/%s__%s_%s_0000.csv", indir,simid, slice, channel)
      
      pattern<-paste("[A-Za-z0-9_]*_Slice_XY_\\d",
                     channel,
                     "0000",
                     sep="_")
      # read the csv file to a matrix, M
      fname = paste(indir,grep(pattern, list.files(simid), value = TRUE),sep="/")
                                   
      print(fname)
      if (file.exists(fname)) return(fname)
      # try variant without exactly matching pattern just in case
      fname2 <- sprintf("*%s*%s*.csv", simid, channel)
      candidates <- Sys.glob(fname2)
      if (length(candidates) > 0) return(candidates[1])
      stop("No file found for simid ", simid, " and channel ", channel)
    } else {
      # search the working directory for a file containing the channel name
      candidates <- Sys.glob(paste0("*", channel, "*.csv"))
      if (length(candidates) == 0) stop("No files found matching channel: ", channel)
      if (verbose && length(candidates) > 1) message("Multiple matches for ", channel, " — using first: ", candidates[1])
      return(candidates[1])
    }
  }
  
  fA <- find_file_for_channel(channelA)
  fB <- find_file_for_channel(channelB)
  if (verbose) message("Using files:\n  A: ", fA, "\n  B: ", fB)
  leader <- 10
  
  # read matrices (assume no header; numeric)
  matA <- as.matrix(read.csv(fA, header = FALSE,skip=leader))
  matB <- as.matrix(read.csv(fB, header = FALSE,skip=leader))
  
  # ensure numeric (in case factors), and same dims
  matA <- apply(matA, c(1,2), as.numeric)
  matB <- apply(matB, c(1,2), as.numeric)
  
  if (!all(dim(matA) == dim(matB))) stop("Channel matrices have different dimensions: ",
                                         paste(dim(matA), collapse = "x"), " vs ", paste(dim(matB), collapse = "x"))
  
  nrowM <- nrow(matA); ncolM <- ncol(matA)
  
  # sum and binarize (>0 -> 1)
  summed <- matA + matB
  bin <- (summed > 0) * 1L
  
  # Convert to data.frame for ggplot; flip Y so that row 1 is plotted at top
  df <- expand.grid(col = seq_len(ncolM), row = seq_len(nrowM))
  # row in df corresponds to matrix row; to plot with origin top-left we invert y:
  df$val <- as.vector(bin)                         # column-major order matches expand.grid?
  # expand.grid by default: col in slowest? safer to build directly:
  # We'll create df explicitly to avoid ordering mistakes:
  df <- data.frame(
    x = rep(seq_len(ncolM), each = nrowM),
    y = rep(seq_len(nrowM), times = ncolM),
    val = as.vector(bin)
  )
  # convert matrix row->plot y so that image has row 1 at top:
  df$y_plot <- nrowM - df$y + 1
  
  # rectangles: convert matrix indices to plotting coordinates.
  # Each pixel at y_plot = nrowM - row + 1 occupies the area
  # [y_plot - 0.5, y_plot + 0.5], so the region spanning rows y1..y2 occupies
  # y_plot values (nrowM-y2+1) through (nrowM-y1+1), giving:
  #   ymin = (nrowM - y2 + 1) - 0.5 = nrowM - y2 + 0.5
  #   ymax = (nrowM - y1 + 1) + 0.5 = nrowM - y1 + 1.5
  rects <- data.frame(
    xmin = c(x1, x3, x5) - 0.5,
    xmax = c(x2, x4, x6) + 0.5,
    ymin = nrowM - c(y2, y2, y2) + 0.5,
    ymax = nrowM - c(y1, y1, y1) + 1.5,   # was + 0.5; +1.5 includes the top pixel row
    region = c("Left_KT", "Inner_Centromere", "Right_KT")
  )
  
  # basic ggplot heatmap
  p <- ggplot(df, aes(x = x, y = y_plot, fill = factor(val))) +
    geom_raster() +
    scale_fill_manual(values = c("0" = "white", "1" = "darkgrey"),
                      name = "presence", labels = c("0","1")) +
    coord_fixed(expand = FALSE) +
    theme_minimal() +
    theme(axis.title = element_blank(),
          axis.text = element_blank(),
          axis.ticks = element_blank()) +
    ggtitle(paste0("Binary presence (", channelA, " + ", channelB, ")"))
  
  # add rectangles (outline only)
  p <- p + geom_rect(data = rects,
                     aes(xmin = xmin, xmax = xmax, ymin = ymin, ymax = ymax, color = region),
                     fill = NA,
                     size = 0.4,
                     inherit.aes = FALSE) +
    scale_color_manual(values = c("Left_KT" = "red", "Inner_Centromere" = "blue", "Right_KT" = "red"),
                       guide = guide_legend(title = "Regions"))
  
  # Counts: slice the binary matrix directly with the original row/column indices.
  # bin[row, col] where row = x-dimension (y1:y2) and col = y-dimension (x1:x2).
  # This avoids any round-trip through y_plot coordinates.
  ry <- y1:y2
  counts <- c(
    Left_KT          = sum(bin[ry, x1:x2]),
    Inner_Centromere = sum(bin[ry, x3:x4]),
    Right_KT         = sum(bin[ry, x5:x6])
  )
  if (verbose) {
    message("Counts of '1' in regions:")
    print(counts)
  }
  
  # return list with plot, binary matrix, counts, summed
  invisible(list(plot = p, binary = bin, summed = summed, counts = counts, rects = rects))
}
