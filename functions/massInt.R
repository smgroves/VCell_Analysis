massInt <- function(
	C, # concentration matrix, processed from VCell
	Cc, 
	chrWidth,
	chrHeight){
	Cinit<-C
	# print("dim C")
	# print(dim(C))
	# print(class(C))
	# subtract out threshold
	C[C < Cc] <- 0
	# for(i in nrow(C)){
	# 	for(j in ncol(C)){
	# 		if(C[i,j] >= Cc){
	# 			# print(paste("before:",C[i,j]))
	# 			# C[i,j] <- C[i,j] - Cc
	# 			C[i,j] <- C[i,j]
	# 			# if(C[i,j]>0){print("yes")}
	# 		}else if(C[i,j] < Cc){
	# 			C[i,j]<-0
	# 		}
	# 	}
	# }
	indices<-(which(C!=0,arr.ind = T))
	print(identical(Cinit,C))
	# print(dim(C))
	# View(C)
	

	# dimension vectors
	x <- seq(from=0, to=chrWidth,length.out=ncol(C))
	y <- seq(from=0, to=chrHeight,length.out=nrow(C))

	# parameters for numerical integration c(dx,dy)
	a <- c(0,0)
	b <- c(chrWidth,chrHeight)
	n <- c(ncol(C)-1,nrow(C)-1)

	# Simpson's rule
	massYZ <- vector()
	# print(massYZ)

	# dx
	for(i in 1:nrow(C)){
		result<-SimpInt(a[1], b[1], n[1], C[i,], Ct=0)
		# result2<-integrate(C[i,],a[i],b[i])
		# print(result)
		massYZ<-append(massYZ, result)
	}
	
	# dy
	fy <- massYZ
	# print(massYZ)
	massZ <- SimpInt(a[2], b[2], n[2], fy, Ct=0)
	# print(paste("massInt2",massZ,sep=": "))
	# return(massZ)
	return(indices)
	# for(j in 1:length(massYZ)){
	# }
}