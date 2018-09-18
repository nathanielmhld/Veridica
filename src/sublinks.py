import lxml.html
from bs4 import UnicodeDammit
from lxml import etree
from .domains import getDomain, getSuffix
from .utils import loadURLDict, UrlCheck, createCSVFile, savenpyfile, loadURL, timeout
from .robotsText import getDisallowed
import os
import sys
import tldextract
from multiprocessing.dummy import Pool as ThreadPool
import time


def getLinks(co):
    response = co.linkToContent[co.website]
    counter = 0
    try:
        html = lxml.html.fromstring(response)

    except UnicodeDecodeError:  # some errors have occurred when decoding characters from non-English languages
        print("Unicode Decode Error with ", co.name)
        co.errors.append("Unicode Decode Error")
    except etree.ParserError:
        print("ParserError with ", co.name)
        co.errors.append("Parser Error")
    except etree.XMLSyntaxError:
        print("XMLSyntaxError with ", co.name)
        co.errors.append("XML Syntax Error")
    else:

        links = []

        for link in html.xpath('//a/@href'):  # find all links on webpage and add to new list
            if len(link) > 0:
                if getDomain(link) == '':
                    if link[0] == '/':
                        domain = getDomain(co.website)
                        suffix = getSuffix(co.website)
                        main_site = 'http://' + domain + '.' + suffix
                        link = main_site + link
                while len(link) > 0 and link[0] == '/':
                    link = link[1:]
                if 'www.' in link:
                    link = link.split('www.', 1)[-1]
                if len(link) > 0 and getDomain(link) == getDomain(co.website):
                    if link[0:4] != 'http':
                        link = 'http://' + link
                    if link not in links:
                        links.append(link)
        return links


def filterSublinks(new_links, disallowed_links, disallowed_parts):
    accepted_links = [link for link in new_links if (link not in disallowed_links and not containsDisallowedParts(link, disallowed_parts))] #add and UrlCheck(link)
    return accepted_links


def checkConnections(new_links):
    working_links = [link for link in new_links if UrlCheck(link)]
    return working_links


def containsDisallowedParts(link, disallowed_parts):
    for part in disallowed_parts:
        if part in link:
            return True
    return False


def getSublinkContent(co):
    start_time = time.time()

    pool = ThreadPool(10)

    linksWithoutContent = []

    if co.linkToContent.keys() is not None:
        for link in co.linkToContent.keys():
            if co.linkToContent[link] is None:
                linksWithoutContent.append(link)  # creates list of websites without html content
    links = [(link, co) for link in linksWithoutContent]


    results = pool.map(loadURLDict, links)
    pool.close()
    pool.join()

    for urlCoDict in results:
        co.linkToContent.update(urlCoDict)

    diff = time.time() - start_time
    if len(linksWithoutContent) != 0:
        print("Obtained sublink HTML from ", co.name)
        print("Took", diff, "seconds to run with average of", diff/len(linksWithoutContent), "seconds per link")
    else:
        print("No sublinks from", co.name)

    return co


"""Functions to be called from outside"""
def appendSublinksToCoList(coList):
    for co in coList:
        if co.website in co.linkToContent and co.linkToContent[co.website] is not None:
            try:
                new_links = getLinks(co)
                if new_links is not None:
                    disallowed_links, disallowed_parts = getDisallowed(co)
                    accepted_links = filterSublinks(new_links, disallowed_links, disallowed_parts)
                    # working_links = checkConnections(accepted_links)
                    print('Number of sublinks for ', co.name, ': ', len(accepted_links))
                    # print('Number of working sublinks for ', co.name, ': ', len(working_links))
                    for link in accepted_links:
                        co.linkToContent[link] = None
                        co.linkToText[link] = None
                    # getSublinkContent(co)
            except:
                print("Error")
    return coList




def obtainSublinkContent(coList):
    # pool = ThreadPool(10)  # run loadURL on 4 processes

    updatedList = []
    for co in coList:
        updatedList.append(getSublinkContent(co))


    # def threadedObtainSublinkContent(co):
    #     pool2 = ThreadPool(5)
    #     #creates list of websites without html content
    #     linksWithoutContent = []
    #
    #     if co.linkToContent.keys() is not None:
    #         for link in co.linkToContent.keys():
    #             if co.linkToContent[link] is None:
    #                 linksWithoutContent.append(link) #creates list of websites without html content
    #
    #
    #
    #     try:
    #         try:
    #             multithread = timeout(len(linksWithoutContent)*2)(pool2.map)
    #             results = multithread(loadURLDict, linksWithoutContent)
    #             pool2.close()
    #             pool2.join()
    #             for newLinkContent in results:
    #                 co.linkToContent.update(newLinkContent)
    #         except TimeoutError:
    #             print('Pool Timeout Error')
    #             pool2.close()
    #             pool2.join()
    #             return co
    #
    #
    #
    #     except KeyboardInterrupt:
    #         return co
    #     try:
    #         print("Obtained sublinks from " + co.name)
    #     except:
    #         return co
    #     else:
    #         return co



    print('Done retreiving sublinks from all companies...')
    return updatedList