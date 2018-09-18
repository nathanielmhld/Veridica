# This file contains functions regarding the use of regular expressions
import re

def findEmails(co):
    emailDict = {}
    for link in list(co.linkToText.keys()):
        text = co.linkToText[link]
        if text is not None:
            emails = re.findall(r'[\w\.-]+@[\w\.-]+', text)
            for email in emails:
                co.keywords[email] = [link]
                emailDict[email] = [link]
    return emailDict


def findTerms(co, key_terms):
    key_terms = [term.lower() for term in key_terms]
    keytermsDict = {}
    for link in list(co.linkToText.keys()):
        text = co.linkToText[link]
        if text is not None:
            text = text.lower() # grab text from the link_text dictionary attribute of Co
            keywords_in_text = [word for word in key_terms if word.lower() in text] # find the keywords that exist in this link
            for word in keywords_in_text:
                if word not in keytermsDict.keys():
                    keytermsDict[word] = [link]
                elif link not in keytermsDict[word]:
                    keytermsDict[word].append(link)
                if word not in co.keywords.keys():
                    co.keywords[word] = [link]
                elif link not in co.keywords[word]:
                    co.keywords[word].append(link) #append the link to the dictionary with word as key and link as the value
    return keytermsDict

def findCompanies(co, coList):
    companyDict = {}
    name_list = [company.name.lower() for company in coList]
    for link in list(co.linkToText.keys()):
        text = co.linkToText[link]
        if text is not None:
            text = text.lower()
            for name in name_list:
                if (' ' + name + ' ' in text or name.title() + ' ' in text) and co.name.lower() != name:
                    if name not in companyDict.keys():
                        companyDict[name] = [link]
                    elif link not in companyDict[name]:
                        companyDict[name].append(link)
                    if name not in co.keywords.keys():
                        co.keywords[name] = [link]
                    elif link not in co.keywords.keys():
                        co.keywords[name].append(link)
    return companyDict

"""Run this in main.py"""
# def findCoInfo(co, key_terms, coList):
#     co = findEmails(co)
#     co = findTerms(co, key_terms)
#     co = findCompanies(co, coList)
#     print("Found info for " + co.name)
#     return co

def findCoListEmails(coList):
    coEmailDict = {}
    for co in coList:
        emailDict = findEmails(co)
        coEmailDict[co.name] = emailDict
    return coList, coEmailDict

def containsCo(findCo, coList):
    for co in coList:
        if findCo.website == co.website:
            return True
    return False

def findCoListCompanies(findingList, coList):
    coCompanyDict = {}
    coList = coList.tolist()
    combinedList = coList + [co for co in findingList if not containsCo(co, coList)]
    for co in findingList:
        companyDict = findCompanies(co, combinedList)
        coCompanyDict[co.name] = companyDict
    return coList, coCompanyDict

def findCoListKeyterms(coList, search_term):
    coKeytermDict = {}
    for co in coList:
        keytermDict = findTerms(co, search_term)
        coKeytermDict[co.name] = keytermDict
    return coList, coKeytermDict

# takes in a coList and key terms (inputted by user) and appends keywords (emails, other company names, and key terms) to co objects in coList
# def findCoListInfo(coList, key_terms):
#     for co in coList:
#         co = findCoInfo(co, key_terms, coList)
#     return coList
