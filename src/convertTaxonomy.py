# from src import coUtils, domains, websearcher, utils, robotsText, analyzeText, langChecker, sublinks, convertTaxonomy

import csv #library for outputting csv files

import time
import string
import numpy
import operator
import os



class CoSort:
    """This class will hold an instantiation of a sorting algorithm"""

    def __init__(self, name = None):
        if name == None:
            name = time.strftime("%Y-%m-%d(%H_%M_%S)") + "-sort"
        self.name = name
        self.categories = []

    def sort(self, sortDict, sortSets): # sortDict: word density dict, sortSets: list of categories to sort from
        #squared difference algorithm
        #zeros are zeros

        catPairs = []
        if(sortDict):
            sortDictmax = sorted(sortDict.items(), key=operator.itemgetter(1))[-1][1]
        else:
            sortDictmax = 1



        for cat in sortSets:
            if(cat.dict):
                catDictmax = sorted(cat.dict.items(), key=operator.itemgetter(1))[-1][1]
            else:
                catDictmax = 1
            catScore = 0
            for word in sortDict.keys():
                if word not in cat.dict:
                    catScore = catScore + pow(sortDict[word]/sortDictmax, 2.0)
                else:
                    catScore = catScore + pow(cat.dict[word]/catDictmax - sortDict[word]/sortDictmax,2.0)

            catPairs.append([cat, catScore])
            #print(catScore)
            #print(cat.name)

        lowcat = [None, 100000]
        for c in catPairs:
            if lowcat[1] > c[1]:
                lowcat = c
        if lowcat[0].subCategories != []:
            return self.sort(sortDict, lowcat[0].subCategories)
        return lowcat[0]


    def show(self):
        print(self.name)
        for cat in self.categories:
            cat.showDown()
    def addNewCategory(self, name):
        self.categories.append(Category(name, None, self))


    def findCategory(self, name): # finds category object by name
        for c in self.categories:
            if c.name == name:
                return c
        for c in self.categories:
            o = c.findCategory(name)
            if o != None:
                return o
        return None

    def exportKeywordFile(self): #exports the keyword file for all categories in this object
        with open(os.path.join(os.getcwd() + os.sep + "output" + os.sep + "keywords.txt"), 'w+', encoding='utf8') as f:
            st = "----KEYWORDS----\n"
            for c in self.categories:
                st += "CATEGORY: " + c.name + " with: "+str(len(c.dict))+" unique words\n"
                for index, word in enumerate(c.keywords(10, self.categories)):
                    st += "WORD #" + str(10 - index) +": "+word[0]+" (" + str(word[1]) + ")\n"
                st += c.exportKeywordFile(1)
            f.write(st)



class Category:
    """This class will hold an instantiation of a category in a sorting algorithm"""

    def __init__(self, name, parent, sort):
        self.name = name
        self.total_words = 0
        self.subCategories = []
        self.dict = {}
        self.parent = parent
        self.sort = sort

    # might have to take some sort of sortSets list as well
    #TODO: add domain sort help stuff

    def keywords(self, howMany, allCats): #returns keywords that are associate with this category as opposed to other categories
        # howmany: number of words to return, allCats: list of categories that are sibling categories to this one
        #the words with the highest std dev above the mean of any in the set.
        #Will have to run through all of them

        abovemeandict = {}
        for word in self.dict.keys():
            l = []
            for c in allCats:
                l.append(c.dict.get(word, 0) + self.sort.categories[1].dict.get(word,0))
            abovemeandict[word] = self.dict[word]*len(l) - sum(l)


        #Simple Value
        #sorted(self.dict.items(), key=operator.itemgetter(1))[-howMany:]
        return sorted(abovemeandict.items(), key=operator.itemgetter(1))[-howMany:]





    def addText(self, newDict):
        #for key in newDict.keys():
        #    print(key)

        for newWord in newDict.keys():
            self.total_words = self.total_words + 1
            if newWord not in self.dict:
                #I think this line is causing a huge glitch
                self.dict[newWord] = newDict[newWord] #/self.population
            else:
                self.dict[newWord] = self.dict[newWord] + newDict[newWord]
                #(self.dict[newWord]*
                                    #    ((self.population-1)/self.population)
                                    #     + newDict[newWord]/self.population)
        if self.parent != None:
            self.parent.addText(newDict)
        #for sub in self.subCategories:
        #    sub.addText(newDict)

    def removeText(self, newDict):
        #self.population = self.population - 1
        for newWord in newDict.keys():
            if newWord in self.dict:# and self.population > 0:
                self.total_words = self.total_words - 1
                #edited here as well
                self.dict[newWord] = self.dict[newWord] - newDict[newWord]
                #((self.dict[newWord]
                                    #     - newDict[newWord]/(self.population + 1))*
                                    #     ((self.population+1)/self.population))
        if self.parent != None:
            self.parent.removeText(newDict)
        #for sub in self.subCategories:
        #    sub.addText(newDict)

    def showDown(self):
        print(self.name)
        for cat in self.subCategories:
            cat.show()
    def showUp(self):
        print(self.name)
        if self.parent != None:
            self.parent.showUp()

    def addNewCategory(self, name):
        self.subCategories.append(Category(name, self, self.sort))


    def findCategory(self, name):
        for c in self.subCategories:
            if c.name == name:
                return c
        for c in self.subCategories:
            o = c.findCategory(name)
            if o != None:
                return o
        return None

    def exportKeywordFile(self, n): #exports the keyword file for all categories in this object
        st = ""
        for c in self.subCategories:
            st += "CATEGORY: " + c.name +" with "+str(len(c.dict))+" unique words\n"
            for index, word in enumerate(c.keywords(10, self.subCategories)):
                st += (n*"    ") + "WORD #" + str(10 - index) +": "+word[0]+" (" + str(word[1]) + ")\n"
            st += c.exportKeywordFile(n + 1)
        return st





def ratioCreator(text):
    text = text.translate(string.punctuation)
    text = text.lower()
    words = text.split()
    #add more language processing here possibly
    d = {}
    for word in words:
        if word not in d:
            d[word] = 1#/len(words)
        else:
            d[word] = d[word] + 1#/len(words)
    return d


####THIS IS WHERE THE GENERALIZED SETUP ENDS AND THE SPECIFIC SORTING BEGINS
#Secondary,Functional,Keywords
#Here is where the software taxonomy pdf is manually converted into the base
#for a sort algorithm
#Think about how a high volume of average words in one category can tilt the whole model towards those words. Figure out how to dispell that effect
def initialize():
    taxonomySort = CoSort()

    taxonomySort.addNewCategory("In")
    taxonomySort.addNewCategory("Out")


    #possibly just strait up add english dictionary to outgroup sorter (Done)
    fullDict = {}
    with open("data/englishwordfreq.csv") as f:
        mycsv = csv.reader(f)
        for row in mycsv:
            fullDict[row[0].split(";")[0]] = int(row[0].split(";")[1])#/450000000

    taxonomySort.categories[1].addText(fullDict)





    taxonomySort.categories[0].addNewCategory("Collaborative Applications")

    taxonomySort.categories[0].subCategories[0].addNewCategory("Conferencing applications")
    taxonomySort.categories[0].subCategories[0].subCategories[0].addText(ratioCreator(
    "Conferencing applications (aka Web, data, visual, electronic, or real-time conferencing) provide a real- time connection for the viewing, exchange, or creation of content and information by two or more users in a scheduled or ad hoc online meeting or event. The functionality of conferencing applications includes, but is not limited to, application and screen sharing including markup and annotation, instant messaging (IM) and presence, livestreaming video, video and audioconferencing, polls and surveys, and whiteboard capabilities also with markup or annotation. Conferencing applications can be delivered to a desktop or smartphone device (using IP, TDM, Web interface, proprietary thin client, or browser) as well as specific video endpoint (either a specialized video room or desktop). The following are representative vendors and products in this market: \
    Adobe (Adobe Connect)\
     Avaya (Aura Conferencing — Web conferencing)\
     Cisco (WebEx)\
     Citrix (GoToMeeting, GoToWebinar)  Microsoft (Lync Server, Lync Online)\
    IDC has defined a submarket of the conferencing applications functional market: Web conferencing applications.\
    Web Conferencing Applications\
    Web conferencing is a set of technologies and services that allow people to hold real-time and synchronous conferences over the Internet. Web conference participants need to use a Web browser and a PC or mobile device to share information and may also include 'converged conferencing' scenarios where Web, IP audio, and desktop video are part of the delivered experience. Web conferencing capabilities include application and screen sharing including markup and annotation, instant messaging and presence, livestreaming video, polls and surveys, whiteboard, and video and audioconferencing (via PSTN/TDM networks or through VoIP). The following are representative vendors and products in this submarket:\
     Cisco (WebEx)\
     Citrix (GoToMeeting, GoToWebinar)  Microsoft (Lync Online)"

    ))

    taxonomySort.categories[0].subCategories[0].addNewCategory("Email applications")
    taxonomySort.categories[0].subCategories[0].subCategories[1].addText(ratioCreator(
    "Email applications provide a framework for electronic messaging. The core integrated functionality can consist of mail messaging, group calendaring and scheduling, shared folders/databases, and threaded discussions. Email applications are based on shared directory messaging platforms where directory integration, access protocols, message encryption and authentication, and custom domains are available functionalities.\
    The following are representative vendors and products in this market:\
     Google (Google for Work)\
     IBM (IBM Verse, IBM Notes, IBM Notes and Domino)\
     Microsoft (Microsoft Exchange Server, Microsoft Exchange Online, Microsoft Outlook)"
    ))
    taxonomySort.categories[0].subCategories[0].addNewCategory("Enterprise social network")
    taxonomySort.categories[0].subCategories[0].subCategories[2].addText(ratioCreator("\
    Enterprise social networks (ESNs) enable social collaboration capabilities to users that are either inside or outside an organization's firewall. Solution capabilities should include, but are not limited to, activity streams, blogs, wikis, microblogging, discussion forums, groups (public or private), ideas, profiles, recommendation engines (people, content, or objects), tagging, bookmarking, and online communities. An ESN provides a social collaboration or relationship layer in a business that can be a discrete standalone solution and/or a set of service-oriented application programming interfaces (APIs) or integrated applications that coexist with other business and communications applications. Discrete solutions may support one type of social functionality (such as online communities, ideation, or innovation management) or a broad-based platform that encompasses many functionality traits.\
    The following are representative vendors and products in the enterprise social networks market:\
     IBM (IBM Connections)\
     Jive Software (Jive-n and Jive-x)\
     Microsoft (Yammer)\
     salesforce.com (Chatter)\
     Lithium Technologies (Online Communities)  Sprinklr (Get Satisfaction)\
    For those applications supporting particular customer-facing social capabilities including social media, monitoring, and management, refer to the customer relationship management definition in this taxonomy."))
    taxonomySort.categories[0].subCategories[0].addNewCategory("Team collaborative applications")
    taxonomySort.categories[0].subCategories[0].subCategories[3].addText(ratioCreator(
    "Team collaborative applications (TCAs) provide a workspace and an integrated set of Web-based tools for ad hoc, unstructured, document-centric collaboration between groups or individuals between known domains. A TCA can be represented by secure 'rooms' that contain documents, chat history, and transaction history in order to maintain a persistent auditable history or a more multipurpose shared workspace where users are able to store, access, and share files. Administration is primarily performed by a known user (that governs access rules), but IT administration controls/management may also be possible. TCA solutions may also allow directory integration, policy management, and integration with social collaboration tools (content shared within the social context of newsfeeds or groups). Communication within the TCA environment is mostly asynchronous, business to business (B2B), and closed to a specific set of eyes. The following are representative vendors and products in this market:\
     Intralinks (Dealspace, Fundspace, Debtspace)\
     Microsoft Office SharePoint Server (a portion of this compound product)  Huddle\
    Team collaborative applications designed for a particular vertical market such as manufacturing product design or life-cycle development (product data management [PDM] and product life-cycle management [PLM]) or application development code sharing are not included here."))
    taxonomySort.categories[0].subCategories[0].addNewCategory("File synchronization and sharing software")
    taxonomySort.categories[0].subCategories[0].subCategories[4].addText(ratioCreator(
    "File Synchronization and Sharing Software\
    Sync and share software are applications that enable users to store file-based content to synchronize files across designated devices and share folders and files with designated people and systems. These applications are typically offered as services and include products that are deployed in a public cloud, in a private datacenter, or as a private-public hybrid. Sync and share software provides a simple method for the content owner or administrator to grant access rights and privileges to other people and systems. Common privileges range from co-owning folders and files to editing, reviewing, viewing, downloading, and uploading.\
    The following criteria are required to be met by solutions in order to be included in this category:\
     Access to files across heterogeneous devices. Sync and share services provide access to content via a browser, as a mobile app across heterogeneous mobile platforms, and through the Windows Explorer and Macintosh Finder file systems.\
     Team sharing. The services enable users to invite other users to share access to files and folders. Users can also publish links to specific files or folders.\
     Storage management. File sync and share applications manage storage and orchestration of files, folders, and permissions to ensure access to the up-to-date version and a version history.\
     Security. All sync and share services have the ability to restrict unauthorized users and systems from accessing files managed by the service.\
     Administration. Administrators can establish privileges and access rights across groups, run reports that keep track of files stored in the service, determine who is accessing content, view download statistics, and set storage quota limits per group, team, or individual.\
     Ease of use. The service is easy to set up and use by an end user (non-IT professional). Although IT may be involved in large enterprise deployments and may have an administrator involved in establishing some of the structured file folders, day-to-day use does not require training or IT involvement with end-user implementation.\
     Separable offering. Services are identified as providing file sync and share as their primary function and are separately priced or packaged, as opposed to being a feature of a product whose primary function (such as content management, collaboration, or backup) is not file sync and share.\
    The following are representative vendors in this market:\
     Accellion\
     Box (Box)\
     Citrix (ShareFile)\
     Dropbox (Dropbox Business)  Egnyte\
     EMC (Syncplicity)\
     Google (Google Drive)\
     Hightail (Workstream)\
     Microsoft (OneDrive)\
     SugarSync"))


    taxonomySort.categories[0].addNewCategory("Content Applications")

    taxonomySort.categories[0].subCategories[1].addNewCategory("Content management")
    taxonomySort.categories[0].subCategories[1].subCategories[0].addText(ratioCreator("Content management software builds, organizes, manages, and stores collections of digital works in any medium or format. The software in this market includes document management, Web content management, capture and image management, digital asset management, and records management. (Additional submarkets include component content management for technical content management and content marketing solutions that support content planning, curation, acquisition, and delivery.)\
    Content management systems that manage enterprise documents and records provide a foundation for knowledge management and compliance; and case management solutions or frameworks that combine content management with business process management and analytics form the foundation for content-enabled applications that automate document-centric business processes. Web content management systems (and, increasingly, digital asset management systems) form the core of the modern digital experience delivery platform.\
    Over the past few years, solutions have emerged that blur the lines between content management, team collaborative applications, and enterprise portals. More recently, file sync and sharing services have begun to offer basic content management capabilities such as versioning, check-in/check-out or locking for edit, policy management, and APIs. Conversely, content management vendors have extended their solutions with collaboration features such as file sync and share, social capabilities (threaded discussions, commenting, voting, and so forth related to the content), and team workspaces — whether on-premise, in the cloud, or in hybrid deployments — further blurring these lines. Applications in this market include one or more of the following functions:\
     Gathering and feeding documents and other media into collections via crawlers or other automated and/or manual means and performing metadata capture/enrichment, classification/categorization, data extraction, formatting, transformations, and/or conversion operations\
     Organizing and maintaining information, including some or all of the following:\
     Indexing, cataloging, and/or categorizing information\
     Building directories and defining content objects, folders, hierarchies, and other entities and maintaining metadata associated with these\
     Record keeping, auditing, and logging\
     Updating and purging content\
     Searching for information in the content management system (embedded tools may be provided)\
     Configuring/designing the user experience, whether for internally focused content-based applications or Web experiences (In addition to user interface design capabilities, solutions may include templated publishing, content syndication, and capabilities for rendition management, personalization, content matching, and other types of content optimization.)\
     Ensuring document security by managing rights and permissions to create, edit, post, or delete materials; managing user access; and protecting intellectual property\
     Integrating with enterprise applications, digital marketing tools, and other systems via APIs, connectors, and other mechanisms to support enterprise business processes and digital experience delivery\
    Representative vendors in the content management market segment include:\
     Document management, capture and image management, records management, and cloud content management: Alfresco, EMC, HP Inc., Hyland, IBM, Laserfiche, Lexmark, Microsoft, OpenText, and Oracle\
     Web content management: Acquia, Adobe, Automattic, EPiServer, IBM, OpenText, Oracle, SDL, Sitecore, and Wix\
     Digital asset management: Adobe, ADAM, Bynder, CELUM, North Plains Systems, OpenText, and Widen"))
    taxonomySort.categories[0].subCategories[1].addNewCategory("Authoring and publishing software")
    taxonomySort.categories[0].subCategories[1].subCategories[1].addText(ratioCreator("Authoring and publishing software is defined as software used to create, author, edit, and publish content, including text documents, spreadsheets, presentations, images, audio, video, and XML- structured documents. It does not include the software used to design and develop Web sites. Authoring and publishing software includes the following categories:\
     Office suites/point products, including word processors, spreadsheets, presentation software, and notetaking applications (e.g., Microsoft Office, Evernote, Google Docs, and Smartsheet)\
     Graphic design and layout, including image editing software and layout and design software (e.g., Adobe's InDesign, Illustrator, and Photoshop and Quark's QuarkXPress)\
     Compound document authoring and publishing, including XML authoring software as well as software for the automated and semiautomated generation of paginated, structured electronic documents from content components (e.g., Adobe FrameMaker, EMC's Document Sciences xPression, HP-Exstream's Dialogue, OpenText StreamServe, Oracle Documaker, PTC Arbortext, and Quark)\
     Forms design and input software, including software to design forms, render the forms for display, and enter data into the forms but not to route, manage, or process the forms beyond form-level validation or actions (e.g., Adobe AEM Forms, Avoka, OpenText LiquidOffice, IBM Forms, and Intelledox)\
     Survey software, which enables users to easily design, field, and analyze Web surveys without programming (e.g., SurveyMonkey and Qualtrics)\
     eSignature solutions, which manage signing/approvals workflows and may provide vaulting or other custodial services (e.g., Adobe Sign and DocuSign)\
     Audio/video (AV) authoring and postproduction software, which lets professionals and advanced consumers edit, manipulate, and assemble audio and video content (e.g., Adobe's Premiere, After Effects, and Audition; Apple Final Cut Pro; Autodesk Max and Maya; and Avid Media Composer)\
     Information diagramming applications, which provide for the diagramming and visual representation of information (e.g., Microsoft Visio and Mindjet MindManager)\
     Other authoring tools, including tools for creating elearning content, online help, and other types of content (e.g., Adobe Captivate RoboHelp and MadCap Flare)\
     Online video platforms, which enable users to manage, publish, syndicate, monetize, analyze, and deliver live and/or on-demand video content over the Internet (e.g., Adobe Primetime, Brightcove, Comcast's thePlatform, Kaltura, Ooyala, and Vidyard)\
     Digital publishing solutions, which enable users to create digital publications for tablets, smartphones, and other devices (e.g., Adobe Publish, Aquafadas, GTxcel Texterity, Nxtbook Media, Quark App Studio, and ZMags)"))
    taxonomySort.categories[0].subCategories[1].addNewCategory("Cognitive/AI systems and content analytics software")
    taxonomySort.categories[0].subCategories[1].subCategories[2].addText(ratioCreator("Cognitive/artificial intelligence (AI) systems and content analytics software analyzes, organizes, accesses, and provides advisory services based on a range of unstructured information and provides a platform for the development of analytic and cognitive applications. large amounts of structured and unstructured data, content analytics, information discovery, and analysis as well as numerous other infrastructure technologies, cognitive/AI systems use deep natural language processing and understanding to answer questions, provide recommendations and direction, hypothesize and formulate possible answers based on available evidence, be trained through the ingestion of vast amounts of content, and automatically adapt and learn from its mistakes and failures. The technology components in this market include software for text (often in multiple languages) and rich media (such\
    as audio, video, and image) tagging, searching, entity and relationship extraction, information discovery, machine learning, deep learning, supervised and unsupervised learning, hypotheses generation, categorization, clustering, question answering, visualization, filtering, alerting, and navigation.\
    This market is divided into three submarkets that handle different aspects of unstructured information analysis and processing. These sub-markets are:\
     Cognitive software platforms: These platforms are used to build smart applications that learn and improve over time using a wide range of information access processes combined with deep learning and machine learning.\
     Search systems: This includes departmental, enterprise, and task-based search and discovery systems as well as cloud-based and personal information access systems. This submarket also includes unified information access tools and systems that combine text analytics, clustering, categorization, and search into a comprehensive information access system.\
     Content analytics: Content analytics systems provide tools for recognizing, understanding, and extracting value from text or by using similar technologies to generate human-readable text. This also includes language analyzers and automated language translation as well as text clustering and categorization tools. This submarket also includes software for recognizing, identifying, and extracting information from audio, voice, and speech data as well as speech identification and recognition plus converting sounds into useful text. Finally, this submarket includes software for recognizing, identifying, and extracting information from images and video, including pattern recognition, objects, colors, and other attributes such as people, faces, cars, and scenery. These tools are used for computer vision applications and clustering, categorization, and search applications.\
    Representative vendors in this market are:\
     Cognitive software platforms: IBM, Saffron Technology/Intel, Palantir, IPsoft, CustomerMatrix, CognitiveScale, Tata/Digitate, and Digital Reasoning\
     Search systems: Dassault Systèmes, Google, Lucidworks, Elasticsearch, HPE, IBM, Oracle, Microsoft, Attivio, Sinequa, Coveo, Smartlogic, Expert System, and Palantir\
     Content analytics: Basis Technologies, SAP, SDL, Linguamatics, Lexalytics, SAS, Automated Insights, Concept Searching, Content Analyst, Expert System, Google, Nuance, Nexidia, Scribe, M*Modal, VoiceBox, Microsoft, IBM, HPE, Cognex, Clarifai, Imagga, Cisco, Honeywell, NICE Systems, ObjectVideo, and IntelliVision Technologies Corp."))
    taxonomySort.categories[0].subCategories[1].addNewCategory("eDiscovery")
    taxonomySort.categories[0].subCategories[1].subCategories[3].addText(ratioCreator(" IDC's eDiscovery software market study focuses on software and applications that span the Electronic\
     Discovery Reference Model (EDRM) including early case assessment applications, eDiscovery review\
     platforms, full spectrum eDiscovery suites, and applications focused on individual EDRM components.\
     These applications automate business process management and data management activities during\
     early case assessment, early data assessment (EDA), collection, review, analysis, and production.\
     These applications primarily offer search, text analytics, and data mining functions but also offer\
     business process workflow automation, project management, document management, and decision\
     support mechanisms. In most instances, these applications are offered as standalone full suite or\
     complementary software products. In some cases, specific applications are offered solely as add-on\
     modules that run atop proprietary archiving or enterprise content management platforms. The following\
     are representative vendors and products in this market:\
      kCura (Relativity)\
     Guidance Software (EnCase eDiscovery)  HPE (Autonomy eDiscovery)\
     Catalyst Repository Systems\
     Symantec (eDiscovery)\
     IBM (StoredIQ eDiscovery)"))
    taxonomySort.categories[0].subCategories[1].addNewCategory("Enterprise portals")
    taxonomySort.categories[0].subCategories[1].subCategories[4].addText(ratioCreator("Enterprise portals integrate access to information and multiple applications and present it to the business user in a useful format. This software often provides a metadata-driven presentation framework for developing applications that tie together capabilities often provided by other product categories, such as team collaboration, content and document management, enterprise search, business intelligence, and workflow and business process management. This software is used by business users that can tailor the look and feel of their environment but must also include IT tools for role-based or rule-based administration governing access. The following are representative vendors and products in this market:\
     IBM WebSphere Portal\
     Microsoft Office SharePoint Server (a portion of this compound product)  Oracle WebCenter Suite\
     SAP NetWeaver Portal"))


    taxonomySort.categories[0].addNewCategory("ERM")
    taxonomySort.categories[0].subCategories[2].addNewCategory("Financial applications")
    taxonomySort.categories[0].subCategories[2].subCategories[0].addText(ratioCreator("Accounting software supports general financial management business processes such as accounts payable, accounts receivable, general ledger, and fixed asset accounting, as well as more specialized functions such as credit and collections management and automation, dispute resolution, expense management, lease management, project accounting and costing, tax and revenue management and reporting, nonprofit fund accounting, point of sale, and transactional financial reporting and analytics embedded into accounting applications. Financial and accounting solutions are used by organizations of all sizes to manage finances.\
    Representative vendors and products are as follows:\
     Accounting: Intuit (QuickBooks Online), Oracle Financials Cloud, SAP Simple Finance, and Workday Financials\
     Point of sale: Epicor Retail Store, Oracle Retail Point-of-Sale, and NetSuite SuiteCommerce Point of Sale\
     Product accounting and costing: Deltek Costpoint Essentials and Unanet Project Accounting\
     Revenue management (including revenue recognition, deal management, price management,\
    and trade promotion accounting): FinancialForce, Flintfox, Revitas, and Vendavo\
     Subscription and media billing: Aria Systems and Zuora\
     Travel and expense management: SAP's Concur, Expensify, and Infor Expense Management\
    Treasury and Risk Management\
    Treasury and risk management applications support corporate treasury operations (including the treasuries of financial services enterprises) with the corresponding financial institution functionality and optimize related cash management, deal management, and risk management functions, as follows:\
     Cash management automation includes several treasury processes involving electronic payment authorization, bank relationship management, and cash forecasting.\
     Deal management automation includes processes for the implementation of trading controls, the creation of new instruments, and market data interface from manual or third-party sources.\
     Risk management automation includes performance analysis, Financial Accounting Standards (FAS) 133 compliance, calculation of various metrics used in fixed-income portfolio analysis, and market-to-market valuations.\
    Representative vendors and products in this submarket include Infor, Kyriba, Misys, SAP, SunGard, Wall Street Systems, and Wolters Kluwer (FRSGlobal)."))
    taxonomySort.categories[0].subCategories[2].addNewCategory("Human capital management")
    taxonomySort.categories[0].subCategories[2].subCategories[1].addText(ratioCreator("Human capital management (HCM) applications software automates business processes that cover the entire span of an employee's relationship with the corporation as well as management of other human resources used by the enterprise (e.g., contingent labor, contractors, and consultants), including — increasingly — human resources employed by suppliers and customers.\
    Core HR\
    The center of the HCM applications suite is designed for core HR functions such as employee records, benefits administration, and payroll preparation. Increasingly, many of these functions are being delivered through employee self-service or manager self-service to automate record keeping and updating as well as consolidating reporting.\
    It is important to note that payroll processing is a separate category that is sized, forecast, and reported out separately from human capital management.\
    The following are representative core HR applications vendors and products:\
     Infor Human Capital Management\
     Oracle's E-Business Suite, PeopleSoft, JD Edwards, and Oracle Cloud Applications  SAP Human Capital Management\
     Ultimate Software UltiPro\
     Workday\
    Globalization, flexible work rules, job mobility, and the strategic importance of people assets have forced organizations to transform their human resources systems into a more real-time, personalized, and operational intelligence business function that goes beyond the traditional view of aggregating personnel data. Core HR functions are being supplemented by extensions that form the basis of a new generation of HCM applications frameworks. The extensions are categorized in five major segments or submarkets: recruiting, incentive and compensation management, performance management, learning management, and workforce or time management. The sections that follow describe the functional aspects of these HCM systems.\
    Recruiting\
    Recruiting applications are designed to automate the recruitment process through better tracking of applicants, screening and skills assessment, profiling and resume processing, and identifying talent inside or outside the organization.\
    Key features include:\
     Managing skills inventories\
     Creating and managing job requisitions\
     Identifying appropriate employment candidates\
     Coordinating team collaboration within hiring processes\
     Facilitating resource planning\
     Deploying workers to appropriate jobs, projects, or teams\
    Representative recruiting applications include:\
     Kenexa (now part of IBM)  PeopleFluent\
     Oracle HCM Cloud\
    Compensation Management\
    Compensation management applications are designed to automate the process of planning and administering workforce compensation, providing both compensation administrators and managers tools to plan, calibrate, and confer salary changes. This category also includes incentive management, which involves cash and noncash incentives to employees through advanced modeling, reporting, and built-in interfacing to payroll accounting systems.\
    Key features include:\
     Salary budgeting and management\
     Quota and territory management\
     Calculation and distribution of commissions, spiffs, royalties, and incentives to employees and channel and business partners\
     Compensation analysis using internal and external data for retention risk analysis\
     Linking incentives — cash and noncash — to business objectives\
     Payroll and payment engine interfaces\
     Accounts payable integration\
    Representative compensation and incentive management applications include:\
     ADP\
     Callidus TrueComp  PeopleFluent\
     Synygy EIM\
     Oracle HCM\
    Workforce Performance Management\
    Workforce performance management applications are designed to automate the aggregation and delivery of information pertinent to the linking of job roles and the mission and goals of the organization. More specifically, the system allows users to automate the performance review process by using mechanisms such as training and key performance indicators (KPIs) to constantly track and monitor the progress of an individual employee, work team, and division.\
    Key features include:\
     Assessment of individual and organizational skills gaps that impede performance and job advancement, as in ability testing\
     Continuous reviews and establishing milestones\
     360-degree evaluation and real-time feedback\
     Performance appraisal automation\
     Competency assessment and management\
     Goal setting and tracking\
     Employee surveys\
     Alignment of workforce objectives to corporate objectives\
     Development and career planning\
     Fast tracks for top performers\
     Career and succession planning\
    Representative performance management applications include:\
     Cornerstone OnDemand\
     Halogen Software\
     PeopleFluent\
     SuccessFactors, an SAP company  Oracle HCM Cloud\
    Learning Management\
    Learning management applications are designed to automate the development, tracking, and delivery of learning content and experiences to employees with the goal of improving employee skills and productivity. Learning content ranges from traditional classroom training to online learning objects to mentoring. Learning management is increasingly integrated with employee performance management to prescribe development activities to ameliorate skills gaps or gaps in performance.\
    Key features include:\
     Course cataloguing and searching\
     Competency and skills tracking\
     Development planning\
     Delivery of online learning\
     Pre- and post-training assessments and tests\
     Online commerce for payments associated with training\
     Tools for trainers to manage class lists, syllabi, and resources  Training resource allocation\
     Content development tools\
    Representative learning management applications include:\
     Saba\
     SuccessFactors, an SAP company  SumTotal\
     Oracle HCM Cloud\
    Workforce Management\
    Workforce management applications are designed to automate the deployment of the workforce through workload planning, scheduling, time and attendance tracking, resource management, and rules and compliance management. Through extensive use of workforce management applications, organizations are also able to develop training guidelines, career advancement plans, and incentive compensation programs to improve, motivate, and sustain the quality of their employees.\
    Key features include:\
     Skills and certification tracking\
     Shift/vacation bidding\
     Workload planning, forecasting, and scheduling\
     Scheduling optimization\
     Customer wait-time forecasts\
     Coverage management\
     Absence management\
     Labor activity tracking\
     Rationalization of revenue per full-time equivalent\
     Cost of sales activities\
     Sales resource planning based on local and regional opportunities\
    Representative workforce management applications include:\
     Ceridian Dayforce\
     Infor's Workbrain Enterprise Workforce Management\
     Kronos\
     Meditech's Integrated HCIS, Scheduling, and Referral Management  WorkForce Software"))
    taxonomySort.categories[0].subCategories[2].addNewCategory("Payroll accounting")
    taxonomySort.categories[0].subCategories[2].subCategories[2].addText(ratioCreator("Payroll accounting functionality provides the calculations for wages, salary, and other labor-related payments including the tracking of stock option compensations, fringe benefits, bonuses, commissions, and other variable and nonvariable payments. Payroll accounting also includes the calculation and withholding of payroll taxes, garnishments, and other deductions.\
    As stated previously, payroll accounting is tracked separately and is not included in human capital management.\
    The following are representative vendors and products in the payroll accounting market:\
     DATEV (LODAS and Lohn und Gehalt)\
     SAP (SAP Core HR and Payroll — payroll only)\
     Intuit (QuickBooks Payroll)\
     Sage (Sage 50 Payroll, Sage One Payroll, Sage Paie, Sage Lohn XL, and Sage NominaPlus)"))
    taxonomySort.categories[0].subCategories[2].addNewCategory("Procurement")
    taxonomySort.categories[0].subCategories[2].subCategories[3].addText(ratioCreator("Procurement applications automate processes relating to purchasing supplies, material (whether direct or indirect; raw, in process, or finished; as a result of or flowing into a product supply chain–specific process; or in support of performing a service), and services (business or professional). The procurement function covers sourcing, procurement, transaction processing, and payments support, all of which are connected to create a single view of the spending levels at an organization. As a result, purchasing activities are integrated into a supplier community that can be easily tracked, benchmarked, and analyzed by both buyers and suppliers.\
    Features of these procurement modules include self-service requisitioning; order entry; approval workflow; transaction processing including electronic data interchange (EDI) and EDI-INT; strategic sourcing; dynamic pricing; commodity strategy and spot buying; contract discovery, management, tracking, and enforcement; catalog aggregation and syndication; supplier performance management; supplier enablement, onboarding, and portals; vendor-managed inventory support; invoice matching; vendor management; spend management; and procurement analytics.\
    The following are representative vendors and products in this market:\
     Basware (e-Procurement and Purchase-to-Pay)\
     Oracle (Oracle Procurement Cloud, Oracle E-Business Suite Advanced Procurement, and PeopleSoft Enterprise Supplier Relationship Management)\
     SAP (Contingent Workforce Management, Direct Procurement, Strategic Sourcing, and Supplier Relationship Management)\
     Workday (Procurement)"))
    taxonomySort.categories[0].subCategories[2].addNewCategory("Order management")
    taxonomySort.categories[0].subCategories[2].subCategories[4].addText(ratioCreator("Order management applications are designed to automate sales order processing from capture to invoice and settlement and include features to handle order planning and demand management capabilities. Item lookup and order placement are the prerequisites of order management applications, followed by the issuance of receipts, advanced shipping notices, and payment processing functions. Order and product configurations, as well as pricing options, freight calculation, and credit checking, are being combined to form an integrated order management application, regardless of the sales channels.\
    Other features include view price history, profit management, multiple order types (including quotes and credit orders), blanket and release orders, direct ship and transfer orders, kit processing, and product returns processing.\
    The following are representative vendors and products in this market:\
     Manhattan Associates (Order Management)\
     Oracle (E-Business Suite Order Management)  IBM (Sterling Order Management)"))
    taxonomySort.categories[0].subCategories[2].addNewCategory("Enterprise performance management applications")
    taxonomySort.categories[0].subCategories[2].subCategories[5].addText(ratioCreator("The enterprise performance management applications market consists of cross-industry applications whose main purpose is to measure, analyze, and optimize financial performance management, planning, forecasting, and certain risk management processes using prepackaged applications that include the following categories:\
     Budgeting and planning includes applications to support operational budgeting processes, corporate budget consolidation and adjustment processes, and planning and forecasting processes.\
     Financial consolidation and close includes applications that support both compliance with statutory requirements and management of financial consolidation, reporting, and adjustment processes across multiple entities and divisions. This includes functionality that manages external financial reporting compliance requirements in the close process, management of internal financial policies across all business operations, and assessment and analysis of the financial risks faced by an organization. It excludes the execution of these policies that are handled by distinct business departments including payroll, treasury management, or procurement.\
     Profitability management and activity-based costing applications include packaged applications to support detailed cost and profitability measurement and reporting processes.\
     Cross-functional strategy and risk management applications include those applications that support a closed-loop performance management methodology such as the balanced scorecard. Strategy management applications incorporate domain expertise across a range of business processes, such as finance, human resources, operations, and CRM, to enable strategic management of the organization. Strategy management applications help companies collect and agree on the risk requirements faced by their operations and monitor how effectively these risk requirements are managed across the enterprise. Enterprise risk assessments help the organization establish the enterprise risk appetite and conduct risk- adjusted performance management. In addition, this software can enable organizations to create and manage contingency plans to be executed as either positive or negative risks are realized. It does not directly manage any single cross-industry or vertical-specific GRC function.\
    The following are representative vendors and products in this market:\
     Adaptive Insights (Adaptive Planning and Adaptive Consolidation)  Host Analytics (Planning Cloud)\
     IBM (Cognos TM1, Cognos Controller, and Cognos FSR)\
     Intelex (Risk Management software)\
     Oracle (Oracle Hyperion Financial Management and Oracle Hyperion Planning)  SAP (Financial Performance Management Suite)\
     SAS (Risk Management and Profitability Management)"))
    taxonomySort.categories[0].subCategories[2].addNewCategory("Project and portfolio management (PPM)")
    taxonomySort.categories[0].subCategories[2].subCategories[6].addText(ratioCreator("Project and portfolio management (PPM) applications are used for automating and optimizing the initiating, planning/scheduling, allocation, monitoring, and measuring of activities and resources required to complete projects. \
    In addition, the portfolio management capabilities enable the tracking of an aggregation of projects, products, programs, and/or initiatives to oversee resource allocation, \
    for making ongoing investment and prioritization decisions, and track risks — as part of an overall portfolio with associated processes and workflows. Ultimately, PPM applications help \
    organizations manage the scope, time, value, and cost of discrete sets of related people processes (projects) on an individual and portfolio basis. PPM applications enable these capabilities and \
    can also be used as a module of a suite in some instances to provide project, program, and portfolio management functionality. There are many vertical and targeted applications of PPM solutions — for example, \
    PPM can be used in architectural/engineering/construction (AEC), manufacturing (new product development and introduction [NPDI]), utilities, professional services, facilities, asset and capital management, and other solutions,\
     leveraging the primary premise of successful 'project' completion as a core business purpose. Enterprise PPM (EPPM) encompasses the use of PPM capabilities across areas as a horizontal use case. IT project portfolio management (ITPPM) incorporates PPM \
     capabilities in the context of IT projects, so this use case can be applied horizontally across areas requiring software creation or other IT initiatives. PPM solutions are used as a core module in vertical enterprise resource planning solutions purpose built for \
     businesses that deliver a project instead of a product, like professional services firms, legal firms, advertising/PR firms, and engineering services. These solutions are called professional services automation (PSA) and services resource planning (SRP). PSA/SRP solutions,\
      although they have a PPM module, are very broad and are covered as a vertical variant of the enterprise resource management (ERM) market. The following are representative vendors and products in this market:\
     CA Technologies (CA Clarity PPM)\
     Meridian Proliance\
     Microsoft Project (Microsoft Project Professional and Microsoft Project Server)\
     Oracle (Oracle Fusion PPM and Oracle Primavera P6 Project Portfolio Management)  Planview\
     SAP PPM (Project and Portfolio Management)"))
    taxonomySort.categories[0].subCategories[2].addNewCategory("Enterprise asset management")
    taxonomySort.categories[0].subCategories[2].subCategories[7].addText(ratioCreator("Enterprise asset management applications software automates the many aspects of managing an organization's physical assets: asset performance management, asset life-cycle management, computerized maintenance management, facilities management, fleet management, integrated workplace management, and maintenance, repair, and overhaul (MRO) operations. The software generally includes functionality for planning, organizing, and implementing maintenance activities, whether they are performed by employees of the organization or by a contractor, volunteer, or other individual. Typical features include equipment history record management, descriptions of items maintained, scheduling, preventive and predictive maintenance on the assets, work order management, labor tracking (if integrated within the maintenance management applications), spare parts management, and maintenance reporting. An organization's assets may include buildings, oil rigs, pipelines, mining equipment, manufacturing equipment, fleets, and more that may be stationary but are often moving, floating, and flying, increasing the need for sensors, mobile, and wearable technologies to manage these large, complex, expensive, and often aging assets.\
    The following are representative vendors and products in the market:\
     ABB Ventyx (Enterprise Asset Management)\
     IBM (IBM Maximo Asset Management and IBM TRIRIGA Facility Management)\
     IFS (Enterprise Asset Management)\
     Infor (Infor EAM Enterprise, Infor EAM Energy Performance Management, and Infor MP2)\
     Oracle (Oracle Enterprise Asset Management and PeopleSoft Asset Lifecycle Management)  Ramco (Enterprise Asset Management)"))


    taxonomySort.categories[0].addNewCategory("SCM")


    taxonomySort.categories[0].subCategories[3].addNewCategory("Logistics")
    taxonomySort.categories[0].subCategories[3].subCategories[0].addText(ratioCreator("Logistics application software automates activities relating to moving inventory or materials of any type. Examples include software that automates distribution resource planning, transportation planning, and transportation optimization business processes that are not specific to an industry. (Logistics applications specific to the transportation industry are included in the services operations management applications market.) The following are representative vendors and products in this market:\
      Manhattan Associates (Transportation Lifecycle Management)\
      RedPrairie (Transportation Management)\
      JDA (Transportation and Logistics Management)"))
    taxonomySort.categories[0].subCategories[3].addNewCategory("Production planning")
    taxonomySort.categories[0].subCategories[3].subCategories[1].addText(ratioCreator("Production planning (PP) applications software automates activities related to the collaborative forecast and continuous optimization of manufacturing processes. PP applications span supply planning, demand planning, and production planning within organizations. These applications identify demand signals, aggregate historical data that informs short- and long-term demand expectations, and provide supplier capabilities across multiple manufacturing sites. Production planning application software is key to any supply chain management initiative because supply and demand planning dictates the rest of the supply chain activities. The following are representative vendors and products in this market:\
     Aspen Technology (Aspen Collaborative Demand Manager and Aspen Supply Chain Planner)\
     Oracle (Advanced Planning Command Center, Advanced Supply Chain Planning,\
    Collaborative Planning, and Demand Management)\
     SAP (Supply Chain Planning and Collaboration)"))
    taxonomySort.categories[0].subCategories[3].addNewCategory("Inventory management")
    taxonomySort.categories[0].subCategories[3].subCategories[2].addText(ratioCreator("Inventory management application software automates activities relating to managing physical inventory, whether direct or indirect; raw, in process, or finished; as a result of or flowing into a product supply chain–specific business process; or in support of performing a service. This includes inventory control/materials management business processes in any industry, not just in manufacturing. It also\
    includes all aspects of warehouse planning and management. The following are representative vendors and products in this market:\
     CDC (CatalystCommand Warehouse Management)  SAP (SAP SCM Warehouse Management)\
     JDA Software (RedPrairie Warehouse Management)"))


    taxonomySort.categories[0].addNewCategory("O&M")

    taxonomySort.categories[0].subCategories[4].addNewCategory("Services operations management")
    taxonomySort.categories[0].subCategories[4].subCategories[0].addText(ratioCreator("Services operations management (SOM) applications support the services supply chain and are unique to particular industries. These industry-specific applications cover a broad range of activities such as automating claim processes (as applied to insurance functions), automating admissions/discharges and transfers of patients (as applied to healthcare functions), or automating energy trading (as applied to energy and utility functions). Other examples of industry-specific applications are those that enable the automation of real estate, business, legal services, banking and finance, education, government, social services, and transportation. SOM also includes software applications that enable communications and data transfer between devices that perform business and services operations that are specific to services industries like healthcare, government, and transportation. Please note that not all applications sold partially or exclusively to one or more vertical industries qualify for this market. If an application performs a payroll function, for example, but it is designed and sold only to the insurance industry, it would still be included in the payroll accounting market. The application must be designed to perform a function unique to a particular industry in order to qualify for the SOM market. The following are representative vendors and products in this market:\
     Cerner Corp. (Millennium)\
     McKesson ClaimsXten for insurance claims management  Oracle Utilities"))
    taxonomySort.categories[0].subCategories[4].addNewCategory("Manufacturing")
    taxonomySort.categories[0].subCategories[4].subCategories[1].addText(ratioCreator("Functional applications in manufacturing include material and capacity requirements planning (MRP), bill of materials (BOMs), recipe management, manufacturing process planning and simulation, work order generation and reporting, shop floor control, quality control and tolerance analysis, and other functions specific to manufacturing execution (MES). The category does not include computer-aided manufacturing (CAM) applications for NC and CMM machine programming. (Advanced planning and scheduling applications are included in the supply chain production planning functional market.) Representative vendors and products in this market are:\
     Aspen Technology's PIMS for production planning and optimization\
     Dassault's DELMIA production process planning and simulation applications  Siemens Tecnomatix's Assembly Planning and Validation"))
    taxonomySort.categories[0].subCategories[4].addNewCategory("Other back office")
    taxonomySort.categories[0].subCategories[4].subCategories[2].addText(ratioCreator("Other back-office applications include various types of application automating functions not otherwise covered previously, such as computer-based training, elearning applications, speech and natural language, translation and globalization software, and environmental health and safety applications. These applications also cover a wide range of point solutions for product-related applications other than services operations management and manufacturing. These applications have at their core a product orientation focused on efficiencies related to item maintenance, replenishment, and site management. Among them are retail- and wholesale-specific applications. Representative vendors and products in this market are:\
     Epicor's Retail Software Systems\
     JDA Trade Event Management for retail\
     Oracle Retail Merchandise Operations Management  SAP EH&S"))


    taxonomySort.categories[0].addNewCategory("Engineering")

    taxonomySort.categories[0].subCategories[5].addNewCategory("Mechanical CAD")
    taxonomySort.categories[0].subCategories[5].subCategories[0].addText(ratioCreator("Mechanical Computer-Aided Design\
    MCAD software is utilized for tasks typically performed by designers and drafters. Specifically, this category includes computer-assisted designing, drafting, and modeling (wire frame, surface, and solid). MCAD also includes conceptual design and/or industrial design, animation and visualization, and assembly design. (Light geometry visualization such as Siemens PLM's [previously UGS'] JT, Oracle's [previously Agile's] AutoVue, or Autodesk's DWF is included in cPDM.) The following are representative vendors and products in this market:\
     Dassault Systèmes CATIA and SOLIDWORKS  PTC Pro/ENGINEER\
     Siemens PLM NX and Velocity"))
    taxonomySort.categories[0].subCategories[5].addNewCategory("Mechanical CAE")
    taxonomySort.categories[0].subCategories[5].subCategories[1].addText(ratioCreator("Mechanical Computer-Aided Engineering\
    Mechanical CAE applications address tasks such as structural/stress analysis, kinematics, fluid dynamics, thermal analysis, and test data analysis. The following are representative vendors and products in this market:\
     ANSYS analysis products\
     Autodesk Moldflow Corp.\
     MSC Software Nastran and Patran analysis products"))
    taxonomySort.categories[0].subCategories[5].addNewCategory("Mechanical CAM")
    taxonomySort.categories[0].subCategories[5].subCategories[2].addText(ratioCreator("Mechanical Computer-Aided Manufacturing\
    Mechanical CAM applications prepare data for actual production on the shop floor (e.g., NC tape generation and data for CNC machines). The following are representative vendors and products in this market:\
     Cimatron CimatronE NC\
     CNC Software Mastercam  Siemens PLM NX"))
    taxonomySort.categories[0].subCategories[5].addNewCategory("Collaborative product data management")
    taxonomySort.categories[0].subCategories[5].subCategories[3].addText(ratioCreator("Collaborative product data management (cPDM) applications provide engineering groups, but also increasingly cross-disciplinary teams across the enterprise as well as outside of its four walls, with software tools to electronically coordinate, manage, and share product data throughout the product life cycle. The major subsegments of this market are product data vaulting, document management, light geometry with view/markup capabilities (collaboration), change management, and parts libraries. Workflow, ideas management, and product-focused environmental compliance management are now emerging as additional application subsegments. The following are representative vendors and products in this market:\
     Oracle Agile Software and AutoVue\
     Siemens PLM Teamcenter\
     Sopheon Accolade for Product Innovation and Accolade Process Manager"))
    taxonomySort.categories[0].subCategories[5].addNewCategory("Other engineering")
    taxonomySort.categories[0].subCategories[5].subCategories[4].addText(ratioCreator("Other engineering applications support electronic design automation, architectural/engineering/construction, and other engineering functions. AEC applications software automates drawing/design of building-related and civil engineering–related projects. (AEC project and portfolio planning and facilities management are part of the project and portfolio management functional market.) The following are representative vendors and products in this market:\
     Autodesk Building Information Modelling (BIM) applications  Bentley Systems GEOPAK Civil Engineering Suite"))

    taxonomySort.categories[0].addNewCategory("CRM")
    taxonomySort.categories[0].subCategories[6].addText(ratioCreator("CRM applications automate the customer-facing business processes within an organization, irrespective of industry specificity (i.e., sales, marketing, customer service, and contact center). Collectively, these applications serve to manage the entire life cycle of a customer — including the process of brand building, conversion of a prospect to a customer, and the servicing of a customer — and help an organization build and maintain successful relationships. Interactions in support of this process can occur through multiple channels of communication. Channels of communication include but are not limited to email, phone, social, and on a Web site.\
    Additional technologies impacting CRM are as follows:\
     Social CRM. IDC includes functionality that incorporates social capabilities within a CRM construct within the relevant functional market. Social listening and social media analytics and social media management and marketing are included in the marketing segment. Social sales applications are included in sales, and social service applications are included in customer service.\
     SaaS. CRM applications that are offered through an on-demand or SaaS delivery model are categorized within the appropriate functional market.\
     Digital commerce. IDC defines digital commerce application software as applications that are directly involved in or linked to the application in which an order is placed or accepted, therefore representing a commitment for a transfer of funds in exchange for goods or services. Included in this process is the presentation of the product to the customer in the form of an online catalog. As is the case with other competitive software markets, digital commerce applications derive from existing functional markets. Applications that manage the catalog and customer-facing portions of the digital commerce process are categorized in the appropriate CRM market.\
    Definitions of the CRM application segments are presented in the sections that follow."))

    taxonomySort.categories[0].subCategories[6].addNewCategory("Sales")
    taxonomySort.categories[0].subCategories[6].subCategories[0].addText(ratioCreator("Sales automation applications include both sales management applications and sales force automation (SFA) applications. Functionality includes the following:\
     Account/contact management  Shopping cart\
     Lead management\
     Mobile sales\
     Opportunity management\
     Partner relationship management (PRM)\
     Sales analysis and planning tools\
     Sales configuration tools including configure, price, and quote  Sales history\
     Team selling\
     Telemarketing and telesales scripting\
     Territory management\
    The following are representative vendors and products in this market:\
     Oracle (Oracle Sales, Oracle's Siebel Sales, Oracle Sales Prospector, and Oracle CRM On Demand Sales)\
     salesforce.com (Sales Cloud2)\
     SAP (SAP Sales and SAP Cloud for Sales)\
     SAVO Group (SAVO)\
     Swiftpage (ACT!)"))
    taxonomySort.categories[0].subCategories[6].addNewCategory("Marketing")
    taxonomySort.categories[0].subCategories[6].subCategories[1].addText(ratioCreator("Marketing applications software automates a wide range of individual and collaborative activities associated with the various components of the marketing process, including strategic marketing activities over more operational, campaign-related activities to catalogue-based digital commerce and trade promotions management. Newer areas of functionality included in the marketing segment are social media analytics, social listening, social influence, and social media management and marketing applications.\
    Functionality includes the following:\
     Ad management/placement\
     Brand management\
     Campaign planning, execution, and management  Collateral management/distribution\
     Direct/database marketing\
     Electronic catalog/storefront solutions\
     Email marketing\
     Social media management and marketing\
     Sentiment analysis\
     Customer, segmentation, and predictive analytics  Event/trade show management\
     Focus groups/media testing\
     Lead generation/qualification/distribution\
     List management\
     Marketing resource management\
     Media and analyst relations\
     Mobile device marketing\
     Personalization\
     Primary research\
     Surveying\
     Trade promotion management\
     Upselling and cross-selling programs\
     Web activity analysis\
     Web advertising\
    The following are representative vendors and products in this market:\
     Adobe (Adobe Marketing Cloud)\
     IBM (Coremetrics [IBM customer analytics solutions], Silverpop, Tealeaf, Unica, and Xtify)\
     Marketo\
     Oracle (Oracle Marketing Cloud)\
     SAP (hybris Marketing suite and SAP Trade Promotion Optimization)\
     Salesforce.com Marketing Cloud (Buddy Media, Radian6, and ExactTarget)\
     SAS (Marketing Resource Management, Campaign Management, and Real-Time Decision Manager)\
     Teradata Integrated Marketing Cloud"))
    taxonomySort.categories[0].subCategories[6].addNewCategory("Customer service")
    taxonomySort.categories[0].subCategories[6].subCategories[2].addText(ratioCreator("Customer service applications provide customer/client (e.g., patient and student) information management (CIM). Each application is designed to enhance the management of relationships with existing customers. Customer service software is used to service customers that are external to an organization. Newer capability added to the segment includes social service response.\
    Defining characteristics of the customer service category include case management, customer history, and incoming contact management. Functionality includes:\
     Automated assistants\
     Case assignment and management  Conferencing\
     Customer communities software\
     Email response management\
     Field service\
     Live collaboration and chat\
     Self-service\
     Web chat\
     Social network response\
    IT help desk applications are covered under 'problem management' in the system management software category and are thus excluded from this market. The following are representative vendors and products in the customer service application market:\
     Amdocs (Contact Center, Smart Agent Desktop, and Customer Service and Support)  Aptean (Consona Service and Support)\
     Lithium (Social Customer Community Software and Social Customer Support)\
     Oracle (Oracle Service and Oracle Service Cloud)\
     salesforce.com (Service Cloud 2)\
     SAP (SAP Cloud for Service and SAP CRM for Service)  Verint (KANA Enterprise and LAGAN Enterprise)"))
    taxonomySort.categories[0].subCategories[6].addNewCategory("Contact center")
    taxonomySort.categories[0].subCategories[6].subCategories[3].addText(ratioCreator("Contact center applications automate functions relating to the operations of the CRM installation. These applications, although enabling in function, do not have a desktop end-user focus. Products included in this category are ACD, predictive dialing, telephony integration, and universal queuing. The following are representative vendors and products in this market:\
     Aspect (Call Center ACD and Unified IP)\
     Avaya (Call Center, Interaction Center, Contact Center Express, and Customer Interaction\
    Express)\
     Genesys (Customer Interaction Management Platform, Agent Desktop, Proactive Contact, and Voice Platform)\
     SAP (SAP Contact Center)"))

    taxonomySort.categories[0].addNewCategory("Structured Data Management")
    taxonomySort.categories[0].subCategories[7].addText(ratioCreator("Structured data management software includes products that manage a common set of defined data that is kept in one or more databases (structures of managed data shared by multiple application programs) and is driven by data definitions and rules, whether this involves single databases accessed directly by applications or distributed databases accessed by multiple applications in multiple locations. The distinguishing characteristic of all structured data management software products is that\
    they use definitions of data structure and behavior along with rules governing their integrity, validity, security, and, in some cases, alternative formats to manage the storage, movement, and manipulation of data kept in databases. The user community for structured data management software typically includes database administrators, data modeling analysts, data administrators, and developers of database-intensive applications.\
    A database management system (DBMS) is a software entity that manages a database in such a way that it may be queried and randomly updated. Two of the functional markets we define in the sections that follow — relational database management systems and nonrelational database management systems — are schematic database management systems. Schematic DBMSs, including relational and nonrelational DBMSs, are governed by schemas. The schema indicates the structure of the data, including its various data objects (which may be referred to as 'record types,' 'object types,' 'classes,' or 'tables,' depending on the paradigm of the DBMS in question and the types of relationships or associations among these objects). The schema contains rules governing the organization of such associations (such as optionality and cardinality) and the object formats (including field, column, or attribute types, valid values). It may also contain security rules governing access to the data. The schema enables multiple applications having separate code bases to share common data without sharing program source code. In most cases (especially with RDBMS), the database may also be queried by an end user without requiring program code specifically developed for that purpose, simply by traversing the data structure as defined by the schema.\
    Dynamic data management systems, the third market in this section, share some characteristics with DBMSs; they support the common storage and retrieval of data that is optimized in a managed environment for quick saving and retrieval, or query, or both. The key difference, and what makes them 'dynamic,' is that they have no schema but depend on program code to define their contents. In some cases, they use embedded tagging to indicate the names of fields. In other cases, that knowledge must be present in the application software. They are used in cases where the data may not be well defined at the time of ingestion or where the application data requirements change so frequently that schematic management represents unacceptable overhead, slowing down the development process."))



    taxonomySort.categories[0].subCategories[7].addNewCategory("Relational database management systems (RDBMSs)")
    taxonomySort.categories[0].subCategories[7].subCategories[0].addText(ratioCreator("The relational database management system market includes multiuser DBMSs that are primarily organized according to the relational paradigm and that use SQL, or a protocol like SQL (such as ODBC or JDBC) as the foundational language for data definition and access. A relational DBMS includes a schema that defines the ways that data is accepted and returned in terms of tables having columns, with rows uniquely identified by a primary key for each table, and with columns that are used to relate rows in different tables to each other through a value reference called a foreign key. Also included in this market are RDBMSs that have been extended to support embedded tables or other nonrelational enhancements or include extended attribute types (such as graphical, geospatial, and audio), object-oriented formalisms (such as data encapsulation), or direct support for XML data. It also includes NewSQL DBMSs that may feature late schema binding, elastic scalability, and dynamic schema change. The following are representative vendors and products in this market:\
     Actian (Ingres, Matrix, and Vector)\
     IBM (DB2 family and the Informix family)\
     Microsoft (Microsoft SQL Server and Azure SQL Database)  NuoDB (NuoDB)\
     Oracle (Oracle Database, TimesTen, and MySQL)\
     SAP (SAP HANA, SAP Adaptive Server Enterprise, SAP IQ, and SAP SQL Anywhere)  Teradata (Teradata and Aster Database)"))
    taxonomySort.categories[0].subCategories[7].addNewCategory("Nonrelational database management systems (NDBMSs)")
    taxonomySort.categories[0].subCategories[7].subCategories[1].addText(ratioCreator("Nonrelational database management systems are schematic DBMSs that are not based on the relational paradigm. They use a variety of other approaches to the organization, management, storage, and retrieval of data. Types of nonrelational DBMSs are discussed in the sections that follow.\
    End-User Database Management Systems\
    End-user DBMSs (EUDBMSs) are schematic, but the schema is simple and its definition process is informal. EUDBMSs enable end users to define and manage their own data without any need for formal database administration. Such DBMSs typically reside on desktop operating environments, on workgroup servers, or in the cloud. They are used by knowledge workers either individually or in collaboration with others. These tools typically include a DBMS engine tightly integrated with a scripting language and report writer or other visualization facility, which provides a localized environment for data management and analysis.\
    Navigational Database Management Systems\
    A navigational DBMS is accessed using explicit navigation of the structure by the problem program and is typically organized using either the CODASYL or a proprietary structure. List oriented, hierarchical, B-tree indexed, network, and inverted list are examples of organizations included in this category. The data is normally managed and accessed through a proprietary language or API, though most of these products also support access through standardized interfaces such as SQL, ODBC, JDBC, ADO.NET, Java Entity Beans, and various Web services.\
    Object-Oriented Database Management Systems\
    Object-oriented DBMSs (OODBMSs) are designed to provide data storage and support services using an object-oriented architecture. An object-oriented DBMS supports the basic features of object- oriented development, including inheritance, polymorphism, encapsulation, and state. Unlike the other types of DBMSs, the OODBMS provides an implicit set of services associated with classes in the application object model that have been identified as 'persistent,' so there is no API, DML, or service call to be invoked by application code. Because of the intimate relationship between the OODBMS data organization and the application, it is schematic, and its database schema must be aligned, either implicitly or explicitly, with the class structure of the application. Also, an OODBMS must explicitly support (through header files and runtime libraries) each language to be used with it. These languages typically include Smalltalk, C++, C#, and Java.\
    Multivalue Database Management Systems\
    A multivalue DBMS is schematic and has an internal structure that supports nested data lists or structures. It layers over that structure a set of access and management services that operate according to one or more abstraction paradigms, which usually include both relational and object- oriented functionality. These products typically have proprietary DDL and DML and sets of APIs or drivers but can be accessed using standard SQL and other standard interfaces as well. Although they may support object-oriented data definition and manipulation, they differ from object-oriented DBMSs in that they make the database an explicit external service to which the application connects through an API or service layer. By contrast, object-oriented DBMSs enable the user to define database components as classes within the application object model and manipulate the database through\
    methods inherited from a DBMS class library, thus making the DBMS itself an implicit service of the application's environment.\
    Representative NDBMS Products by Type\
    The following are representative vendors and products in the nonrelational DBMS market:\
     End-user database management systems:\
     Binary Brilliant (Brilliant Database)\
     CA Technologies (Clipper)\
     FileMaker, subsidiary of Apple Computer (FileMaker)  Microsoft (Access and FoxPro)\
     Navigational DBMSs:\
     CA Technologies (IDMS and Datacom)  IBM (IMS)\
     Oracle (Berkeley DB)\
     Software AG (Adabas)\
     Object-oriented database management systems:  Actian (Versant ODS)\
     Objectivity (Objectivity/DB)\
     ObjectStore (ObjectStore)\
     Multivalue DBMSs:\
     Enea (Polyhedra)\
     InterSystems (Caché)\
     Matisse (Matisse)\
     Rocket Software (UniVerse and UniData)  TigerLogic (TL Pick)"))
    taxonomySort.categories[0].subCategories[7].addNewCategory("Dynamic data management systems")
    taxonomySort.categories[0].subCategories[7].subCategories[2].addText(ratioCreator("A dynamic data management system can accept data without requiring that the structure and elements of the data be defined in advance. These include scalable data collection managers (the most common being Hadoop) and dynamic DBMSs. Because they do not require the use of SQL, dynamic DBMSs are sometimes called NoSQL database systems. There are two categories of dynamic DBMS:\
     Semi-schematic — where the data may be governed by a schema, but one is not required (Any data may be entered into the database that conforms to the general data format of the DBMS if no schema is present. If a schema is present, it governs the data and optimizes database operation on that basis.)\
     Non-schematic — where no schema is required and any data conforming to the general format of the database may be added\
    The resulting collection of data may end up being rationalized under a schematic structure (in the semi-schematic case), mapped based on field names and values, or simply accessed by means of key-value pairs. Types of dynamic data management systems are discussed in the sections that follow.\
    Document-Oriented Database Systems\
    Document-oriented database systems manage data blocks containing fields that are identified according to a generally accepted document format. The two most common such formats are Extensible Markup Language (XML) and JavaScript Object Notation (JSON). Some document-oriented databases require the documents to be uniquely identified by a key value, and others do not. Some are semi-schematic, supporting the assertion of a document schema to ensure structural consistency, or simply facilitate document queries, and others are not. Some index all the fields, others allow users to designate some fields for indexing, and some don't index at all. Some document-oriented database systems have full DBMS capabilities for those that wish to take advantage of them, including schema support, optimized SQL query support, and relationship integrity constraint support.\
    Key-Accessible Database Systems\
    Key-accessible databases are non-schematic and store data in a way that supports random retrieval by key value or retrieval in key-value order. They are not true database management systems, since they merely facilitate the storage and retrieval of data according to certain optimized techniques but do not actually manage the database per se; the applications do that. There are two recognized key- accessible database system types:\
     Keyed block stores, also called key-value stores: These are the simplest in concept. They store blocks of data that are identified by key value; the rest of the data is program defined. They incorporate no intrinsic knowledge of fields or relationships.\
     Keyed column stores, sometimes called wide column stores: These store blocks of data- containing columns, which are lists of values. One of these columns is the key column. The columns are grouped into column families. Within each family, the values in each column are related to the values in every other column according to their position in the list. They are sometimes called wide column stores because column families often have very large numbers of columns, and the data is typically completely un-normalized.\
    Graph Database Management Systems\
    Graph DBMS software manages data as graph structures. These contain objects sometimes called 'nodes' or 'vertices' with recursive attributed relationships, sometimes called 'edges.' The attributes of the objects and relationships are called 'properties.' Unlike a fully schematic database, the structure of a graph database is derived from the relationship structure that is found in the instance data.\
    Such databases can be thought of as schematic in some cases because some graph DBMSs support the assignment of attributes and constraints for nodes and vertices in metadata. In a larger sense, however, schemas do not define data organization; rather the database is designed to discover that organization. In some cases, the schema structure (i.e., the acceptable patterns of combinations of nodes, edges, and properties) may be predefined and fixed, and in other cases, it may be inferred from the data as it is ingested. Graph databases are used to capture and analyze extremely complex relationship instance structures. Common use cases include genealogy-based, spatial-based, and law enforcement (or intelligence service)–based 'known associates' analysis. Graphs are also used in pharmacological research, epidemiology, and utility network analysis.\
    Scalable Data Collection Managers\
    Scalable data collection managers are not really DBMSs since they do not manage data directly but provide an environment for data management. These systems are sets of cluster management, file management, and application execution software designed to facilitate applications that collect large\
    amounts of data, sift through and organize that data, and perform analytics on the data. The data collection may or may not end up containing one or more databases.\
    Currently, the only software in this category comes from the Apache Hadoop family of open source software projects. The relevant components, in this regard, are so-called 'core Hadoop' (Hadoop Common, HDFS, Hadoop MapReduce, and YARN) as well as Spark, Ambari, Pig, Tez, and ZooKeeper. It should be noted that Apache Spark, though usually deployed on HDFS, can run on its own clustering environment without Hadoop at all, but is closely related to Hadoop and supported by all the leading Hadoop distributors. HBase is a keyed column store, and Hive is data access infrastructure software in the data integration and integrity software market, though when these are bundled under a single subscription fee with core Hadoop, their revenue is counted altogether in this market.\
    Representative DDMS Products by Type\
    The following are representative vendors and products in the dynamic data management systems market:\
     Document-oriented database systems:  Amazon DynamoDB\
     Couchbase\
     IBM (Cloudant)\
     MongoDB\
     MarkLogic (MarkLogic)\
     Software AG (webMethods Tamino)  Xpriori (XMS)\
     Key-accessible database systems:  Amazon (SimpleDB)\
     Apache HBase\
     Basho (Riak)\
     DataStax (distributor of Apache Cassandra)\
     Google (Bigtable, a component of Google App Engine)  Oracle (Oracle NoSQL Database)\
     Graph database management systems:  DataStax (Titan)\
     Franz Inc. (AllegroGraph)\
     Neo Technology (Neo4j)\
     Objectivity (InfiniteGraph)  OrientDB\
     YarcData (Urika)\
     Scalable data collection managers  Amazon EMR\
     Cloudera (Hadoop)\
     Hortonworks (Hadoop)\
     MapR (Hadoop)\
     Microsoft HDInsight  Pivotal HD"))
    taxonomySort.categories[0].subCategories[7].addNewCategory("Database development and management tools")
    taxonomySort.categories[0].subCategories[7].subCategories[3].addText(ratioCreator("Database development and management tools are used to develop, load, reload, reorganize, recover, or otherwise manage and optimize databases and maintain replica databases for recovery, performance, or availability purposes. Tools used to archive, mask, and subset database data also belong to this market. Tools used to build logical models of the data are also included. This category also includes database-specific accelerators, SQL optimization tools, database security, and other database utilities. This market includes the submarket segments that follow.\
    Database Administration Tools\
    This submarket includes database monitoring and tuning tools and other tools for performing routine database administration (DBA) tasks such as reorganizations, rebuilding indexes, reallocating database storage, changing and redefining indexes, and tuning optimization options. Representative companies include:\
     BMC (BMC Data Management for IMS and DB2 on z/OS)\
     CA Technologies (CA Database Management products for DB2 and IMS)  Dell (Toad product family)\
     IDERA (Database Management Solutions)\
    Database Replication Software\
    This software is used for maintaining an exact copy of a live database or a subset of a live database, typically for recoverability, high availability, or nonstop maintenance purposes, or to distribute the database workload or isolate workload components by segregating them and assigning them to separate, replicated instances. Representative companies include:\
     Dell (SharePlex)\
     Oracle (Oracle GoldenGate)\
     SAP (SAP Replication Server)  Vision Solutions (MIMIX)\
    Data Modeling Tool\
    Data modeling (DM) tools address database design, development, and master data management. Representative vendors and products include:\
     Embarcadero Technologies (ERwin)  IBM (InfoSphere Data Architect)\
    Database Archiving and ILM Software\
    Products in this segment are used to manage the evolution of data from its creation to removal from the database and include database subsetting, data masking, and test data–generation tools as well as tools that build and maintain archives of databases, often allowing transparent access to archived data, preserving original schema information about archived data and intelligence for selecting referentially complete subsets of data for archiving. (Such products can also be used to create referentially complete subsets of databases for populating subset or test databases.) Examples of companies in this submarket include:\
     HPE (HP Integrated Archive Platform)\
     IBM (Optim)\
     Informatica (Informatica Data Archive, Data Subset, and Data Privacy)  Solix (Solix Enterprise Data Management Solutions)\
    Database Development and Optimization Software\
    This segment includes database management software such as SQL authoring tools and SQL optimization and analysis tools. It also includes software for database security, database caching, and database acceleration. Sample providers are:\
     Dell (Toad for Database Developers)\
     Delphix\
     IDERA (Database Development Solutions)  ScaleArc\
    Database Security Software\
    This segment includes software that enhances database security, usually in one or more of four ways: through database log analysis for the detection of improper data access, database access control, dynamic data masking, or database encryption. Sample providers are:\
     BlueTalon\
     Imperva\
     Protegrity (Data Security Platform)  Trustwave (DbProtect)"))
    taxonomySort.categories[0].subCategories[7].addNewCategory("Dynamic data grid managers")
    taxonomySort.categories[0].subCategories[7].subCategories[4].addText(ratioCreator("Dynamic data grid managers (DDGMs) manage data that is being used and constantly altered by running application processes. This software enables those processes, running either on a single system or multiple systems in a network, to share this data. The data is transient rather than recorded data and so is relevant to application tasks at the specific time it is accessed and is generally contextually specific. As such, this software does not include database management systems, which manage recorded data that is application neutral and independent of context.\
    Like a DBMS, a DDGM usually (though not always) has metadata that defines the data it manages, and it may also ensure recoverability of long application tasks through a persistent log or by redundant systems synchronization. A DDGM may be associated with a back-end DBMS that records the final state of data collections that the DDGM manages; that back-end DBMS may be specific to the DDGM, or it may be a general-purpose DBMS, such as a RDBMS. The DBMS is not part of this product, however.\
    The DDGM is typically memory based, managing its data as collections in main memory (which may be swapped to disk in cases where the amount of memory is insufficient to handle all the data; in this way, it resembles a virtual memory manager). It may or may not use locking to control concurrent access, and it may or may not have a notion of write ownership of specific data elements. Even in such cases, its method of granting access to data is generally less formal than that of a DBMS.\
    The purpose of the DDGM is to allow an application's processes to be spread across many servers in a network or nodes in a cluster while closely sharing data. Typical application architectures for DDGM include a service-oriented architecture (SOA) and a distributed process Web application running on a cluster. Sometimes, a DDGH is persistent, writing its data to disk for recoverability, and its vendor may\
    call it a 'database.' It is not a DBMS, however, if it cannot be used to share data across applications (except by sharing program code) or query end users. Thus key-value stores used to share data across instances of an application for the purpose of performance and scalability, without governing metadata for application-neutral data sharing, are also DDGMs.\
    Examples of DDGMs include:\
     Aurea Software (DataXtend SI)  Oracle (Oracle Coherence)\
     Red Hat (JBoss Data Grid)\
     SAP Data Services\
     Pivotal (GemFire)"))
    taxonomySort.categories[0].subCategories[7].addNewCategory("Data integration and integrity software")
    taxonomySort.categories[0].subCategories[7].subCategories[5].addText(ratioCreator("Data integration and integrity (DI) software enables the access, blending, movement, and integrity of data among multiple data sources. The purpose of data integration is to ensure the consistency of information where there is a logical overlap of the information content of two or more discrete systems. Data integration is increasingly being used to capture, prepare, and curate data for analytics. It is also the conduit through which new data types, structures, and content transformation can occur in modern IT environments that are inclusive of relational, nonrelational, and semi-structured data repositories.\
    Data integration software employs a wide range of technologies, including, but not limited to, extract, transform, and load (ETL); change data capture (CDC); federated access; format and semantic mediation; data quality and profiling; and associated metadata management. Data access is increasingly becoming open with standards-based APIs; however, there is still a segment of this market focused on data connectivity software, which includes data connectors and connectivity drivers for legacy technologies and orchestration of API calls.\
    DI software may be used in a wide variety of functions. The most common is that of building and maintaining a data warehouse, but other uses include enterprise information integration, data migration, database consolidation, master data management (MDM), reference data management, metadata management, and database synchronization, to name a few. Data integration may be deployed and executed as batch processes, typical for data warehouses, or in near-real-time modes for data synchronization or dedicated operational data stores. A data migration can also be considered a one-time data integration. Although most applications of DIA software are centered on structured data in databases, they may also include integrating data from disparate, distributed unstructured or semi-structured data sources, including flat files, XML files, and legacy applications, Big Data persistence technologies, and the proprietary data sources associated with commercial applications from vendors such as SAP and Oracle. More recently, an interactive form of data integration has emerged in the application of self-service data preparation.\
    The data integration and integrity software market includes the submarkets discussed in the sections that follow.\
    Bulk Data Movement Software\
    This software, commonly referred to as extract, transform, and load software, selectively draws data from source databases, transforms it into a common format, merges it according to rules governing possible collisions, and loads it into a target. A derivative of this process, extract, load, and transform (ELT), can be considered synonymous with ETL for the purpose of market definition and analysis. ELT\
    is an alternative commonly used by database software vendors to leverage the inherent data processing performance of database platforms. ETL and/or ELT software normally runs in batch but may also be invoked dynamically by command. It could be characterized as providing the ability to move many things (data records) in one process.\
    The following are representative companies in this submarket:\
     IBM (InfoSphere DataStage)\
     Informatica (PowerCenter)\
     Oracle (Oracle Data Integrator)\
     SAP (SAP Data Integrator, SAP Data Services, HANA Smart Data Integration)  SAS (SAS Data Management)\
     Talend (Open Studio for Data Integration)\
    Dynamic Data Movement Software\
    Vendors often refer to this functionality as providing 'real time' data integration; however, it can only ever be 'near' real time due to the latency inherent in sensing and responding to a data change event occurring dynamically inside a database. Data changes are either captured through a stored procedure associated with a data table or field trigger or a change data capture (CDC) facility that is either log or agent based.\
    These solutions actively move the data associated with the change among correspondent databases, driven by metadata that defines interrelationships among the data managed by those databases. The software is able to perform transformation and routing of the data, inserting or updating the target, depending on the rules associated with the event that triggered the change. It normally either features a runtime environment or operates by generating the program code that does the extracting, transforming, and routing of the data and updating of the target. It could be characterized as software that moves one thing (data record or change) many times.\
    The following are representative companies in this segment:\
     ETI (ETI)\
     IBM (InfoSphere Data Replication)\
     Informatica (PowerCenter Real Time Edition)\
     Oracle (Oracle GoldenGate)\
     SAP (SAP Replication Server, SAP Data Services)\
    Data Quality Software\
    This submarket includes products used to identify errors or inconsistencies in data, normalize data formats, infer update rules from changes in data, validate against data catalog and schema definitions, and match data entries with known values. Data quality activities are normally associated with data integration tasks such as match/merge and federated joins but may also be used to monitor the quality of data in the database, either in near real time or on a scheduled basis.\
    The data quality software submarket also includes purpose-built software that can interpret, deduplicate, and correct data in specific domains such as customers, locations, and products. Vendors with domain-specific capabilities typically offer products that manage mailing lists and feed data into customer relationship management and marketing systems. The following are representative companies in this submarket:\
     Experian Data Quality\
     IBM (InfoSphere Discovery, BigInsights BigQuality)\
     Informatica (Informatica Data Quality and Data as a Service)  Melissa Data\
     Pitney Bowes (Code-1 Plus and Finalist)\
     SAP (SAP Data Services, SAP HANA Smart Data Quality)\
     SAS Data Quality\
     Talend (Talend Open Studio for Data Quality)\
     Trillium Software\
    Data Access Infrastructure\
    This software is used to establish connections between users or applications and data sources without requiring a direct connection to the data source's API or hard-coded database interface. It includes cross-platform connectivity software. It also includes ODBC and JDBC drivers and application and database adapters. The following are representative companies in this submarket:\
     Micro Focus (Attachmate Databridge)\
     Information Builders (iWay Integration Solutions)\
     Progress Software (DataDirect Connect and DataDirect Cloud)  Rocket Software (Rocket Data)\
    Composite Data Framework\
    This market segment includes data federation and data virtualization software, enabling multiple clients (usually applications, application components, or databases running on the same or different servers in a network) to share data in a way that reduces latency. Usually involving a cache, this software sometimes also provides transaction support, including maintaining a recovery log.\
    Data federation permits access to multiple databases as if they were one database. Most are read only, but some provide update capabilities. Data virtualization products are similar but offer full schema management coordinated with the source database schemas to create a complete database environment that sits atop multiple disparate physical databases. Originally created to provide the data services layer of a service-oriented architecture, data virtualization has been applied to multiple use cases including data abstraction, rapid prototyping of data marts and reports, and providing abilities for data distribution without replication.\
    The following are representative companies in this submarket:\
     Cisco Data Virtualization Platform\
     Denodo\
     IBM (InfoSphere Federation Server)  Informatica Data Virtualization\
     Red Hat (JBoss Data Virtualization)  SAS (SAS Federation Server)\
    Master Data Definition and Control Software\
    The master data definition and control software market segment includes products that help organizations define and maintain master data, which is of significance to the enterprise and multiple\
    systems. Master data is usually categorized by one of four domains: party (people, organizations), product (including services), financial assets (accounts, investments), and location (physical property assets).\
    Master data definition and control software manages metadata regarding entity relationships, attributes, hierarchies, and processing rules to ensure the integrity of master data for where it is to be used. Key functionalities include master data modeling, import and export, and the definition and configuration of rules for master data handling such as versioning, access, synchronization, and reconciliation.\
    This market segment also includes reference data management software. Reference data is used to categorize or classify other data and is typically limited to a finite set of allowable values aligned with a value domain. Domains can be public such as time zones, countries and subdivisions, currencies, units of measurement, or proprietary codes used within an organization. Domains can also be industry specific such as medical codes, SWIFT BIC codes, and ACORD ICD codes. As with master data, reference data is referenced in multiple places within business systems and in some cases, can deviate across disparate systems. Reference data management software could be considered a subset of master data management software and in many cases, may share the same code base as master data management software sold by the same vendor.\
    Master data definition and control products can include operational orchestration facilities to coordinate master data management processes across multiple information sources in either a batch, a service, or an event-based context. Master data definition and control software provides capabilities to facilitate single or multiple master data entity domain definition and processing and usually serves as the core technical component to a broader master data management solution (a competitive market in the IDC taxonomy).\
    Representative vendors and products include:\
     IBM (IBM InfoSphere Master Data Management)\
     Informatica (Multi-Domain MDM, PIM)\
     Oracle (Oracle Product Hub, Oracle Customer Hub, Oracle Site Hub, Oracle Higher Education Constituent Hub, and Oracle Data Relationship Management)\
     SAP (SAP Master Data Governance)\
     TIBCO (Master Data Management Platform)\
    Metadata Management Software\
    Metadata is a data about data. It is commonly associated with unstructured data, as a structure in which to describe the content. However, it is increasingly being used in the structured data world, as the data becomes more complex in its definition, usage, and distribution across an enterprise. At a basic level, metadata includes definitions of the data, when, how, and by whom the data was created and last modified. More advanced metadata adds context to the data, traces lineage of the data, cross- references where and how the data is used, and improves interoperability of the data. Metadata has become critical in highly regulated industries as a useful source of compliance information.\
    The metadata management submarket has grown out of the database management, data integration, and data modeling markets. Metadata management solutions provide the functionality to define metadata schema, automated and/or manual population of the metadata values associated with structured data, and basic analytic capabilities for quick reporting. These solutions also offer\
    application program interfaces for programmatic access to metadata for data integration and preparation for analytics.\
    Representative vendors and products include:\
     ASG (Rochade)\
     IBM (InfoSphere Information Governance Catalog)\
     Informatica (Metadata Manager and Business Glossary)\
     Oracle (Enterprise Metadata Management)\
     SAP (SAP Information Steward Metadata Management and Metapedia)\
    Self-Service Data Preparation Software\
    Self-service data preparation is an emerging segment in the data integration and integrity functional market. Demand is coming from today's tech-savvy business users wanting access to their data in increasingly complex environments, without IT getting in the way. IT has also been looking for technology that can put data preparation capabilities into the hands of business users, where the requirements and desires of analytic outcomes are best understood.\
    These solutions are targeted at business analysts, but some offer a range of user interfaces by persona. Some require deeper levels of data analytics knowledge, and others require deeper levels of data integration knowledge. Functionality ranges from cataloging data sets within repositories, providing interactive capabilities for cleansing and standardizing data sets, joining disparate data sets, performing calculations, and varying degrees of analytics for validation prior to visualization.\
    Software in this segment represents vendors that explicitly sell self-service data preparation components. Business intelligence and analytics vendors that offer self-service data preparation capability within a suite as part of the analytics process they support are excluded from this segment. Representative vendors and products include:\
     Alteryx (Designer)\
     Datawatch (Monarch)\
     Paxata\
     SAP (Agile Data Preparation)  Talend (Data Preparation)\
     Trifacta (Wrangler)\
     Unifi"))


    taxonomySort.categories[0].addNewCategory("Application Development Software")
    taxonomySort.categories[0].subCategories[8].addText(ratioCreator("The application development software markets include software, tools, and development environments used by developers, business analysts, and other professionals to create both Web-based and traditional applications. Development languages, environments, and tools; business rules engines; and modeling and architecture tools (MATs) are included. Application development software also encompasses markets pertaining to component-based development and includes the specific markets discussed in the sections that follow."))


    taxonomySort.categories[0].subCategories[8].addNewCategory("Development languages, environments, and tools")
    taxonomySort.categories[0].subCategories[8].subCategories[0].addText(ratioCreator("The development languages, environments, and tools market includes development-side tools such as integrated development environments (IDEs) and code editors as well as programming language\
    compilers and client-side, mobile, and embedded application development tools; runtimes; and frameworks, including Web frameworks and browsers. Also included in this market are standalone tools used during the code construction process such as debuggers and code profilers.\
    This market does not include tools whose primary function is to support formalized modeling and business rules methodologies that assist in generating application requirements, data definitions, and programming specifications. Server-side application platforms, including application servers and mobile back-end services, are not tracked in this market.\
    The development languages, environments, and tools functional market includes:\
     IDEs. IDEs are the environments through which developers access the various tools available to develop in any given language, or framework, or a combination thereof. IDEs are increasingly multifaceted, encompassing multiple stages of the development and multiple languages and tools to control them in one graphical user interface.\
     Compiled languages or 3GLs. Such compilers and associated tools (aka 3GL tools) typically compile directly to machine or system process architecture languages in a distinct compilation stage without an executable immediate language. Compiled languages encompass traditional programming languages, such as C, C++, COBOL, and FORTRAN and include tools, such as editors, linkers, optimizers, compilers, debuggers, and other language-specific tools used primarily in the code-building process. C/C++, FORTRAN, Ada, and COBOL continue to be the primary 3GL languages that developers use to produce business technology solutions, although the group includes commercial proprietary languages like Delphi, academic languages like Modula 2, and new languages like Erlang and Haskell. Compiled languages may have interpreted varieties often used for prototyping or experimentation, but their design center is primarily to produce efficient high-performance code through a compilation process. The use of such relatively low-abstraction languages is increasingly found in commercial applications where high performance and flexibility are weighted more heavily than developer productivity or agility.\
     Managed languages. Managed languages are those that include higher levels of functionality in their richer execution environment or runtime, such as type checking, error and exception handling, and memory management services such as garbage collection. In most cases, managed languages compile to intermediate languages (e.g., Java Bytecode or Microsoft's Common Intermediate Language [CIL]), which permits the interoperability of different languages layered on top of the bytecode virtual machine execution environment through the sharing of a common lower-level infrastructure framework.\
     Web design and development tools. Web design and development tools provide Web site and Web page layout and design, object integration for site and page development, and the tools needed to create Web-based applications on both the client side and the server side including the associated scripting and dynamic languages used for this purpose. Although HTML editing is often provided, tools in this category typically offer visual abstraction away from HTML through WYSIWYG page editors, animation and other rich media, JavaScript and/or VBScript features, Asynchronous JavaScript and XML (AJAX), simple data integration, and deployment scenarios. This category includes all execution environments inside of browsers and browser extension languages and execution environments like Adobe Flash or Microsoft Silverlight. In addition, tools designed to address mashups and compositional user interface configurations are included in this category.\
     Client-side model-driven tools. These tools, also known as rapid application development (RAD) tools, are higher-level integrated authoring and execution environments used by professional programmers or business analysts to build business applications. Such tools typically provide a higher level of abstraction than a 3GL. The focus of such client application\
    platforms is often development productivity and agility and involves a trade-off between support for industry-standard and proprietary approaches to achieve these results. This category is focused on client-side and mobile technologies, though it may also include integrated end-to-end development targeting both client and server execution. Similar model- driven tools, which focus exclusively on back-end application platforms and authoring tools, are counted elsewhere in the taxonomy.\
     Server-side scripting and interpreted languages. This category aggregates server-side languages and frameworks such as Perl, PHP, Python, Ruby, and Node On Rails, which use interpretation or virtual machine technology. The category is a catchall for the varied programming language environments available today — not described previously. The majority of such tools are considered parts of the broader Web tools ecosystem, with many being open source based. The use of such tools can be compositional in nature or as a glue for IT automation or for the construction of larger pieces of code forming a major chunk of some applications.\
    The following are representative vendors and products in the development languages, environments, and tools market:\
     Adobe (AIR, Flash, and Flex)\
     Embarcadero (JBuilder)\
     Four Js (Genero)\
     IBM (WebSphere Studio Developer)  Critical Path (OpenLaszlo)\
     Microsoft (Visual Studio.NET, Silverlight, SharePoint Designer, and ASP.NET)  Nexaweb (Enterprise Web 2.0)\
     TIBCO (General Interface)\
     Zend (Zend Studio)"))
    taxonomySort.categories[0].subCategories[8].addNewCategory("Software construction components")
    taxonomySort.categories[0].subCategories[8].subCategories[1].addText(ratioCreator("Software construction components (SCCs) are functionally specific software subassemblies and libraries sold apart from a programming development environment that may or may not be designed for use with a specific programming development environment. Examples include class libraries, frameworks, ActiveX controls, Java applets, JavaBeans, Enterprise JavaBeans (EJBs), DLLs, and other forms of API-specific libraries. Software components that fall into this category are intended to be used by developers to assemble applications as opposed to fully functional applications that are intended to run on their own. The following are representative vendors and products in this market:\
     GrapeCity (ComponentOne Studio Enterprise)\
     Developer Express (DXperience and DevExtreme)  Infragistics (.NET Controls)"))
    taxonomySort.categories[0].subCategories[8].addNewCategory("Business rules management systems")
    taxonomySort.categories[0].subCategories[8].subCategories[2].addText(ratioCreator("Business rules management systems (BRMSs) are defined as discrete systems that define, manage, and execute conditional logic in concert with other IT processes and actions. BRMSs are well known for their ability to automatically recognize the inter-rule relationships that evolve as rules are added or changed, thereby eliminating the need for the careful and complex rule sequencing and conflict resolution that would otherwise be necessary. The following are representative vendors and products in this market:\
     CA Technologies (CA Aion)\
     Progress Software (Corticon BRMS)  FICO (Blaze Advisor)\
     IBM (ILOG JRules)\
     Pegasystems (PegaRULES)"))
    taxonomySort.categories[0].subCategories[8].addNewCategory("Modeling and architecture tools")
    taxonomySort.categories[0].subCategories[8].subCategories[3].addText(ratioCreator("Modeling and architecture tools software includes those tools that support the design and analysis of applications and systems that reside in the IT domain. These tools may also define information regarding an organization's business architecture or leverage functional requirements to provide a context for the design and analysis of IT applications and systems. A fundamental characteristic of MATs is their internal support for objects, relationship, and patterns. This enables an architectural tool to convey an accurate and consistent understanding of IT assets from current, future, and differential perspectives.\
    The MAT market includes the submarkets discussed in the sections that follow.\
    Object Modeling Tools\
    Object modeling (OM) tools address application design largely using UML notation. The primary use cases for these tools are enterprise application development or real-time and embedded system development. Representative vendors and products include:\
     Atego (Artisan Studio)\
     IBM (Rational Software Architect and IBM Rhapsody)\
    Business Process Modeling Tools\
    Business process modeling (BPM) tools address process model and/or event-driven model design largely using business process modeling notation (BPMN) and other process or event-oriented notations. Representative vendors and products include:\
     MEGA (MEGA Process)  Software AG (ARIS)\
    Enterprise Architecture Tools\
    Enterprise architecture (EA) tools support the definition and alignment of an organization's business architecture, application architecture, information architecture, and technical architecture. Representative vendors and products include:\
     Troux (Troux)\
     MooD International (MooD Platform)"))


    taxonomySort.categories[0].addNewCategory("Quality & Life-Cycle Tools")


    taxonomySort.categories[0].subCategories[9].addNewCategory("Automated software quality (ASQ)")
    taxonomySort.categories[0].subCategories[9].subCategories[0].addText(ratioCreator("Automated software quality (ASQ) tools support software unit testing, system testing, user integration testing, and software quality assurance. Functions such as test specification, generation, execution, results analysis, 'bug tracking,' test data and QA management, functional/regression, and stress and\
    load testing are included in this category. ASQ SaaS and testing in the cloud and of cloud applications (private, public, and hybrid), virtual test lab management, and service virtualization as well as software quality analysis and measurement are included in this category. Emerging platform and software testing support for mobile, video, crowdsourcing, end-user experience, embedded software quality, and other areas (e.g., enterprise resource planning [ERP], mainframe) are also included. The software quality analysis and measurement aspect of ASQ consists of software tools that enable organizations to observe, measure, and evaluate software complexity, size, productivity, and risk. Examples of capabilities provided by these software analysis tools include architectural assessment of design consequences (on software performance, stability, adaptability, and maintainability), static analysis, dynamic analysis, and quality metrics for complexity, size, risk, and productivity to establish baselines and help judge project progress and resource capabilities.\
    The following are representative vendors and sample products in this market:\
     Compuware (Gomez Web Load Testing, Gomez Cross-Browser Testing, Gomez Render Inspector, Dynatrace Purepath, Xpediter, Hiperstation, and DevEnterprise)\
     Coverity (acquired by Synopsys 1Q14)\
     HPE (HPE Quality Center, HPE Performance Center, HPE Test Data Management, and HPE\
    Fortify 360)\
     IBM (Rational Functional Tester, Rational GreenHat, AppScan, Rational Performance Tester, Rational Robot, and Rational PurifyPlus)\
     Micro Focus (Silk Test, Silk Performer, and Silk Central Test Manager)\
     Perfecto Mobile\
     SOASTA"))

    taxonomySort.categories[0].subCategories[9].addNewCategory("Software change, configuration, and process management")
    taxonomySort.categories[0].subCategories[9].subCategories[1].addText(ratioCreator("Software change, configuration, and process management (SCCPM) tools are used by application development organizations to provide software revision control, versioning, and change and software configuration management. IDC's broader SCCPM functional category encompasses additional capabilities such as process management; requirements visualization; definition and management; distributed, continuous team development support; and deployment orchestration (solutions managing the software release handoff from development to deployment). SCCPM also includes methodologies and related solutions, such as Agile (Scrum, Kanban, etc.), SEI's CMMI, agile project management, and code management automation, as well as management of open source software as part of complex sourcing of applications. Code management also demands end-to-end deployment strategies that encompass the handoff from development to operations as described by the term DevOps. Release management capabilities to automate and facilitate that process are also included in this category.\
    The following are representative vendors and products in this market:\
     Atlassian (JIRA, JIRA Agile)\
     Black Duck\
     CA Technologies (Endevor, Software Change Manager, and Nolio)\
     IBM Rational (ClearCase, ClearQuest, Method Composer, DOORS, and UrbanCode)  iRise\
     Microsoft (Visual SourceSafe and Visual Studio)\
     Rally Software\
     Serena (ChangeMan and TeamTrack)\
    Software license life-cycle management is a submarket of the SCCPM functional market. Capabilities\
    include:\
     Entitle management: This phase involves the identification and authorization of transactions involving the software SKU.\
     Delivery: This phase includes 'fulfillment' of the software and a 'right to use' license.\
     Installation: This phase includes the installation and reporting of software added to any type of\
    computing device.\
     Control: Incorporating the elements of discovery/inventory and software metering, this phase represents the control and compliance phase, including identifying and managing software license assets.\
    Vendor examples for this submarket include Flexera and SafeNet."))


    taxonomySort.categories[0].addNewCategory("Application Platforms")
    taxonomySort.categories[0].subCategories[10].addText(ratioCreator("The application platform secondary market includes technologies that present a cohesive application execution environment for applications built on a server or back-end component. Application platforms are back-end server middleware that execute application logic; mediate access to data, content sources, and Web services; coordinate authentication; manage sessions; and provide quality of service (QoS) to offer scalability, performance, reliability, and availability to applications executed and managed by the platform.\
    Applications built on modern application server middleware are used over TCP/IP networks and are built using standard frameworks, such as Java Enterprise Edition (JEE),.NET, and Spring. Older legacy application server middleware is deployed on mainframes.\
    Application platforms were formerly called application server middleware. In this change, we are calling out are three types of application platforms:\
     Deployment-centric application platforms (DCAPs)  Model-driven application platforms\
     Transaction processing monitors (TPMs)"))

    taxonomySort.categories[0].subCategories[10].addNewCategory("Deployment- centric application platforms")
    taxonomySort.categories[0].subCategories[10].subCategories[0].addText(ratioCreator("Deployment-centric application platforms are on-premise and cloud middleware that host application logic and provide common services that allow the application to operate effectively.\
    By using DCAPs, developers gain access to extensions that include connectivity between the presentation layer, middleware services, data sources, and infrastructure. These platforms also coordinate and manage access to third-party services via APIs, and they also offer a range of QoS capabilities, including transaction processing reliability, availability, throughput, scalability, security, and management.\
    DCAPs use common programming models, such as JEE,.NET, Ruby on Rails, and Spring, that developers use to build their applications. They may also provide a language-specific framework, such as PHP or Ruby, for communicating between the front-end, back-end, and data sources. DCAPs also include containerization technology for process isolation.\
    DCAPs are used by ISVs to build and deploy applications sold separately and by enterprises for custom development and to deploy packaged applications. Many vendors build commercial software on top of this category of software and sell the product as a new category. For example, when a portal is built on an application server but sold as a portal, the application server software portion is not counted in this market. However, when an ERP is purchased separately from the application server required to make it run, the application server revenue is counted.\
    Where the DCAP is part of a multipurpose product, such as Microsoft Windows Server, and we can determine what portion of the software is used as an application server software platform (ASSP), we will include that portion in ASSP revenue.\
    The DCAP market includes software deployed on-premise as well as in public and private cloud settings supporting Web and mobile applications' front ends.\
    Within DCAPs, there are three basic categories: application server software platforms, mobile back end as a service (MBaaS), and deployment-centric application platform as a service.\
    Application Server Software Platforms\
    Application server software platforms are traditionally used to run custom and packaged apps in datacenters. The following list is representative of the vendors and products we follow in this market:\
     IBM WebSphere Application Server\
     IBM Liberty Buildpack on Bluemix\
     Microsoft Windows Server Internet Information Services  Oracle WebLogic Server\
     Red Hat JBoss Enterprise Application Server\
     EMC Pivotal tc Server\
    Deployment-Centric Application Platform as a Service\
    This category consists of deployment-oriented platforms operating in public and private clouds. The following list is representative of the vendors and products we follow in this market:\
     ActiveState Stackato  Apprenda Platform\
     Docker\
     Engine Yard Cloud\
     Google App Engine  Microsoft Azure\
     EMC Pivotal Cloud Foundry\
     Red Hat OpenShift\
     Salesforce.com Heroku Cloud Application Platform\
    Mobile Back End as a Service\
    Mobile back end as a service (MBaaS) consists of deployment-oriented platforms operating in public and private clouds that coordinate with mobile front ends as well as third-party application, cloud infrastructure, and data and middleware services through APIs. The following list is representative of the vendors and products we follow in this market:\
     Backendless\
     Buddy Platform  FatFractal\
     FeedHenry\
     Kinvey"))
    taxonomySort.categories[0].subCategories[10].addNewCategory("Model-driven application platforms")
    taxonomySort.categories[0].subCategories[10].subCategories[1].addText(ratioCreator("Model-driven application platforms combine development and runtime into a single offering. They typically consist of graphical modeling environments and point-and-click configurations as well as relatively simple scripting. These environments are popular for rapid development as well as development teams that include both business participants and developers.\
    Data-Centric Application Platforms\
    These model-driven application platforms tools, also known as data or RAD tools or 4GLs, are higher- level integrated authoring and execution environments used by professional programmers or business analysts to build business applications. The focus of such application platforms is often development productivity and agility and involves a trade-off between support for industry-standard and proprietary approaches to achieve these results. This category is focused on server or back-end technologies. Similar model-driven tools, which include integrated front-end application platforms and authoring tools, are counted elsewhere in the taxonomy.\
    The following list is representative of the vendors and products we follow in this market:\
     Asteor Software Techcello  Caspio\
     Intuit QuickBase\
     Mendix\
     OrangeScape\
     OutSystems Platform\
     Progress Pacific (Rollbase)\
     salesforce.com Force\
     Servoy Business Application Platform  TrackVia\
    Process-Centric Application Platforms\
    A process is the series of activities that accomplish work in a routine way. Process-centric application platforms are used by enterprises and ISVs to develop and execute custom process workflows and automation. Process-centric application platforms automate people-oriented activities that require manual steps or human decision making, such as loan approvals or bringing new employees onboard. They also support system-to-system activities that are part of the process.\
    BP platforms are sophisticated products and portfolios of offerings that provide enterprises with capabilities to support strategic process improvement initiatives. Process automation involves human task and system-to-system automation as well as management of cases. It increasingly involves automated opportunity and problem detection and coordination across larger end-to-end processes spanning multiple applications inside a single enterprise datacenter, across datacenters, in the cloud, and with business partners. These platforms also coordinate and manage cross-border processes\
    (multiple languages and time zones) and complex integration scenarios that may involve legacy custom or packaged applications, a variety of data sources, and/or Web services.\
    BPM suites include capabilities that are optimized for human-centric workflow, ad hoc requirements, and worker adaptability. These are primarily used to improve worker productivity and operational efficiency, supporting individual worker and collaboration-based processes. The focus is on business/developer partnership in development and an effort to minimize the need to use developers to make minor changes and tweaks to the process in runtime. BPM suites are optimized for rapid development, and many elements are straightforward enough for business analysts to play a meaningful role as a member of the development team. BPM suites are able to support departmental, matrixed, and team projects as well as process automation for small and midsize businesses.\
    Enterprises that adopt a BPM suite are able to use the product broadly and repeatedly across the organization, particularly for bottom-up improvements in efficiency and productivity. Because there are so many of these types of projects across organizations, enterprises that invest and learn how to improve productivity at the smallest team unit through horizontal processes will improve overall profitability — one project at a time.\
    This category of software was previously covered in process automation middleware. That term is now obsolete. The following are representative vendors and products in process-centric application platforms:\
     Appian Enterprise BPMS and Appian Cloud  AuraPortal BPMS\
     Bizagi Suite\
     IBM Business Process Manager\
     K2 Platform\
     Nintex Workflow 2010\
     OpenText Process Suite\
     Oracle Business Process Management Suite  Pegasystems Pega 7\
     PNMsoft BPM\
     TIBCO ActiveMatrix BPM\
     SAP Process Orchestration"))
    taxonomySort.categories[0].subCategories[10].addNewCategory("Transaction processing monitors")
    taxonomySort.categories[0].subCategories[10].subCategories[2].addText(ratioCreator("Transaction processing monitors mediate and optimize transaction processing between clients and a mainframe database. TPMs have evolved to the point where they currently can act as application servers for legacy mainframe and client/server applications. The following are representative vendors and products in this category:\
     IBM CICS\
     Oracle Tuxedo\
    Integration and Orchestration Middleware\
    The integration and orchestration middleware markets include tools used by developers and business analysts to integrate applications, exchange business transactions between enterprises, transfer files inside and outside organizations, publish and process events, and monitor the business and process performance of these applications and automated processes.\
    This middleware is deployed on-premise as software implemented on servers, in appliances, and as public and hybrid cloud offerings.\
    In the IDC taxonomy, there are four specific types of integration and orchestration middleware, along with an 'other' category that includes legacy software and integration-related middleware not yet large enough to be categorized in a standalone market:\
     Business-to-business middleware  Integration middleware\
     Event-driven middleware\
     Managed file transfer software"))


    taxonomySort.categories[0].addNewCategory("Integration and Orchestration Middleware")

    taxonomySort.categories[0].subCategories[11].addNewCategory("Business-to- business middleware")
    taxonomySort.categories[0].subCategories[11].subCategories[0].addText(ratioCreator("Business-to-Business Middleware\
    B2B middleware consists of software and services used to receive, route, and convert standards- based structured interenterprise files and messages related to transactions. Those standards can be\
    community-based standards built around electronic data interchange, such as X12 or HIPAA 5010, or between party-agreed-upon formats.\
    B2B Gateway Middleware\
    B2B gateway middleware is software deployed on-premise used to automate and monitor the interenterprise exchange of data. At the heart of these platforms are conversion, translation, and data exchange–related orchestration capabilities. Additional features include:\
     More generalized process automation  Receipt and delivery of messages\
     Connectivity software\
     Business activity monitoring (BAM)\
     Reporting\
     Development environment\
    There are strong similarities between B2B gateway platforms and other types of integration middleware. However, the strength of these platforms is in the embedded support of common-standard industry models for electronic message exchange, such as electronic data interchange. In addition, they are optimized to operate at the edge between two or more enterprises, including the ability to send acknowledgements to senders once a message is received. The following are representative vendors and products in this category:\
     Axway Business Integration Network\
     IBM B2B Integrator\
     Informatica B2B Data Exchange\
     SEEBURGER Business Integration Server\
     Software AG webMethods Trading Networks  TIBCO B2B Gateway\
    B2B Networks and B2B Managed Services\
    B2B networks are secure, private networks that receive, store, and forward structured interenterprise messages related to transactions. B2B networks include customizable hosted solutions and SaaS offerings. Many of the vendors in this category also offer end-to-end managed services.\
    B2B networks broadly support EDI-based standards across industries. Beyond reliable, secure delivery of messages, features include protocol conversion, message and file translation, monitoring, exception reporting, paper-to-digital conversion, and partner self-service, including Web forms for submitting transactions and documents and self-testing capabilities. The following are representative vendors and products in this category:\
     OpenText's Easylink Data Messaging\
     GXS Trading Grid\
     IBM Collaboration Network\
     SPS Commerce Trading Partner Integration Center  SWIFT SWIFTnet FIN and InterAct"))
    taxonomySort.categories[0].subCategories[11].addNewCategory("Integration middleware")
    taxonomySort.categories[0].subCategories[11].subCategories[1].addText(ratioCreator("Integration middleware is server software or appliances installed on-premise inside a datacenter or offered in a public or private cloud to integrate applications. Integration middleware supports passing data through a Web service or receiving data by calling a Web service. Integration handles normalization and transformation to ensure an application is able to send or receive data in the correct format. Integration also handles orchestration needed to hand off data for data quality or pass to one or more applications.\
    API Management Software\
    API management software and cloud services support the secure and scalable publishing and management of application programming interfaces. This software helps API publishers design, monitor, manage, and update APIs and scale access to the services that connect to the APIs. Representative vendors and products include the following:\
     Apigee Enterprise API Management  Axway API Management\
     CALayer7\
     IBM API Management\
     Intel Mashery\
     MuleSoft API Manager\
     SOA Software (now known as Akana) API Management  TIBCO API Exchange\
    Enterprise Service Bus Middleware\
    Enterprise service bus (ESB) was created to support application integration for applications built on a standards-based service-oriented architecture. ESBs operate in request-response and event-driven paradigms. Under the more common request-response model, ESBs receive service consumption requests, route the requests to the correct service provider, transform the requests to a format compatible with the service provider, wait for the results, and deliver them back to the service consumer.\
    In an event-driven model, ESBs receive an event, transform it, and forward it, based on routing instructions managed within the ESB.\
    There are many types of ESBs in the market, with orientations based on the preexisting middleware that was used as the basis for the ESB. In addition, there are some ESBs that were built from the ground up to provide services-oriented routing and transformation capabilities. Representative vendors and products include the following:\
     IBM Integration Bus\
     Oracle SOA Suite\
     Red Hat JBoss Fuse Service Works\
     SAP NetWeaver Process Integrator\
     Software AG webMethods Integration Server  TIBCO BusinessWorks\
    Connectivity Middleware\
    Connectivity middleware is installed on end systems to send and receive data and instructions directly from other systems and via middleware. Depending on how it is deployed, connectivity middleware — adapters and sensors — can perform transformations prior to delivering the data back to the targeted system or can transfer as is.\
    There are different deployment paradigms for the adapters. They can fetch or deliver data on request. They can be set up to look for new data on a scheduled basis. They can also support an event model in which a data change is automatically captured by an adapter, which generates a message that is published to message-oriented middleware (MOM).\
    Most deployment platform vendors have their own collection of standard or common adapters. They tend to be bundled into the price of platform software and, therefore, are not counted in this category. This category includes the standalone purchase of connectivity middleware. Representative vendors and products include the following:\
     Information Builders iWay Universal Adapter Suite  Software AG webMethods Adapters\
     TIBCO adapters"))
    taxonomySort.categories[0].subCategories[11].addNewCategory("Managed file transfer software")
    taxonomySort.categories[0].subCategories[11].subCategories[2].addText(ratioCreator("Managed file transfer software provides secure, guaranteed high-speed delivery of a file over a network. The file transfer can be from one enterprise to another or within an enterprise, across datacenters, or systems. This software includes the free software that delivers files over file transfer protocol (FTP) and commercial software that offers better security, reliability, and speeds. Examples include:\
     Accellion\
     Aspera\
     Attunity MFT\
     Axway MFT\
     CA Technologies XCOM\
     Data Expedition\
     Globalscape\
     IBM Sterling Control Center  TIBCO MFT"))
    taxonomySort.categories[0].subCategories[11].addNewCategory("Event-driven middleware")
    taxonomySort.categories[0].subCategories[11].subCategories[3].addText(ratioCreator("Event-driven middleware is used to detect events and automatically pass them to applications, systems, and people. An event is a data or application change of state. The technologies that make up event- driven middleware are key components of an event-driven infrastructure, which is implemented to:\
     Predict and detect problems or opportunities at the earliest possible moment they are identifiable.\
     Support automated processes to reduce cycle times and remove waste, errors, and redundancy from an enterprise's operations.\
     Improve the scalability and processing speeds of applications and application infrastructure. Event-driven middleware consists of the following three types of software: message-oriented\
    middleware, complex event processing (CEP) software, and business activity monitoring.\
    In essence, MOM can be considered the nervous system that listens for stimuli and informs the brain. CEP is the brain, which contains the short-term memory and executive decision-making ability to send instructions through the nervous system to the appropriate parts of the body. BAM is the eyes of an event-driven infrastructure.\
    Business Activity Monitoring\
    Business activity monitoring informs users about the current status of areas in which they are interested and notifies them when thresholds are crossed that warrant attention. BAM typically is deployed as a continuously updated dashboard of key performance indicators that describe the metrics that are important to an individual user. There are a variety of graphical displays in which the KPIs are embedded, including standard graphs, heat maps, and process model views. There are also graphical indicators of current performance.\
    While BAM dashboards are typically presented in a portal, notification of out-of-bounds performance is sent out via email. In some cases, vendors are taking KPIs and their associated graphical representations and making them available as gadgets that can be displayed in a mashup.\
    BAM is implemented in many scenarios. In this case, we count BAM products sold as a standalone offering, which excludes the embedded BAM sold as part of a BPM suite. The following are representative vendors and products in this category:\
     Oracle BAM\
     Software AG Optimizer  Axway Systar\
    Complex Event Processing Middleware\
    CEP middleware manages descriptions of conditions and their state, correlates new events to the conditions, and tests for matches. Once matched, a new event is created and fired off to other systems listening for the event. CEP is used primarily as infrastructure for temporal (time) and spatial (location) applications.\
    A condition describes the relationship of two or more events to each other. These can be simple, such as calculating the impact of a change in stock price over a set time window to see whether it meets a certain threshold, or complicated, such as calculating the impact of a flight delay on all of the systems affected by that delay.\
    CEP products are based on different technologies, with the three most common being:\
     Continuous query software that automatically runs SQL or SQL-like queries upon the receipt of new data\
     Rules engines that apply new data to all the rules and rule relationships\
     Software that allows users to model the condition\
    The following are representative vendors and products in this category:\
     Amazon AWS Kinesis Streams  EsperTech Esper and NEsper  IBM InfoSphere Streams\
     Informatica RulePoint\
     SAS ESP\
     Software AG Apama\
     TIBCO StreamBase Server  TIBCO BusinessEvents\
    Message-Oriented Middleware\
    When a relevant event occurs, MOM creates a structured message containing the data of the event, the time the event was created, and the metadata about the event. MOM delivers the message in the following paradigms:\
     Point to point, where one sending system publishes a message directly to a receiving system for processing\
     To a queue, where the message can be picked up for processing by any authorized system\
     Publish and subscribe, which broadcasts messages without concern for whether the event is\
    actually received by any system\
    In the latter two paradigms, each message includes metadata that describes the topic or the subject of the message. Subscribers listening for that topic receive all messages that are broadcast out. When a system picks messages off of a queue, it also looks for specific message types, based on the metadata.\
    MOM is also capable of transforming a message to a structure that is compatible with the receiving system. Whether the transformation is handled within MOM or by other integration middleware, such as an ESB, is an architectural decision made by the enterprise during system design.\
    Although many vendors offer commodity MOM based on the Java Message Service (JMS) standard, the standalone offerings differentiate and compete on low latency, reliability, and high throughput. The following are representative vendors and products in this category:\
     IBM WebSphere MQ and Message Hub  Informatica Ultra Messaging\
     Real-Time Innovations (RTI) Connext\
     Splunk App for Stream\
     TIBCO (Rendezvous, Enterprise Message Service, FTL)"))


    taxonomySort.categories[0].addNewCategory("Data Access, Analysis, and Delivery")
    taxonomySort.categories[0].subCategories[12].addText(ratioCreator("Data access, analysis, and delivery products are end-user–oriented tools for ad hoc data access, analysis, and reporting as well as production reporting. Products in this category are most commonly used by information consumers or power users rather than by professional programmers. Examples include query, reporting, multidimensional analysis, and data mining and statistics tools. The data access, analysis, and delivery markets are defined in the sections that follow."))



    taxonomySort.categories[0].subCategories[12].addNewCategory("End-user query, reporting, and analysis")
    taxonomySort.categories[0].subCategories[12].subCategories[0].addText(ratioCreator("End-User Query, Reporting, and Analysis\
    Query, reporting, and analysis software includes ad hoc query and multidimensional analysis tools as well as dashboards, data visualization, and production reporting tools. Query and reporting tools are designed specifically to support ad hoc data access and report building by either IT or business users. This category does not include other application development tools that may be used for building reports but are not specifically designed for that purpose. Multidimensional analysis tools include both server- and client-side analysis tools that provide a data management environment used for modeling\
    business problems and analyzing business data. Packaged data marts, which are preconfigured software combining data transformation, management, and access in a single package, usually with business models, are also included in this functional market. The following are representative vendors and products in this market:\
     Actuate (Actuate BIRT)\
     IBM (IBM Cognos Business Intelligence)\
     Information Builders (WebFOCUS)\
     Microsoft (Microsoft SQL Server Reporting and Analysis Services)  MicroStrategy (MicroStrategy 9)\
     Oracle (Oracle Business Intelligence Enterprise Edition)\
     QlikTech (QlikView)\
     SAP (SAP BusinessObjects)\
     Tableau Software (Tableau Desktop and Tableau Server)\
     TIBCO (TIBCO Spotfire and TIBCO Jaspersoft)"))
    taxonomySort.categories[0].subCategories[12].addNewCategory("Advanced and predictive analytics software")
    taxonomySort.categories[0].subCategories[12].subCategories[1].addText(ratioCreator("Advanced and predictive analytics software includes data mining and statistical software. It uses a range of techniques to create, test, and execute statistical models. Some techniques used are machine learning, regression, neural networks, rule induction, and clustering. Advanced and predictive analytics are used to discover relationships in data and make predictions that are hidden, not apparent, or too complex to be extracted using query, reporting, and multidimensional analysis software. Products on the market vary in scope. Some products include their own programming language and algorithms for building models, but other products include scoring engines and model management features that can execute models built using proprietary or open source modeling languages. The following are representative vendors and products in this market:\
     SAS (SAS Analytics and SAS Enterprise Miner)\
     IBM (IBM SPSS Predictive Analytics Software)\
     FICO (FICO Model Builder)\
     SAP (SAP Predictive Analytics and SAP Infinite Insight)  Oracle (Oracle Data Mining)\
     TIBCO (TIBCO Spotfire S+)\
     Dell (StatSoft)\
     Revolution Analytics (Revolution R Enterprise)  RapidMiner (RapidMiner Server)\
     Predixion Software (Predixion Insight)\
     Blue Yonder (Forward Demand)"))
    taxonomySort.categories[0].subCategories[12].addNewCategory("Spatial information management software")
    taxonomySort.categories[0].subCategories[12].subCategories[2].addText(ratioCreator("Spatial information management (SIM) software (also called geographic information system [GIS]) includes tools for data entry/conversion (surveying/COGO, aerial photo rectification, remote sensing, GPS, and others), mapping/spatial query, and business analysis. The following are representative vendors and products in this market:\
     Autodesk (Autodesk Map)\
     Esri (ArcInfo)\
     Hexagon (Intergraph GeoMedia)\
    System Infrastructure Software Market Definitions\
    System infrastructure software includes software and SaaS solutions that provide both the basic foundational layers of software that enable bare metal infrastructure hardware resources to host higher-level application development and deployment software and application software and the virtualization and management software used to configure, control, automate, and share use of those resources across heterogeneous applications and user groups. System infrastructure software includes five groups of infrastructure software products — system management software, network software, security software, storage software, and system software. These five secondary markets are discussed in the sections that follow."))

    taxonomySort.categories[0].addNewCategory("System Management Software")
    taxonomySort.categories[0].subCategories[13].addText(ratioCreator("System management software and SaaS services are used to manage all the computing resources for the end user, small business, workgroup, or enterprise, including physical and virtual systems, middleware, applications, cloud services, desktop, and client and endpoint devices. This market does not include storage management or network management software. System management software is further segmented into the categories discussed in the sections that follow."))

    taxonomySort.categories[0].subCategories[13].addNewCategory("IT event and log management tools")
    taxonomySort.categories[0].subCategories[13].subCategories[0].addText(ratioCreator("IT event and log management software automates the analysis and response of the systems to nonscheduled system and application events and root cause analysis. Included are console automation products, global event management applications, event correlation and root cause analysis software, event action engines, log management, and log analytics. This category does not include automation of responses to scheduled events. The following are representative vendors and products in this market:\
     BMC TrueSight Operations Management (portions thereof) and BMC TrueSight Intelligence  Oracle Management Cloud (portions thereof)\
     HPE Operations Analytics (portions thereof)\
     IBM Operations Analytics — Log Analysis and IBM Tivoli Netcool (portions thereof)\
     Splunk Enterprise and Splunk Cloud\
     VMware vRealize Operations (portions thereof)\
     Microsoft Operations Management Suite (portions thereof)"))
    taxonomySort.categories[0].subCategories[13].addNewCategory("Workload scheduling and automation software")
    taxonomySort.categories[0].subCategories[13].subCategories[1].addText(ratioCreator("Workload scheduling and automation software manages the provisioning, placement, migration, and execution flow of workloads on systems and the provisioning, scaling, and management orchestration of images, operating systems (OSs), containers, and applications onto physical and virtual servers. It also includes service brokering, optimization, and self-service provisioning solutions used to enable cloud and software-defined datacenter systems and applications management. The worldwide workload scheduling and automation software market is made up of two submarkets — workload management (formerly called job scheduling) and datacenter operations automation — as defined in the sections that follow.\
    Workload Management\
    Workload management includes software tools that manage the execution flow of workloads and applications on systems using calendar or other fixed-schedule metrics as well as event-driven triggers such as file events or completion of jobs. It also includes process automation, orchestration, and self- service tools specifically for job scheduling, workload management, and workload process orchestration. This market is limited to tools that work at the application level rather than the system level. It does not include workload-balancing applications that work at the system level (e.g., high- availability software). It encompasses both mainframe and distributed platforms.\
    The following are representative vendors and products in this market:\
     BMC Control-M\
     CA Technologies Workload Automation Suite  IBM Workload Automation\
     Hitachi JP1\
    Datacenter Operations Automation\
    Datacenter operations automation includes software running on distributed, non–mainframe platforms that enables dynamic automated physical and virtual server and application provisioning, workload and VM allocation and reclamation, self-service cloud provisioning portals and cloud service brokers, runbook automation, workflow orchestration, and software-defined datacenter and hybrid cloud resource optimization and provisioning including container management and orchestration. Configuration automation solutions, both proprietary and commercial open source, are also included.\
    Task-level automation capabilities included in software that is primarily focused on asset discovery, software license management, and software distribution are not included here as they are part of the change and configuration management software market. Task-level automation capabilities included in software that is primarily focused on service desk operations are not included here as they are part of the problem management software market.\
    The following are representative vendors and products in this market:\
     BMC BladeLogic Automation Suite, Atrium Orchestrator, and Cloud Lifecycle Management  Chef\
     Cisco ONE Enterprise Cloud Suite (portions thereof)\
     Docker DataCenter Universal Control Plane (Docker Swarm) (portions thereof)\
     Google Container Engine (Kubernetes)\
     HPE Operations Orchestration, Server Automation, and Cloud Service Automation  IBM Cloud Orchestrator\
     Puppet\
     Red Hat CloudForms and Ansible\
     ServiceNow Cloud Management\
     VMware vRealize Automation"))
    taxonomySort.categories[0].subCategories[13].addNewCategory("Output management tools")
    taxonomySort.categories[0].subCategories[13].subCategories[2].addText(ratioCreator("Output management tools automate the operation, control, administration, tracking, and delivery of print and digital information within an organization. This market encompasses three submarkets:\
     Device management\
     Print management\
     Enterprise output management\
    It is important to note that many vendors (including those listed as representatives in the following submarkets) offer suites of solutions that include software in several, or all, of these submarkets.\
    Device Management\
    Device management tools are software-based solutions designed to install, activate, configure, monitor, and control office-imaging equipment deployed as part of a networked fleet of devices. This includes monitoring of supplies and end-user authorization to use the device. The solutions can be delivered as either hardware-embedded, on-premise, or cloud-based applications. These solutions are primarily aimed at reducing costs by providing greater control of hardcopy output infrastructure and visibility into print volume and print spend. Representative vendors and products in this submarket are:\
     HP (Web Jetadmin)  Netaphor (SiteAudit)  PrintFleet\
     Print Audit\
    Print Management\
    Print management tools are software-based solutions for tracking, measuring, monitoring, reporting, and managing end-user behavior and the printed output produced by an office-imaging equipment deployed as part of a networked fleet of devices. Functionality includes, but is not limited to, rules- based printing, secure print release, and job auditing and accounting.\
    This segment additionally includes mobile printing solutions that deliver print jobs from a mobile touch point (smartphones or tablets) to an output device using cloud (external) or internally hosted server. These tools include both secure enterprise (behind the firewall) deployments and public (cloud) printing solutions. Direct peer-to-peer print (e.g., AirPrint) or direct wireless print is excluded. Pages are tracked in the same manner as if jobs were initiated from a PC or laptop (and may be managed by the toolset previously described).\
    In addition to cost reduction, these tools are primarily aimed at optimizing device usage, increasing productivity, improving device and content security, and helping meet sustainability goals. Representative vendors and products in this submarket are:\
     Canon (uniFLOW)\
     Nuance (Equitrac and SafeCom)  Pharos (Blueprint)\
     PaperCut\
     YSoft (SafeQ)\
    Enterprise Output Management\
    Enterprise output management is software that automates the production, distribution, and management of output streams from enterprise or desktop applications to any physical or virtual output channel. Functionality includes, but is not limited to, data transformation, format conversion, print server elimination, application integration, and multichannel delivery. Included are fax servers and other applications that manage the dissemination of output. The term output includes not only\
    hardcopy devices such as multifunction peripherals (MFPs), printers, and fax machines but also digital destinations such as email, Web pages, and other digital channels. This category does not include workflow applications or packaged online viewing applications for specific vertical industries. Representative vendors and products in this submarket are:\
     CA Technologies (Dispatch)\
     LRS Dynamic Report System, VPSX  Plus Technologies (OM Plus)\
     HP (Output Server)\
     Ricoh (InfoPrint Manager)\
     Nuance (Output Manager)"))
    taxonomySort.categories[0].subCategories[13].addNewCategory("Performance management software")
    taxonomySort.categories[0].subCategories[13].subCategories[3].addText(ratioCreator("Performance management software is used for compute infrastructure and application performance monitoring, performance data collection, performance tracking, forecasting, capacity and performance analysis, simulation and planning software, predictive analytics, and business performance impact analysis enabled by IT and APM performance data. It also includes service-level management software when applied to systems and applications including mobile devices, mobile applications, and public and hybrid cloud services. Resource accounting software for resource utilization tracking and reporting and IS-specific financial management and planning is also included. The following are representative vendors and products in this market:\
     AppDynamics\
     BMC TrueSight Capacity Optimization, TrueSight Operations Management (portions thereof),\
    and MainView\
     CA Technologies CA Application Performance Manager and CA Unified Infrastructure Management\
     Compuware Strobe\
     Dynatrace Application Monitoring, User Experience Management, and Synthetic Monitoring\
     HPE AppPulse\
     IBM APM\
     New Relic\
     Microsoft System Center (Operations Manager module)\
     VMware vRealize Business and vRealize Operations (portions thereof)"))
    taxonomySort.categories[0].subCategories[13].addNewCategory("Change and configuration management software")
    taxonomySort.categories[0].subCategories[13].subCategories[4].addText(ratioCreator("Change and configuration management software provides change, configuration, compliance and asset tracking for physical and virtual systems, application software containers, cloud infrastructure and services and client, desktop, mobile devices, and peripheral hardware and software assets but not network devices. Software for planning, tracking, and applying system hardware and software changes is also included, as is software distribution, hardware and software discovery and inventory, CMDBs, license management, settings and state management, and auditing. The following are representative vendors and products in this market:\
     BMC Discovery (formerly ADDM), IT Asset Management, and BMC FootPrints  Dell KACE\
     HPE Asset Manager\
     IBM Endpoint Manager\
     Microsoft System Center Configuration Manager and Virtual Machine Manager  VMware vCenter Server\
     Red Hat Satellite\
     SAP IT Infrastructure Management and Landscape Virtualization Management\
    Problem Management Software"))
    taxonomySort.categories[0].subCategories[13].addNewCategory("Problem management software")
    taxonomySort.categories[0].subCategories[13].subCategories[5].addText(ratioCreator("Problem management software tracks, records, and manages problems related to IT end users, devices, infrastructure, and operations. This category includes IT help desk applications and related problem determination and resolution applications, including knowledge bases. This category is separate from externally focused problem resolutions solutions within customer relationship management. To the extent that IT infrastructure library (ITIL) and IT service management–based solutions help in the resolution of problems as well as preventative activities such as root cause analysis, those functions are included here as well. The following are representative vendors and products in this market:\
     BMC Remedy IT Service Management Suite\
     CA Technologies — CA Service Desk Manager and CA Cloud Service Management  HPE Service Manager and HPE Service Anywhere\
     IBM Control Desk (portions thereof)\
     Cherwell Software\
     ServiceNow IT Service Management"))


    taxonomySort.categories[0].addNewCategory("Network Software")
    taxonomySort.categories[0].subCategories[14].addText(ratioCreator("The network software market includes a broad set of networking and communications technologies that are deployed across enterprise, cloud provider, and communication service provider (CSP) domains. These encompass the products and technologies that are primarily deployed to build and support local area or wide area networks for established and emerging applications including voice and video, across enterprise/private and public, and fixed and mobile networks. Network software is a secondary market that includes two functional markets:"))

    taxonomySort.categories[0].subCategories[14].addNewCategory("Network infrastructure software")
    taxonomySort.categories[0].subCategories[14].subCategories[0].addText(ratioCreator("Network infrastructure software encompasses software that enables virtualized networking, optimization, orchestration, and related network infrastructure functions across enterprise, datacenter, and communication service provider networks. This software can be an alternate deployment model running on commodity hardware while providing networking and/or communications functionality. It may work at any or all layers of the network stack and can include data plane software and control plane software, as well as the broad areas of network virtualization across all types of enterprise and service provider networks.\
    As networking technologies transition into software-based architectural approaches that encompass software-defined networks (SDN) and network functions virtualization (NFV), the networking software used for such a deployment is included here. However, this designation also includes network software that may or may not be used in a SDN- or NFV-type deployment.\
    Within NIS, IDC plans to track three submarkets as the market and technology domains evolve:\
     Network application delivery, including the application delivery controller (ADC) and WAN optimization markets, with vendors such as F5 (Big-IP), Citrix (Netscaler), Riverbed (SteelHead), Silver Peak (VX/VRX), Cisco (WaaS), and Radware (vADC)\
     Software-defined networks, including the network virtualization, SDN controller, and network services markets, with vendors such as Cisco (ACI), VMware (NSX), Juniper (Contrail), Brocade (Vyatta), and Alcatel-Lucent (Nuage VSP)\
     Telecom equipment provider NIS, including the traditional CSP equipment domains with vendors such as Ericsson, Nokia, Huawei, Oracle, and Alcatel-Lucent\
    The first submarket, network app delivery, has already been tracked and reported within IDC's Software Tracker. We are now commencing tracking of the second submarket, namely the network virtualization and SDN controller market, as illustrated by some of the vendors/solutions highlighted in the aforementioned list. IDC will continue to watch the third submarket closely, building revenue models gradually, with the aim of reporting on these segments when there is sufficient and credible data.\
    Network Application Delivery Software\
    The application delivery market is made up of two markets: the application delivery controller (ADC) market, also known as the Layer 4–7 switching market and the WAN optimization market. The products and the suppliers in the space have contributed to the increasing business relevance of the network, with ADCs ensuring the availability, performance, reliability, and security of application workloads in the datacenter and WAN optimization, ensuring the delivery of applications from the datacenter to branch offices, to remote users, and to other datacenters.\
    Broadly speaking, these networking software products make intelligent decisions regarding the effective and optimized delivery of applications for enterprise customers and service providers. Key among the products' priorities is the need to provide a secure, reliable architecture to enterprise applications and, in many instances, Web applications, but in all instances, to applications that are running over TCP/IP. They enable network policies specific to the applications running on the network, and they operate in a class of products known as network and security services, meaning that like a variety of security products, they reside at Layers 4–7 of the OSI protocol stack.\
    This product category, comprising ADCs and WAN optimization, provides a range of specific features but generally works to enable customers to implement reliable, resilient network architectures that provide essential network services to and support for business-critical client server, Web, and cloud workloads. Although software (virtual appliances) is tracked here, these platforms are also available as physical appliances — the full view is available in IDC's networking trackers/QViews.\
    Application Delivery Controllers\
    Also known as Layer 4–7 switches, ADCs make forwarding decisions based on packet information contained in the upper layers of the OSI model, specifically the transport, session, presentation, and application layers. An ADC can determine what type of user or device is requesting content and what type of content is being requested and make traffic management decisions accordingly. Functionality can include local and global load balancing, access control, bandwidth management, firewall load balancing, secure sockets layer switching and offload, traffic prioritization, and URL and cookie switching.\
    WAN Optimization\
    The primary goal of WAN optimization products is to cost effectively enhance and optimize the delivery of applications across the WAN, either from the datacenter to branch or remote offices or between datacenters. WAN optimization products must have the following features to be included in the market: compression of datastreams, the ability to monitor traffic flows, traffic prioritization, bandwidth optimization, and caching.\
    Network Virtualization and SDN Controller Software\
    Network virtualization and SDN controller software comprises network virtualization overlays and SDN controllers used in datacenter networks. Both overlays and controllers bring alternate SDN architectures to the network, supporting multiple protocols and southbound/northbound interfaces/APIs. Network virtualization overlays are logical, virtual networks that run over (on top of) physical network infrastructure. SDN controller software also runs on top of physical network infrastructure (residing between applications and the network), providing logically centralized network control and a means for application policy to be enacted across the network. It can also facilitate automated network management and networkwide visibility.\
    Examples of the platforms and solutions included in this submarket include:\
     Cisco (ACI), VMware (NSX)\
     Juniper (Contrail)\
     Brocade (Vyatta)\
     Alcatel-Lucent (Nuage VSP)\
     Midokura (Enterprise MidoNet)  PLUMgrid (ONS)\
     HPE (VAN)\
     NEC (ProgrammableFlow)"))
    taxonomySort.categories[0].subCategories[14].addNewCategory("Network management software")
    taxonomySort.categories[0].subCategories[14].subCategories[1].addText(ratioCreator("Network management software includes solutions for managing the network components of enterprise infrastructures. It includes two categories: network performance management and network operations management. The products within network management often and increasingly will integrate with cross-domain infrastructure management tools such as service desks, application management, systems management, and business dashboards across multiple platforms and topologies, including data, voice, video, traditional networks, and wireless networks. Network management includes solutions that manage network availability by collecting and correlating events, service levels, alarms, response times, and performance. It also includes network configuration management products that manage, control, and audit changes to the network infrastructure. However, solutions solely for network service providers are excluded.\
    Representative vendors include:\
     CA (Spectrum, Network Flow)\
     EMC (Service Assurance/NCM)  HPE (ANM, IMC)\
     IBM (Netcool)"))


    taxonomySort.categories[0].addNewCategory("Security")
    taxonomySort.categories[0].subCategories[15].addText(ratioCreator("The security software market includes a wide range of technologies used to improve the security of computers, information systems, Internet communications, networks, and transactions. It is used for confidentiality, integrity, privacy, and assurance. Through the use of security applications, organizations can provide security management, access control, authentication, malware protection, encryption, data loss prevention (DLP), intrusion detection and prevention, vulnerability assessment, and perimeter defense. All these tools are designed to improve the security of an organization's networking infrastructure and help advance value-added services and capabilities. Security software includes traditional security software as well as security software-as-a-service offerings. The market covers both corporate and consumer security software.\
    Security software is divided into seven specific functional markets — identity and access management (IAM), endpoint security, messaging security, network security, Web security, security and vulnerability management, and other security software. Each of these markets has additional submarkets."))


    taxonomySort.categories[0].subCategories[15].addNewCategory("Identity and access management")
    taxonomySort.categories[0].subCategories[15].subCategories[0].addText(ratioCreator("Identity and access management is a comprehensive set of solutions used to identify users (employees, customers, contractors, and others) in an IT environment and control their access to resources within that environment by associating user rights and restrictions with the established identity and assigned user accounts. Subcategories of the IAM market include identity management suites, user provisioning, privileged account management (PAM), cloud single sign-on (CSSO), advanced authentication (software for both PKI and supporting personal portable security devices such as smartcards and OTP tokens), and legacy authorization, such as RACF and ACF-2.\
    The following are representative vendors and products in the identity and access management market:\
     CA Technologies (CA SiteMinder, CA ControlMinder, and CA CloudMinder sets of products)\
     CyberArk (CyberArk Enterprise Password Vault and CyberArk Privileged Session Manager)\
     Dell (Dell Identity Manager, Dell One Identity Cloud Access Manager, and Dell Privileged Password Manager)\
     IBM (IBM Security Identity and Access Manager, Tivoli Federated Identity Manager, and IBM Security zSecure Admin)\
     Ping Identity (PingOne, PingFederate, and PingAccess)\
     RSA, the Security Division of EMC (RSA Identity Management and Governance, RSA Access\
    Management, and SecurID)"))
    taxonomySort.categories[0].subCategories[15].addNewCategory("Endpoint security")
    taxonomySort.categories[0].subCategories[15].subCategories[1].addText(ratioCreator("The endpoint security market covers both the corporate and the consumer segments. The market includes client antimalware software, file/storage server antimalware, personal firewall software, host intrusion prevention software, file/disk encryption, white listing, patch management desktop URL filtering, and endpoint data loss prevention. Example vendors and products in this category include:\
     Bit9 (Security Platform)\
     ESET (ESET Endpoint Security and ESET Multi-Device Security)\
     Intel (McAfee Complete Endpoint Protection, McAfee SaaS Endpoint Protection Suite, and McAfee Deep Defender)\
     Kaspersky Lab (Kaspersky Endpoint Security for Business Advanced and Kaspersky PURE Total Security)\
     Symantec (Norton 360, Symantec Endpoint Protection, and Symantec Endpoint Encryption)  Trend Micro (OfficeScan Deep Security and Titanium Internet Security)"))
    taxonomySort.categories[0].subCategories[15].addNewCategory("Messaging security")
    taxonomySort.categories[0].subCategories[15].subCategories[2].addText(ratioCreator("The messaging security market includes both software and SaaS platforms. The security technologies include antispam, antimalware, content filtering, and DLP. Example vendors and products in this category include:\
     Intel (McAfee GroupShield and IronMail)\
     Proofpoint (Proofpoint Enterprise Protection)\
     Sophos (Sophos Secure Email Gateway and PureMessage)\
     Symantec (Symantec Messaging Gateway, Symantec Gateway Email Encryption, and Symantec Premium AntiSpam)\
     Trend Micro (InterScan, ScanMail, and Hosted Email Security)\
     Trustwave (Trustwave Secure Email Gateway)"))
    taxonomySort.categories[0].subCategories[15].addNewCategory("Network security")
    taxonomySort.categories[0].subCategories[15].subCategories[3].addText(ratioCreator("The network security market includes enterprise firewall software, network intrusion detection and prevention software, unified threat management software, IPSec/SSL VPN software, network access control, and the associated management software. Example vendors and products in this market include:\
     Check Point (Firewall Software Blade, IPS Software Blade, and Anti-Bot Software Blade)  Cisco (IOS Firewall, IOS IPS, IOS SSL VPN, and Snort)\
     IBM (IBM Security Network Intrusion Prevention System Virtual Appliance)\
     Juniper (vGW Series)\
     Sophos (Sophos UTM virtual appliance) "))
    taxonomySort.categories[0].subCategories[15].addNewCategory("Web security")
    taxonomySort.categories[0].subCategories[15].subCategories[4].addText(ratioCreator("Web security includes both software and SaaS platforms. The security technologies include Web filtering, Web antimalware, Web application firewall, Web 2.0 security, and Web DLP. Example vendors and products in this category include:\
     Barracuda Networks (Barracuda Web Security Service and Barracuda Web Filter Vx)\
     Cisco (Cisco Cloud Web Security SaaS)\
     Intel (McAfee Web Protection)\
     Trend Micro (InterScan Web Security and Trend Micro Smart Protection Network)\
     Websense (now known as Forcepoint) (Websense Cloud Web Security and Websense Web Security Gateway Anywhere)\
     Zscaler (Cloud Web Security)"))
    taxonomySort.categories[0].subCategories[15].addNewCategory("Security and vulnerability management software")
    taxonomySort.categories[0].subCategories[15].subCategories[5].addText(ratioCreator("Security and vulnerability management software is a comprehensive set of solutions that focus on allowing organizations to determine, interpret, and improve their risk posture. Software products in this market include those that create, monitor, and assess and report security policy; determine the configuration, structure, and attributes for a given device; perform assessments and vulnerability scanning; aggregate and correlate security logs; and provide management of various security\
    technologies from a single point of control. The following are representative vendors and products in this market:\
     EMC (RSA Security Analytics, RSA Archer GRC, and RSA IT Security Risk Management Solution)\
     HPE (ArcSight and HP Fortify)\
     IBM (Tivoli Security Policy Manager, IBM QRadar SIEM, and Rational AppScan)\
     Intel (McAfee Vulnerability Manager, McAfee ePolicy Orchestrator, and McAfee Asset Manager)\
     Qualys (QualysGuard)"))
    taxonomySort.categories[0].subCategories[15].addNewCategory("Other security software")
    taxonomySort.categories[0].subCategories[15].subCategories[6].addText(ratioCreator("Other security software covers emerging security functions that do not fit well into an existing category. It also includes some of the underlying security functions, such as encryption tools and algorithms that are the basis for many security functions found in other software and hardware products. Also included in this category are products that fit a specific need but have yet to become established in the marketplace. Products currently in this category will either grow into their own categories or eventually be incorporated into the other market segments.\
    Areas covered by other security software include, but are not restricted to, encryption toolkits, security product verification testing, storage security, Web services security, and secure operating systems. Note that the products covered here are only those that do not qualify for one of the more established categories. The following are representative vendors and products in this market:\
     Green Hills Software (INTEGRITY RTOS)\
     RSA, the Security Division of EMC (BSAFE)  SafeNet (DataSecure and ProtectV)\
     Axway (Vordel SOA Gateway)"))


    taxonomySort.categories[0].addNewCategory("Storage Software")
    taxonomySort.categories[0].subCategories[16].addText(ratioCreator("Storage software manages, stores, and/or ensures the accessibility, availability, and performance of information stored on physical storage media ranging from memory-based devices to hard drive–based devices to magnetic-based devices. This category does not include operating systems or subsystems. This category includes vendor revenue for the delivery of software functionality that is offered in the form of perpetual licensing, subscription-based licensing, and public cloud SaaS services.\
    However, IDC tracks only storage software revenue associated with purchasable products or services that have a related SKU or license. IDC makes no attempt to derive or estimate any financial value associated with storage systems features that are included at no cost, or bundled with a storage system sale, without a SKU or software license that is clearly attributable to the software. Since some within the storage supplier community bundle storage software with a system, attribution of revenue for some storage software offerings differs. Differences arise when one vendor charges for a software feature, and another vendor includes it with a system sale at no cost. Some storage systems suppliers, for example, charge for thin provisioning, while others bundle thin provisioning with the storage system at no cost. This gives the first vendor a revenue attribution advantage within IDC's storage software numbers but may also put that vendor at a competitive disadvantage if the broad market trend is toward bundling. The storage software secondary market is broken down into six functional software markets, as described in the sections that follow."))


    taxonomySort.categories[0].subCategories[16].addNewCategory("Data protection and recovery software")
    taxonomySort.categories[0].subCategories[16].subCategories[0].addText(ratioCreator("Data protection software includes revenue from both software and online data protection services (also known as online backup or backup as a service [BaaS]) licensed in a subscription fashion. Data protection and recovery software is focused on protection, restoration, and recovery of data in the event of physical or logical errors. Included within the data protection and recovery market are data protection, continuous data protection (CDP), bare metal restore, virtual tape library (VTL), and backup/recovery reporting products. These capabilities include or span products that support both physical and virtual infrastructure.\
    Data Protection Software\
    Data protection software includes both traditional backup software and continuous data protection software and modules that integrate snapshot or cloning capabilities with traditional backups. These solutions provide continuous as well as point-in-time copy functionality for defined data sets to tape, disk, or optical devices and are used to recover part or all of the data set if needed because of logical or physical error or site disaster. Today, capacity-optimized disk is one of the leading mechanisms for operational protection and recovery processes — both on-premise and with cloud services.\
    However, many products support data protection to both disk and tape. As a result, included in data protection and recovery are library and tape media management tools. Backup is often used in conjunction with snapshot and data replication software to improve data protection performance. If using traditional tape backup products, recovering data from a backup set generally requires the initiation of a separate process. For environments with faster or more granular recovery objectives, continuous data protection, snapshots, clones, and/or replication approaches are used.\
    Representative vendors and products are:\
     Commvault (Simpana)\
     Veeam (Veeam Backup)\
     VMware (Advanced Data Protection)\
    Virtual Tape Library Software\
    This software, commonly an option or module to a broader offering, presents a virtualized view of physical tape drives and media to a host, thus emulating traditional tape devices and tape formats and acting like a tape library with the performance of modern disk drives. During a VTL process, data is deposited onto disk drives just as it would be deposited onto a tape library, only faster. A virtual tape library generally consists of a virtual tape appliance or server and VTL software that emulates traditional tape devices and formats. Representative vendors and products are:\
     EMC Data Domain (VTL software)  FalconStor (Virtual Tape Library)\
    Backup and Recovery Reporting Software\
    This software is designed for heterogeneous, standalone backup reporting and management across different backup applications, configurations, and locations. Reports are generated on backup environment parameters such as backup job status, tape media capacity, and backup performance. Representative vendors and products are:\
     Bocada (Bocada Enterprise)\
     EMC (Data Protection Advisor)  APTARE (Backup Manager)"))
    taxonomySort.categories[0].subCategories[16].addNewCategory("Storage replication software")
    taxonomySort.categories[0].subCategories[16].subCategories[1].addText(ratioCreator("Storage replication software includes software designed to create image copies of virtual machines, volumes, or files via techniques such as hypervisor-based replicas, clones, mirrors, and snapshots. Replication may be storage system, application server, hypervisor based, fabric based, or appliance based and may occur locally or between remote sites, potentially separated by long distances. Replication and snapshot software is often used in conjunction with backup software to improve data protection performance. This market does not include database replication software that operates at the database, table, or record level.\
    Host or Hypervisor-Based Replication Software\
    This software typically resides at the file system or logical volume level within the operating system and makes a point-in-time copy or snapshot of a data set to disk used for disaster recovery, testing, application development, or reporting. In recovery, replication eliminates the intermediary step of a restore process. Representative vendors and products are:\
     Commvault (Simpana Replication)  VMware (vSphere Replication)\
     Zerto (Virtual Replication)\
    System and Data Migration Software\
    This block-based or file-based migration software is used to migrate data from one platform to another for system upgrades and technology refreshes, moving the data to a new platform. Representative vendors and products are:\
     Hitachi (Hitachi Tiered Storage Manager)  EMC (Federated Live Migration)\
    Fabric- and Appliance-Based Replication Software\
    Fabric- and appliance-based replication software makes use of intelligent switches and heterogeneous array products to provide block-level replication within the SAN. The intelligent switches have technologies that perform the volume management and replication process and eliminate the overhead on the host while providing any-to-any replication. It also includes a software component to appliance-based replication. Representative vendors and products are:\
     EMC (RecoverPoint)\
     FalconStor (Network Storage Server)\
    Array-Based Replication Software\
    This software makes a block-based point-in-time block copy or snapshot of storage to disk used for disaster recovery, testing, application development, reporting, and other uses. Representative vendors and products include the following:\
     EMC (Symmetrix Remote Data Facility)  NetApp (SnapMirror)\
    Replication Management Software\
    This software is used to control, monitor, and/or schedule the point-in-time copies made by the replication product. It may automate various replication tasks, such as sync, split, and mount. Copy data management (CDM) is also included within replication management software. Copy data management software optimizes the number of data copies required, such that all use cases and service levels are served while eliminating superfluous copies of the original data. Copied data refers to any copies of original data created by any mechanism such as snapshots, mirrors, and replication that are redundant to the primary copy. Copied data does not include RAID 10 copies.\
    Representative vendors and products are:\
     EMC (Replication Manager)\
     Hitachi (HiCommand Replication Monitor)  Catalogic Software (ECX)"))
    taxonomySort.categories[0].subCategories[16].addNewCategory("Archiving software")
    taxonomySort.categories[0].subCategories[16].subCategories[2].addText(ratioCreator("The archiving software market includes software that provides policy-based controls for copying, moving, purging (delete from primary storage), retaining (in read-only fashion for a defined period), and deleting (delete from secondary storage) data. Some tools provide for more sophisticated functions such as content-based data management, indexing, and search/retrieval. Archiving software makes tiering decisions based on file properties and business rules, but not file properties alone. Business rules may be based on metadata such as custodian of information, business unit of origin, or indexed content. Archiving software typically requires software on a host to manage the archiving\
    process. All archiving products except those that perform database archiving are included in this market.\
    Email Archiving Software\
    Included within the archiving software market are specialized email archive software products that integrate with collaborative email systems through APIs to migrate email, based on policy, to a secondary archive. Included in email archiving software are functions for email retention and searching. Representative vendors and products are:\
     Symantec (Enterprise Vault)\
     Barracuda (Barracuda Message Archiver)\
    File and Other Archiving Software\
    File archiving software automates, based upon a defined policy, the migration of data to a different tier of storage and media and automatically recalls files back to primary storage when required for application or user access. File archiving software creates, based upon a defined policy, a copy of a data set or a group of files that are transported to an alternate location or committed to long- or intermediate-term storage. Original copies of the data set may be deleted when the archive is created to free primary storage space, or they may be left in place if frequent access is expected. Other archiving options include archiving for SharePoint or other unstructured content (social media, etc.) Representative vendors and products are:\
     EMC (SourceOne for File systems and SharePoint)  IBM (Content Collector for Files and SharePoint)\
    Storage and Device Management Software\
    The storage and storage device management software includes both lower-level device and element management software, as well as homogeneous and heterogeneous storage management functions for tasks such as provisioning, reporting, monitoring, and high-level troubleshooting.\
    SRM and Heterogeneous SAN Management Software\
    This software is designed for heterogeneous, end-to-end discovery; topology mapping; capacity utilization; and performance reporting, planning, monitoring, and management. It includes software modules for advanced functions such as storage provisioning, host-level reporting, file-level analytics, application and file systems integration, and event management. To qualify as a storage management product, the product must provide for the management of a diverse set of storage systems, storage switches, servers, and applications. Device management tools that provide discovery and configuration of a single device type or asset are not included. Representative vendors and products are:\
     EMC (EMC ControlCenter)  HP (HP Storage Essentials)\
    SRM and SAN Management Software for Homogeneous Environments\
    This software is designed for homogeneous, end-to-end discovery; topology mapping; capacity utilization; and performance reporting, planning, monitoring, and management. It includes software modules for advanced functions such as storage provisioning, host-level reporting, file-level analytics, application and file systems integration, and event management. Representative vendors and products are:\
     HDS (Hitachi Command Suite)\
     NetApp (OnCommand System Manager)"))
    taxonomySort.categories[0].subCategories[16].addNewCategory("Storage and device management software")
    taxonomySort.categories[0].subCategories[16].subCategories[3].addText(ratioCreator("Storage device management software performs a specific set of functions for a specific, homogeneous brand or class of storage device. Device management software utilities capture basic information on the storage device and tend to support only that device or device family (not a heterogeneous management tool). The functions provided by device management software include storage device discovery, configuration, and management, with basic levels of reporting. It includes software used to control the configuration and management of disk devices, storage arrays, and networks as well as the associated utilities, element managers, and agents. This market also includes utilities for low-level disk device functions such as optimization, defragmentation, and compression. Representative vendors and products are:\
     EMC (Symmetrix Management Console)  NetApp (OnCommand System Manager)\
    Other Storage Management Software\
    These applications provide standalone storage management functionality such as predictive change management, performance management, problem management, capacity planning, forecasting, or SLA management. Representative vendors and products are:\
     NetApp (OnCommand Insight)\
     Dell (NetVault: Report Manager Pro)"))
    taxonomySort.categories[0].subCategories[16].addNewCategory("Storage infrastructure software")
    taxonomySort.categories[0].subCategories[16].subCategories[4].addText(ratioCreator("The storage infrastructure software category is made up of the following types of enabling software:\
     Storage virtualization and federation software\
     File systems and volume management software  Access and path management software\
     Automated storage tiering software\
     Storage acceleration software\
    All of the software categories listed here are enabling software only — and not standalone or autonomous platforms. Complete, standalone, or autonomous platforms are captured in the software- defined storage controller software functional market. In other words, software categories listed here include software not packaged and sold as complete storage platforms by themselves.\
    Storage Virtualization and Federation Software\
    Array-based virtualization (enabling) software provides advanced volume virtualization for storage within the array as well as other SAN-connected storage arrays. This software provides abstraction and pooling capabilities but lacks the data access capabilities available within SDS platform offerings. In other words, this virtualization software is an enabling component of a hardware-defined or hardware-based storage platform. Representative vendors and products include:\
     Hitachi Universal Volume Manager  EMC VPLEX\
    Host-Based File Systems and Volume Management Software\
    File systems and volume management software is installed on storage hosts and enables the management of physical disks as logical devices and POSIX-compliant data constructs for application access.\
    Volume management software enhances data storage management by controlling space allocation, performance, data availability, device installation, and system monitoring of dedicated and shared storage systems. While volume management software commonly comes with a host operating system, some volume management software offerings remain available as standalone products or are included with broader storage management suites. A representative vendor and product is:\
     Veritas (Veritas Volume Manager)\
    File system software provides a POSIX-compliant hierarchical structure for organizing data. In other words, file systems provide the organization and structure for storing and retrieving data as files, folders, and directories. File systems can be unitary in nature — meaning they are confined to a single host or controller — or they can be distributed in nature — meaning that the file system is shared between more than one host/controller. Software covered in this market segment only includes standalone or distributed file systems that are enabling in nature (i.e., provide data organizational elements but cannot exist as independent storage platforms). Products include clustered file system, wide area file system, and file virtualization software. A representative vendor and product is:\
     Veritas (Veritas File System)\
    Access and Path Management Software\
    Access and path management software provides for storage path and access configuration, management, load balancing, and failover on path failure. Only software sold as a separate software product or option is included in the revenue for this market. Representative vendors and products are:\
     EMC (PowerPath)\
     Hitachi (Hitachi Dynamic Link Manager)  Veritas Dynamic Multi-Pathing (DMP)\
    Automated Storage Tiering Software\
    Automated storage tiering software enables the automated movement of data sets between differing tiers of storage resources. This may occur at the volume level or at a subvolume level. Tiers may be defined by performance, capacity, and/or resiliency requirements of the data/applications. Representative vendors and products are:\
     EMC (Fully Automated Storage Tiering [FAST])  HDS (Hitachi Tiered Storage Manager)\
    Storage Acceleration Software\
    Storage acceleration software allows data to be cached onto an application server's internal memory or flash-based storage resources. Storage acceleration software is designed to improve an application's read/write response time by leveraging the performance characteristics of flash-based storage media and by eliminating the need for IOs to travel between a server and an externally attached storage system. Data sets can be permanently pinned to a server's flash-based resources or destaged to external storage resources as the need for acceleration subsides. Acceleration software has the ability to monitor IOs and automatically cache data sets based on various read/write patterns.\
    Storage acceleration software is sometimes referred to as host-based solid state caching or server- side caching. Representative vendors and products are:\
     PernixData (FVP Software)  Condusiv (V-locity)"))
    taxonomySort.categories[0].subCategories[16].addNewCategory("Software-defined storage controller software")
    taxonomySort.categories[0].subCategories[16].subCategories[5].addText(ratioCreator("Software-defined storage controller software (previously called 'software-defined storage platforms') is IDC's newest storage software functional market. Originally referred to as software-defined storage platforms, IDC has updated the name of this market to better reflect the role of these products within the storage software ecosystem. This functional market includes and combines block, file, object, and hyperconverged software offerings that enable the creation of a storage system.\
    Software-defined storage fundamentally alters how storage systems are delivered (supplier view) or procured (buyer view). IDC refers to software-defined storage as complete systems that deliver the full suite of storage services via a software stack that uses (but is not dependent on) commodity hardware built with off-the-shelf components.\
    For any solution to be included within the software-defined storage controller software functional market, it needs to be extensible, autonomous, and allow data access via known and/or published interfaces (APIs or standard file, block, or object interfaces). For any solution to be classified as software-defined storage, it must satisfy the following requirements:\
     The solution should not contain any proprietary hardware components like custom ASICs, chipsets, memory components, or CPUs — and the software code should not make any assumption of such components being present to offer any essential storage (or storage efficiency) services.\
     The solution should be able to run on multiple (physical or virtual) hardware instances that are not factory configured by the supplier. Buyers should be able to procure the platform as software and deploy it in a virtual environment or directly on any physical hardware of their choice (as long as this hardware belongs to the same peer class listed in the supplier's hardware compatibility list).\
     The solution is a standalone or autonomous system. In other words, it provides all essential northbound storage services and handles all southbound data persistence functions without requiring additional hardware or software. IDC therefore considers file systems and logical volume managers to be building blocks of a software-defined storage solution rather than complete systems.\
    Note: IDC does not state that commodity means x86 platforms only. There are several non-x86 platforms like Power and ARM that are becoming commoditized and may ultimately be deemed suitable for mass consumption. Also, the term controller refers to a commodity/off-the-shelf/industry- standard server that performs the same role as that of a controller in a hardware-defined/based storage system. In the case of a hardware-defined/based system, such software is often referred to as a firmware or a storage OS. In fact, several storage suppliers are making the same controller firmware or storage OS available as a software-defined storage controller software. The chief difference is that the latter is devoid of any hardware-specific dependencies. IDC uses data organization as the starting point for a classification of software-defined storage controller software. In other words, most software- defined storage solutions use controller software that organizes data in the form of file, object, and/or block. Furthermore, SDS solutions can leverage a variety of persistent data storage resources such as internal storage resources (like PCIe/NVMe flash cards, nonvolatile memory, solid state drives, and hard disk drives), external disk arrays (as long as no storage-specific functions are 'offloaded' to these\
    arrays), tape drives, and even higher-level services like NoSQL databases, object storage, and cloud- based resources. SDS solutions should offer a full suite of data access interfaces, storage, and data management services (included federation services). Finally, SDS solutions should be delivered in multiple forms including appliances, software, and subscription-based offerings.\
    IDC does not make any presumption on the operating platforms used in SDS solutions. SDS platforms can be built using open source operating platforms (e.g., Linux, OpenSolaris, and FreeBSD) or using proprietary operating platforms (e.g., Solaris and Windows). The use of the latter does not alter or invalidate the classification of the solution as SDS.\
    Block-Based Software-Defined Storage Controller Software\
    Block-based software-defined storage controller software employs a block-based data organization scheme. It is similar to the mechanisms employed by logical volume managers wherein data is organized in the form of blocks. Physical resources are grouped in the form of disk or RAID groups and then chunked up into logical constructs such as plexes and volumes (and soon VM-specific constructs like VVOLS). Volumes are then presented as logical units with SCSI identifiers referred to as logical unit numbers (LUNs). Block-based data organization is widely used in several virtual tape libraries that present a tape-drive interface but use files and volumes to organize data.\
    Block-based SDS software enables storage array–independent management of storage or data. It isolates and abstracts the internal details of different storage systems and services and simplifies storage management by masking physical complexities from servers, applications, and other network resources. Such software is frequently used for pooling or aggregating storage or to add new capabilities to available storage resources. It is common for block-based storage virtualization to be a feature of a storage system. However, only software sold as a separate software product or option is included in this market. Representative vendors and products are:\
     DataCore (SANsymphony-V)  IBM (SAN Volume Controller)  FalconStor (IPStor)\
    File-Based Software-Defined Storage Controller Software\
    File-based software-defined storage controller software employs a file system for organizing data and providing standard storage interfaces. Storage platforms that employ file-based data organization provide the organization and structure for storing and retrieving data as files, folders, and directories, and a namespace provides external (to the file system) or network-based data access.\
    File-based software-defined storage controller software can be unitary in nature — meaning it is confined to a single host or controller — or distributed in nature — meaning that the data organization and interfaces are shared between more than one host/controller. Software covered in this market segment therefore includes standalone, distributed file-based platforms for which the primary purpose is to provide access to storage access. These file-based platforms support sophisticated intersystem record and file locking capabilities because of the underlying file system that they use. Representative vendors and products are:\
     ZFS-based storage platforms\
     GlusterFS-based storage (Red Hat Storage Server 2.0)  IBM GPFS- and LTFS-based platforms\
    Object-Based Software-Defined Storage Controller Software\
    Object-based software-defined storage controller software solutions employ a higher level of service (often constructed on top of local file systems or databases with extensible attribute management capabilities) that includes a container-type mechanism for data organization (rather than a hierarchical tree-based structure found in file systems and one in which data is stored as objects with a reference ID) and a separate metadata repository (which often at times is NoSQL based) that is used to store rich contextual information on the objects. In addition, object platforms extensively employ either erasure coding (a form of data redundancy that replaces RAID and strict replication) and/or data replicas (in which data copies are created and distributed across multiple nodes for redundancy).\
    Representative vendors and products are:\
     IBM (Cleversafe)\
     Western Digital (AmpliStor XT)\
     NetApp (StorageGRID Webscale Software)\
    Hyperconverged Software–Defined Storage Controller Software\
    Hyperconverged software–defined storage controller software solutions natively collapse core storage, compute, and storage networking functions into a single software solution or appliance. This is in contrast to traditional integrated platforms and systems in which autonomous compute, storage, and networking systems are integrated at the factory or by resellers. While these systems will often use an Ethernet switch to cluster multiple nodes together, they do not rely on disparate storage networking equipment for data movement between the storage and compute. In addition to bringing storage and computing into a single node (or a cluster of nodes, each offering compute and storage), all revenue related to OSS components, packaged and distributed using container technology, remains part of the OSS functional market.\
    Hyperconverged systems utilize a hypervisor that provides workload adjacency and containerization, hardware abstraction, and data management. The hypervisor also hosts essential management software needed to manage the solution. Representative vendors and products are:\
     Microsoft (Storage Spaces)\
     VMware (VSAN)\
     Nutanix (Nutanix Operating System)"))


    taxonomySort.categories[0].addNewCategory("System Software")

    taxonomySort.categories[0].subCategories[17].addNewCategory("Operating systems and subsystems")
    taxonomySort.categories[0].subCategories[17].subCategories[0].addText(ratioCreator("Operating system and subsystem software includes the machine-level instructions and general- purpose functions that control the operation and use of CPU resources (both centralized and networked). These operating systems quite often also include network services such as Dynamic Host Configuration Protocol (DHCP) for IP address assignment, distributed naming services (DNS) software (which provides a shared database of system resources and access control information), and directory service software (such as Microsoft's Active Directory or LDAP services), as well as other integrated network facilities such as print and file services. Operating systems and subsystems also include revenue from certain mobile devices including smartphones, tablets, and convertibles.\
    Representative vendors and products include the following:\
     Apple Computer (OS X and iOS)\
     HPE (HP-UX)\
     IBM (z/OS, IBM i, and AIX)\
     Microsoft (Windows 10, Windows 8, Windows 7, Windows Server 2012, Windows Server 2008, as well as older Windows products)\
     Micro Focus (Novell Open Enterprise Server, SUSE Linux Enterprise Server, and SUSE Linux Enterprise Desktop)\
     Oracle (Solaris, Oracle Linux)\
     Red Hat Linux (Red Hat Enterprise Linux and Red Hat Enterprise Linux Desktop)\
    OSS functionality is also provided on a nonrevenue-generating basis by open source versions of client and server products (including Ubuntu, CentOS, and Debian), as well as mobile implementations typically but not exclusively based on the publicly available Android code base. These free solutions do not contribute revenue to this market but do serve as a foundation for revenue-producing products at other layers of the software stack.\
    Revenue related to OSS components, packaged and distributed, using container technology remains part of the OSS functional market."))
    taxonomySort.categories[0].subCategories[17].addNewCategory("Availability and clustering software")
    taxonomySort.categories[0].subCategories[17].subCategories[1].addText(ratioCreator("Availability and clustering software virtualizes the system services of multiple systems (physical servers or virtual servers), so that they appear in some sense as a single computing resource. This market includes failover clustering software, which maintains a 'heartbeat' between the linked servers and restarts workloads on alternate servers if the heartbeat (or the lack of it) signals that one of the servers is offline. It also includes cluster managers and compute farm managers, as well as load- balancing software and application virtualization software that stands between the user request and the processors or systems that are supporting applications or services. This software determines which processor or system has the most available capacity and routes the workload to that computing resource. Representative vendors and products include the following:\
     HPE Serviceguard\
     IBM PowerHA SystemMirror (formerly IBM HACMP)\
     Microsoft Windows Server 2008 Failover Clustering (formerly Microsoft Cluster Service [MSCS])\
     IBM (Platform Computing's LSF)\
     Symantec Veritas Cluster Server (VCS)\
    Virtual Client Computing\
    IDC defines the virtual client computing (VCC) functional market as a client computing model that leverages a range of brokering software and display protocols to enable server-based client computing and improve upon the limitations associated with the traditional distributed desktop environment. The VCC market includes products that enable centralized virtual desktop, virtual user session, and other forms of client virtualization, to include type 2 hypervisor, containerized, and cloud-based solutions for delivering virtualized desktops and applications.\
    Representative vendors and products include the following:\
     Citrix's XenDesktop, XenApp, and XenClient\
     Microsoft's App-V, Remote Desktop Services, and RemoteApp  VMware's Horizon View, Fusion, and Horizon Air\
     Ericom's Connect"))
    taxonomySort.categories[0].subCategories[17].addNewCategory("Virtual client computing")
    taxonomySort.categories[0].subCategories[17].subCategories[2].addText(ratioCreator("Virtual machine software (VMS), also known today as hypervisor software, uses low-level capabilities offered by certain hardware environments or installs a complete hardware emulation layer using software to support multiple operating environments and the related stacks of applications, application development and deployment software, and system infrastructure software. This segmentation is often referred to as server virtualization or partitioning. Hypervisors also increasingly serve as the foundational infrastructure software for public and private clouds.\
    Representative vendors and revenue-generating products include the following:\
     Citrix XenServer (portions thereof)\
     IBM (PowerVM)\
     Microsoft Hyper-V (included with Windows Server)\
     Oracle VM for x86, Oracle VM for SPARC, Oracle Solaris Kernel Zones  Red Hat Enterprise Virtualization (portions thereof)\
     VMware vSphere\
    Container Engine Software\
    Software containers are an operating system virtualization technology, similar in concept to hypervisors except they abstract an OS instead of server hardware. Each application is presented with a pristine virtual copy of the OS, and the application is made to believe that it is the only application installed and running on that OS. An application and its immediate dependencies are packaged into a container file. Optionally, various OS user-space tools and libraries may also be included.\
    The core container virtualization and execution software technology is allocated into two primary system software markets. The operating system kernel is responsible for handling the basic isolation that makes containers possible and is an inherent feature of the operating system. This revenue is recognized within the existing operating systems and subsystems (OSS) market.\
    Container engine software is responsible for packaging/building the container, implementing the kernel container isolation features, and then unpacking and executing the container as needed. Representative vendors with revenue-generating products include the following:\
     Canonical (LXD)\
     CoreOS Rkt (as part of CoreOS and CoreOS Tectonic)\
     Docker Engine (as part of Docker Datacenter, Docker Universal Control Plane)  Microsoft Windows Containers (as part of Windows Server)\
     Red Hat Atomic Host\
     Oracle Solaris Native Zones\
     Virtuozzo (portions thereof)\
     VMware's Integrated Containers, Photon OS, and Photon Machine\
    Cloud System Software\
    Cloud system software represents a tightly bundled combination of server abstraction software and node-level controller software, often sold as part of a larger cloud infrastructure platform solution. The compute resource layer represents a combination of virtual machine, container engine, and/or operating system software running on a physical server, which is designated as a cloud compute node. The controller software virtualizes groups of compute nodes into a single logical compute resource. Cloud system software also exposes APIs that simplify the scheduling and control of VMs, containers, and bare metal servers running on the node and maintains a database of resource state and policies.\
    Representative vendors and revenue-producing products that include cloud system software are:\
     Accelerite CloudPlatform, based on CloudStack (acquired from Citrix)  Canonical Ubuntu OpenStack (portions thereof)\
     HPE Helion OpenStack and Helion Eucalyptus (portions thereof)\
     IBM Cloud Manager with OpenStack (portions thereof)\
     Microsoft Azure Stack (portions thereof)\
     Mirantis OpenStack (portions thereof)\
     Oracle OpenStack (portions thereof)\
     Red Hat OpenStack Platform (portions thereof)  SUSE Cloud (portions thereof)\
     VMware (VMware Integrated OpenStack, vCloud Director)"))
    taxonomySort.categories[0].subCategories[17].addNewCategory("Software-defined compute software")
    taxonomySort.categories[0].subCategories[17].subCategories[3].addText(ratioCreator("Software-defined compute (SDC) software encompasses a number of compute abstraction technologies that are implemented at various layers of the system software stack. These software technologies are often used in the context of public or private clouds but can also be implemented in noncloud environments, particularly virtualized environments.\
    Commercial solutions today increasingly offer SDC software bundled with other infrastructure software, management software, and application platforms. Software-defined compute software revenues reported in the IDC Software Tracker are limited to SDC license, subscription, and maintenance revenues. Self-supported open source does not generate revenue in IDC's Software Tracker markets but does generate shipment numbers, which may be tracked elsewhere. Suites that bundle multiple products together may allocate revenue to multiple functional markets with only portions of the product's revenue being allocated to SDC."))
    taxonomySort.categories[0].subCategories[17].addNewCategory("Other system software")
    taxonomySort.categories[0].subCategories[17].subCategories[4].addText(ratioCreator("Other system software is infrastructure software for systems and applications (but not storage) that is not otherwise categorized. Such software is used mainly by system programmers and administrators to perform housekeeping functions and add functions to operating systems that are not otherwise supplied. Examples include file conversion utilities, screen drivers and fonts, remote control software, and sort utilities. This category also includes enterprise connectivity software that enables devices to exchange, modify, and/or present host-based network data. Representative vendors and products include the following:\
     Adobe (Fonts)\
     EMC/Softworks (Catalog Solution)\
     IBM (Communications Server and WebSphere Host Integration and WebSphere Edge Server)  Microsoft (Host Integration Server)\
     Symantec (Norton Utilities)\
     TeamViewer (TeamViewer)\
     LogMeIn (Rescue, Central, Pro, and join.me)"))

    return taxonomySort
