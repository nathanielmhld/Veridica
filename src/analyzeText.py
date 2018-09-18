import collections
from bs4 import BeautifulSoup
import re
from textblob import TextBlob, Word
#from .coUtils import Co
from multiprocessing import Pool as ThreadPool
# Function to scrape text from one link
from unidecode import unidecode
from .domains import getDomain
from .utils import timeout
import string
import time

def textScrapeLink(linkCoTuple): #linkCoTuple contains (link, co)
    link = linkCoTuple[0]
    co = linkCoTuple[1]
    html = co.linkToContent[link]
    co.linkToContent[link] = None
    if html is not None:
        try:
            timedsouper = timeout(30)(souper)
            text = timedsouper(html)
        except:
            print(link, " took too long to parse.")
            return None
        return {link: text}
    return None


def souper(html):
    soup = BeautifulSoup(html, "html.parser")  # get html from site
    # kill all script and style elements

    for script in soup(["script", "style"]):
        script.extract()
        # get text
    text = soup.get_text()
    # break into lines and remove leading and trailing space on each
    text = unidecode(text)
    # put text into co.text
    return text

#function to scrape all links within Co
def textScrapeCo(co):
    for linkKey in co.linkToContent:
        if co.linkToContent[linkKey] is not None and co.linkToText[linkKey] is None:
            co.linkToText[linkKey] = textScrapeLink(co.linkToContent[linkKey])

def words_in_text(text):
    return TextBlob(text).words



# check whether the word is actually a word in the English dictionary. If not, it may attempt to correct the word
# def is_word(word): #Also has to check whether the word is a proper noun or not...read more on textblob functionarlity
#     if Word(word.lower()).spellcheck()[0][1] == 1.0:
#         return True
#     else:
#         return False
# change a word into a singular form
def singularize(word):
    word = Word(word)
    word = word.singularize()

    return word

#function that create a list of words in website

def word_list(text):
    text = re.sub('[' + string.punctuation + ']', '', text)
    text = TextBlob(text)
    wordList = []
    for word_tag in text.tags:
        wordList.append(word_tag[0].lower())
    return wordList

#function to find word density of a text (string)
def wordIndex(text):
    wordCount = collections.Counter() # sets up a counter where we put words into
    if text is None:
        return wordCount
    wordList = word_list(text) #find correct words and make them lower case
    total_words = len(wordList) # find total words on webpage

    for word in wordList:
        wordCount[word] += 1
    #for word in wordCount.keys():
    #    wordCount[word] = wordCount[word]/total_words
    return wordCount

def coWordIndex(co):
    for linkKey in co.linkToText:
        co.linkToText[linkKey] = textScrapeLink(co.linkToContent[linkKey])
# function to return total word density of all sites
def word_scrape_list_of_sites(colist):
    # function to combine counters (type: collection.counter()) generated by word_index
    def combine_counters(list_of_counters):
        total_index = collections.Counter()
        for counter in list_of_counters:
            total_index.update(counter)
        return total_index
    listIndex = [] # list of dictionary that consists of word density of each site
    for co in colist:
        if co.linkToText == {}:
            textScrapeCo(co)
            print('Text Scraped')

        for linkKey in co.linkToText:
            if co.linkToText != {} and co.linkToText[linkKey] != '':
                listIndex.append(wordIndex(co.linkToText[linkKey]))

    return combine_counters(listIndex) # returns a dictionary with words as keys and word densities as values

def coUpdateText(co):
    start_time = time.time()
    links = list(co.linkToContent.keys())
    links = [(link, co) for link in links]
    # if co.website not in links:
    #     links.append(co.website)

    pool3 = ThreadPool(10)

    results = pool3.map(textScrapeLink, links)
    pool3.close()
    pool3.join()

    for linkTextDictPair in results:
        if linkTextDictPair is not None:
            co.linkToText.update(linkTextDictPair)

    diff = time.time() - start_time

    try:
        if len(links) != 0:
            print("Took", diff, "seconds to run with average of", diff/len(links), "seconds per link")
            print("Parsed HTML from " + co.name)
        else:
            print("No sublinks from" + co.name)
    except:
        co.name = getDomain(co.website)
        print("Parsed HTML from " + co.name)
    return co


    # for link in links:
    #     try:
    #         co_html = co.linkToContent[link]
    #         if co_html is not None:# and link in co.linkToText and co.linkToText[link] is None:
    #             try:
    #                 timedScrape = timeout(60)(textScrapeLink)
    #                 text = timedScrape(co_html)
    #                 co.linkToText[link] = text
    #                 print(link)
    #             except:
    #                 print("Timed Out for ", link)
    #                 co.linkToText[link] = None
    #         else:
    #             co.linkToText[link] = None
    #     except:
    #         co.linkToText[link] = None
    #     co.linkToContent[link] = None
    # try:
    #     print("Parsed HTML from " + co.name)
    # except:
    #     co.name = getDomain(co.website)
    #     print("Parsed HTML from " + co.name)
    # return co


def coListUpdateText(coList):
    """
    for co in coList:
        coUpdateText(co)
    """
    print("Starting parsing process of HTML into text of all companies...")
    updatedList = []
    for co in coList:
        updatedList.append(coUpdateText(co))
    print("Done parsing HTML from companies.")
    #    savenpyfile(coList)
    return coList