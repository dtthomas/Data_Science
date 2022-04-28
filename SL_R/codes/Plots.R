###Pie chart
slices <- c(10,12,4, 16,8)
pct <- round(slices/sum(slices)*100)  #it will return a vector with value for each slices item :-)
lbls <- paste(c("UK","Canada","France","USA","Australia")," ",pct,"%",sep = "")
pie(slices,labels = lbls,col = rainbow(5),main = "Pie chart with percentages" )

###Histogram
#break decides the no of bins in hist
hist(mtcars$mpg, breaks=10, col="red")

###Kernal density plot
density_data <- density(mtcars$mpg)
plot(density_data, main = "Kernal density of miles per gallon")
polygon(density_data, col = "skyblue", border = "black")

#Histogram and kernal density plots together
hist(mtcars$mpg, freq = FALSE)  #freq is false means it is a probability density not counts.
#Try help("hist") to get full info.
density_data <- density(mtcars$mpg)
# Add density
lines(density_data, lwd = 2, col = "red")  #line chart for density plot

###heatmap
mat <- as.matrix(mtcars)
heatmap(mat,scale = "column")  #when you use scale the heat map will order the columns based on similarity


###wordcloud
#use is natural language processing


