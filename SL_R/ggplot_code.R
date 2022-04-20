#We use ggplot2 when we need to put multiple plots(look in to multivariate) together
#This breaks the graphs in to semantic components such as scales and layers
library("ggplot2")
ggplot(airquality,aes(x=Ozone))+geom_histogram()

##ggplot works with dataframes
# Setup
options(scipen=999)  # turn off scientific notation like 1e+06
library(ggplot2)
data("midwest", package = "ggplot2")  # load the data
# midwest <- read.csv("http://goo.gl/G1K41K") # alt source 

# Init Ggplot
# aes() function is used to specify the X and Y axes. That’s because, any information that is part of the source dataframe has to be specified inside the aes() function.
ggplot(midwest, aes(x=area, y=poptotal))  # area and poptotal are columns in 'midwest'
#the above will give you a blank chart
#simple scatter plot
ggplot(midwest, aes(x=area, y=poptotal)) + geom_point()

#lm is for linear model. It will give you best fit line
g <- ggplot(midwest, aes(x=area, y=poptotal)) + geom_point() + geom_smooth(method="lm")  # set se=FALSE to turnoff confidence bands
plot(g) 

#the chart was not built from scratch but rather was built on top of g(layers)
# Delete the points outside the limits
g + xlim(c(0, 0.1)) + ylim(c(0, 1000000))   # the line of best fit change
#you can add more layers like this

# Zoom in without deleting the points outside the limits. 
# As a result, the line of best fit is the same as the original plot, means the first plot we saw without xlim and ylim
g1 <- g + coord_cartesian(xlim=c(0,0.1), ylim=c(0, 1000000))  # zooms in
plot(g1)

# Add Title and Labels
g1 + labs(title="Area Vs Population", subtitle="From midwest dataset", y="Population", x="Area", caption="Midwest Demographics")

# or

g1 + ggtitle("Area Vs Population", subtitle="From midwest dataset") + xlab("Area") + ylab("Population")

# Here is the Full Plot call
library(ggplot2)
ggplot(midwest, aes(x=area, y=poptotal)) + 
  geom_point() + 
  geom_smooth(method="lm") + 
  coord_cartesian(xlim=c(0,0.1), ylim=c(0, 1000000)) + 
  labs(title="Area Vs Population", subtitle="From midwest dataset", y="Population", x="Area", caption="Midwest Demographics")