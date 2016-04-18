#===============================================================================
# Name: ParseDIT
# Purpose: To parse the DIT websites listing its courses and their content 
# 
# Author: Michael O'Brien
# Requirements:  
# Python 2.7.10 including pip package to install the BeautifulSoup4 and selenium modules
# Firefox web browser to be driven by python selenium to open urls and navigate

# Libraries
# BeautifulSoup4 used to extract the content from the html
# Selenium is used to parse the overlay that shows the course lists for each department
# urlib2 used to call the url's 
# unicode csv to write unicode to csv files

# Created: Nov 2015
#===============================================================================

# Import the beautiful soup library
from bs4 import BeautifulSoup
from bs4 import SoupStrainer
# import requests library to actually go get the webpage for Beautiful Soup (previously used urllib2 but requests seems better able to handle urls with spaces
import requests


# Import the unicode csv library installed using pip unicodecsv 
import unicodecsv as csv
import sys
import os.path #needed to get the list of existing files processed to avoid pulling them again
#Needed to write unicode to text file
import codecs
from string import replace

def get_navi_tabs(SourceHTML):
    NaviURLs =[]
    try:
        #Getting the urls for the various tabs on a DIT programme/module page and return an array
        ModTabList = SourceHTML.find("ul",class_="progmod_tabs") 
            #Populate the array with the urls for the individual tabs
        for links in ModTabList.find_all("a"):
            NaviURLs.append(links.get('href'))
        print("Navigation Tabs = ",NaviURLs)
        return NaviURLs #
    except :
        e = sys.exc_info()
        print(e)
        Value = "PARSING Navigation Tabs ERROR"
        return Value

def ParseModulePages(ModuleURL,NavigationTabsStrainer,ModuleDetailsStrainer,ModuleTimeOut=10, BaseURL='http://www.dit.ie'):
    #
    ModTabs =[]
    ExtractedContent =''
    #get the module content now e.g process this type of page http://www.dit.ie/catalogue/Modules/Details/ACCT9022
    #With a 3 second timeout 
    
    with requests.Session() as s:
        #This will make sure the session is closed as soon as the with block is exited, even if unhandled exceptions occurred.
        ModuleWebPage = s.get(ModuleURL,timeout=ModuleTimeOut)
        if ModuleWebPage.status_code == 200:
            #Parse the tabs because the webpage was returned successfully
            NaviTabs = BeautifulSoup(ModuleWebPage.text,"html.parser",parse_only=NavigationTabsStrainer)
            # Call the function to get the navigation tabs
            ModTabs = get_navi_tabs(NaviTabs)
            #Now start to get the contents of the various tabs after creating a h2 header
            ExtractedContent = "<h2> Module Content </h2>"
            ExtractedContent = ExtractedContent + "<div>" + str(ModuleURL) +"</div>"
            for Tab in ModTabs:
                #print(Tab)
                ModTabUrl = ModuleURL + str(Tab)
                #Get the content from the tab
                Modresponse = s.get(ModTabUrl,timeout=3)
                print("Module TabURL----",Modresponse," for ", ModTabUrl)
                ModContent = BeautifulSoup(Modresponse.text,"html.parser",parse_only=ModuleDetailsStrainer)
                #Add a heading to separate out each new block of text
                ExtractedContent = ExtractedContent + "<div><h3>" + str(Tab).replace("?tab=", '').strip() + "</3></div>"
                ExtractedContent = ExtractedContent + ModContent.prettify(formatter = "html")
                #print("WHILE IN MODULE LOOP-",ExtractedContent)
        else:
            LoadError = "<div><h3>Error-getting-module-content "+ ModuleWebPage.status_code + "for " + ModuleURL +"</3></div>"
            print(LoadError)
            ExtractedContent = ExtractedContent + LoadError        
    # Return the content 

    return ExtractedContent

def main(OutputFileName="DITCourseList.csv", FileDelimiter=";", GetCoursesFromURL='http://www.dit.ie/catalogue/Programmes/Search', BaseURL='http://www.dit.ie', WebPageLoadDelay=10):
    #
    # Create files to store the output in (w)rite mode and add the header to the FileDelimiter specified in the function parameters 
    MyCSVFile = open(OutputFileName, "wb")    
    CourseList = csv.writer(MyCSVFile, delimiter=FileDelimiter)
    # This strainer is used to only import the table in the search page
    TableStrainer = SoupStrainer("table")
    # This strainer is used to only import the div containing the programme/module details on the individual pages 
    ProgModDetailsStrainer = SoupStrainer("div",id="progmod_detail")
    ProgContentStrainer = SoupStrainer("div", class_="progmod_content")
    URLToParse = GetCoursesFromURL
    #Create a dictionary for the programme tabs
    ProgTabs = []
    ProgTabsContent=""
    ModuleText =''
    # Open the webpage using 
    WebContent = requests.get(URLToParse,timeout=WebPageLoadDelay)
    #Parse the content using soup but only parse the table tags
    DITTable = BeautifulSoup(WebContent.text, "html.parser",parse_only=TableStrainer)
    #print DITTable.prettify(formatter="html")
    CourseList.writerow(['Dept', 'link', 'CourseName','CourseAward', 'CourseCode','CourseLevel', 'CourseDelivery', 'Duration', 'CourseNFQLevel'])
    
    #Get the rows in the table
    rows = DITTable.find_all('tr')
    
    for row in rows:
        data = row.find_all("td")
        # Var = data[index].get_text() returns the Unicode text of the cell i.e the contents wrapped in a unicode string
        CourseTitle = str(data[0].get_text())
        CourseLink = BaseURL + str(data[0].find('a').get('href'))
        CourseCode = data[1].get_text()
        CourseLevel = data[2].get_text()
        CourseAward= data[3].get_text()
        #Replace Level with a blank string, then strip all the extra whitespace from the string leaving just the NQAI number value
        CourseNQAI = replace(str(data[4].get_text()),"Level",'').strip()
        CourseMode = data[5].get_text()
        CourseLength = data[6].get_text()
        CourseSchool = data[7].get_text()
        #print("Writing to file ",CourseSchool,CourseLink,CourseTitle,CourseAward,CourseCode,CourseLevel,CourseMode,CourseLength,CourseNQAI) 
        CourseList.writerow([CourseSchool,CourseLink,CourseTitle,CourseAward,CourseCode,CourseLevel,CourseMode,CourseLength,CourseNQAI])
        #Push the changes from buffer to disk for the csv file so the csv file will always be up to date even if the file hasn't been parsed already
        MyCSVFile.flush()
        FileNameToWrite = CourseCode+".html"
        #If the file doesn't exist already in the current directory then build it
        if not os.path.isfile(FileNameToWrite):
            #Get the text data for the programme
            with requests.Session() as WebSession:
                ProgContent = WebSession.get(CourseLink,timeout=WebPageLoadDelay)
                #Parse the contents of the programme page but strain it so only the relevant details are left
                ProgSoup = BeautifulSoup(ProgContent.text,"html.parser",parse_only=ProgModDetailsStrainer)
                #print(ProgSoup.prettify(formatter="html"))
                print("Processing ",CourseLink, " now...")
                #Open the file where the text will be saved
                MyHTMLFile = codecs.open(FileNameToWrite, "w",encoding='utf-8')
                HeaderText = "<h1>Text for Course "+CourseCode +" "+ CourseTitle +" </h1>"
                MyHTMLFile.write(HeaderText)
                MyHTMLFile.write(CourseLink)
                #If the tab dictionary is empty
                if not ProgTabs:
                    #Get the programme tabs urls 
                    ProgTabs = get_navi_tabs(ProgSoup)
                #Get the separate tabs for this programme
                print(ProgTabs)
                for Tab in ProgTabs:
                    #print(Tab)
                    TabUrl = CourseLink + str(Tab)
                    response = WebSession.get(TabUrl)
                    print("TabURL----",response," for ", TabUrl)
                    print(response)
                    #ProgContentTabs = urllib2.urlopen(TabUrl)
                    print("Processing ", Tab ," for course", CourseTitle)
                    ProgContent = BeautifulSoup(response.text,"html.parser",parse_only=ProgContentStrainer)
                    #Create a header based off the tab value and write it to the file
                    HeaderText = str(Tab).replace("?tab=", '').strip()
                    print("Adding ",HeaderText,"to the file for ",CourseTitle)
                    HeaderText = "<h2>" + HeaderText + "</h2>"
                    MyHTMLFile.write(HeaderText)
                    #If the tab is the Programme Structure tab
                    if "Programme Structure" in TabUrl:
                            print("Getting the module contents for ",CourseTitle, "on ",TabUrl)
                            #ModuleText = ParseModulePages(ProgContent, TabUrl,ProgModDetailsStrainer,BaseURL)
                            #ProgTabsContent ="<div id=" +"moduleContent" +" >" + ModuleText + "</div>"
                            #get the module urls and parse them 
                            for Modulelink in ProgContent.findAll('a'):
                                FullLink = str(BaseURL + Modulelink.get('href'))
                                print("Processing the module url by calling a function..", FullLink)
                                ModuleText = ModuleText + ParseModulePages(FullLink,ProgModDetailsStrainer,ProgContentStrainer,WebPageLoadDelay, BaseURL='http://www.dit.ie')
                                # Now outside the loop write the module text to the file
                                MyHTMLFile.write(ModuleText)
                    else:                        
                            #print(ProgContent.prettify(formatter="html"))
                            ProgTabsContent = ProgContent.prettify(formatter="html") 
                            #Write the contents to the tab after wrapping it in a 
                            ProgTabsContent = "<div id="+str(CourseCode)+" >" + ProgTabsContent +"</div>"
                            MyHTMLFile.write(ProgTabsContent)
                            MyHTMLFile.close
                            #Clear the module text and ProgTabsContent before the next iteration of the loop
                            ModuleText =''
                            ProgTabsContent =''
        else:
        # The file by that name already exists (Used to overcome the timeouts for requests after about 250 files were downloaded and lets me build up the documents in batches
            print(FileNameToWrite," already exists so not processing it again")
                    
    # Close the csv file
    print('File', MyCSVFile.name ,' closed')
    MyCSVFile.close
    #MyHTMLFile.close()    
        
    # Exit successfully
    sys.exit(0)

if __name__ == '__main__':
    main()