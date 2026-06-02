get_cumulative_bound_CPC <- function(
    SimID,
    tInit = 0,
    tSpan,
    importPath,
    exportPath,
    dataDim,
    chromWidth,
    chromHeight,
    kt_width = "Metacentric_Relaxed",
    KK_dist_relaxed = 0.575,
    KK_dist_tensed  = 1.15,
    KT_width  = 0.075,
    KT_height = 0.3,
    cohesin_width = 0.09,
    leader = 10
) {
  
  # ── 1. Resolve SimID ────────────────────────────────────────────────────────
  pattern <- paste("[A-Za-z0-9_]*", "exported", sep = "")
  cond    <- grepl(pattern, SimID)
  SimID   <- ifelse(cond, SimID, paste(SimID, "exported", sep = "_"))
  
  # ── 2. Compute region boundaries (mirrors line_plot.R logic) ────────────────
  pixels_per_um_x <- dataDim[2] / chromWidth
  center_x        <- dataDim[2] / 2
  
  if (grepl("tensed", kt_width, ignore.case = TRUE)) {
    kk_half <- KK_dist_tensed / 2
  } else {
    kk_half <- KK_dist_relaxed / 2
  }
  center_half_um <- cohesin_width / 2
  
  x3 <- ceiling(center_x - center_half_um * pixels_per_um_x)
  x4 <- ceiling(center_x + center_half_um * pixels_per_um_x)
  if (x3 > x4) { x3 <- max(1, x4 - 1); x4 <- min(dataDim[2], x3 + 1) }
  
  pixels_per_um_y <- dataDim[1] / chromHeight
  if (grepl("metacentric", kt_width, ignore.case = TRUE)) {
    half_px <- (KT_height / 2) * pixels_per_um_y
    center_px <- dataDim[1] / 2
    y1 <- max(1, ceiling(center_px - half_px))
    y2 <- min(dataDim[1], floor(center_px + half_px))
  } else {
    y1 <- 1
    y2 <- min(dataDim[1], ceiling(KT_height * pixels_per_um_y))
  }
  
  cat(sprintf("Inner centromere region: rows %d:%d, cols %d:%d\n", y1, y2, x3, x4))
  
  # ── 3. Loop over timepoints ──────────────────────────────────────────────────
  timepoints  <- seq(tInit / 10, tSpan / 10)   # integer indices used in filenames
  times_sec   <- timepoints * 10                # actual time in seconds
  n_tp        <- length(timepoints)
  
  cumsum_vec  <- numeric(n_tp)   # cumulative sum (total molecules in region)
  mean_vec    <- numeric(n_tp)   # mean concentration in region (for reference)
  
  simdir <- file.path(importPath, SimID)
  
  for (z in seq_along(timepoints)) {
    
    t <- timepoints[z]
    
    # Build zero-padded dataPoint string (matches VCell export convention)
    dataPoint <- formatC(as.integer(t), width = 4, flag = "0")
    
    # Find the matching file for bound_CPC
    file_pattern <- paste("[A-Za-z0-9_]*_Slice_XY_\\d", "bound_CPC", dataPoint, sep = "_")
    matched_file <- grep(file_pattern, list.files(simdir), value = TRUE)
    
    if (length(matched_file) == 0) {
      warning(sprintf("No file found for bound_CPC at t=%s — filling with NA", dataPoint))
      cumsum_vec[z] <- NA
      mean_vec[z]   <- NA
      next
    }
    
    M <- tryCatch({
      data.matrix(
        read.csv(file.path(simdir, matched_file[1]),
                 header = FALSE, skip = leader)
      )[1:dataDim[1], 1:dataDim[2]]
    }, error = function(e) {
      warning(sprintf("Failed to read file at t=%s: %s", dataPoint, e$message))
      return(NULL)
    })
    
    if (is.null(M)) { cumsum_vec[z] <- NA; mean_vec[z] <- NA; next }
    
    # Clamp negatives to zero (matches matrixZero logic in line_plot.R)
    M[M < 0] <- 0
    
    region        <- M[y1:y2, x3:x4]
    cumsum_vec[z] <- sum(region,  na.rm = TRUE)
    mean_vec[z]   <- mean(region, na.rm = TRUE)
  }
  
  # ── 4. Build results table ───────────────────────────────────────────────────
  results_df <- data.frame(
    Time_index        = timepoints,
    Time_s            = times_sec,
    CumulativeSum_IC  = cumsum_vec,
    MeanConc_IC       = mean_vec
  )
  
  # ── 5. Export table ──────────────────────────────────────────────────────────
  dir.create(file.path(exportPath, "data"), showWarnings = FALSE, recursive = TRUE)
  csv_path <- file.path(exportPath, "data", "cumulative_bound_CPC_IC.csv")
  write.csv(results_df, csv_path, row.names = FALSE)
  cat(sprintf("Table saved to: %s\n", csv_path))
  
  # ── 6. Barplot: cumulative sum vs time ───────────────────────────────────────
  p_cumsum <- ggplot(results_df, aes(x = Time_s, y = CumulativeSum_IC)) +
    geom_bar(stat = "identity", fill = "#377eb8", color = NA, width = 8) +
    labs(
      title    = "Cumulative bound CPC at inner centromere over time",
      subtitle = sprintf("Region: rows %d:%d, cols %d:%d", y1, y2, x3, x4),
      x        = "Time (s)",
      y        = "Cumulative sum of bound CPC (a.u.)"
    ) +
    theme(
      panel.background = element_rect(fill = "transparent"),
      axis.line        = element_line(color = "black"),
      axis.text        = element_text(size = 12),
      axis.title       = element_text(size = 14),
      plot.title       = element_text(size = 16),
      plot.subtitle    = element_text(size = 11, color = "gray40")
    )
  
  # ── 7. Barplot: mean concentration vs time ───────────────────────────────────
  p_mean <- ggplot(results_df, aes(x = Time_s, y = MeanConc_IC)) +
    geom_bar(stat = "identity", fill = "#e41a1c", color = NA, width = 8) +
    labs(
      title    = "Mean bound CPC concentration at inner centromere over time",
      subtitle = sprintf("Region: rows %d:%d, cols %d:%d", y1, y2, x3, x4),
      x        = "Time (s)",
      y        = expression("Mean concentration (" * mu * "M)")
    ) +
    theme(
      panel.background = element_rect(fill = "transparent"),
      axis.line        = element_line(color = "black"),
      axis.text        = element_text(size = 12),
      axis.title       = element_text(size = 14),
      plot.title       = element_text(size = 16),
      plot.subtitle    = element_text(size = 11, color = "gray40")
    )
  
  # ── 8. Save plots ────────────────────────────────────────────────────────────
  ggsave(
    filename = "cumulative_bound_CPC_IC.pdf",
    plot     = gridExtra::grid.arrange(p_cumsum, p_mean, ncol = 1),
    path     = exportPath,
    width    = 8, height = 10, units = "in", dpi = 300
  )
  cat(sprintf("Plot saved to: %s\n", file.path(exportPath, "cumulative_bound_CPC_IC.pdf")))
  
  invisible(results_df)
}