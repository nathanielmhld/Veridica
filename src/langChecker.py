from mstranslator import Translator, ArgumentOutOfRangeException as outofrange
from bs4 import BeautifulSoup
from lxml import etree
import csv  # library for outputting csv files
import lxml.html
import os
import time
import numpy as np
from .utils import loadURL, createCSVFile
import sys


# find the language of a website or co object's website
# def findLanguage(sourceType, source, translator): # sourceType can be either "url" or "co", source is the url or co object
#     a = ''
#     if sourceType == "url":
#         response = loadURL(source)
#         if response is None:
#             return a
#     if sourceType == "co":
#         if source.linkToContent[source.website] is not None:
#             response = source.linkToContent[source.website]
#         else:
#             return a
#     try:
#         html = lxml.html.fromstring(response)
#         a = html.xpath('//html/@lang')
#     except UnicodeDecodeError:  # some errors have occurred when decoding characters from non-English languages
#         print("Unicode Decode Error")
#
#     except etree.ParserError:
#         print("ParserError")
#     except etree.XMLSyntaxError:
#         print("XMLSyntaxError")
#     else:
#         if a == []:
#             soup = BeautifulSoup(response, "lxml")  # get html from site
#             for script in soup(["script", "style"]):
#                 script.extract()
#             text = soup.get_text()
#             lines = (line.strip() for line in text.splitlines())
#             # break multi-headlines into a line each
#             chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
#             # drop blank lines
#             text = '\n'.join(chunk for chunk in chunks if chunk)
#             text = text[:500]
#             try:
#                 a = translator.detect_lang(text)
#             except TypeError:
#                 a = 'type error'
#         else:
#             a = a[0]
#     return a

def findLanguage(co, translator):
    language = co.language
    if language is None and co.website in co.linkToContent and co.linkToContent[co.website] is not None:
        response = co.linkToContent[co.website]
    else:
        print("No HTML to analyze from " + co.name)
        return None
    try:
        html = lxml.html.fromstring(response)
        language = html.xpath('//html/@lang')
    except UnicodeDecodeError:  # some errors have occurred when decoding characters from non-English languages
        print("Unicode Decode Error")

    except etree.ParserError:
        print("ParserError")
    except etree.XMLSyntaxError:
        print("XMLSyntaxError")
    except:
        e = sys.exc_info()[0]
        print(e)
    else:
        if language is None:
            soup = BeautifulSoup(response, "lxml")  # get html from site
            for script in soup(["script", "style"]):
                script.extract()
            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            # break multi-headlines into a line each
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            # drop blank lines
            text = '\n'.join(chunk for chunk in chunks if chunk)
            text = text[:200]
            try:
                language = translator.detect_lang(text)
            except TypeError:
                language = 'type error'
    return language

#create a CSV file of service providers with the language of their website
def listLang(coList, translator):
    language = []

    for co in coList:
        language.append((co.name, co.website, findLanguage(co, translator)))
    curr_dir = os.getcwd()
    savepath = curr_dir + "/data/"
    createCSVFile(savepath, "Languages", language)


def appendLanguageToCoList(coList, translator):
    for co in coList:
        if co.language is None:
            co.language = findLanguage(co, translator)
    return coList

# translator = Translator('40b49a7a195e4a05a7bbe800342e073d')
# coList = npyImport("01_01_2017.npy")
# listLang(coList, translator)
