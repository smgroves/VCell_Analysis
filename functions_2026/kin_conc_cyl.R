kin_conc_cyl <- function(
  kinDiameter=0.3, # in um
  kinLength=0.075, # in um
  Ndc80_copy=244, # molecules at kinetochore
  Knl1_copy=151){ # molecules at kinetochore
  
  kinCopy<-c(Ndc80_copy,Knl1_copy)
  kinConc<-vector()

  conversionFactor_mol_to_umol <- 1e6
  conversionFactor_um3_to_L <- 1e-15
  
  N_A <- 6.02e23
  
  for(i in 1:length(kinCopy)){
    N_mol <- kinCopy[i]/N_A
  
    N_umol <- N_mol*conversionFactor_mol_to_umol
    
    kinVol_um3 <- pi*(kinDiameter/2)^2*kinLength
    kinVol_L <- kinVol_um3*conversionFactor_um3_to_L
    
    kinConc[i] <- round(N_umol/kinVol_L,digits=6)
  }
  
  print(paste("Ndc80 (uM):",kinConc[1]))
  print(paste("Knl1 (uM):",kinConc[2]))
  return(kinConc)
}