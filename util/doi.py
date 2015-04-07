"""
Functions for working with DOI strings.
"""

import re

def extract(value):
    """
    Attempt to extract a DOI from a string by checking for common formatting types.
    
    :param value: String to extract DOI from
    :raises ValueError: If value does not contain a DOI
    :returns: String with the DOI that was extracted
    """
    matches = _doiRegex.finditer(value)
    for i in matches:
        if _validateStart(value, i):
            return i.group('doi').rstrip('-./')
    raise ValueError('DOI could not be extracted from string')

def _validateStart(value, match):
    """
    Make sure that the characters preceding a DOI number do not invalidate the match. The match is considered to
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

# Regular expression for matching a DOI
# This looks for patterns starting with '10.', followed by a series of integers and periods, followed by a backslash,
# followed by a series of alphanumeric values, backslashes, periods, parentheses, and hyphens. The matching string is
# saved in a group named 'doi'.
_doiRegex = re.compile('(?P<doi>10\.[0-9\.]+/\S+)(?!\w)')
