kin_conc_rect <- function(x=0.3,y=0.075,Ndc80_copy,Knl1_copy){
	copy<-c(Ndc80_copy,Knl1_copy)
	kin_conc<-1e6*(copy/6.02e23)/(x*y*1e-15)
	print(paste("Ndc80 (uM):",kin_conc[1]))
	print(paste("Knl1 (uM):",kin_conc[2]))
	return(kin_conc)
}