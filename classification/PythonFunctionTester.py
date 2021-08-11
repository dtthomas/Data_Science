import numpy as np
from sklearn.impute import SimpleImputer

imp_mean = SimpleImputer(missing_values=np.nan, strategy='mean')
X = [[7, 2, 3], [4, np.nan, np.nan], [10, 5, np.nan]]

#This function is used in the training data
# Calculate the mean and variance and then tranform the data
X = imp_mean.fit_transform(X) #doing the same thing as the fit() and tranform() method.

# In testing data we use the fit and tranform seperately.
# Because we use the mean and variance calculated from the training set is used to transform the test data.
# This function is calculating the mean and variance of the each features
# imp_mean.fit(X)  #Return value is a SimpleImputer()
# X = imp_mean.transform(X)  #every missing values will be replaced with the mean value of that column


print(X)


