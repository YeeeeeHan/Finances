import re


def del_pattern_from_text(regex_pattern, text):
    _text = text
    _text = re.sub(regex_pattern, '', _text)

    return _text


def retrieve_pattern_from_text(regex_pattern, text):
    found = re.search(regex_pattern, text, re.IGNORECASE)
    if found:
        return found.group(0)


def is_pattern_in_text(regex_pattern, text):
    regexp = re.compile(regex_pattern)
    return regexp.search(text)
