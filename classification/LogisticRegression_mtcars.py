#Import the Library
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

#Import the dataset
dataset = pd.read_csv('Social_Network_Ads.csv')
dataset
X = dataset.iloc[:,:-1].values #independent
y = dataset.iloc[:,-1].values

# Taking Care of the Missing of the Value
from sklearn.impute import SimpleImputer
imputer = SimpleImputer(missing_values = np.nan,strategy = 'mean')
imputer.fit(X)
X = imputer.transform(X)

# Split the dataset into the training and the test set
from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(X,y,test_size = 0.2,random_state = 2)
X_test

# Feature Scaling
from sklearn.preprocessing import StandardScaler
sc = StandardScaler()
X_train = sc.fit_transform(X_train)
X_test = sc.transform(X_test)

# Feature Scaling
from sklearn.preprocessing import MinMaxScaler
sc = MinMaxScaler()
X_train = sc.fit_transform(X_train)
X_test = sc.transform(X_test)
X_test

# Training the Logistic Regression Model on the Training Set
from sklearn.linear_model import LogisticRegression
classifier = LogisticRegression(random_state = 2)
classifier.fit(X_train,y_train)

#Prediction
print(classifier.predict(sc.transform([[35,88000]])))
y_pred = classifier.predict(X_test)
print(np.concatenate((y_pred.reshape(len(y_pred),1),y_test.reshape(len(y_test),1)),1))

#Make the Confusion Matrix
from sklearn.metrics import confusion_matrix, accuracy_score
cm = confusion_matrix(y_test,y_pred)
print(cm)

accuracy_score(y_test,y_pred)