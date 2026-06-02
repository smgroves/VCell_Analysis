get_sim_id <- function(run_name, workspace_path) {
  # Auto-detect the SimID string for a pyvcell workspace folder.
  #
  # Looks for the unique *.fvinput file that pyvcell writes into every
  # simulation output directory.  The base filename (without extension) is
  # the SimID string expected by vcell_heatmap / line_plot, e.g.
  #   "SimID_1105102268_0_"
  # which those functions convert to the exported sub-folder name
  #   "SimID_1105102268_0__exported"
  #
  # Args:
  #   run_name       – character, workspace folder name (e.g. "_005_20_26_...")
  #   workspace_path – character, absolute path to the workspace directory
  #
  # Returns:
  #   character(1) – SimID string ready to pass as the `sims` argument

  run_dir <- file.path(workspace_path, run_name)

  if (!dir.exists(run_dir)) {
    stop("Workspace folder not found: ", run_dir)
  }

  fvinput_files <- list.files(run_dir, pattern = "\\.fvinput$", full.names = FALSE)

  if (length(fvinput_files) == 0) {
    stop(
      "No .fvinput file found in '", run_dir, "'.\n",
      "  Has the simulation been run and the CSVs exported?"
    )
  }
  if (length(fvinput_files) > 1) {
    warning(
      "Multiple .fvinput files found in '", run_dir,
      "'; using the first: ", fvinput_files[1]
    )
  }

  tools::file_path_sans_ext(fvinput_files[1])
}
