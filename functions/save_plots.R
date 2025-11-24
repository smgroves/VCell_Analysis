save_plots <- function(
    sims,
    names,
    heatmap_species,
    heatmap_info_list,
    all_data,
    all_species,
    species_info_list,
    tInit,
    tSpan,
    desiredInterval,
    cutoff,
    funcPath,
    importPath,
    exportPath,
    kt_width,
    movie = TRUE,
    lineplots = TRUE
    )
  
{
  
  tic()
  
  
  tryCatch(
    expr = {
  
  
  for(hm in 1:length(heatmap_info_list)){
    
    heatmap<-vcell_heatmap(
      SimID=sims,
      names=names,
      species=heatmap_species[[hm]],
      speciesName=heatmap_info_list[[hm]],
      cutoff_color=cutoff,
      tInit=tInit,
      tSpan=tSpan,
      tInterval=10,
      desiredInterval=desiredInterval,
      row_1=1,
      row_2=dataDim[1],
      col_1=1,
      col_2=dataDim[2],
      importPath=importPath,
      exportPath=exportPath)
    
  }
      

  
},

error = function(e){
  message("Can't get heatmaps!")
  print(e)
},
finally = {
  
}

)
  if (lineplots == TRUE){
tryCatch(
  expr = {
    
    line_plot(
        SimID=sims,
        names=names,
        all_data,
        all_species,
        species_info_list,
        tInit=0,
        tSpan=tSpan,
        row_1=1,
        row_2=dataDim[1],
        col_1=1,
        col_2=dataDim[2],
        importPath=importPath,
        exportPath=exportPath,
        kt_width = kt_width
    )
},
error = function(e){
  message("Can't get line plots!")
  print(e)
},
finally = {
  

}
)
  }
  if (movie == TRUE){
  tryCatch(
    expr = {
  
  
  for(hm in 1:length(heatmap_info_list)){
    
    heatmap_movie<-heatmap_movie(
      SimID=sims,
      names=names,
      species=heatmap_species[[hm]],
      speciesName=heatmap_info_list[[hm]],
      cutoff_color=cutoff,
      tInit=tInit,
      tSpan=tSpan,
      tInterval=10,
      frame_interval=1,
      row_1=1,
      row_2=dataDim[1],
      col_1=1,
      col_2=dataDim[2],
      importPath=importPath,
      exportPath=exportPath)
    
  }


  
},
error = function(e){
  message("Can't get heatmap movie!")
  print(e)
},
finally = {
  
}

)
  }
  toc()
  

}