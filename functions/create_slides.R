create_slides <- function(
    title
  
){
  
  Sys.setenv("GCS_DEFAULT_BUCKET" = "vcell_bucket")
  Sys.setenv("GCS_AUTH_FILE"="C:/Users/sam/Downloads/disco-basis-393613-adc3747a6a2d.json")
  gcs_global_bucket("vcell_bucket")
  
  authorize("648818067522-j37u914d2bao6372o6jgorq7glnc25eg.apps.googleusercontent.com",
            "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")
  
  gcs_auth("C:/Users/sam/Downloads/disco-basis-393613-adc3747a6a2d.json")
  
  slide_id <- rgoogleslides::create_slides("Test Analysis NEXT")
  
  return(slide_id)
}