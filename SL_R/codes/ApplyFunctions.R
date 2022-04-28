#Apply functions
###apply()
m <- matrix(c(1,2,3,4),2,2)
print(m)
apply(m,1,sum)  #row sum
apply(m,2,sum) #col sum

###lapply()
#arguement is a list, and returns a list with the same length
l <- list(a=c(1,1),b=c(2,2),c=c(3,3))
print(l)
lapply(l,sum)  #sum each vector in the list

###sapply()
#if all the elements in the list are same size and >1, it will return a matrix.
#if all the elements in the list are size 1, it will return a vector
#Sapply in R is more efficient than lapply() in the output returned 
#because sapply() store values direclty into a vector. 
l <- list(a=c(1,1),b=c(2,2),c=c(3,3))
print(l)
sapply(l,sum)

l1 <- list(a=c(1,2),b=c(1,2,3),c=c(1,2,3,4))
sapply(l1,sum)

