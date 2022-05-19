#Project 2 - comcast complaints analysis

### set working directory
#Can use this command if you have Rstudio IDE
setwd(dirname(rstudioapi::getActiveDocumentContext()$path))

### Libraries
library(logr)
library(lubridate) #for date parsing
library(dplyr)
library(ggplot2)  #visualization
library(reshape2) #pivot tble
library(stringr)
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
data <- read.csv("./Comcast Telecom Complaints data.csv")

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
data_grp_mth<-arrange(data_grp_mth,desc(cnt))
max_month <- format(data_grp_mth$month[1],"%B-%Y")
log_print(paste("By looking at the daily and monthly plots, we can conclude that most number of complaints are added in ",max_month,".",sep = ""),hide_notes = TRUE)
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
#head(ComplTypeCnt_mat, 5)
#Create a wordcloud picture
set.seed(1234)  #for reproducing the same result
wordcloud(words = ComplTypeCnt_mat$word, freq = ComplTypeCnt_mat$cnt, random.order=TRUE,colors = brewer.pal(8,"Dark2"),scale=c(3.5,0.25)) #brewer.pal for R color palettes, scale for adjusting the pic
### Observations ###
ComplTypeCnt_mat<-arrange(ComplTypeCnt_mat,desc(cnt))
log_print(paste("By looking at Complaint Type Count matrix, we can conclude that most number of complaints are added in the categories of:",ComplTypeCnt_mat$word[1],ComplTypeCnt_mat$word[2],ComplTypeCnt_mat$word[3],ComplTypeCnt_mat$word[4],ComplTypeCnt_mat$word[5],ComplTypeCnt_mat$word[6],sep=","),hide_notes = TRUE)
log_print("To get a better understanding, please look at the wordcloud picture.",hide_notes = TRUE)
### Observations ###

# Q. Create a new categorical variable with value as Open and Closed. 
# Open & Pending is to be categorized as Open and Closed & Solved is to be categorized as Closed.
data <- data %>%
  mutate(Status_2 = case_when(
    (Status == 'Open' | Status == 'Pending') ~ "Open",
    (Status == 'Closed' | Status == 'Solved') ~ "Closed"
  ))
data$State <- tolower(data$State)  #To avoid duplicates
# Q. Provide state wise status of complaints in a stacked bar chart. 
#plot data
ggplot(data = data, aes(y = State)) + 
  geom_bar(aes(fill = Status_2)) + 
  ggtitle("State wise status of complaints ")

# Q. Use the categorized variable from Q3. Provide insights on:
#  - Which state has the maximum complaints
# group by state and status
data_grp_stateNStatus <- data %>% 
  group_by(State,Status_2) %>%
  summarize(cnt = n_distinct(Customer.Complaint))
Statewise_status<-dcast(data_grp_stateNStatus, State ~ Status_2, value.var="cnt")
Statewise_status$Total <- Statewise_status$Closed + Statewise_status$Open
Statewise_status<-arrange(Statewise_status,desc(Total))
log_print(paste(str_to_title(Statewise_status$State[1]), "state has maximum number of complaints.",sep = " "),hide_notes = TRUE)
#  - Which state has the highest percentage of unresolved complaints
Statewise_status$UnresolvedPerc <- (Statewise_status$Open / Statewise_status$Total)*100
Statewise_status_unres<-arrange(Statewise_status,desc(UnresolvedPerc))
log_print(paste(str_to_title(Statewise_status_unres$State[1]),"has highest percentage of unresolved complaints.",sep = " "),hide_notes = TRUE)
log_print("In this data set, Kansas has higher unresolved rate. However, it only got 1 Open complaint and 1 Unresolved.That is why it got 50% unresolved rate. So this result doesn't mean much. I am not entirely sure whether this is what we want.",hide_notes = TRUE)
#  - Provide the percentage of complaints resolved till date, which were received through the Internet and customer care calls.
data_grp_res <- data %>% 
  group_by(Received.Via,Status_2) %>%
  summarize(cnt = n_distinct(Customer.Complaint))
data_grp_res$perc <-  (data_grp_res$cnt/nrow(data)) * 100
data_resPerc_call <- filter(data_grp_res,Received.Via=="Customer Care Call" & Status_2=="Closed")
log_print(paste("The resolved rate for Customer call is:",data_resPerc_call$perc[1],sep = ""),hide_notes = TRUE )
data_resPerc_Internet <- filter(data_grp_res,Received.Via=="Internet" & Status_2=="Closed")
log_print(paste("The resolved rate for Internet is:",data_resPerc_Internet$perc[1],sep = ""),hide_notes = TRUE )
log_print("In this data set, both methods have similar resolved rate.", hide_notes = TRUE)
# Close log
log_close()
