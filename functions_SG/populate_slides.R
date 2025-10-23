populate_slides <- function(

    exportPath,
    slide_id,
    var,
    slide_plots
    
){
  
  slide_id <- slide_id
  
  ### GENERAL TITLE SLIDE ###
  
  # Create another slide
  requests <- add_create_slide_page_request(predefined_layout = "TITLE")
  commit_to_slides(slide_id, requests)
  
  # Update slide details
  slide_details <- rgoogleslides::get_slides_properties(slide_id)
  
  # Update all slide_page_ids
  slide_page_id <- slide_details$slides$objectId
  
  # Get the last page
  slide_data <- get_slide_page_properties(slide_id, slide_page_id[length(slide_page_id)])
  
  # Change text
  request_insert <- add_insert_text_request(object_id = slide_data$get_text_boxes()$object_id[1], text = var)
  commit_to_slides(slide_id, request_insert)
  
  
  
  for(plot in 1:length(slide_plots)){
    
    Sys.sleep(3)
    
    url = paste(paste(exportPath, slide_plots[plot], sep = "/"), "png", sep = ".")
    
    # Determine the dimensions of the image
    image <- png::readPNG(url)
    dimension <- dim(image)
    
    if(length(grep("heatmap", slide_plots[plot])) > 0){
    image_width <- dimension[1]/3 # Calculate to your requirements
    image_height <- dimension[2]/3 # Calculate to your requirements
    }else{
      image_width <- dimension[1] # Calculate to your requirements
      image_height <- dimension[2]
    }
    
    
    aa = googleCloudStorageR::gcs_upload(url, predefinedAcl = "bucketLevel")
    signedURL = gcs_signed_url(aa)
    
    
    
    ### PLOTS ###
    
    # Create another slide
    requests <- add_create_slide_page_request(predefined_layout = "TITLE_ONLY")
    commit_to_slides(slide_id, requests)
    
    # Update slide details
    slide_details <- rgoogleslides::get_slides_properties(slide_id)
    
    # Update all slide_page_ids
    slide_page_id <- slide_details$slides$objectId
    
    # Get the last page
    slide_data <- get_slide_page_properties(slide_id, slide_page_id[length(slide_page_id)])
    
    # Change text
    request_insert <- add_insert_text_request(object_id = slide_data$get_text_boxes()$object_id[1], text = var)
    commit_to_slides(slide_id, request_insert)
    
    # Get the position details of the element on the slide
    page_element <- rgoogleslides::aligned_page_element_property(slide_page_id[length(slide_page_id)],
                                                                 image_height = image_height,
                                                                 image_width = image_width)
    
    request <- rgoogleslides::add_create_image_request(url = signedURL, page_element_property = page_element)
    response <- rgoogleslides::commit_to_slides(slide_id, request)
  }
  
  
  
  
  
}