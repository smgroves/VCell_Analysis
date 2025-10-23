SimpInt <- function(a, b, n, f, Ct=0){
	sum <- 0
	h = (b-a) / n
	if((!is.null(Ct)) && (length(f)-3 > 0)){
		cutoff <- rep_len(Ct,length.out=length(f)-3)
	}else{

	}
	if(n==1){
		sum <- Trap(h,f[length(f)-1],f[(length(f))])
	}else{
		m <- n
		if((n%%2)!=0 && n>1){
			if(is.null(Ct)){
				sum <- sum+Simp38(h, f[length(f)-3], f[length(f)-2], f[length(f)-1], f[length(f)])
				# print(paste("SimpInt",sum,sep=": "))
			}else{
				sum <- sum+Simp38(h, f[length(f)-3], f[length(f)-2], f[length(f)-1], f[length(f)])-Simp38(h,Ct,Ct,Ct,Ct)
				# print(paste("SimpInt",sum,sep=": "))
			}
			
			m <- n-3
		}
		if(m>1){
			if(is.null(Ct)){
				sum <- sum+Simp13m(h,m,f[1:m+1])
				# print(paste("SimpInt",sum,sep=": "))
			}else{
				sum <- sum+Simp13m(h,m,f[1:m+1])-Simp13m(h,m,cutoff)
				# print(paste("SimpInt",sum,sep=": "))
			}
			
		}
	}
	return(sum)
}