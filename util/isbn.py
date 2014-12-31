"""
Functions for working with ISBN strings.
"""

import re

def extract(value):
    """
    Attempt to extract an ISBN from a string by checking for common formatting types.
    
    :param value: String to extract ISBN from
    :raises ValueError: If value does not contain a ISBN
    :returns: String with the ISBN that was extracted
    """
    value = value.replace('-', '')
    matches = _isbnRegex.finditer(value)
    for i in matches:
        if _validateStart(value, i) and _validateEnd(value, i):
            return i.group('id')
    raise ValueError('ISBN could not be extracted from string')

def _validateStart(value, match):
    """
    Make sure that the characters preceding an ISBN number do not invalidate the match. The match is considered to
    be invalid if it is preceded by any alphanumeric character.
    
    :param value: String that was being searched
    :param match: MatchObject returned from regular expression function
    :returns: True if characters before match are valid
    :returns: False if characters before match are not valid
    """
    if match.start() > 0:
        preString = value[match.start()-1:match.start()]
        if re.match('\w', preString) is not None:
            return False
    return True

def _validateEnd(value, match):
    """
    Make sure that the characters preceding an ISBN number do not invalidate the match. The match is considered to
    be invalid if it is followed by any alphanumeric character.
    
    :param value: String that was being searched
    :param match: MatchObject returned from regular expression function
    :returns: True if characters before match are valid
    :returns: False if characters before match are not valid
    """
    if match.end() < len(value):
        postString = value[match.end():match.end()+1]
        if re.match('\w', postString) is not None:
            return False
    return True

# Regular expression for case-insensitive match to 'isbn:'
_isbnRegex = re.compile('(?P<id>[0-9]{13}|[0-9]{10})')
