# ###NYC 311 complaint Analysis#####
import pandas as pd
#import numpy as np
from datetime import datetime
import os
import sys
import traceback
import re

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

# ##Import a 311 NYC service request.
data = pd.read_csv(dn_parent_2 + '/data/NYC311_Service_Requests_from_2010_to_Present.csv')
#print(data.head())

#make date in YMD format
def validateDate(dt):
    months = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12'] #used it to get one digit moths 0 padded)
    if(pd.isnull(dt) == False):
        #if dt != '':
        try:
            datehead = "{0:}-{1:}-{2:}".format(dt.year,months[dt.month-1],dt.day) #to deal with dates less than 1900
        except:
            f.write(getDateTime() + " " + str(dt) + " causing problems in date conversion\n")
            f.write(traceback.format_exc())
        #else:
        #f.write(getDateTime() + " " + str(dt) + " converted suucessfully\n")
        return datehead

##date parsing for unicode dates
def dateParsing1(dt):
    #print dt
    #print "inside date parsing 1\n"
    if(pd.isnull(dt) == False):
        date_string = " ".join(re.findall(r'\w+', str(dt))) # normalize delimiters
        #print date_string
        for date_format in ["%Y %m %d %H %M %S","%Y %m %d %I %M %S %p", "%Y %m %d", "%b %d %Y", "%d %b %Y", "%d %m %Y","%d %b %y","%B %d %Y","%Y %b %d","%B %d %y","%b %d %y"]:  #can not add delimiters because if unicode the delim are different
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

logfile = dn + "/NYC311_ComplaintAnalysis.log"
##set up log file
try:
    f = open(logfile,'w')
    #f2 = open(datafile_hb_missing_accCols,'w')
except (OSError,IOError) as e:
    print("Error value:" + str(e) + "\n")
else:
    f.write(getDateTime() + " Logging file is created successfully:%s\n" % logfile)

f.close()

