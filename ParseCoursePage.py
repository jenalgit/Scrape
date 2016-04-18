#===============================================================================
# Name: Parse Course Page
# Purpose: To parse the websites using AKARI Curriculum Management version 4.0.29 to show course and module content 
#          and extract those details into files as its not possible to do so directly in Rapidminer 5. 
# Author: Michael O'Brien
# Requirements:  
# Python 2.7.10 including pip package to install the BeautifulSoup4 library

# Libraries
# BeautifulSoup4 used to extract the content from the html
# SoupStrainer used to reduce the amount of parsing down on the module pages
# urlib2 used to call the url's 

# Created: Nov 2015
#===============================================================================

# Import the beautiful soup library
from bs4 import BeautifulSoup
# Import the soup strainer 
from bs4 import SoupStrainer
#To help deal with text in different formats
from bs4 import UnicodeDammit
# import urllib2 library to actually go get the webpage for Beautiful Soup
import urllib2
import sys


# Definitions
# function to help extract the relevant content from nested tables using the table header value then strip and clean the text
def parse_table_by_header_name(Source_table, header):
    try:
        RequiredTable = Source_table.find("th", text=header).find_parent("table")
        parsed_text = RequiredTable.get_text()
        # Remove the 1st occurance of the header text from the result
        parsed_text = parsed_text.replace(header, "", 1)
        # Remove the extra whitespaces
        parsed_text = parsed_text.strip()
        return parsed_text  #
    except :
        e = sys.exc_info()
        print(e)
        Value = "PARSING TABLE ERROR" + header
        return Value

# function to help extract the relevant content from nested tables using cssClass Value and some unique text value then strip and clean the text
def parse_table_by_Contents_and_cssClass(Source_table, FindThisText, cssClass):
    try:
        for tables in Source_table.find_all("table", class_=cssClass):
            rawText = tables.get_text()
            if rawText.find(FindThisText) != -1:
                return rawText.strip()
    except :
        e = sys.exc_info()
        print(e)
        Value = "PARSING ERROR TABLE by Contents " + FindThisText +'and CSSClass ' + cssClass
        return Value

            
def main(CourseURL ='http://courses.it-tallaght.ie/index.cfm/page/course/courseId/30', BaseURL = 'http://courses.it-tallaght.ie/'):
    #Process the Course URL stored in the file 
    Spacer = "----------Parsing Course Page ------_"
    CourseText = "<div> Course--Details</div>"
    #The results will be stored in a Dictionary Data Structure
    ResultsDictionary ={}
    # This strainer is used to only import the module descriptor page with the give id and the rest isn't parsed.
    ModuleDescriptorStrainer = SoupStrainer(id="moduleDescriptor")

    # Open the webpage using urlib and store in a Soup object using the html parser
    WebContent = urllib2.urlopen(CourseURL)
    soup = BeautifulSoup(WebContent, "html.parser")

    # Just get the table with the programme details 
    ProgrammeDetails = soup.find(id="programmeDescriptor")

    # print(ProgrammeDetails.prettify())
    # print(ProgrammeDetails.get_text())

    #print(Spacer)
    ResultsDictionary['CourseAward'] = parse_table_by_header_name(ProgrammeDetails, "Awards")
    ResultsDictionary['CourseCode'] = parse_table_by_header_name(ProgrammeDetails, "Programme Code:")
    ResultsDictionary['CourseDelivery'] = parse_table_by_header_name(ProgrammeDetails, "Mode of Delivery:") 
    ResultsDictionary['SemesterCount'] = parse_table_by_header_name(ProgrammeDetails, "No. of Semesters:") 
    ResultsDictionary['CourseNFQLevel'] = parse_table_by_header_name(ProgrammeDetails, "NFQ Level:") 
    ResultsDictionary['CourseDepartment'] = parse_table_by_header_name(ProgrammeDetails, "Department:")  
    # The Course Outcomes are stored in a table with a css class id of borders but thats not unique so include a string to get the Outcomes text
    ResultsDictionary['CourseOutcomes'] = parse_table_by_Contents_and_cssClass(ProgrammeDetails, "Knowledge - Breadth", "borders")
    # Get the module links 
    #print("-----------------Module Tables-----------------")
    for courselink in ProgrammeDetails.findAll('a'):
        # Build up the url needed
        ModuleLink = BaseURL + courselink.get('href')
        print(Spacer)
        print('Now processing module', ModuleLink, 'in course code', ResultsDictionary['CourseCode'])
        # Get the module page but strain it first so only the module details are parsed and not the rest of the webpage content
        WebContent = urllib2.urlopen(ModuleLink)
        ModuleSoup = BeautifulSoup(WebContent, "html.parser", parse_only=ModuleDescriptorStrainer)
        # Store the html output and add a spacer string between modules with their content stored in html if you use ModuleSoup.prettify(formatter="html")
        # Or use ModuleSoup.get_text()
        CourseText = CourseText + ModuleSoup.prettify(formatter="html")
        print(Spacer)
    #Outside of For loop assign the Course Text to the Results Dictionary as all the modules would be loaded by then 
    ResultsDictionary['CourseModuleText'] = CourseText

    print("Results stored in ",ResultsDictionary.keys(),"Dictionary Keys")
    #print(ResultsDictionary['CourseModuleText'])
    # Return the values stored in the dictionary
    return ResultsDictionary  


if __name__ == '__main__':
    main()



