Simp13m <- function(h, n, f){
	# if(!identical(n+1,length(f))){
	if(FALSE){
		print("Error: number of segments, n, does not match length of data vector, f")
	}else{
		sum <- 0

		for(i in 1:length(f)){
			if(i==0 || i==length(f)){ #first and last data points
				sum <- sum + f[i]
				# print(paste("Simp13m",sum,sep=": "))
			}else if((i%%2)==0){ #even data point, *4
				sum <- sum + 4*f[i]
				# print(paste("Simp13m",sum,sep=": "))
			}else if((i%%2)==1){ #odd data point, *2
				sum <- sum + 2*f[i]
				# print(paste("Simp13m",sum,sep=": "))
			}
		}

		return (sum*(h/3))
	}
}