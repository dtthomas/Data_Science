setwd(dirname(rstudioapi::getActiveDocumentContext()$path))

data<- read.csv("Data.csv")

str(data)
summary(data)
head(data)

# loading psych package
library(psych)
psych::describe(data)
#Description of the output
#mad - median absolute deviation

#boxplot(data)

boxplot(data$Price_house)

data2 <- data[data$Price_house <10198905, ]
boxplot(data2$Price_house)

data3 <- data2[data2$Price_house > 30000, ]
boxplot(data3$Price_house)

library(corrgram)  #to show correlation matrix
x=corrgram(data, order=TRUE) #order - Should variables be re-ordered? Use TRUE or "PCA" for PCA-based re-ordering
x

## Check the missing value (if any)
sapply(data, function(x) sum(is.na(x)))

data <- na.omit(data) #delete the missing rows


library(caret)
fit<- lm(Price_house ~ Taxi_dist    +	Market_dist    +	Hospital_dist    +	Carpet_area  
         +	Builtup_area    +	Parking_type    +	City_type    +	Rainfall  
         , data=data)
summary(fit)

fit<- lm(Price_house ~ Taxi_dist    +	Market_dist    +	Hospital_dist    +	Carpet_area  
         +	Parking_type    +	City_type 
         , data=data)
summary(fit)


##Final model 
fit<- lm(Price_house ~ 	Hospital_dist    +	Carpet_area  
         +	Parking_type    +	City_type 
         , data=data)
summary(fit)
#predicted value 
data$pred <- fitted(fit)

#mape
library(Metrics)
mape(actual = data$Price_house, data$pred)

#Multicorelation 
library(car)
vif(fit)
# Histogram to check the distribution of errors
hist(lmModel$residuals, color = "grey")

library("lmtest")
dwtest(fit)#Auto corelation

# Breusch-Pagan test
bptest(fit) 
#Homogenous 