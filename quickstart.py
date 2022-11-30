from googleapiclient.discovery import build
import pprint
import re

import credentials


def iterate_all(iterable, returned="value"):
    """Returns an iterator that returns all keys or values
       of a (nested) iterable.

       Arguments:
           - iterable: <list> or <dictionary>
           - returned: <string> "key" or "value"

       Returns:
           - <iterator>
    """

    if isinstance(iterable, dict):
        for key, value in iterable.items():
            if returned == "key":
                yield key
            elif returned == "value":
                if not (isinstance(value, dict) or isinstance(value, list)):
                    yield value
            else:
                raise ValueError("'returned' keyword only accepts 'key' or 'value'.")
            for ret in iterate_all(value, returned=returned):
                yield ret
    elif isinstance(iterable, list):
        for el in iterable:
            for ret in iterate_all(el, returned=returned):
                yield ret


def google_search(search_term, api_key, cse_id, **kwargs):
    service = build("customsearch", "v1", developerKey=api_key)
    res = service.cse().list(q=search_term, cx=cse_id, **kwargs).execute()
    return res['items']


results = google_search('KITH - MILLENIA WALK', credentials.my_api_key, credentials.my_cse_id, num=10)

result_list = []
for i in iterate_all(results):
    result_list.append(i)

# -------------------------------------------------------------------------------------------------------------

import collections
import pandas as pd
import matplotlib.pyplot as plt
# Read input file, note the encoding is specified here
# It may be different in your text file
a = " ".join(result_list)
# Stopwords
stopwords = set(line.strip() for line in open('stopwords.txt'))
stopwords = stopwords.union(set(['mr', 'mrs', 'one', 'two', 'said']))
# Instantiate a dictionary, and for every word in the file,
# Add to the dictionary if it doesn't exist. If it does, increase the count.
wordcount = {}
# To eliminate duplicates, remember to split by punctuation, and use case demiliters.
for word in a.lower().split():
    # word = word.replace(".", "")
    # word = word.replace(",", "")
    # word = word.replace(":", "")
    # word = word.replace("\"", "")
    # word = word.replace("!", "")
    # word = word.replace("â€œ", "")
    # word = word.replace("â€˜", "")
    # word = word.replace("*", "")
    # word = word.replace("-", "")
    # word = word.replace(" ", "")
    # word = word.replace("@", "")
    # word = word.replace("·", "")
    # word = word.replace("|", "")
    # word = word.replace("<b>", "")
    # word = word.replace("</b>", "")
    # word = word.replace("&", "")
    # word = word.replace("#", "")
    # word = word.replace("?", "")
    # word = word.replace("(", "")
    # word = word.replace(")", "")
    # word = re.sub(r'\W', "", word, count=0, flags=0)

    if word not in stopwords:
        if word not in wordcount:
            wordcount[word] = 1
        else:
            wordcount[word] += 1
# Print most common word
print("The 10 most common words are as follows\n")
word_counter = collections.Counter(wordcount)
del word_counter[""]
print(word_counter.keys())
for word, count in word_counter.most_common(10):
    if word == "":
        continue
    print(word, ": ", count)

