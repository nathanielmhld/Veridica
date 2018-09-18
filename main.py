"""
Created on Mar 03 2017 by Nathaniel Mahowald, Johnny Wong, Jacky Zhu
"""
#BEFORE CAN RUN, MUST DO python3 -m textblob.download_corpora
# This file:
#   0. construct data.npy file
#   1. import data.npy file
#   2. searches for new company and verify each one
#   3. classifies each website (beta)
#   4. find contact information and keywords from each site
#   5. update website access information and keywords
#   6. export neccessary documents (excel)

"""***Imports***"""
import os
from datetime import datetime
import numpy as np
import time
import pickle
from src import coUtils, domains, websearcher, utils, robotsText, analyzeText, langChecker, sublinks, findExpressions, convertTaxonomy
from mstranslator import Translator
from tkinter import messagebox
from tkinter import *
from tkinter import ttk

#======================================================================================================================
startTime = datetime.now()


npy_file = "data.npy"
Co = coUtils.Co
curr_dir = os.getcwd()
savepathtodata = os.path.join(curr_dir + os.sep + "data" + os.sep)
translator = Translator('40b49a7a195e4a05a7bbe800342e073d')

def searchNewCompanies(coList, search_term):
    # Fill in these parameters for Google search
    my_api_key = "AIzaSyCW8JvHh0bb8xU6fymo7Y2gWnuR_MwOsx0"  # Google Search API
    my_cse_id = "005958816095987214880:ckc6brg0jk4"  # Google Search API

    num_results = 10
    start_index = 1
    UrlDict = websearcher.GoogleSearchToDict(num_results, start_index, search_term, my_api_key, my_cse_id)
    potentialColist = coUtils.urlsToCo(UrlDict)
    potentialColist = domains.compareDomains(coList, potentialColist)  # append the new websites to existing New_Websites.csv file (which savepathtodata should lead to)
    return potentialColist

# both dictionary inputs are nested dictionaries in the form {company name : {key word : link}}
def updateNestedDicts(dictToBeUpdated, sourceDict):
    for name in sourceDict.keys():
        if name in dictToBeUpdated:
            dictToBeUpdated[name].update(sourceDict[name])
        else:
            dictToBeUpdated[name] = sourceDict[name]
    return dictToBeUpdated

def findEmails(coList): # returns nested dictionary in this format {company: {key term: link}}
    coList, coEmailDict = findExpressions.findCoListEmails(coList)
    return coEmailDict

def findCompanies(findingList, coList):
    coList, coCompanyDict = findExpressions.findCoListCompanies(findingList, coList)
    return coCompanyDict

def findKeywords(coList, search_term):
    coList, coKeywordDict = findExpressions.findCoListKeyterms(coList, search_term)
    return coKeywordDict

def clearHTML(coList):
    for co in coList:
        co.linkToContent = {}
        co.linkToContent[co.website] = None
    return coList


"""***********************************************************************************"""
"""                                 Update Data.npy for Search                        """
"""***********************************************************************************"""
def updateNpyForSearch(npy_file, search_term, emailSearch, companySearch):
    coList = utils.npyImportPathSpecific(savepathtodata, npy_file)
    with open(os.getcwd() + os.sep + 'data' + os.sep + "sort.pkl", 'rb') as f:
        taxonomySort = pickle.load(f)

    dirtyCoList = searchNewCompanies(coList, search_term) # returns potential coList
    #classify potential colist
    filteredCoList = domains.compareDomains(coList, dirtyCoList)  # Assume compareDomains works...return filteredCoList not in coList
    #get the content from the main url
    filteredCoList = coUtils.coUpdateHTML(filteredCoList)  # updates html of main website

    potentialCoList = analyzeText.coListUpdateText(filteredCoList)
    newCoList = []
    for co in potentialCoList:
        wordDict = analyzeText.wordIndex(co.linkToText[co.website])

        if len(wordDict.keys()) == 0:
            cat = taxonomySort.categories[1]
        else:
            cat = taxonomySort.sort(wordDict, taxonomySort.categories)

        if cat.name.lower() != "out":
            co.secondary = cat.parent.name
            co.functional = cat.name
            cat.addText(wordDict)
            newCoList.append(co)
    #append colist to npy

    print("Finished sort")
    newCoList = langChecker.appendLanguageToCoList(newCoList, translator)  # updates language
    utils.coFindOldestAccess(newCoList)  # finds oldest date on wayback
    utils.coFindRecentAccess(newCoList)  # finds newest date on wayback
    newCoList = sublinks.appendSublinksToCoList(newCoList)  # parses html of main site to find sublinks
    newCoList = sublinks.obtainSublinkContent(newCoList)  # updates html of sublinks
    newCoList = analyzeText.coListUpdateText(newCoList)  # parses html of sublinks to obtain text
    newCoList = clearHTML(newCoList)

    if emailSearch or companySearch:
        regexSearchColist(newCoList, [], emailSearch, companySearch)

    coList = coList.tolist()
    if newCoList != []:
        coList += newCoList # append potential verified colist to existing coList
    with open(os.getcwd() + os.sep + 'data' + os.sep + "sort.pkl", 'wb') as f:
        pickle.dump(taxonomySort, f)
    utils.createOutCSV(coList)    #exports potential verified colist to csv
    utils.savenpyfile(coList) #save npy file

"""***********************************************************************************"""
"""                       Update Data.npy for Out (runs on startup)                   """
"""***********************************************************************************"""
def updateNpyForOut(npy_file):
    coList = utils.npyImportPathSpecific(savepathtodata, npy_file)
    with open(os.getcwd() + os.sep + 'data' + os.sep + "sort.pkl", 'rb') as f:
        taxonomySort = pickle.load(f)
    csvDict = utils.csvToDict(os.getcwd() + os.sep + 'output' + os.sep + 'out.csv') # create dictionary from CSV {company: (website, secondary, functional)}
    newCoList = []
    for co in coList: #iterate through oldCoList:
        if co is not None:
            # look up name in dictionary:
            if co.name in csvDict.keys(): #if exists:
                # do nothing if both are the same
                # if secondary is different
                if co.secondary != csvDict[co.name][1] or co.functional != csvDict[co.name][2]: #check if primary and secondary are the same
                    # update sorting algorithm
                    taxonomySort.findCategory(co.functional).removeText(analyzeText.wordIndex(co.linkToText[co.website]))
                    taxonomySort.findCategory(csvDict[co.name][2]).addText(analyzeText.wordIndex(co.linkToText[co.website]))
                    # create new Co object to add to newCoList
                    co.secondary = csvDict[co.name][1] # update co object and pkl object if different
                    co.functional = csvDict[co.name][2]
                    newCoList.append(co)
                else:
                    newCoList.append(co)
                del csvDict[co.name]
            else:   # if not exists
                    #delete co object from colist (create new colist and append everything but that.
                    #set the old colist to empty)
                # move co object to out category
                    #removes text from ingroup
                taxonomySort.findCategory(co.functional).removeText(analyzeText.wordIndex(co.linkToText[co.website]))
                    #adds text to outgroup
                taxonomySort.categories[1].addText(analyzeText.wordIndex(co.linkToText[co.website]))
    #if dict is not empty:
    addedCoList = []
    for key in csvDict.keys():
     #create colist from remaining terms and append website
        if key is not None and key != '':
            newCo = Co(name = key, website = csvDict[key][0])
            if csvDict[key][1] != '' and csvDict[key][1] != None:
                newCo.secondary = csvDict[key][1]
            if csvDict[key][2] != '' and csvDict[key][2] != None:
                newCo.functional = csvDict[key][2]
            addedCoList.append(newCo)
     # run updates on this addedCoList
    if addedCoList != []:
        addedCoList = coUtils.coUpdateHTML(addedCoList) # updates html of main website
        addedCoList = sublinks.appendSublinksToCoList(addedCoList) # parses html of main site to find sublinks
        addedCoList = langChecker.appendLanguageToCoList(addedCoList, translator) # updates language
        addedCoList = sublinks.obtainSublinkContent(addedCoList) # updates html of sublinks
        addedCoList = analyzeText.coListUpdateText(addedCoList) # parses html of main site to obtain text
        addedCoList = langChecker.appendLanguageToCoList(addedCoList, translator) # updates language
        utils.coFindOldestAccess(addedCoList) # finds oldest date on wayback
        utils.coFindRecentAccess(addedCoList) # finds newest date on wayback
        addedCoList = clearHTML(addedCoList)
    for co in addedCoList:
        if co.secondary == None:
            taxonomySort.categories[0].addText(analyzeText.wordIndex(co.linkToText[co.website]))
            cat = taxonomySort.sort(analyzeText.wordIndex(co.linkToText[co.website]), taxonomySort.categories[0].subCategories)
            co.secondary = cat.parent.name
            co.functional = cat.name
        elif co.functional == None:
            #deal with the correct secondary that has been inputed
            corrSec = taxonomySort.findCategory(co.secondary)
            corrSec.addText(analyzeText.wordIndex(co.linkToText[co.website]))
            #sort the functional
            cat = taxonomySort.sort(analyzeText.wordIndex(co.linkToText[co.website]), corrSec.subCategories)
            co.functional = cat.name
        else:
            #if neither of them are none
            corrFunc = taxonomySort.findCategory(co.functional)
            corrFunc.addText(analyzeText.wordIndex(co.linkToText[co.website]))

    if addedCoList != []:
        newCoList += addedCoList        #append addedCoList to oldCoList

    with open(os.getcwd() + os.sep + 'data' + os.sep + "sort.pkl", 'wb') as f:
        pickle.dump(taxonomySort, f)
    utils.createOutCSV(newCoList)
    utils.savenpyfile(newCoList)
    #Export a new keyword file
    taxonomySort.exportKeywordFile()


"""***********************************************************************************"""
"""                                 Refresh Database                                         """
"""***********************************************************************************"""
def refreshDatabase(npy_file):
    print('refreshing database')
    coList = utils.npyImportPathSpecific(savepathtodata, npy_file)
    with open(os.getcwd() + os.sep + 'data' + os.sep + "sort.pkl", 'rb') as f:
        taxonomySort = pickle.load(f)

    for co in coList:
        #clear all html and text and sublinks from main website and sublinks (key terms??)
        co.linkToContent = {}
        co.linkToText = {}
        co.linkToContent[co.website] = None
        co.linkToText[co.website] = None


    coList = coUtils.coUpdateHTML(coList) # updates html of main website
    coList = sublinks.appendSublinksToCoList(coList) # parses html of main site to find sublinks
    coList = analyzeText.coListUpdateText(coList) # parses html of main site to obtain text
    utils.coFindRecentAccess(coList) # finds newest date on wayback
    coList = sublinks.obtainSublinkContent(coList) # updates html of sublinks
    coList = analyzeText.coListUpdateText(coList) # parses html of sublinks to obtain text
    coList = clearHTML(coList)

    newCategorizer = convertTaxonomy.initialize()
    #retains the old outgroup
    #newCategorizer.categories[1] = taxonomySort.categories[1]
    for co in coList:
        cat = newCategorizer.findCategory(co.functional)
        cat.addText(analyzeText.wordIndex(co.linkToText[co.website]))

    with open(os.getcwd() + os.sep + 'data' + os.sep + "sort.pkl", 'wb') as f:
        pickle.dump(newCategorizer, f)
    utils.createOutCSV(coList)
    utils.savenpyfile(coList)
    #Export a new keyword file
    taxonomySort.exportKeywordFile()


"""***********************************************************************************"""
"""                                 Regex Search                                      """
"""***********************************************************************************"""
def regexSearch(npy_file, search_term, emailSearch, companySearch): # search_term is a list of exact phrases to look up

    coList = utils.npyImportPathSpecific(savepathtodata, npy_file)
    regexSearchColist(coList, search_term, emailSearch, companySearch)

def regexSearchColist(findingList, search_term, emailSearch, companySearch):
    mainDict = {}
    # add conditional statements for when to run these 3 functions below
    coList = utils.npyImportPathSpecific(savepathtodata, npy_file)
    if search_term != []:
        keytermDict = findKeywords(findingList, search_term)
        mainDict = updateNestedDicts(mainDict, keytermDict)
    if emailSearch:
        emailDict = findEmails(findingList)
        mainDict = updateNestedDicts(mainDict, emailDict)
    if companySearch:
        companyDict = findCompanies(findingList, coList)
        mainDict = updateNestedDicts(mainDict, companyDict)

    utils.outputxlsx(mainDict)
    print("Finished Regex Search!")



"""***********************************************************************************"""
"""                                 Main GUI                                         """
"""***********************************************************************************"""
#update data.npy before doing anything.
updateNpyForOut(npy_file)



# Functionalities after clicking run
def mainsearch():
    searchphrase = str(searchPhraseVar.get())
    if searchphrase == '' or searchphrase == None:
        searchphrase = []
    else:
        searchphrase = [phrase.strip() for phrase in searchphrase.split(',')]
        searchphrase = [phrase for phrase in searchphrase if phrase is not '']

    email_search = int(runEmails.get()) # run if value of 1, don't run if value of 0
    company_search = int(runCompanies.get()) # run if value of 1, don't run value of 0
    web_search = int(webSearchVar.get()) # run if value of 1, don't run value of 0
    regex_search = int(regexSearchVar.get()) # run if value of 1, don't run value of 0

    if web_search and regex_search:
        messagebox.showinfo(message = "Please choose web OR regex Search")
    elif web_search:
        if not searchphrase:
            messagebox.showinfo(message = 'Please input search term for web search.')
        else:
            webSearch(npy_file, search_term = searchphrase, emailSearch = email_search, companySearch = company_search)
    elif regex_search:
        if not searchphrase:
            messagebox.showinfo(message = 'Please input search term for local keyword search.')
        else:
            regexSearch(npy_file, search_term = searchphrase, emailSearch = email_search, companySearch = company_search)
    elif not searchphrase:
        if email_search or company_search:
            regexSearch(npy_file, search_term = searchphrase, emailSearch = email_search, companySearch = company_search)




#refreshes database after clickng refresh database button
def refresh():
    refreshDatabase(npy_file)

def callback():
    result = messagebox.askquestion(title = 'WARNING', message = 'CAUTION: THIS MAY TAKE A LONG TIME. DO YOU STILL WANT TO RUN THIS?', icon = 'warning')
    if result == 'yes':
        refresh()
    else:
        messagebox.showinfo(message= "Operation Cancelled")

def webSearch(npy_file, search_term, emailSearch, companySearch):
    updateNpyForSearch(npy_file, search_term, emailSearch, companySearch)


#Everything below is for the GUI
root = Tk()
root.title("Veridica")

mainframe = ttk.Frame(root, padding = "3 3 12 12")
mainframe.grid(column=0, row=0, sticky=(N, W, E, S))

searchPhraseVar = StringVar()
runEmails = IntVar()
runCompanies = IntVar()
webSearchVar = IntVar()
regexSearchVar = IntVar()

ttk.Label(mainframe, text="Search Term").grid(column=1, row=2, sticky=E)
num_results_entry = ttk.Entry(mainframe, width = 20, textvariable = searchPhraseVar)
num_results_entry.grid(column = 2, row = 2, sticky = (W, E))

Checkbutton(mainframe, text="Perform search for emails", onvalue = 1, offvalue = 0, variable=runEmails).grid(column=1, row=3, sticky=W)
Checkbutton(mainframe, text="Perform search for company names", onvalue = 1, offvalue = 0, variable=runCompanies).grid(column=1, row=4, sticky=W)
Checkbutton(mainframe, text="Web Search", onvalue = 1, offvalue = 0, variable=webSearchVar).grid(column=1, row=5, sticky=W)
Checkbutton(mainframe, text="Keyword Local Search", onvalue = 1, offvalue = 0, variable=regexSearchVar).grid(column=1, row=6, sticky=W)


ttk.Button(mainframe, text="Refresh Database", command=callback).grid(column=1, row=7, sticky=W)
ttk.Button(mainframe, text="Run", command=mainsearch).grid(column=3, row=7, sticky=W)
for child in mainframe.winfo_children(): child.grid_configure(padx=5, pady=5)
num_results_entry.focus()

root.mainloop()

