Simp38 <- function(h, f0, f1, f2, f3){
	sum <- f0 + 3*(f1 + f2) + f3
	# print(paste("Simp38",sum,sep=": "))
	return (sum*(3*h/8))
}