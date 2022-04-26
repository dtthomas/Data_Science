#Project 2 - comcast complaints analysis

### set working directory
#Can use this command if you have Rstudio IDE
setwd(dirname(rstudioapi::getActiveDocumentContext()$path))

### Libraries
library(logr)
library(lubridate) #for date parsing
library(dplyr)
library(ggplot2)  #visualization
#NLP packages
library(tm)  #Text mining package
#library(SnowballC) #collapsing word to common root-Stemming
library(RColorBrewer) #provide color schemes for maps
library(wordcloud)

### Set up log file
tmp <- file.path(dirname(rstudioapi::getActiveDocumentContext()$path), "SL_R_Proj3_Comcast.log")
# Open log
lf <- log_open(tmp)
# Send message to log
log_print("Simlilearn - DS with R Pgming - Project 2")

### Q.Import data in to R
data <- read.csv("../data/Comcast Telecom Complaints data.csv")

### To check missing values
#apply(is.na(data),2, which)
# No missing values found

### Functions
date_parsing <- function(dt) {
    #print(dt)
    if(!is.na(dt)){
      for(date_format in c("%d/%m/%Y","%d-%m-%Y")){
        datehead <- format(strptime(as.character(dt),date_format),"%Y-%m-%d")
        if(is.na(datehead)){}
        else{break}
      }#end of for
    }# end of if
  return(datehead)
}

### Data cleaning - make dates in to same format
#str(data) # to get info about the dataframe columns. Here all cols are in chr format
data$newDate <- unlist(lapply(data$Date,date_parsing))

### Q.Plot data monthly
#create year month column
data$newDate <- as.Date(data$newDate)
#write.csv(data,'./log/temp.csv',row.names = F)
#group by month
data_grp_mth <- data %>% 
  group_by(month = lubridate::floor_date(newDate, "month")) %>%
  summarize(cnt = n_distinct(Customer.Complaint))
#plot data
ggplot(data_grp_mth, aes(month, cnt)) + 
  geom_point() + 
  geom_line() +
  xlab("Month") + 
  ylab("Number of Complaints") +
  ggtitle("Monthly Comcast complaint frequency")

### Q.Plot data daily
#group by daily
data_grp_day <- data %>% 
  group_by(newDate) %>%
  summarize(cnt = n_distinct(Customer.Complaint))
#plot data
ggplot(data_grp_day, aes(newDate, cnt)) + 
  geom_point() + 
  geom_line() +
  xlab("Date") + 
  ylab("Number of Complaints") +
  ggtitle("Daily Comcast complaint frequency")

### Observations ###
log_print("By looking at the daily and monthly plots, we can conclude that most number of complaints are added in June 2015.")
### Observations ###
  
### Q.Provide a table with the frequency of complaint types.
### Q.Which complaint types are maximum i.e., around internet, network issues, or across any other domains.
#Identify different complaint types from Customer.complaint column values and their count

#corpus - collection of text docs. VectorSource because we are using a column of the dataframe.
corpus = Corpus(VectorSource(data$Customer.Complaint)) 
#converting to lower case
corpus = tm_map(corpus, PlainTextDocument) #tm_map - Doing transformations in texts
corpus = tm_map(corpus, tolower)
corpus = tm_map(corpus, removePunctuation)
#stop words - words that doesn't have much meaning. eg: is, are
corpus = tm_map(corpus, removeWords, c("and", stopwords("english")))
#Stemming - Find the root words
corpus = tm_map(corpus, stemDocument)
#Eliminate white spaces
corpus = tm_map(corpus, stripWhitespace)

#creating term document matrix
dtm <- TermDocumentMatrix(corpus) #Terms as rows and docs as columns
#inspect(dtm)
mat <- as.matrix(dtm) #make it a dense matrix
mat_sort <- sort(rowSums(mat),decreasing=TRUE)
ComplTypeCnt_mat <- data.frame(word = names(mat_sort),cnt=mat_sort) #created a dataframe with two columns - word and cnt
write.csv(ComplTypeCnt_mat,'./log/OutputFiles/ComplaintTypes_Freq.csv',row.names = F)
#Most used words
head(ComplTypeCnt_mat, 5)
#Create a wordcloud picture
set.seed(1234)  #for reproducing the same result
wordcloud(words = ComplTypeCnt_mat$word, freq = ComplTypeCnt_mat$cnt, random.order=TRUE,colors = brewer.pal(8,"Dark2"),scale=c(3.5,0.25)) #brewer.pal for R color palettes
### Observations ###
log_print("By looking at Complaint Type Count matrix, we can conclude that most number of complaints are added in the categories of internet,service,bill and data.")
### Observations ###

# Q. Create a new categorical variable with value as Open and Closed. 
# Open & Pending is to be categorized as Open and Closed & Solved is to be categorized as Closed.
data <- data %>%
  mutate(Status_2 = case_when(
    (Status == 'Open' | Status == 'Pending') ~ "Open",
    (Status == 'Closed' | Status == 'Solved') ~ "Closed"
  ))

# Q. Provide state wise status of complaints in a stacked bar chart. 
# group by state and status
data_grp_stateNStatus <- data %>% 
  group_by(State,Status_2) %>%
  summarize(cnt = n_distinct(Customer.Complaint))

# Q. Use the categorized variable from Q3. Provide insights on:
#  - Which state has the maximum complaints
#  - Which state has the highest percentage of unresolved complaints
#  - Provide the percentage of complaints resolved till date, which were received through theInternet and customer care calls.
# Close log
log_close()
