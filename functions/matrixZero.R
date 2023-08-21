matrixZero <- function( #make sure no negative values in concentration matrix
    matrixList){
    for(i in 1:length(matrixList)){
      for(j in 1:nrow(matrixList[[i]])){
        for(k in 1:ncol(matrixList[[i]])){
          if(matrixList[[i]][j,k] < 0){
            # matrixList[[i]][j,k] <- 0
            return(print("Error: negative concentration detected"))
          }
        }
      }
    }
    return(matrixList)
  }