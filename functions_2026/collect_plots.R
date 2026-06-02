collect_plots <- function(
    plot_name,            # filename stem to search for (without .pdf); partial matches OK
    var,                  # character vector of workspace folder names, one per model
    workspace_path,       # absolute path to the workspace directory
    labels        = NULL, # optional named vector (var -> display label); defaults to var
    output_path   = NULL, # where to save the combined PDF; defaults to workspace_path
    output_name   = NULL, # filename stem for the output (without .pdf)
    label_size    = 11,   # font size for the model name printed on each page
    dpi           = 150,  # rendering resolution for converting PDF pages to images
    width         = 11,   # output PDF width (inches)
    height        = 8.5   # output PDF height (inches)
) {
  # ── dependencies ──────────────────────────────────────────────────────────
  for (pkg in c("pdftools", "png", "grid")) {
    if (!requireNamespace(pkg, quietly = TRUE))
      stop("Package '", pkg, "' is required. Install with install.packages('", pkg, "')")
  }

  # ── defaults ──────────────────────────────────────────────────────────────
  if (is.null(labels))      labels      <- setNames(var, var)
  if (is.null(output_path)) output_path <- workspace_path
  if (is.null(output_name)) output_name <- paste0(gsub("[^A-Za-z0-9._-]", "_", plot_name), "_combined")

  out_file <- file.path(output_path, paste0(output_name, ".pdf"))

  # ── locate one PDF per model ───────────────────────────────────────────────
  found   <- list()
  skipped <- character()

  for (model in var) {
    plots_dir <- file.path(workspace_path, model, "plots")

    if (!dir.exists(plots_dir)) {
      warning("plots/ directory not found — skipping: ", plots_dir)
      skipped <- c(skipped, model)
      next
    }

    # Match the supplied stem against filenames (case-insensitive, .pdf only)
    candidates <- list.files(
      plots_dir,
      pattern     = paste0(plot_name, "\\.pdf$"),
      ignore.case = TRUE,
      full.names  = TRUE
    )

    if (length(candidates) == 0) {
      warning("No PDF matching '", plot_name, "' found in: ", plots_dir)
      skipped <- c(skipped, model)
      next
    }
    if (length(candidates) > 1)
      message("Multiple matches for '", plot_name, "' in '", model,
              "' — using first: ", basename(candidates[1]))

    found[[model]] <- candidates[1]
  }

  if (length(found) == 0)
    stop("No matching PDFs found for '", plot_name, "' in any of the supplied folders.")

  message("Collecting ", length(found), " plot(s) for '", plot_name, "'...")
  if (length(skipped) > 0)
    message("  Skipped (not found): ", paste(skipped, collapse = ", "))

  # ── build combined PDF ────────────────────────────────────────────────────
  pdf(out_file, width = width, height = height)

  for (model in names(found)) {
    fpath   <- found[[model]]
    label   <- if (model %in% names(labels)) labels[[model]] else model
    n_pages <- pdftools::pdf_info(fpath)$pages

    for (pg in seq_len(n_pages)) {
      # Render this page to a temporary PNG, then read it back as a native raster
      tmp_png <- tempfile(fileext = ".png")
      pdftools::pdf_convert(
        fpath,
        format    = "png",
        pages     = pg,
        filenames = tmp_png,
        dpi       = dpi,
        verbose   = FALSE
      )
      img <- png::readPNG(tmp_png, native = TRUE)   # native raster for grid
      file.remove(tmp_png)

      # ── lay out one page ─────────────────────────────────────────────────
      grid::grid.newpage()

      # Model label at the top
      grid::grid.text(
        label,
        x    = 0.5, y = 0.985,
        just = "top",
        gp   = grid::gpar(fontsize = label_size, fontface = "bold", col = "black")
      )

      # Plot image below the label (leaves ~5 % of height for the label)
      img_vp <- grid::viewport(x = 0.5, y = 0.46, width = 0.98, height = 0.90)
      grid::pushViewport(img_vp)
      grid::grid.raster(img, width = grid::unit(1, "npc"), height = grid::unit(1, "npc"))
      grid::popViewport()
    }
  }

  dev.off()
  message("Saved: ", out_file)
  invisible(out_file)
}
