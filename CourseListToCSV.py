#===============================================================================
# Name: CourseListToCSV
# Purpose: To parse the websites using AKARI Curriculum Management version 4.0.29 to show course and module content 
#          and extract those details into files as its not possible to do so directly in Rapidminer 5. 
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
# import urllib2 library to actually go get the webpage for Beautiful Soup
import urllib2

# Import Selenium and the code needed to wait for the page to load
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Import the unicode csv library installed using pip unicodecsv 
import unicodecsv as csv
import sys
#Needed to write unicode to text file
import codecs

# Import my code that parses the individual course pages and the module pages listed there in
import ParseCoursePage

def main(OutputFileName="ITTCourseList.csv", FileDelimiter=";", GetCoursesFromURL='http://courses.it-tallaght.ie/',DeptListDivID='homeProgrammes', WebPageLoadDelay=10):
    # Function Parameters for IT-Tallaght  OutputFileName="ITTCourseList.csv", FileDelimiter=";", GetCoursesFromURL='http://courses.it-tallaght.ie/',DeptListDivID='homeProgrammes', WebPageLoadDelay=10
    # Function Parameters for IT-Blanch Course: OutputFileName="ITBlanchCourseList.csv", FileDelimiter=";", GetCoursesFromURL='http://courses.itb.ie/',DeptListDivID='homeProgrammesWide', WebPageLoadDelay=10
    Spacer ="\n------File Writer------\n"
    TextContentsFileName ="Text/"
    # Create files to store the output in (w)rite mode and add the header to the FileDelimiter specified in the function parameters 
    MyCSVFile = open(OutputFileName, "wb")    
    CourseList = csv.writer(MyCSVFile, delimiter=FileDelimiter)
    # Write the 1st row to give the column names
    CourseList.writerow(['Dept', 'link', 'CourseName','CourseAward', 'CourseCode', 'CourseDelivery', 'SemesterCount', 'CourseNFQLevel', 'CourseDepartment']) 
    URLToParse = GetCoursesFromURL
    # Open the webpage using 
    WebContent = urllib2.urlopen(URLToParse)
    #Parse the content using soup but strip out non ascii chars first
    soup = BeautifulSoup(WebContent, "html.parser")
    # Open the webpage using selenium
    driver = webdriver.Firefox()
    # Give the page time to load before continuing by waiting 5 seconds
    driver.implicitly_wait(WebPageLoadDelay)  # seconds
    print('Trying to parse ', URLToParse ,' now')
    driver.get(URLToParse)
    subset = driver.find_element_by_id(DeptListDivID)
    # Just get the part of the document that contains the list of department #  xpath //*[(@id = "homeProgrammes")] contains the list of departments but just need the id field here
    print('Finding the DIV Id', DeptListDivID, " on the webpage")
    Depts = soup.find(id=DeptListDivID)
    # print("Print out the nicely formatted Unicode with tags on their own line")
    #print(soup.prettify())
    # print("Print just the part of the doc where the id homeProgrammes was found")
    # print(Depts)
    for links in Depts.findAll('a'): 
            print(links)
            # print("--------SPACER-----------------")
            print('Processing Department ',links.string,' link(s) now')
            # Using selenium find the link to the depts list of courses that matches the link string from beautiful soup and click it
            FollowLink = subset.find_element_by_link_text(links.string)
            FollowLink.click()
            # Try waiting 10 seconds for the element with ID 'ProgrammeListForDepartment' is available 
            try: 
                # Get the Overlay i.e the list of the course in the div ProgrammeListForDepartment (it could also be homeProgrammesWide so check the webpage source and use the appropriate parameter 
                Overlay = WebDriverWait(driver, WebPageLoadDelay).until(EC.presence_of_element_located((By.ID, "ProgrammeListForDepartment")))
                # Get it as a Beautiful soup object too as its easier to read
                SoupOverlay = BeautifulSoup(Overlay.get_attribute('outerHTML'), "html.parser")
                #print(Soup.prettify())
                # close the overlay
                Overlay.find_element_by_link_text("close").click()
            except NoSuchElementException: 
                print(NoSuchElementException.msg())
                # Exit now
                sys.exit(1)
                # loop over the links 
            for courselink in SoupOverlay.findAll('a'): 
                if courselink.get('href') != "":  
                    FullLink = URLToParse + courselink.get('href')
                    # Add them to the file
                    # = [links.string, courselink.get_text(), FullLink];
                    print("--Found these non blank urls--")
                    print("Dept: ", links.string, " link ",FullLink," Course Name", courselink.getText())
                    #Parse the course link itself and its child modules
                    print('Getting the course details and module text for ',courselink.getText()," now")
                    CourseContentsDictionary = ParseCoursePage.main(FullLink, URLToParse)
                    print("Got the following keys", CourseContentsDictionary.keys(), " back from the parsing function")
                    #Use the Coursecode as the unique filename
                    TextContentsFileName = CourseContentsDictionary['CourseCode']
                    #Get the non-unicode value so u'CourseCode' don't corrupt the html when its printed to file
                    TextContentsFileName = str(TextContentsFileName.strip())
                    #Create a file with utf-8 encoding
                    MyHTMLFile = codecs.open(TextContentsFileName+".html", "w",encoding='utf-8')
                    HeaderText = "<h1> Course Outcomes for "+ TextContentsFileName +"</h1>"
                    MyHTMLFile.write(HeaderText)
                    #Add html div tags to the CourseOutcomes text and include an ID value for equal measure
                    EncasedCourseOutcomes = "<div id=",TextContentsFileName,">",CourseContentsDictionary['CourseOutcomes'],"</div>"
                    MyHTMLFile.write(EncasedCourseOutcomes.__str__()) 
                    MyHTMLFile.write("<h1> Module Content </h1>")
                    MyHTMLFile.write(CourseContentsDictionary['CourseModuleText']) 
                    print("Writing the Module contents for ",TextContentsFileName," to file")
                    # Write the results to the file after calling the ParseCoursePage function to pull the data from that page and the module pages linked to it
                    print('Writing ', courselink.getText(), 'to file','TextContentsFile')
                    #CourseList. Row Structure (['Dept', 'link', 'CourseName','CourseAward', 'CourseCode', 'CourseDelivery', 'SemesterCount', 'CourseNFQLevel', 'CourseDepartment', 'CourseOutcomes', 'CourseModuleText']) 
                    CourseList.writerow([links.string, FullLink, courselink.getText(),CourseContentsDictionary['CourseAward'] ,CourseContentsDictionary['CourseCode'],CourseContentsDictionary['CourseDelivery'], CourseContentsDictionary['SemesterCount'] ,CourseContentsDictionary['CourseNFQLevel'] ,CourseContentsDictionary['CourseDepartment']])
                    MyCSVFile.flush()       
    # Close the csv file
    print('File', MyCSVFile.name ,' closed')
    MyCSVFile.close
    MyHTMLFile.close()
    driver.close()
    print('External Web browser closed')
    # Exit successfully
    sys.exit(0)

# End of Main

if __name__ == '__main__':
    main()

