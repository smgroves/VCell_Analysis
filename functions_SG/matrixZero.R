matrixZero <- function( #make sure no negative values in concentration matrix
    matrixList){
    print_count = 0
  
    for(i in 1:length(matrixList)){
      for(j in 1:nrow(matrixList[[i]])){
        for(k in 1:ncol(matrixList[[i]])){
          if(matrixList[[i]][j,k] < 0){
            if (print_count == 0){
              print("Warning: negative concentration(s) detected. This may be the result of  Set to 0.")
              # print(matrixList[[i]][j,k])
              print_count = 1}
            matrixList[[i]][j,k] <- 0
            # return(print("Warning: negative concentration detected. Set to 0."))
          }
        }
      }
    }
    return(matrixList)
  }