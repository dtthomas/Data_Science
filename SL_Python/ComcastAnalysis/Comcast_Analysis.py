import pandas as pd
import numpy as np
from datetime import datetime
import os
import sys
import traceback
import re
import matplotlib.pyplot as plt
import seaborn as sns
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from wordcloud import WordCloud
import string
from sklearn.feature_extraction.text import CountVectorizer

# ###functions
def getDateTime():
    now = datetime.now()
    now1 = str(now.strftime("%Y-%m-%d %I:%M"))
    return str(now1)

def getScriptPath():
    return os.path.dirname(os.path.realpath(sys.argv[0]))

dn = getScriptPath()  #get the path of the script
os.chdir(dn)  #set working directory as script directory
# dn_parent = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
# dn_parent_2 = os.path.abspath(os.path.join(dn_parent, os.pardir))

# ##Import data into Python environment.
data = pd.read_csv(dn + '/Comcast_telecom_complaints_data.csv')
# print(data.head(5))
# ##output files
ComType_Count = dn + "/output/ComplaintType_Count.csv"

plot_data_monthly = dn + "/output/ComplaintCnt_Monthly.pdf"
plot_data_daily = dn + "/output/ComplaintCnt_daily.pdf"
plot_data_wordcloud = dn + "/output/Complaint_wordcloud.pdf"
plot_ComType_cnt = dn + "/output/ComplaintType_Cnt.pdf"

##date parsing for unicode dates
def dateParsing1(dt):
    #print dt
    #print "inside date parsing 1\n"
    if(pd.isnull(dt) == False):
        date_string = " ".join(re.findall(r'\w+', str(dt))) # normalize delimiters
        #print date_string
        for date_format in ["%d %m %y","%y %m %d"
            ,"%Y %m %d", "%b %d %Y", "%d %b %Y", "%d %m %Y","%d %b %y"
            ,"%B %d %Y","%Y %b %d","%B %d %y","%b %d %y"]:  #can not add delimiters because if unicode the delim are different
            try:
                #print date_format
                datehead = datetime.strptime(date_string,date_format).strftime("%Y-%m-%d")   #change to YMD format
                break
            except ValueError:  ##pass ifd the date_string tried with a wrong format
                pass
        else: # no break
            #print "Date value is different from all the format\n"
            f.write(getDateTime() + " Date value is different from all the format-date_value:%s\n" % dt)
            return dt   #return the string as it is. not in date format.  May cause problems later for importing
            #sys.stderr.write( getDateTime() + " failed to parse " + dt + "\n") #not raising the error
        return datehead

logfile = dn + "/Comcast_Analysis.log"
##set up log file
try:
    f = open(logfile,'w')
    #f2 = open(datafile_hb_missing_accCols,'w')
except (OSError,IOError) as e:
    print("Error value:" + str(e) + "\n")
else:
    f.write(getDateTime() + " Logging file is created successfully:%s\n" % logfile)

f.write("There are %d records in the input file.\n" % len(data))

#eleminate space from column names
data.columns = data.columns.str.replace(' ','_')
# print(data.columns)
# print(data.dtypes)

data_desc = data.describe(include='all')
print(data_desc)

#Check missing values
num_vars = data.columns[data.dtypes != 'object'] #numerical columns
cat_vars = data.columns[data.dtypes == 'object'] #non-numerical columns, categorical or dates
#missing values in percentage
#Numercal columns
data_missing_num = (data[num_vars].isnull().sum().sort_values(ascending=False)/len(data))*100
data_missing_num = pd.DataFrame({'num_col_name':data_missing_num.index, 'missing_val_perc':data_missing_num.values})
print(data_missing_num)
#Non numerical - Categorical, dates
data_missing_cat = (data[cat_vars].isnull().sum().sort_values(ascending=False)/len(data))*100
data_missing_cat = pd.DataFrame({'num_col_name':data_missing_cat.index, 'missing_val_perc':data_missing_cat.values})
print(data_missing_cat)

f.write("\nThere are no missing values in the data.\n")

data = data.drop('Date_month_year', axis=1)
f.write("Date and Date_month_year columns are the same. Dropped Date_month_year column.\n")

#make sure all dates are in the same format
datefields = ['Date']
for datecol in datefields:
    f.write("\n" + getDateTime() + "####processing datefield %s\n" % datecol)
    try:
        data[datecol] = data[datecol].apply(dateParsing1) #make all dates to same format
    except Exception as e:
        f.write(traceback.format_exc())  #catch traceback msg
    else:
        data[datecol]=pd.to_datetime(data[datecol])  #convert from object type to date time
        f.write("\n" + getDateTime() + " Date format change to yyyy-mm-dd - done sucessfully for %s\n" % datecol)

# # ##Provide the trend chart for the number of complaints at monthly and daily granularity levels.
data['Date_year'] = data['Date'].apply(lambda x: x.year)
data['Date_month'] =  data['Date'].apply(lambda x: x.month)
data['Date_ym'] = data['Date_year'].map(str) + "-" + data['Date_month'].map(str)
# data['Date_day'] = data['Date'].apply(lambda x: x.day)

#monthly plot
plt.figure(figsize=(8,4))
plt.xticks(fontsize=5)
plt.xticks(rotation=90)
data_Mnth_grp =  data.groupby('Date_ym')['Customer_Complaint'].count().reset_index(name='Count')
lp_m = sns.lineplot(x='Date_ym', y= 'Count', data = data_Mnth_grp, sort=False,markers = "o")
plt.ylabel("Complaint Count")
# plt.show()
plt.savefig(plot_data_monthly)

#daily plot
plt.figure(figsize=(8,4))
plt.xticks(fontsize=5)
plt.xticks(rotation=90)
data_day_grp =  data.groupby('Date')['Customer_Complaint'].count().reset_index(name='Count')
lp_m = sns.lineplot(x='Date', y= 'Count', data = data_day_grp, sort=False,markers = "o")
plt.ylabel("Complaint Count")
# plt.show()
plt.savefig(plot_data_daily)

data_Mnth_grp = data_Mnth_grp.sort_values(by='Count',ascending=False)
f.write("%s has maximum number of complaints.\n" % data_Mnth_grp.iloc[0]['Date_ym'])

# ##Provide a table with the frequency of complaint types.
# ##Which complaint types are maximum i.e., around internet, network issues, or across any other domains.
nltk.download('stopwords')
corpus = []
all_stopwords = stopwords.words('english')
all_stopwords.append('comcast')
all_stopwords.append('complaint')
for i in range(0,len(data)):
    complaint = re.sub('[^a-zA-Z]',' ', data['Customer_Complaint'][i])
    complaint = complaint.lower()
    complaint = complaint.translate(str.maketrans('', '', string.punctuation)) #remove punctuation
    complaint = complaint.split()
    ps = PorterStemmer()
    complaint = [ps.stem(word) for word in complaint if not word in set(all_stopwords)] #remove stop words and find stem
    complaint = ' '.join(complaint)
    corpus.append(complaint)
# print(type(corpus))
corpus = list(filter(None, corpus)) #remove empty strings
# print(corpus)
str_corpus = str(corpus)
str_corpus = str_corpus.replace("'","") #replace the quotes with nothing
# print(all_stopwords)
# print(type(all_stopwords))

#plot wordcloud
width = 12
height = 12
plt.figure(figsize=(width, height))
#text = 'all your base are belong to us all of your base base base'
wordcloud = WordCloud(width=1800,height=1400,background_color='white').generate(str_corpus)
plt.imshow(wordcloud)
plt.axis("off")
# plt.show()
plt.savefig(plot_data_wordcloud)

#count of complaint types
# Count Vectorizer
vect = CountVectorizer()
vects = vect.fit_transform(corpus)

# Select the first five rows from the data set
td = pd.DataFrame(vects.todense())
td.columns = vect.get_feature_names()
term_document_matrix = td.T
term_document_matrix.columns = ['Doc '+str(i) for i in range(1, len(term_document_matrix.columns)+1)]
term_document_matrix['total_count'] = term_document_matrix.sum(axis=1)
#save to file
term_document_matrix.reset_index(inplace=True)
term_document_matrix = term_document_matrix.sort_values(by ='total_count',ascending=False)
tdm_TotCnt = term_document_matrix[['index','total_count']]
tdm_TotCnt.to_csv(ComType_Count,sep=',',index=False,encoding='utf-8')

#plot count
# Top 25 words
term_document_matrix = term_document_matrix[:25]
# print(term_document_matrix)
plt.figure(figsize=(6,4))
plt.bar(term_document_matrix['index'],term_document_matrix['total_count'].tolist(),color=['lightblue'],edgecolor='black')
plt.xlabel("Complaint Type")
plt.ylabel("Count")
plt.xticks(fontsize=8)
plt.xticks(rotation=90)
plt.title("Top 25 Complaint Types")
# plt.show()
plt.savefig(plot_ComType_cnt)

f.close() #close log file