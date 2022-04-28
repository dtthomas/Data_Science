###Movie review Recommender system
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import pairwise_distances

#Read data file
df = pd.read_csv("../data/Amazon - Movies and TV Ratings.csv")

###Interim files
data_temp = "./data_temp.csv"


print("####Exploratory Data Analysis#######")
#1. Which movies have maximum views/ratings?
#2. What is the average rating for each movie? Define the top 5 movies with the maximum ratings.
#3. Define the top 5 movies with the least audience.

#to get count and mean
df_desc = df.describe()
#Transpose the data to draw a graph
df_desc_T = df_desc.T
#sort the df based on descending order of count.
df_desc_T_cnt = df_desc_T.sort_values(by='count',ascending=False)
#"""
#Movie with most views - Movie 127, has 2313 views
#Average rating of each movie can be found in the mean column
df_desc_T_avgR = df_desc_T.sort_values(by='mean',ascending=False)

#To show the Top 5 movies with maximum ratings by looking at the mean column,
#I am going to select the top 5 rows from df_desc_T_avgR
df_desc_T_topAvgR = df_desc_T_avgR.head(5)
###Plot the graph - Top avg Ratings
# MovieNames = df_desc_T_topAvgR.index
# ratings = df_desc_T_topAvgR['mean']
# plt.bar(MovieNames,ratings)
# plt.xlabel("Movies")
# plt.ylabel("Ratings")
# plt.title("Movies Vs AvgRatings")
# plt.show()
#this actually doesn't show anything because if the movie only got one rating and it is 5, it will show up in the top 5 . So I am assuming, the question is not actually asking for this.

#To show the Top 5 movies with maximum view count,
#I am going to select the top 5 rows from df_desc_T_cnt
df_desc_T_topVwCnt = df_desc_T_cnt.head(5)
###Plot the graph - Top count of views
MovieNames = df_desc_T_topVwCnt.index
views = df_desc_T_topVwCnt['count']
plt.bar(MovieNames,views)
plt.xlabel("Movies")
plt.ylabel("View Count")
plt.title("Movies with Max View Count")
plt.show()
#Top movies are Movie 127, 140, 16, 103 and 29
print(f'Movies with top views are:{MovieNames}\n')

#To show the Top 5 movies with least audience,
#I am going to select the last 5 rows from df_desc_T_cnt
#df_desc_T_LeastVwCnt = df_desc_T_cnt.tail(5)
df_desc_T_LeastVwCnt = df_desc_T_cnt[df_desc_T_cnt['count']==1] #I see that the lest no of view in the data set is 1
###Plot the graph - Top count of views
MovieNames = df_desc_T_LeastVwCnt.index
views = df_desc_T_LeastVwCnt['count']
plt.bar(MovieNames,views)
plt.xlabel("Movies")
plt.ylabel("View Count")
plt.title("Movies with least audience")
plt.show()

print(f"There are {len(df_desc_T_LeastVwCnt.index)} movies with only one view. Those are the least audience movies.")
print(f"Those movies are: {sorted(list(df_desc_T_LeastVwCnt.index))}\n\n")

##Note: I also see that the ratings ranges from 1 to 5, not -1 to 10 as per the problem statement.
#"""

print("####Recommender system ######")
print("####****1. Divide the data into training and test data")
print("###Group similar users??")
#There are 206 movies and 4848 users
df2 = df.set_index("user_id")
df2_T = df2.T
df2_T_desc = df2_T.describe()
sparsity = (df2_T_desc.sum(axis=1)[0])/(4848*206)
sparsity *= 100
Avg_user_movie_rat = (df2_T_desc.sum(axis=1)[0])/4848
max_no_rat_user = df2_T_desc.max(axis=1)[0]
print(f"Only {round(sparsity,2)} percentage of User-Movie ratings have value. The file is extremely sparse.\nThe maximum number of rating a user has given is {max_no_rat_user}.\nAverage number of movie ratings a user has given is {round(Avg_user_movie_rat,2)}.")
print("Since the a user is rated only 1 movie average, I am not sure how can I split this data set in to Train and test using users.\nSo I am going to split the data not based on users but based on movies, means group similar movies instead grouping similar users.\n\n")

print("###Group similar movies???")
avg_view_perMovie = df_desc_T.mean(axis=0)[0]
print(f"Avg view per movie is {round(avg_view_perMovie,2)}.\n")

print("Decided to take 30% of view records of a movie to test data.\nEx: If there are 20 ratings for a movie, then we take 6 ratings to test data.\n")
df_desc_T['test_cnt'] = df_desc_T['count']*0.3
df_desc_T['test_cnt'] = df_desc_T['test_cnt'].apply(np.floor)
#df_desc_T.to_csv(data_temp,sep=',',index=False,encoding='utf-8')

#Create a dictionary with movie and no of ratings that I need to move to test data
Movie_testCnt = dict(zip(df_desc_T.index, df_desc_T.test_cnt))

train = df.copy()
train = train.set_index('user_id')
train = train.fillna(0)  #0 means no review
train = train.astype(int)
ratings=train.copy()

test = train.copy()
for col in test.columns:
    test[col].values[:] = 0

for mov in train.columns:
    #print(mov)
    test_cnt=int(Movie_testCnt[mov])
    if test_cnt>0:
        #select the ratings to move to test data randomly
        test_ratings = np.random.choice((train.loc[:,mov].values).nonzero()[0],size=test_cnt,replace=False)
        for t in test_ratings:
            train.iloc[t][mov]=0
            test.iloc[t][mov]=ratings.iloc[t][mov]

train.to_csv('./train.csv',sep=',',index=True,encoding='utf-8')
test.to_csv('./test.csv',sep=',',index=True,encoding='utf-8')
print("Successfully devided the data in to test and train data\n\n")
print("####****2. Build a recommendation model on training data")
train=train.T
movie_similarity = pairwise_distances( train, metric="cosine" )
np.fill_diagonal( movie_similarity, 0 )

ratings_matrix = pd.DataFrame(movie_similarity,index=train.index,columns=train.index)

ratings_matrix.to_csv(data_temp,sep=',',index=True,encoding='utf-8')
print("Successfully built the similarity matrix between movies\n\n")
#put recommendation system in to action
try:
    user_inp=input('Enter the reference movie title based on which recommendations are to be made: ')

    similarity = ratings_matrix.loc[user_inp]
    similarity=similarity.sort_values(ascending=False)
    print(f"Recommended movies based on your choice of {user_inp }: \n")
    print(similarity.index[0:10])
    print("\n\n")
except:
    print("The movie name you have entered does not exist in the list, however, below are the top movies recommended in general\n\n")

print("####****3. Make predictions on the test data")
print("Failed to do this part.")