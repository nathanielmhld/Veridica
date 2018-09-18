from src import coUtils, convertTaxonomy, utils
import os
import pickle


"""***********************************************************************************"""
"""                           Software Initialization                                 """
"""***********************************************************************************"""


taxonomySort = convertTaxonomy.taxonomySort
curr_dir = os.getcwd()

if not os.path.exists(curr_dir + os.sep + "output"):
    os.makedirs(curr_dir + os.sep + "output")
with open(os.getcwd() + os.sep + 'data' + os.sep + "sort.pkl", 'ab') as f:
    pickle.dump(taxonomySort, f)
coList = [coUtils.Co(name = "<INITIAL>", website = "<INITIAL>")]
utils.savenpyfile(coList)

coList = coUtils.excelToCo(curr_dir + os.sep + "data", excel_file_name = 'cloudshare.xlsx')
#caution, excelToCo will create malformed secondary markets that need to be cleaned
#here
for co in coList:
    if taxonomySort.findCategory(co.secondary) == None and co.secondary != None:
        oldCat = co.secondary
        for secCat in taxonomySort.categories[0].subCategories:
            if secCat.name in co.secondary:
                co.secondary = secCat.name
        if oldCat == co.secondary:
            co.secondary = None


utils.createOutCSV(coList)
