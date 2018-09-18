from urllib.request import Request, urlopen #Modules used to access websites with their URLs
from urllib.error import URLError, HTTPError #Modules used to deal with errors with accessing websites
from http.client import IncompleteRead #Strange error catch
from ssl import CertificateError #Strange error catch and bypass
import tldextract
from .utils import npyImportPathSpecific, loadURL, timeout
import os
import numpy as np
import time
from bs4 import BeautifulSoup
import pprint

savepath = os.getcwd() + os.sep + 'data'




def printRobot(filename):
    coList = npyImportPathSpecific(savepath, filename)
    for co in coList:
        pprint.pprint(co.robotstxt)


def getRobotsText(co):
    if co.errors == []:
        parsedUrl = tldextract.extract(co.website)
        domain = parsedUrl[1]
        suffix = parsedUrl[2]

        robotstextsite = 'http://' + domain + '.' + suffix + '/robots.txt'
        try:
            loadURLTimed = timeout(10)(loadURL)
            response = loadURLTimed(robotstextsite)
        except UnicodeError:
            print("Unicode Error")
            return None
        else:
            return response

def parseRobotsText(co, robotsresponse):
    if robotsresponse is not None:
        soup = BeautifulSoup(robotsresponse, "html.parser")
        disallow = False
        parsedUrl = tldextract.extract(co.website)
        domain = parsedUrl[1]
        suffix = parsedUrl[2]

        disallowed_urls = []
        disallowed_parts = []
        main_site = 'http://' + domain + '.' + suffix
        for line in soup.get_text().split("\n"):
            if len(line) >= 10 and line[:10] == 'User-agent':
                if line[11] == '*' or line[12] == '*':
                    disallow = True
                else:
                    disallow = False
            if len(line) >= 9 and line[:8] == 'Disallow' and disallow:
                disallowed_url = line.split(': ', 1)[-1]
                if len(disallowed_url) > 0:
                    if '#' in disallowed_url:
                        disallowed_url = disallowed_url[:disallowed_url.index('#')]
                        if len(disallowed_url) <= 0:
                            continue
                    if disallowed_url[0] == '/':
                        while len(disallowed_url) > 0 and disallowed_url[0] == '/':
                            disallowed_url = disallowed_url[1:]
                        if '\r' in disallowed_url:
                            disallowed_url = disallowed_url.replace('\r', '')
                        if '*' in disallowed_url:
                            disallowed_part = disallowed_url.replace('*', '')
                            if disallowed_part not in disallowed_parts:
                                disallowed_parts.append(disallowed_part)
                        else:
                            disallowed_url = main_site + '/' + disallowed_url
                            if disallowed_url not in disallowed_urls:
                                disallowed_urls.append(disallowed_url)

        return disallowed_urls, disallowed_parts
    else:
        return [], []



"""These functions are to be used outside the class"""
def getDisallowed(co):

    robotsresponse = getRobotsText(co)
    disallowed_list, disallowed_parts = parseRobotsText(co, robotsresponse)
    return disallowed_list, disallowed_parts
