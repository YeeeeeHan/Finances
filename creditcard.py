import re
from PyPDF2 import PdfReader
from enum import Enum
from collections import defaultdict
import constant
import catfile
from lib import util

import pdfplumber
import pandas as pd


class CreditCardPatterns(Enum):
    Date = r'\d{1,2} (JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)'
    Card = '\d\d\d\d-\d\d\d\d-\d\d\d\d-\d\d\d\d'
    Amount = r'\d{1,3}(,\d{3})*(\.\d+)'


class Mode(Enum):
    DEBIT_CARD_TRANSACTION = "Debit Card Transaction"
    FUNDS_TRANSFER = "Funds Transfer"
    GIRO = "GIRO"


class CreditCardExpenditure:
    def __init__(self):
        self.name = ""
        self.date = ""
        self.amount = 0
        self.category = None
        self.subcategory = None


def DetermineCategory(s):
    for cat in list(catfile.Category):
        for keyword in cat.value:
            if keyword.lower() in s.lower():
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

    # Get cat and subCat
    newExp.category, newExp.subcategory = DetermineCategory(newExp.name)

    if newExp.category is None:
        pass
    return newExp


# --------------------------------------------------------------------------------------

document_folder = "statements/dbswomen/"
document_name = "november2022.pdf"
document_link = document_folder + document_name

# Pandas
df = pd.DataFrame(columns=["date", "name", "amount", "category", "subcategory"])

newTransactions = False
with pdfplumber.open(document_link) as pdf:
    for page in pdf.pages:
        text = page.extract_text()
        pLines = text.splitlines()
        for line in pLines:
            if line == "NEW TRANSACTIONS LIM YEE HAN":
                newTransactions = True
            if "STATEMENT ADJUSTED EXPIRED" in line:
                newTransactions = False

            # Ensure that line is an entry that matches pattern "24 SEP ___"
            # as well as not '31 DEC 2022', a random pattern found
            if newTransactions and util.is_pattern_in_text(CreditCardPatterns.Date.value, line):
                exp = ParseExpenditure(line)
                entry = pd.DataFrame.from_dict({
                    "date": [exp.date],
                    "name": [exp.name],
                    "amount": [exp.amount],
                    "category": [exp.category],
                    "subcategory": [exp.subcategory],
                })
                df = pd.concat([df, entry], ignore_index=True)

df.to_csv("output.csv")

# # Pretty print pandas
# from tabulate import tabulate
# print(tabulate(df, headers='keys', tablefmt='psql'))
