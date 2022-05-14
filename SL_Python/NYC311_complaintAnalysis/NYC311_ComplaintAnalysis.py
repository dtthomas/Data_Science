# ###NYC 311 complaint Analysis#####
import pandas as pd
import numpy as np
from datetime import datetime
import os
import sys
import traceback
import re
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.api as sm
from statsmodels.formula.api import ols
from scipy.stats import chi2_contingency

# ###functions
def getDateTime():
    now = datetime.now()
    now1 = str(now.strftime("%Y-%m-%d %I:%M"))
    return str(now1)

def getScriptPath():
    return os.path.dirname(os.path.realpath(sys.argv[0]))

dn = getScriptPath()  #get the path of the script
os.chdir(dn)  #set working directory as script directory
dn_parent = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
dn_parent_2 = os.path.abspath(os.path.join(dn_parent, os.pardir))

# ##Q1. Import a 311 NYC service request.
data = pd.read_csv(dn_parent_2 + '/data/NYC311_Service_Requests_from_2010_to_Present.csv')
#print(data[['Created Date','Closed Date']].head(5))
# ##output files
grpBy_Loc = dn + "/output/data_GrpBy_LocType.csv"
grpBy_City = dn + "/output/data_GrpBy_City.csv"
grpBy_ComTyp = dn + "/output/data_GrpBy_ComTyp.csv"
dataDesc = dn + "/output/data_description.csv"
NumMissing_perc = dn + "/output/NumericCols_MissingVals_Percentage.csv"
CatMissing_perc = dn + "/output/CategoricalCols_MissingVals_Percentage.csv"

plot_ComType_ReqCloseTime = dn + "/output/ComplaintType_ReqCloseTime_plot.pdf"
plot_Monthly_counts = dn + "/output/ComplaintCnt_Monthly.pdf"
plot_ComplaintType_counts = dn + "/output/ComplaintTypes_Cnt.pdf"
plot_Borogh_counts = dn + "/output/ComplaintBorogh_Cnt.pdf"
plot_BoroghComTyp_ReqCloseTime = dn + "/output/ComType_Borogh_ReqCloseTime.pdf"

#Global vars
observations = "\n\n****OBSERVATIONS****\n"
ln = 0

##date parsing for unicode dates
def dateParsing1(dt):
    #print dt
    #print "inside date parsing 1\n"
    if(pd.isnull(dt) == False):
        date_string = " ".join(re.findall(r'\w+', str(dt))) # normalize delimiters
        #print date_string
        for date_format in ["%Y %m %d %H %M %S","%Y %m %d %H %M","%m %d %Y %I %M %S %p"
            ,"%Y %m %d %I %M %S %p","%m %d %y %H %M"
            , "%Y %m %d", "%b %d %Y", "%d %b %Y", "%d %m %Y","%d %b %y"
            ,"%B %d %Y","%Y %b %d","%B %d %y","%b %d %y"]:  #can not add delimiters because if unicode the delim are different
            try:
                #print date_format
                datehead = datetime.strptime(date_string,date_format).strftime("%Y-%m-%d %H:%M:%S")   #change to YMD format
                break
            except ValueError:  ##pass ifd the date_string tried with a wrong format
                pass
        else: # no break
            #print "Date value is different from all the format\n"
            f.write(getDateTime() + " Date value is different from all the format-date_value:%s\n" % dt)
            return dt   #return the string as it is. not in date format.  May cause problems later for importing
            #sys.stderr.write( getDateTime() + " failed to parse " + dt + "\n") #not raising the error
        return datehead

logfile = dn + "/NYC311_ComplaintAnalysis.log"
##set up log file
try:
    f = open(logfile,'w')
    #f2 = open(datafile_hb_missing_accCols,'w')
except (OSError,IOError) as e:
    print("Error value:" + str(e) + "\n")
else:
    f.write(getDateTime() + " Logging file is created successfully:%s\n" % logfile)

f.write("There are %d records in the input file.\n" % len(data))

# ##Q2. Read or convert the columns ‘Created Date’ and Closed Date’ to datetime datatype
datefields = ['Created Date','Closed Date']
for datecol in datefields:
    f.write("\n" + getDateTime() + "####processing datefield %s\n" % datecol)
    try:
        data[datecol] = data[datecol].apply(dateParsing1) #make all dates to same format
    except Exception as e:
        f.write(traceback.format_exc())  #catch traceback msg
    else:
        data[datecol]=pd.to_datetime(data[datecol])  #convert from object type to date time
        f.write("\n" + getDateTime() + " Date format change to yyyy-mm-dd HH:MM:SS - done sucessfully for %s\n" % datecol)

#print(data.dtypes)
#Exploratory Data Analysis
data_desc = data.describe()
data_desc.to_csv(dataDesc,sep=',',index=True,encoding='utf-8')  #write the records to a file
#By looking at the description we can see that there are some columns which do not have values.
#Check missing values
num_vars = data.columns[data.dtypes != 'object'] #numerical columns
cat_vars = data.columns[data.dtypes == 'object'] #non-numerical columns, categorical or dates
#missing values in percentage
#Numercal columns
data_missing_num = (data[num_vars].isnull().sum().sort_values(ascending=False)/len(data))*100
data_missing_num = pd.DataFrame({'num_col_name':data_missing_num.index, 'missing_val_perc':data_missing_num.values})
data_missing_num.to_csv(NumMissing_perc,sep=',',index=False,encoding='utf-8')  #write the records to a file
#Non numerical - Categorical, dates
data_missing_cat = (data[cat_vars].isnull().sum().sort_values(ascending=False)/len(data))*100
data_missing_cat = pd.DataFrame({'num_col_name':data_missing_cat.index, 'missing_val_perc':data_missing_cat.values})
data_missing_cat.to_csv(CatMissing_perc,sep=',',index=False,encoding='utf-8')

#data cleaning - remove the empty fields
# empty_cols = ['School or Citywide Complaint','Vehicle Type','Taxi Company Borough','Taxi Pick Up Location','Garage Lot Name']
empty_cols = data_missing_num[data_missing_num['missing_val_perc']==100].num_col_name.tolist() #columns with 100% missing values
data_1 = data.drop(data.loc[:,empty_cols], axis=1)
f.write("Data cleaning - %s columns are deleted because they are empty. None of the Non-numerical columns are empty." % empty_cols)

#eleminate space from column names
data_1.columns = data_1.columns.str.replace(' ','_')

# ##Q2. create a new column ‘Request_Closing_Time’ as the time elapsed between request creation and request closing.
data_1['Request_Closing_Time'] = ((data_1['Closed_Date'] - data_1['Created_Date']).dt.total_seconds())/60 #in minutes
# ##Q3. Provide major insights/patterns that you can offer in a visual format (graphs or tables);
# at least 4 major conclusions that you can come up with after generic data mining.
# Complaint Types and Request Closing Time
p = sns.catplot(x="Complaint_Type", y="Request_Closing_Time",data=data_1)
plt.xticks(fontsize=5)
plt.xticks(rotation=90)
plt.ylim(0,15000)  #There are outliers. So to get a good idea, limited the y axis range
# plt.figure(figsize=(3, 3))
# p.figure.show()
plt.savefig(plot_ComType_ReqCloseTime)
ln = ln + 1
observations = observations + str(ln) + " - By looking at the plot, we can see that the complaint types which are taking longer closing times are Derelict Vehicle,Illegal Parking and Blocked Driveway.\n"

# group by status
data_1['Status_1'] = np.where(data_1['Status']== 'Closed', 'Closed', 'Open')
data_status_grp = data_1.groupby(['Status_1'])['Complaint_Type'].count().reset_index(name="Count")
data_status_grp['perc'] = (data_status_grp['Count']/len(data_1))*100
data_closed = data_status_grp[data_status_grp['Status_1']=='Closed']
ln = ln + 1
observations = observations + str(ln) + " - When you group by data based on status, we can see that %f percentage complaints are resolved so far.\n" % data_closed['perc']

#group by created month
data_1['Created_Year'] = data_1['Created_Date'].apply(lambda x: x.year)
data_1['Created_Month'] =  data_1['Created_Date'].apply(lambda x: x.month)
data_1['Created_ym'] = data_1['Created_Year'].map(str) + "-" + data_1['Created_Month'].map(str)
data_1['Created_Day'] = data_1['Created_Date'].apply(lambda x: x.day)
data_1['Created_DayOfWeek'] = data_1['Created_Date'].apply(lambda x: x.dayofweek)
dmap = {0:'Mon',1:'Tue',2:'Wed',3:'Thur',4:'Fri',5:'Sat',6:'Sun'}
data_1['Created_DayOfWeek']=data_1['Created_DayOfWeek'].map(dmap)
#plot
plt.figure(figsize=(8,4))
plt.xticks(fontsize=5)
plt.xticks(rotation=90)
data_CreMnth_grp = data_1.groupby('Created_ym')['Complaint_Type'].count().reset_index(name='Count')
lp_m = sns.lineplot(x='Created_ym', y= 'Count', data = data_CreMnth_grp, sort=False,markers = "o")
plt.ylabel("Complaint Count")
# plt.show()
plt.savefig(plot_Monthly_counts)
data_CreMnth_grp_srt = data_CreMnth_grp.sort_values('Count',ascending=False)
ln = ln + 1
observations = observations + str(ln) + " - %s received the largest number of calls. %s received minimum number of calls." % (data_CreMnth_grp_srt.iloc[0]['Created_ym'],data_CreMnth_grp_srt.iloc[-1]['Created_ym'])
observations = observations + "We can see in the plot that 2015-March has very low number of complaints. I am not sure there is dip in 2015-March.\n"

# Complaints per Borough through the year
data_1.groupby(['Created_ym','Borough']).size().unstack().plot(figsize=(15,6))
plt.legend(loc='center left', bbox_to_anchor=(1.0, 0.5));
plt.ylabel("Complaint Count")
plt.xticks(fontsize=5)
plt.xticks(rotation=90)
plt.savefig(plot_Borogh_counts)

#Complaint Types Count
data_ComTyp_grp = data_1.groupby(['Complaint_Type'])['Complaint_Type'].count().sort_values(ascending=False).reset_index(name="Count") #returned a df
ln = ln + 1
observations = observations + str(ln) +  " - More frequent complaint types are %s,%s." % (data_ComTyp_grp['Complaint_Type'][0],data_ComTyp_grp['Complaint_Type'][1])
observations = observations + "%s and %s are right after that." % (data_ComTyp_grp['Complaint_Type'][2],data_ComTyp_grp['Complaint_Type'][3])
observations = observations + "%s and %s are right after that in the same level of count." % (data_ComTyp_grp['Complaint_Type'][4],data_ComTyp_grp['Complaint_Type'][5])
observations = observations + "We can see that there are different kinds of noise complaints. City official may need to do something about it.\n "
plt.figure(figsize=(6,4))
plt.barh(data_ComTyp_grp['Complaint_Type'].tolist(),data_ComTyp_grp['Count'].tolist(),color=['lightblue'],edgecolor='black')  #barh for horizontal bar graph
plt.xlabel("Complaint Type")
plt.ylabel("Count")
plt.title("Counts of different Complaint Types")
#plt.show()
plt.savefig(plot_ComplaintType_counts)

# Q4. Order the complaint types based on the average ‘Request_Closing_Time’, grouping them for different locations.
#group them based on Location Types
data_loc_grp = (data_1.groupby((['Borough','Complaint_Type']), as_index=False)['Request_Closing_Time'].mean()).sort_values('Request_Closing_Time')
data_loc_grp.to_csv(grpBy_Loc,sep=',',index=False,encoding='utf-8')  #write the records to a file
# observations = observations + "%s is the Borogh with minimum average Request closing time - %f.\n" % (data_loc_grp.iloc[0]['Borogh'],data_loc_grp.iloc[0]['Request_Closing_Time'])
# observations = observations + "%s is the Borogh with maximum average Request closing time - %f.Need further investigation to find out why the closing time is high.\n" % (data_loc_grp.iloc[-1]['Borogh'],data_loc_grp.iloc[-1]['Request_Closing_Time'])

f.write(observations)
# Q5. Please note: For the below statements you need to state the Null and Alternate and then provide a statistical test to accept or reject the Null Hypothesis along with the corresponding ‘p-value’.
#Whether the average response time across complaint types is similar or not (overall).
f.write("\n\n****Hypothesis Testing****\n")
f.write("Test 1: Whether the average response time across complaint types is similar or not (overall)")
f.write("H0: There is no significant difference in Request_Closing_Time across different complaint types.\n")
f.write("H1: There is at least one complaint type with significant difference in the Request_Closing_Time.\n")
f.write("\nSince there are more than 2 means to compare, we are going to use one-way ANOVA test.\n")
data_stat = data_1[['Complaint_Type','Request_Closing_Time']]
data_stat.dropna(inplace=True)
# ANOVA using Ordinary Least Squares (OLS) model
model = ols('Request_Closing_Time ~ Complaint_Type', data=data_stat).fit()
anova_table = sm.stats.anova_lm(model, typ=2) #use type 2 because there is no interaction between independant variable, because there is one independant variable in this dataframe
f.write("Anova table is:\n")
f.write(anova_table.to_string())
if(anova_table.iloc[0]['PR(>F)']<0.05):
    f.write("Since the p-value is less than the cut off value 0.01, we can reject the Null hypothesis. That means there is at least one complaint type which has the Request_Closing_Time mean different than the others.\n")
else:
    f.write("Failed to Reject H0. That means there are no significant difference between the complaint types.\n.")

#Are the type of complaint or service requested and location related?
f.write("\n\nTest 2: Are the type of complaint or service requested and location related?\n")
f.write("We are going to perform chi-square test to see if Complaint Type and Location Type are related.\n")
f.write("H0:Complaint Type and Location Types are independent - means not related.\n")
f.write("H1:Complaint Type and Location Types are dependent - means related.\n")

data_chi = data_1[['Complaint_Type','Location_Type']]
data_chi.dropna(inplace=True)
data_crosstab = pd.crosstab( data_chi["Complaint_Type"],data_chi["Location_Type"])
stat, p, dof, expected = chi2_contingency(data_crosstab)
# interpret p-value
alpha = 0.05
f.write("p value is " + str(p) + "\n")
if p <= alpha:
    f.write('Dependent (reject H0) - means Complaint Type and Location Type are related.\n')
else:
    f.write('Independent (H0 holds true) - means Complaint Type and Location Type are NOT related.\n')

f.close()

