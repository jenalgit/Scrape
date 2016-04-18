import nltk
#Also need to download nltk so call nltk.download() to launch a GUI to do that
# Warning it can take a long time to do that and probably best running from its own python command line


#nltk.download('all')


#WORK AROUND FOR ERROR IN POS_TAG March 2016
#https://github.com/nltk/nltk/commit/d3de14e58215beebdccc7b76c044109f6197d1d9#diff-26b258372e0d13c2543de8dbb1841252

from nltk.tokenize import sent_tokenize, word_tokenize
# Import the beautiful soup library
from bs4 import BeautifulSoup
from bs4 import SoupStrainer
#Import the MySQL database connector
import mysql.connector
from mysql.connector import errorcode

import unicodecsv as csv
import string
from nltk.tag import pos_tag
from nltk.tag.util import str2tuple

#DB Config
#Took out  as no password used
#Took out 
config = {
  'user': 'root',
  'password': '',
  'host': '127.0.0.1',
  'port': '3306',
  'database': 'text-assignment',
  'raise_on_warnings': True,
}


try:
    cnx = mysql.connector.connect(**config)
    print(cnx)
except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("Something is wrong with your user name or password")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("Database does not exist")
    else:
        print(err)

#Output to csv file
OutputFileName="POSList.csv"
MyCSVFile = open(OutputFileName, "wb")    
SentenceFile = csv.writer(MyCSVFile, delimiter="|")
#Write the header row
#['Dept', 'TableID', 'OldKey', 'Cleaned_LearningOutComeTokens', 'FileNameOnDisk', 'learning_outcomes_cleansed_id', 'Institution']
SentenceFile.writerow(['TableID', 'Institution', 'Dept','FileNameOnDisk', 'OldKey','Cleaned_LearningOutComeTokens','POS_Tags'])

#Returnes the data as a Python Dictionary
cursor = cnx.cursor(buffered=True,dictionary=True)
#DB Query Remember to remove the Limit 10 
GetLearningOutcomesQuery =("SELECT * FROM `text-assignment`.`learning_outcomes_cleansed` ")
cursor.execute(GetLearningOutcomesQuery)
print("Rows Returned ",cursor.rowcount)

for row in cursor: 
    #print("Keys used in Dictionary",list(row.keys()))
    #Keys used in Dictionary ['Dept', 'TableID', 'OldKey', 'Cleaned_LearningOutComeTokens', 'FileNameOnDisk', 'learning_outcomes_cleansed_id', 'Institution']
    TextToUse = row["Cleaned_LearningOutComeTokens"]
    Inst = row['Institution']
    TableID = row['TableID']
    Dept = row['Dept']
    FileNameOnDisk = row['FileNameOnDisk']
    OldKey = row['OldKey']
    tokens = word_tokenize(TextToUse)
    #print("My Tokens are ", tokens)
    PartsOfSpeech = pos_tag(tokens)
    print("Speech Parts", PartsOfSpeech)
    SentenceFile.writerow([TableID, Inst, Dept,FileNameOnDisk, OldKey,tokens,PartsOfSpeech])
    MyCSVFile.flush()
    
cnx.close()   
