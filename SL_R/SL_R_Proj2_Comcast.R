#Project 2 - comcast complaints analysis

### set working directory
#Can use this command if you have Rstudio IDE
setwd(dirname(rstudioapi::getActiveDocumentContext()$path))

### Libraries
library(logr)
library(lubridate)
library(dplyr)

### Set up log file
tmp <- file.path(dirname(rstudioapi::getActiveDocumentContext()$path), "SL_R_Proj3_Comcast.log")
# Open log
lf <- log_open(tmp)
# Send message to log
log_print("Simlilearn - DS with R Pgming - Project 2")

### Import data in to R
data <- read.csv("../data/Comcast Telecom Complaints data.csv")

### To check missing values
#apply(is.na(data),2, which)
# No missing values found

### Functions
date_parsing <- function(dt) {
    print(dt)
    for(date_format in c("%d/%m/%Y","%d-%m-%Y")){
      datehead <- format(strptime(as.character(dt),date_format),"%Y-%m-%d")
      if(is.na(datehead)){}
      else{break}
    }#end of for
  return(datehead)
}

### make dates in to same format
#str(data) # to get info about the dataframe columns. Here all cols are in chr format
data$newDate <- lapply(data$Date,date_parsing)

### Plot data monthly
#create year month column
#data$year_month <- floor_date(data$newDate,unit = "month") #floor date to nearest month


# Close log
log_close()
