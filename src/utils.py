# This file contains:
#   1. npyImportPathSpecific function returns a list of Co objects loaded from an npy file
#   2. loadURL function returns the HTML content from a given URL
#   3. UrlCheck returns a boolean that indicates whether a website is accessible with our scraper
#   4. writeIntoCSV appends a row of data onto an existing CSV file
#   5. getColumnFromCSV returns a specified column of data from a CSV file as a list
#   6. createCSVFile creates a CSV file with the given savepath, name, and rows (as a list of lists) parameters
#   7. shownpyfile creates a CSV file that displays all the attributes of a list of Co objects in a given npy file


import numpy as np
from urllib.request import Request, urlopen #Modules used to access websites with their URLs
from urllib.error import URLError, HTTPError  #Modules used to deal with errors with accessing websites
from http.client import IncompleteRead #Strange error catch
from ssl import CertificateError #Strange error catch and bypass
import ssl
import csv
import time
import os
import sys
import os
from threading import Thread
import functools
import requests
from tldextract import extract
import xlsxwriter
from multiprocessing.dummy import Pool as ThreadPool





# imports a npy file from a specified path
def npyImportPathSpecific(path, name = 'data.npy'):
    if path[-1] != os.sep:
        path = path + os.sep
    print('Loading npy file...')
    try:
        return np.load(path + name)
    except EOFError:
        return {}
    #RETURNS A COLIST


# input url and return HTMLelement containing data of website
#timeout function
def timeout(timeout):
    def deco(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            res = [Exception('function [%s] timeout [%s seconds] exceeded!' % (func.__name__, timeout))]
            def newFunc():
                try:
                    res[0] = func(*args, **kwargs)
                except Exception as e:
                    res[0] = e
            t = Thread(target=newFunc)
            t.daemon = True
            try:
                t.start()
                t.join(timeout)
            except Exception as je:
                print('error starting thread')
                raise je
            ret = res[0]
            if isinstance(ret, BaseException):
                raise ret
            return ret
        return wrapper
    return deco


def loadURL(url):

    # function to limit time on each website

    if url[0:4] != 'http':
        url = 'http://' + url
    context = ssl._create_unverified_context()  # bypasses SSL Certificate Verfication (proabably not a good idea, but it got more sites to work)
    req = Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
        'Accept-Encoding': 'none',
        'Accept-Language': 'en-US,en;q=0.8',
        'Connection': 'keep-alive'})  # changing the header prevents some webscraper blocking techniques
    try:
        try:
            urlopenWithTimeout = timeout(20)(urlopen)
            response = urlopenWithTimeout(req, context=context).read()  # opens the URL and returns data (in bytes)
        #except ConnectionResetError:
        #    try:
        #        print('Server didn\'t send data' + ' ' + url)
        #        return
        #    except:
        #        ("Server failed to send data")
        #        return
        except HTTPError as e:
            try:
                print('HTTPError: ' + str(e.code) + ' ' + url)
                return
            except:
                print("HTTPERROR")
                return
        except URLError as e:
            try:
                print('We failed to reach a server. ' + url)
                return
            except:
                print("Failed to reach server")
                return
        except CertificateError:
            try:
                print("SSL Certificate Error with ", url)
                return
            except:
                print("SSL Error")
                return
        except IncompleteRead as e:
            try:
                print("IncompleteRead Error with ", url)
                return
            except:
                print("IncompleteRead Error")
                return
        except:
            # catches unicode exception from printing url.
            try:
                print(url + ' takes too long')
                return
            except:
                print('Website takes too long')
                return
    except:
        e = sys.exc_info()[0]
        return
        try:
            print(e + ' ' + url)
        except:
            print(e)
    else:
        return response




def loadURLDict(linkCoTuple): # linkCoTuple contains (url, co)
    link = linkCoTuple[0]
    co = linkCoTuple[1]
    try:
        timedLoader = timeout(5)(loadURL)
        response = timedLoader(link)
    except:
        print(link, " took too long to parse.")
        return {link: None}
    return {link: response}

# checks if URL works, returns True if it does and False if it doesn't
def UrlCheck(url):
    if url[0:4] != 'http':
        url = 'http://' + url
    try:
        context = ssl._create_unverified_context()  # bypasses SSL Certificate Verfication (proabably not a good idea, but it got more sites to work)
        req = Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
            'Accept-Encoding': 'none',
            'Accept-Language': 'en-US,en;q=0.8',
            'Connection': 'keep-alive'})  # changing the header prevents some webscraper blocking techniques

        urlopen(req, context=context)  # opens the URL and returns data (in bytes)
    except:
        return False
    else:
        return True


# write a single row into a given csvfile (path needs to be included in parameter)
def writeIntoCSV(csvfile, row):
    with open(csvfile, 'a') as f:
        writer = csv.writer(f)
        writer.writerow(row)

def getColumnFromCSV(column, csvfile):
    columnList = []
    with open(csvfile) as f:

        mycsv = csv.reader(f)
        for row in mycsv:
            if len(row) > 0:
                columnList.append(row[column])
    return columnList


# from a CSV file, compile the elements from one column into a list (in this case, a list of URLs, but other things can work too)
def getUrlsFromCSV(csvfile):
    UrlList = []
    with open(csvfile) as f:
        list = [line.split() for line in f]  # create a list of lists
        for x in list:  # print the list items
            UrlList.append(x[1])
    f.close()
    return UrlList


# create a CSV file with the given savepath, filename and rows (in array form) info
def createCSVFile(savepath, filename, rows):

    # adds date and time to end of file name to avoid overwriting
    savepath = os.path.join(savepath + filename + ".csv")

    with open(savepath, "w", encoding = 'utf-8') as output:
        writer = csv.writer(output, lineterminator='\n')
        for row in rows:
            writer.writerow(row)


def shownpyfile(filename):
    savepath = os.getcwd() + os.sep + 'data' + os.sep
    coList = npyImportPathSpecific(savepath, filename)
    data = []
    data.append(("Company", "Website", "Language", "Content", "Errors", "References", "Links"))
    for co in coList:
        data.append((co.name, co.website, co.language, co.linkToContent[co.website] is not None, co.errors, co.reference[0], list(co.linkToContent)))
    createCSVFile(savepath, filename[:10], data)

def createOutCSV(coList):
    csvSavepath = os.getcwd() + os.sep + 'output' + os.sep
    data = []
    data.append(("Company", "Website", "Language", "First Accessed",
                 "Recent Accessed", "User Accessed", "Secondary Market", "Functional Market"))
    for co in coList:
        data.append((co.name, co.website, co.language, co.oldestAccess, co.recentAccess,
                     co.userAccess, co.secondary, co.functional))
    createCSVFile(csvSavepath, 'out', data)

def csvToDict(csvfile):
    newDict = {}
    with open(csvfile, mode = 'r') as infile:
        for row in csv.reader(infile):
            if row[0] != "Company" and newDict.get(row[0],None) == None:
                newDict.update({row[0]: (row[1], row[6], row[7])})
        return newDict

def savenpyfile(coList):
    print('npy saving...')
    np.save(os.getcwd() + os.sep + 'data' + os.sep + "data", coList)
    print('npy saved!')


def showText(filename):
    if not os.path.exists(os.getcwd() + os.sep + 'data' + os.sep + 'regex'):
        os.mkdir(os.getcwd() + os.sep + 'data' + os.sep + 'regex' + os.sep)
    savepath = os.getcwd() + os.sep + 'data' + os.sep + 'regex' + os.sep
    importpath = os.getcwd() + os.sep + 'data' + os.sep
    coList = npyImportPathSpecific(importpath, filename)

    for co in coList:
        emails = []
        other_companies = []
        emails.append([co.name])
        for email in co.emails.keys():
            emails.append((email, co.emails[email]))
        other_companies.append([co.name])
        for name in list(co.other_companies.keys()):
            other_companies.append((name, co.other_companies[name]))
        name = co.name
        if os.sep in co.name:
            name = co.name.replace(os.sep, '_')
        createCSVFile(savepath, name + "emails", emails)
        createCSVFile(savepath, name + "other_companies", other_companies)
""" *** Wayback Machine *** """
""" Exports timestamp (YYYY-MM-DD)"""

def grabDomain(url):
    extract_url = extract(url)
    return extract_url[1] + '.' + extract_url[2] #combines the domain and suffix
def getTimeStamp(archive_url):
    try:
        r = requests.get(archive_url)
        website_info = r.json()
        timestamp = website_info['archived_snapshots']['closest']['timestamp']
        timestamp = timestamp[:4] + '-' + timestamp[4:6] + '-' + timestamp[6:8]
        try:
            print(archive_url + ": " + timestamp)
        except:
            print(archive_url)
        return timestamp
    except:
        return "unable to retrieve timestamp"



def findRecentAccess(url):
    wayback_url = "http://archive.org/wayback/available?url=" + grabDomain(url) #find most recent website capture
    return getTimeStamp(wayback_url)

def findOldestAccess(url):
    wayback_url = "http://archive.org/wayback/available?url=" + grabDomain(url) + '&timestamp=19000101' #find website capture closest to 01-01-1900
    return getTimeStamp(wayback_url)

def coFindRecentAccess(colist):
    for co in colist:
        try:
            co.recentAccess = findRecentAccess(co.website)
        except:
            print('Error retreiving recent access timestamp')

def coFindOldestAccess(colist):
    for co in colist:
        try:
            if co.oldestAccess is None:
                co.oldestAccess = findOldestAccess(co.website)
        except:
            print('Error retreiving oldest access timestamp')

#This function should be passed a dictionary of the form {company : subdict}
#The subdicts should be of the form {keyword : [link, link]}
#This function will export those values as an HTML document
def outputhtml(companydict):
    curr_dir = os.getcwd()
    savepath = os.path.join(curr_dir + "/output/")
    if not os.path.exists(savepath + os.sep + time.strftime("%d_%m_%Y")):
        os.makedirs(savepath + os.sep + time.strftime("%d_%m_%Y"))
    f = open(savepath + os.sep + time.strftime("%d_%m_%Y") + os.sep + time.strftime("%H_%M_%S") + '.html', 'w')
    for company in companydict.keys():
        f.write(company)
        f.write(" : ")
        for keyword in companydict[company].keys():
            for link in companydict[company][keyword]:
                f.write("<a href=\"" + link + "\">" + keyword + "</a>  ")
        f.write("<br><br>")

def outputxlsx(companydict):
    curr_dir = os.getcwd()
    savepath = os.path.join(curr_dir + "/output/" + os.sep + time.strftime("%d_%m_%Y"))

    if not os.path.exists(savepath):
        os.makedirs(savepath)
    workbook = xlsxwriter.Workbook(savepath + os.sep + time.strftime("%H_%M_%S") + '.xlsx')
    worksheet = workbook.add_worksheet('Hyperlinks')

    url_format = workbook.add_format({'color': 'blue', 'underline': 1})
    reg_format = workbook.add_format({'color': 'black', 'underline': 0})

    x = 0
    worksheet.set_column(0, len(companydict.keys()), 30, url_format)
    for company in companydict.keys():
        worksheet.write_string(0, x, company, reg_format)
        y = 1
        for keyword in companydict[company].keys():
            for link in companydict[company][keyword]:
                worksheet.write_url(y, x, link, url_format, keyword)
                y += 1
        x += 1