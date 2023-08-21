zip_purge <- function(data_path=getwd()){
	setwd(data_path)
	file_list<-list.files(data_path) # get filenames
	pattern<-paste("[A-Za-z0-9_]*","\\.zip",sep="") 
	zip_files<-grep(pattern , file_list , value =TRUE) # filter filenames by .zip extension
	folder_names<-gsub(".zip" , "" , zip_files) # get new folder names minus the .zip

	# unzip each folder and save as new folder
	for(i in 1:length(zip_files)){
		print(zip_files[i])
		unzip(zip_files[i],exdir=folder_names[i])
		print(folder_names[i])
		percent<-100*(i/length(zip_files))
		console_update<-paste(percent,"% complete",sep="")
		print(console_update)
	}

	# remove remnant zip files
	file.remove(zip_files)
}