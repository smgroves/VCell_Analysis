fold_enrich <- function(C){ # m x n matrix, C
	
	# remove void
	C[C==0]<-NA

	# mat dims
	m<-nrow(C)
	n<-ncol(C)
	x_mid<-round(n/2)
	y_mid<-round(m/2)

	# max, min, inner cent C
	C_max<-max(C,na.rm=TRUE)
	C_min<-min(C,na.rm=TRUE)
	C_0<-C[y_mid,x_mid]

	# 1) CPC[0,0] / min[CPC] –> fold enrichment at the inner centromere
	ic_enrich<-C_0/C_min

	# 2)  (CPC[0,0] – min[CPC]) / (max[CPC] – min[CPC]) –> Inner centromere enrichment relative to the most enrichment observed in the simulation
	max_enrich<-(C_0 - C_min) / (C_max - C_min)

	# 3) CPC[0,0] / min[CPC(0,:)] –> fold enrichment along the horizontal axis 
	x_enrich<-C_0 / min(C[y_mid,],na.rm=TRUE)

	# 4)  (CPC[0,0] – min[CPC]) / (max[CPC(0,:)] – min[CPC]) –> Inner centromere enrichment relative to the most enrichment observed along the horizontal axis
	x_enrich_ratio<-(C_0 - C_min) / (max(C[y_mid,],na.rm=TRUE) - C_min)

	# 5) CPC[0,0] / min[CPC(:,0)] –> fold enrichment along the vertical axis 
	y_enrich<-C_0 / min(C[,x_mid],na.rm=TRUE)

	# 6)  (CPC[0,0] – min[CPC]) / (max[CPC(:,0)] – min[CPC]) –> Inner centromere enrichment relative to the most enrichment observed along the vertical axis
	y_enrich_ratio <- (C_0 - C_min) / (max(C[,x_mid],na.rm=TRUE) - C_min)

	output<-c("C_max"=C_max,
		"C_min"=C_min,
		"C_0"=C_0,
		"ic_enrich"=ic_enrich,
		"max_enrich"=max_enrich,
		"y_enrich"=y_enrich,
		"y_enrich_ratio"=y_enrich_ratio,
		"x_enrich"=x_enrich,
		"x_enrich_ratio"=x_enrich_ratio)
	return(output)
}