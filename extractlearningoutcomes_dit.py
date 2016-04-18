import nltk
#Also need to download nltk so call nltk.download() to launch a GUI to do that
# Warning it can take a long time to do that and probably best running from its own python command line


#nltk.download('all')

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

#Output to csv file
OutputFileName="DITLO-SentenceList.csv"
MyCSVFile = open(OutputFileName, "wb")    
SentenceFile = csv.writer(MyCSVFile, delimiter="|")
#Write the header row
SentenceFile.writerow(['TableID', 'Institution', 'Dept','FileNameOnDisk', 'OldKey','LearningOutComeTokens'])

#Attempt to open DB connection
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
#Returnes the data as a Python Dictionary
cursor = cnx.cursor(buffered=True,dictionary=True)
#Parse only the tables with a class value of borders
LearningOutcomesStrainer =SoupStrainer("div", class_="progmod_content")
#DB Query Remember to select the correct Institution and remove the Limit 10 
GetLearningOutcomesQuery =("SELECT * FROM `text-assignment`.`allcourses_raw` WHERE `Institution` = 'DIT' and MATCH (OriginalTextFromDocument) AGAINST ('Learning Outcome')")
cursor.execute(GetLearningOutcomesQuery)
print("Rows Returned ",cursor.rowcount)
print
# Data returned as dictionary wtih the following keys
#Institution', 'FileNameOnDisk', 'Dept', 'ScrappedDate', 'OriginalTextFromDocument', 'OldKey', 'id'
for row in cursor: 
    #print("Keys used in Dictionary",list(row.keys()))
    TextForSoup = row["OriginalTextFromDocument"]
    Inst = row['Institution']
    TableID = row['id']
    Dept = row['Dept']
    FileNameOnDisk = row['FileNameOnDisk']
    OldKey = row['OldKey']
    WebSpans = BeautifulSoup(TextForSoup,"html.parser",parse_only=LearningOutcomesStrainer)
    #print(WebSpans.prettify(formatter="html"))
        
    #TableHeaders = WebTables.findAll("p")
    for head in WebSpans:
        #print(head.prettify(formatter="html"))
        if "Learning Outcome" in head.get_text():
            #Inside the div where Learning Outcomes are listed 
            #Now I have a table get me the table rows
            LearningRows = head.findAll("p")
            for row in LearningRows:
                #print(row.get_text())
                rowValue = row.get_text()
                SentenceList = sent_tokenize(rowValue.strip())
                for sentence in SentenceList:
                    WriteSentence = sentence.strip()
                    WordList = word_tokenize(WriteSentence)
                    #Remove punctation characters from WordList
                    WordList = [i for i in WordList if i not in string.printable]
                    print("Writing Learning Outcome Tokens to Disk ", WordList)
                    SentenceFile.writerow([TableID, Inst, Dept,FileNameOnDisk, OldKey,WordList])
                    #print(Inst,TableID,sentence)
                    MyCSVFile.flush()
                #Sentence Tokenise using NLTK and store back in database
                
cnx.close()