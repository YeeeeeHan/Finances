import re
from PyPDF2 import PdfReader
from enum import Enum
from collections import defaultdict
import constant
import catfile
from lib import util
from quickstart import GoogleSearch

import pdfplumber
import pandas as pd

# Settings
GoogleSearchUnknownCategory = False
PrintSearchResults = False
PrintLines = True
PrintPandas = True
ToCSV = False
BuildAggregates = True



class CreditCardPatterns(Enum):
    Date = r'\d{1,2} (JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)'
    Amount = r'\d{1,3}(,\d{3})*(\.\d+)'


class CreditCardExpenditure:
    def __init__(self):
        self.name = ""
        self.date = ""
        self.amount = 0
        self.category = None
        self.keyword = None


def DetermineCategory(str):
    for cat in list(catfile.Category):
        for keyword in cat.value:
            if keyword.lower() in str.lower():
                return cat.name, keyword

    return None, None


def ParseExpenditure(line):
    newExp = CreditCardExpenditure()
    if not line:
        return

    # Get Date
    newExp.date = util.retrieve_pattern_from_text(CreditCardPatterns.Date.value, line)
    # Get Amount
    newExp.amount = util.retrieve_pattern_from_text(CreditCardPatterns.Amount.value, line)
    # Get Name
    _line = util.del_pattern_from_text(CreditCardPatterns.Date.value, line)
    newExp.name = util.del_pattern_from_text(CreditCardPatterns.Amount.value, _line)

    # Get Cat and subCat
    newExp.category, newExp.keyword = DetermineCategory(newExp.name)
    if newExp.category is None and GoogleSearchUnknownCategory:
        keywords = GoogleSearch(newExp.name)
        newExp.keyword = keywords
        if PrintSearchResults:
            print(f"SEARCH RESULTS: ExpName: {newExp.name} | Category: {newExp.category} | Keyword: {newExp.keyword} | GoogleTerms: {keywords}")

    return newExp


def CreateEntry(exp):
    entry = pd.DataFrame.from_dict({
        "date": [exp.date],
        "name": [exp.name],
        "amount": [exp.amount],
        "category": [exp.category],
        "keyword": [exp.keyword],
    })
    return entry


# --------------------------------------------------------------------------------------

document_folder = "statements/hsbcrevolution/"
# document_folder = "statements/dbswomen/"
document_name = "november2022"
document_link = document_folder + document_name + ".pdf"

# Pandas
df = pd.DataFrame(columns=["date", "name", "amount", "category", "keyword"])

expList = []
categoryMap = defaultdict(int)
newTransactions = True
with pdfplumber.open(document_link, password="16Jun1996160338") as pdf:
    for page in pdf.pages:
        text = page.extract_text()
        pLines = text.splitlines()
        for line in pLines:
            print(line)
            if line == "NEW TRANSACTIONS LIM YEE HAN":
                newTransactions = True
            if "STATEMENT ADJUSTED EXPIRED" in line:
                newTransactions = False

            # Ensure that line is an entry that matches pattern "24 SEP ___"
            if newTransactions and util.is_pattern_in_text(CreditCardPatterns.Date.value, line):
                exp = ParseExpenditure(line)
                expList.append(exp)
                entry = CreateEntry(exp)
                df = pd.concat([df, entry], ignore_index=True)

                if PrintLines:
                    print(f"Date:{exp.date} | Name:{exp.name} | Amount:{exp.amount}")

# Pretty print pandas
if PrintPandas:
    from tabulate import tabulate
    print(tabulate(df, headers='keys', tablefmt='psql'))

# To CSV
if ToCSV:
    df.to_csv(document_folder + "/outputs_" + document_name + ".csv")

# Build aggregates
if BuildAggregates:
    for exp in expList:
        categoryMap[exp.category] += round(float(exp.amount))
    print(categoryMap)
