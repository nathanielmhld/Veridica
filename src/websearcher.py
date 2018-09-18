from .utils import getColumnFromCSV
import itertools

import operator
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
#Make this into an object
#The object will hold
#  A) Past search information
#  B) Including how many searches have happened
#  C) A list of URLs of websites identified as non-company URLs




def GoogleSearchToDict(num_results, start_index, search_term, my_api_key, my_cse_id):
    def google_search(search_term, api_key, cse_id, start_index, num_results, **kwargs):
        # search_term (string): what are you searching for
        # api_key (string): api_key of api
        # cse_id (string):
        items = []
        num_calls = (num_results // 10) + 1
        service = build("customsearch", "v1", developerKey=api_key)
        maxed_out = False
        while num_calls > 0 and maxed_out is False:
            if num_calls == 1:
                numberofresults = num_results - ((num_results // 10) * 10)
                if numberofresults == 0:
                    break
            else:
                numberofresults = 10
            try:
                res = service.cse().list(q=search_term, cx=cse_id, num=numberofresults, start=start_index, **kwargs).execute()
            except HttpError:
                print("Max searches reached")
                maxed_out = True
                break
            else:
                num_calls -= 1
                start_index += 10
                items.extend(res['items'])
        return items, maxed_out
    results, maxed_out = google_search(search_term, my_api_key, my_cse_id, start_index, num_results)
    URLs = {}
    for result in results:
        URLs[result["link"]] = search_term
        print(result["link"])
    return URLs


