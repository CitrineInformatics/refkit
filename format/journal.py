"""
Functions for working with journal names.
"""

import re
import pickle
import os.path

# Variables to hold abbreviations
_abbrDir      = os.path.abspath(os.path.join(os.path.dirname(__file__), 'abbr'))
_journals     = pickle.load(open(os.path.join(_abbrDir, 'journals.p')))
_infixes      = pickle.load(open(os.path.join(_abbrDir, 'infixes.p')))
_prefixes     = pickle.load(open(os.path.join(_abbrDir, 'prefixes.p')))
_suffixes     = pickle.load(open(os.path.join(_abbrDir, 'suffixes.p')))
_replacements = pickle.load(open(os.path.join(_abbrDir, 'replacements.p')))

def getAbbreviation(name):
    """
    Generate the abbreviated form of a journal name.
    
    :param name: Full name of the journal to abbreviate
    :returns: Abbreviated form of the journal name
    """
    try:
        return _getJournalAbbreviation(name)
    except Exception:
        res = []
        parts = name.split(':')
        for i in parts:
            res.append(_abbreviateSubtitle(i, i is parts[0]))
        return ': '.join(res)

def _getJournalAbbreviation(name):
    """
    Check if the name of the journal is recognized.
    
    :param name: Name of the journal to abbreviate
    :raises: ValueError if name is not in the abbreviated journal dictionary
    :returns: Abbreviated form of name
    """
    try:
        return _journals[re.sub('[\W]', '', name.lower())]
    except Exception:
        raise

def _abbreviateSubtitle(name, checkForJournal):
    """
    Generate the abbreviated form of a journal subtitle.
    
    :param name: Full subtitle of the journal to abbreviate
    :param checkForJournal: True to check for journal name. False otherwise
    :returns: Abbreviated form of the journal subtitle
    """
    if checkForJournal:
        try:
            return _getJournalAbbreviation(name)
        except Exception:
            pass
    res = []
    parts = name.split('-')
    for i in parts:
        res.append(_abbreviateParts(i, True))
    return '-'.join(res)

def _abbreviateParts(name, forcePrintFirst):
    """
    Generate the abbreviated form of part of a journal title.
    
    :param name: Part of the journal name to abbreviate
    :param forcePrintFirst: True to force the first item to be printed. False otherwise.
    :returns: Abbreviated form of the journal name
    """
    res = []
    parts = name.split()
    for i in parts:
        try:
            res.append(_abbreviateWord(i).title())
        except Exception,e:
            if i is parts[-1] or (forcePrintFirst and i is parts[0]):
                res.append(i.title())
    return ' '.join(res)

def _abbreviateWord(name):
    """
    Abbreviate a single word.
    
    :param name: Word to abbreviate
    :raises: KeyError if an abbreviation is not available
    :returns: Abbreviated form of name
    """
    lowercaseName = name.lower()
    res = _getFullReplacement(lowercaseName)
    if res is None:
        res = _getPrefixReplacement(lowercaseName)
    if res is None:
        res = _getSuffixReplacement(lowercaseName)
    if res is None:
        res = _getInfixReplacement(lowercaseName)
    if res is None:
        raise KeyError('Abbreviation not available')
    return res if res.rstrip('.').lower() != lowercaseName else name

def _getFullReplacement(name):
    """
    Get the abbreviation for a full replacement of a string.
    
    :param name: Lowercase copy of the name to replace
    :returns: Abbreviation for name or None if not found
    """
    return _replacements.get(name, None)

def _getPrefixReplacement(name):
    """
    Get the abbreviation for a replacement of the prefix of a string.
    
    :param name: Lowercase copy of the name to replace
    :returns: Abbreviation for name or None if not found
    """
    for i in range(len(name), -1, -1):
        try:
            replacement = _prefixes[name[:i]]
            return replacement
        except Exception:
            pass
    return None

def _getSuffixReplacement(name):
    """
    Get the abbreviation for a replacement of the suffix of a string.
    
    :param name: Lowercase copy of the name to replace
    :returns: Abbreviation for name or None if not found
    """
    for i in range(0, len(name) + 1):
        try:
            replacement = _suffixes[name[i:len(name)]]
            return name[:i] + replacement
        except Exception:
            pass
    return None

def _getInfixReplacement(name):
    """
    Get the abbreviation for a replacement of the infix of a string.
    
    :param name: Lowercase copy of the name to replace
    :returns: Abbreviation for name or None if not found
    """
    for i in range(len(name), -1, -1):
        end = len(name) - i
        for j in range(0, end + 1):
            try:
                replacement = _infixes[name[j:i+j]]
                return name[:j] + replacement
            except Exception:
                pass
    return None
