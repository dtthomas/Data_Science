#Data Structures
###Array - Homo geneous 
#List and Dataframes are heterogeneous
vector1 <- c(2,9,3)
vector2 <- c(10,16,17,13,11,15)
#dim indices in each dimension. Here it means 4 rows, 2 columns, 1 matrix
result <- array(c(vector1,vector2),dim = c(4,2,1))
print(result)


###Factors
#are categorical values
#Class and levels are the attributes here
x<-factor(c("male","female","female","male"))
print(x)
x<-factor(c("male","female","female","male"), levels=c("male","female"))
print(x)
#In dataframes if you set StringsAsFactors=True, the strings will become factors 
#so that you can group them better later
