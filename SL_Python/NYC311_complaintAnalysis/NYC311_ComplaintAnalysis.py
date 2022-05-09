# ###NYC 311 complaint Analysis#####
import pandas as pd
#import numpy as np
from datetime import datetime
import os
import sys
import traceback
import re
import matplotlib.pyplot as plt

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
dataDesc = dn + "/output/data_description.csv"
NumMissing_perc = dn + "/output/NumericCols_MissingVals_Percentage.csv"
CatMissing_perc = dn + "/output/CategoricalCols_MissingVals_Percentage.csv"

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

# ##Q2. create a new column ‘Request_Closing_Time’ as the time elapsed between request creation and request closing.
#print(data.dtypes)
#data cleaning - delete rows which do not have a Created Date or Closed Date
data_1 = data[(~data['Created Date'].isnull()) & (~data['Closed Date'].isnull())]
f.write("\nData cleaning: %d rows are eleminated because they do not have either Created Date or Closed Date.\n" % (len(data)-len(data_1)))
data_1['Request_Closing_Time'] = ((data_1['Closed Date'] - data_1['Created Date']).dt.total_seconds())/60 #in minutes
#print(data.dtypes)
#print(data[['Created Date','Closed Date','Request_Closing_Time']].head(5))

# Q4. Order the complaint types based on the average ‘Request_Closing_Time’, grouping them for different locations.
#group them based on Location Types
data_loc_grp = (data_1.groupby('Location Type', as_index=False)['Request_Closing_Time'].mean()).sort_values('Request_Closing_Time')
data_loc_grp.to_csv(grpBy_Loc,sep=',',index=False,encoding='utf-8')  #write the records to a file
print("\n%s is the location type with minimum average Request closing time - %f.\n" % (data_loc_grp.iloc[0]['Location Type'],data_loc_grp.iloc[0]['Request_Closing_Time']))
print("%s is the location type with minimum average Request closing time - %f.\n" % (data_loc_grp.iloc[-1]['Location Type'],data_loc_grp.iloc[-1]['Request_Closing_Time']))
f.write("%s is the location type with minimum average Request closing time - %f.\n" % (data_loc_grp.iloc[0]['Location Type'],data_loc_grp.iloc[0]['Request_Closing_Time']))
f.write("%s is the location type with minimum average Request closing time - %f.\n" % (data_loc_grp.iloc[-1]['Location Type'],data_loc_grp.iloc[-1]['Request_Closing_Time']))

# ##Q3. Provide major insights/patterns that you can offer in a visual format (graphs or tables);
# at least 4 major conclusions that you can come up with after generic data mining.
data_desc = data.describe()
data_desc.to_csv(dataDesc,sep=',',index=True,encoding='utf-8')  #write the records to a file
#By looking at the description we can see that there are some columns which do not have values.
#Check missing values
num_vars = data.columns[data.dtypes != 'object'] #numerical columns
cat_vars = data.columns[data.dtypes == 'object'] #non-numerical columns, categorical or dates
#missing values in percentage
data_missing_num = (data[num_vars].isnull().sum().sort_values(ascending=False)/len(data))*100
data_missing_num.to_csv(NumMissing_perc,sep=',',index=True,encoding='utf-8')  #write the records to a file
data_missing_cat = (data[cat_vars].isnull().sum().sort_values(ascending=False)/len(data))*100
data_missing_cat.to_csv(CatMissing_perc,sep=',',index=True,encoding='utf-8')

#data cleaning - remove the empty fields
# empty_cols = ['School or Citywide Complaint','Vehicle Type','Taxi Company Borough','Taxi Pick Up Location','Garage Lot Name']
data_missing_num.reset_index(drop=True,inplace=True)
empty_cols = data_missing_num[data_missing_num.iloc[:,1]==100]
print(empty_cols)
# data_2 = data.drop(data.loc[:,empty_cols], axis=1)
# f.write("Data cleaning - %s columns are deleted because they are empty." % empty_cols)



#plot Complaint types distribution
#data_ComTyp_grp = data_2.groupby(['Complaint Type '])['Complaint Type '].count().sort_values(ascending=False)

f.close()

