import tldextract
import csv
from .utils import createCSVFile
from .utils import npyImportPathSpecific, UrlCheck, writeIntoCSV, getUrlsFromCSV
from .langChecker import findLanguage
#from urllib.request import Request, urlopen #Modules used to access websites with their URLs
#from urllib.error import URLError, HTTPError #Modules used to deal with errors with accessing websites
from http.client import IncompleteRead #Strange error catch
from ssl import CertificateError #Strange error catch and bypass
import ssl


def getDomains(fromSource, returnType, urllist = None, coList = None, savepath = None, sourcefilename = None, sourcefilepath = None):
    domainsdict = {}
    if fromSource == "npy":
        coList = npyImportPathSpecific(sourcefilepath, sourcefilename)
        fromSource = "coList"

    if fromSource == "coList":
        for co in coList:
            parsed_url = tldextract.extract(co.website)
            domain = parsed_url[1].lower()
            domainsdict[domain] = co.website

    if fromSource == "urllist":
        for url in urllist:
            domain = getDomain(url)
            domainsdict[domain] = url

    if fromSource == "csv":
        with open(sourcefilepath + sourcefilename) as f:
            mycsv = csv.reader(f)
            for row in mycsv:
                if len(row) > 1:
                    domainsdict[row[0]] = row[1]

    if returnType == "urldomaindict":
        return domainsdict
    if returnType == "csv":
        createCSVFile(savepath, "domains", list(domainsdict.items()))
    if returnType == "list":
        return list(domainsdict.keys())


def getDomain(url):
    try:
        parsed_url = tldextract.extract(url)
    except:
        return "TypeError"
    else:
        domain = parsed_url[1].lower()
        return domain

def getSuffix(url):
    try:
        parsed_url = tldextract.extract(url)
    except:
        return "TypeError"
    else:
        suffix = parsed_url[2]
        return suffix


def compareDomain(domain1, domain2):
    return domain1.lower() == domain2.lower()


# obtains old coList and potentialCoList and creates a newCoList consisting of Co's in
# potentialCoList but not in old coList by comparing the domain names of the Cos' websites
def compareDomains(coList, potentialCoList):
    existingdomains = getDomains("coList", "list", coList = coList)

    newCoList = [co for co in potentialCoList if co.name not in existingdomains]
    return newCoList #returns potential colist that's not in our original colist

