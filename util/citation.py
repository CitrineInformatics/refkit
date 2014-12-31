"""
Functions for working with full citation strings.
"""

import re

# Regular expression to find all non alphanumeric characters
_subRegex = re.compile('\W')

def overlap(lookup, citation):
    """
    Break the string lookup into words then determine the number of those words that appear in citation. Returns the
    ratio of the number of words found in citation to the number of words in lookup.
    
    :param lookup: String being search for
    :param citation: Full citation string
    :returns: Ratio of the number of words from lookup found in citation to the number of words in lookup
    """
    wordsInLookup   = _subRegex.sub(' ', lookup  ).lower().split()
    wordsInCitation = _subRegex.sub(' ', citation).lower().split()
    matches = [ 1 if i in wordsInCitation else 0 for i in wordsInLookup ]
    return float(sum(matches)) / len(wordsInLookup)
