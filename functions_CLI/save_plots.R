save_plots <- function(
    sim,
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
    heatmaps = TRUE,
    lineplots=TRUE
    )
  
{
  
  tic()
  
  if (heatmaps==TRUE){
  tryCatch(
    expr = {
  
  
  for(hm in 1:length(heatmap_info_list)){

    print(heatmap_species[[hm]])
    
    heatmap<-vcell_heatmap(
      SimID=sim,
      names=names,
      species=heatmap_species[[hm]],
      speciesName=heatmap_info_list[[hm]],
      cutoff_color=cutoff,
      tInit=tInit,
      tSpan=tSpan,
      tInterval=10,
      desiredInterval=desiredInterval,
      dataDim=c(128,64), #updated
      row_1=1,
      row_2=dataDim[1],
      col_1=1,
      col_2=dataDim[2],
      chromWidth=1.6, #um
      chromHeight=3.2, #um #updated
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
  }
  
  
if (lineplots==TRUE){
tryCatch(
  expr = {
    
    all_plot(
        SimID=sim,
        names=names,
        all_data,
        all_species,
        species_info_list,
        tInit=0,
        tSpan=tSpan,
        chromWidth=1.6, #um
        chromHeight=3.2, #um updated
        dataDim=c(128,64), #updated 
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
  
  toc()

}