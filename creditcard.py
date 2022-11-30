import re
from PyPDF2 import PdfReader
from enum import Enum
from collections import defaultdict
import constant
import catfile
from lib import util


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


# Returns bool whether Date pattern is found in s
def PatternFound(pattern, s):
    found = re.search(pattern, s)
    if found:
        return True
    else:
        return False


# --------------------------------------------------------------------------------------

reader = PdfReader("statements/dbswomen/november2022.pdf")

count = 0
expList = []
categoryMap = defaultdict(int)
subcategoryMap = defaultdict(int)

for page in reader.pages[0:]:
    pageLines = page.extract_text().split("\n")

    # If page = THIS PAGE IS INTENTIONALLY LEFT, break
    if 'THIS PAGE IS INTENTIONALLY LEFT' in pageLines[0]:
        break

    regexp = re.compile(constant.entryPattern)

    for line in pageLines:
        print(line + "\n")
        # Ensure that line is an entry that matches pattern "24 SEP ___"
        # as well as not '31 DEC 2022', a random pattern found
        if util.is_pattern_in_text(CreditCardPatterns.Date.value, line) and line != '31 DEC 2022':
            exp = ParseExpenditure(line)
            # if exp:
            #     expList.append(line)

# for exp in expList:
#     categoryMap[exp.category] += round(exp.amount)
#     subcategoryMap[exp.subcategory] += round(exp.amount)
#
#     if exp.category == Category.TRANSPORT.name:
#         print(exp.name, exp.amount)
#
# print(categoryMap)
