import re
from PyPDF2 import PdfReader
from enum import Enum
from collections import defaultdict
import catfile


class Pattern(Enum):
    Date = "\d\d/\d\d/\d\d\d\d"
    Card = '\d\d\d\d-\d\d\d\d-\d\d\d\d-\d\d\d\d'
    Amount = '\d+\.\d\d'


class Mode(Enum):
    DEBIT_CARD_TRANSACTION = "Debit Card Transaction"
    FUNDS_TRANSFER = "Funds Transfer"
    GIRO = "GIRO"

class Expenditure:
    def __init__(self):
        self.name = None
        self.amount = 0
        self.mode = None
        self.category = None
        self.subcategory = None

    def HandleDebitCardTransaction(self, exp):
        # Handle amount
        str = exp[2]
        str = re.sub(Pattern.Card.value, "", str)
        res = re.findall(Pattern.Amount.value, str)
        self.amount = float(res[0])
        # print(exp)

        # Handle category
        cat, subcat = DetermineCategory(exp[1])
        if cat is None:
            pass
        return cat, subcat


def DetermineCategory(s):
    for cat in list(catfile.Category):
        for keyword in cat.value:
            if keyword in s.lower():
                return cat.name, keyword

    return None, None


def DetermineMode(s):
    if PatternFound(Mode.DEBIT_CARD_TRANSACTION.value, s):
        return Mode.DEBIT_CARD_TRANSACTION


def ParseExpenditure(exp):
    newExp = Expenditure()
    if not exp:
        return

    type = DetermineMode(exp[0])
    match type:
        case Mode.DEBIT_CARD_TRANSACTION:
            newExp.name = exp[1]

            newExp.mode = Mode.DEBIT_CARD_TRANSACTION.value
            cat, subcat = newExp.HandleDebitCardTransaction(exp)
            newExp.category = cat
            newExp.subcategory = subcat

    return newExp


# Returns an array of string that represents an expenditure object,
# given all the lines in a page and the current line number
def BuildExpenditure(lines, i):
    found = PatternFound(Pattern.Date.value, lines[i])
    exp = []
    if found:
        # Add Header line
        exp.append(lines[i])
        i += 1

        # Continue to iterate as long as not header line
        while i < len(lines) - 1 and not PatternFound(Pattern.Date.value, lines[i]):
            exp.append(lines[i])
            i += 1

        return exp

    else:
        return []


# Returns bool whether Date pattern is found in s
def PatternFound(pattern, s):
    found = re.search(pattern, s)
    if found:
        return True
    else:
        return False


reader = PdfReader("statements/debitcard/august2022.pdf")
text = ""

count = 0
expList = []
categoryMap = defaultdict(int)
subcategoryMap = defaultdict(int)

for page in reader.pages[1:]:
    lines = page.extract_text().split("\n")

    for i in range(len(lines)):
        exp = BuildExpenditure(lines, i)
        exp = ParseExpenditure(exp)
        if exp:
            expList.append(exp)

for exp in expList:
    categoryMap[exp.category] += round(exp.amount)
    subcategoryMap[exp.subcategory] += round(exp.amount)

    # if exp.category == catfile.Category.TRANSPORT.name:
    #     print(exp.name, exp.amount)

print(categoryMap)
