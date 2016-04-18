'''
Created on 7 Jan 2016

@author: michael.obrien
'''

import os
from bs4 import BeautifulSoup
from bs4 import SoupStrainer
import unicodecsv as csv
import re
from _csv import QUOTE_NONE


def main(OutputFileName="DITISCEDCodes.csv", FileDelimiter=";"):
    #Open the file for writing
    MyCSVFile = open(OutputFileName, "wb") 
    DITCodesFileHandle = csv.writer(MyCSVFile, delimiter=FileDelimiter,quoting = csv.QUOTE_NONE,quotechar='')
    
    #Structure of the 
    #<span class="inline_label">
    #ISCED:
    #</span>
    #<span class="inline_value">
    #0410: Business &amp; Admin not defined
    #</span>
    #Strain using #div class="progmod_content" so the rest of the html file isn't parsed by BS
    
    #Write the header row
    DITCodesFileHandle.writerow(['Course', 'ISCEDCode'])
    
    ISCEDStrainer = SoupStrainer("div",class_="progmod_content")
    #Process the files in the folder  
    for fileToProcess in os.listdir(os.curdir):
        #Get all the html files
        if fileToProcess.endswith(".html"):
            #Open the file into BS, straining it so only the section we want is available, 
            WebText = BeautifulSoup(open(fileToProcess),"html.parser",parse_only=ISCEDStrainer)
            #print(WebText.prettify(formatter = "html"))
            #Because there is no unique way to get the ISCED use this from Stackoverflow to 
            #Use the ISCED code to up back up the parse tree to the parent then back to the next sibling
            for el in WebText(text=re.compile(r'ISCED')):
                myText=el.parent.find_next_sibling().get_text()
                #Print the filename without the extension and the ISCED code found
                #Remove the extra characters that come in with BSoup text
                myText=myText.strip()
               # myText=myText.strip()
                Name = str(os.path.splitext(fileToProcess)[0])
                print(Name, myText)
                #Write the value to file
                DITCodesFileHandle.writerow([Name,myText])
                MyCSVFile.flush()
            #myText = re.findall("ISCED:(.*)",WebText.prettify())
            #myText= re.compile("ISCED:(.*)")
    
    #close the file after processing the folder
    print("Finished processing the files")        
    MyCSVFile.close       

if __name__ == '__main__':
    main()

