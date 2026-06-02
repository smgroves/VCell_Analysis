analysis_function <- function(
  ){

  # cpc recruitment over time
  # sum up all the CPC species
  sum_list<-reduce(all_data,`+`)
  ## dimensional setup
  # get dimensions of summed array
  t<-dim(sum_list)[1]
  x<-dim(sum_list)[2]
  y<-dim(sum_list)[3]
  # t
  # all_t_points<-seq(from=t_0,to=t_end,by=t_div)
  # desired_t_points<-seq(from=t_0,to=t_end,by=t_desired)
  t_index<-match(desired_time,seq(t_0,t_end,t_div))
  t_len<-length(t_index)

  # all species recruitment, final time point

  # fold enrichment

  # timecourse plot
}