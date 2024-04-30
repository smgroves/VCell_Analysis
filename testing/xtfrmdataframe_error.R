library(dplyr)
filtered_active_ic = data.frame("CPCa" = c( 0.000000e+00,8.154741e-05, 1.597113e-04,2.422989e-04,3.737700e-04,6.678071e-04),
                  "pH2A_Sgo1_CPCa"=c( 0.000000e+00, 1.019566e-05,9.010610e-05,3.277025e-04,1.035288e-03,3.488490e-03),
                  "pH3_CPCa"=c( 0.000000e+00,1.053720e-05,8.105472e-05,3.137797e-04,1.237790e-03,5.702568e-03),
                  "pH2A_Sgo1_pH3_CPCa" =c( 0.000000e+00 ,1.350773e-06,4.578161e-05,3.253510e-04,1.585614e-03,7.410987e-03))
highlight_active_ic <- filtered_active_ic %>% summarise_if(is.numeric, list(~ max(., na.rm=TRUE)))

data.matrix = as.matrix(highlight_active_ic)
order.of.columns = order(data.matrix[1,], decreasing = FALSE)
sorted.df = highlight_active_ic[, order.of.columns]

n_highlight <- 4

highlight_active_ic <- filtered_active_ic %>% select(all_of(colnames(sorted.df))[1:n_highlight])

sorted.df = highlight_active_ic[, order(as.matrix(highlight_active_ic)[1,], decreasing = FALSE)]
