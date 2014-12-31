"""
Functions for working with author names.
"""

import re

def formatName(givenName, familyName, abbreviate = False, familyNameFirst = False):
    """
    Format the given (first) and family (last) names of a person. Optionally move the last name before the first.
    
    :param givenName: Given (first) name
    :param familyName: Family (last) name
    :param abbreviate: True to abbreviate the name. False otherwise
    :param familyNameFirst: True to return the family name before the first. False otherwise
    :returns: Formatted version of given and family names
    """
    formattedGivenName = formatGivenName(givenName, abbreviate)
    formattedFamilyName = formatFamilyName(familyName)
    if familyNameFirst:
        return formattedFamilyName + ', ' + formattedGivenName
    else:
        return formattedGivenName + ' ' + formattedFamilyName

def formatGivenName(name, abbreviate = False):
    """
    Format the given (first) name of a person.
    
    :param name: Name to format
    :param abbreviate: True to abbreviate the name. False otherwise
    :returns: Formatted version of the name
    """
    capitalizedName = re.sub('\s+', ' ', _capitalizeName(name, False).replace('.', '. ')).strip()
    return capitalizedName if not abbreviate else _abbreviateName(capitalizedName)

def formatFamilyName(name):
    """
    Format the family (last) name of a person.
    
    :param name: Name to format
    :returns: Formatted version of the name
    """
    return _capitalizeName(name, True)

def splitName(name):
    """
    Break a full name into the given name and family name.
    
    :param name: Full name to split into part
    :returns: Dictionary with the given name and family name separated
    """
    givenName, familyName = _splitNameIntoParts(name)
    return {'givenName': givenName, 'familyName': familyName}

def _capitalizeName(name, isFamilyName):
    """
    Format the name of a person.
    
    :param name: Name to format
    :param isFamilyName: True if name is a family name. False otherwise
    :returns: Formatted version of the name
    """
    res = []
    parts = name.split()
    for i in parts:
        res.append(_capitalizeHyphenatedName(i, isFamilyName))
    return ' '.join(res)

def _capitalizeHyphenatedName(name, isFamilyName):
    """
    Format the part of a name that may contain a hyphen. The input string should already have spaces removed.
    
    :param name: Name to format
    :param isFamilyName: True if name is a family name. False otherwise
    :returns: Formatted version of the name
    """
    res = []
    parts = name.split('-')
    for i in parts:
        if not i.isupper():
            res.append(i)
        elif isFamilyName:
            res.append(_setCapitalization(i))
        else:
            res.append(i.title())
    return '-'.join(res)

def _setCapitalization(name):
    """
    Set the capitalization of a name.
    
    :param name: Name to capitalize
    :returns: Capitalized version of the name
    """
    res = []
    parts = name.lower().split('\'')
    for i in parts:
        if i.find('mc') == 0:
            res.append('Mc' + i.lstrip('mc').title())
        elif i.find('mac') == 0:
            res.append('Mac' + i.lstrip('mac').title())
        else:
            res.append(i.title())
    return '\''.join(res)

def _abbreviateName(name):
    """
    Convert a name to be in abbreviated form.
    
    :param name: Name to abbreviate
    :returns: Abbreviated form of the name
    """
    res = []
    parts = name.split()
    for i in parts:
        res.append(_abbreviateHyphenatedName(i))
    return ' '.join(res)

def _abbreviateHyphenatedName(name):
    """
    Abbreviate the part of a name that may contain a hyphen. The input string should already have spaces removed.
    
    :param name: Name to abbreviate
    :returns: Abbreviated form of the name
    """
    res = []
    parts = name.split('-')
    for i in parts:
        res.append(_abbreviateAbbreviatedName(i))
    return '-'.join(res)

def _abbreviateAbbreviatedName(name):
    """
    Abbreviate the part of a name that may contain abbreviations. The input string should already have spaces and
    hyphens removed.
    
    :param name: Name to abbreviate
    :returns: Abbreviated form of the name
    """
    res = []
    parts = name.split('.')
    for i in parts:
        try:
            res.append(i[0] + '.')
        except Exception:
            pass
    return ' '.join(res)

def _splitNameAtComma(name):
    """
    Split a name at the first instance of a comma and return resulting parts.
    
    :param name: Name to split at comma
    :returns: List of parts of the name
    """
    return filter(len, [ i.strip() for i in name.split(',', 1) ])

def _splitNameIntoParts(name):
    """
    Split a name into given and family names.
    
    :param name: Name to split into parts
    :returns: Two values: Given name, Family name
    """
    parts = _splitNameAtComma(name)
    if len(parts) == 2:
        return parts[1], parts[0]
    else:
        return _splitNameByWords(name)

def _splitNameByWords(name):
    """
    Split a name into parts. It should have already been checked that the name does not contain a comma. In other
    words, it is expected that the given name comes before the family name in the input argument.
    
    :param name: Name to split into parts
    :returns: Two values: Given name, Family name
    """
    parts = name.split()
    if len(parts) == 0:
        return '', ''
    elif len(parts) == 1:
        return '', parts[0]
    elif len(parts) == 2:
        return parts[0], parts[1]
    else:
        return _identifyPartsOfName(parts)

def _identifyPartsOfName(parts):
    """
    Determine what the parts of a name are (given vs. family) when more than two items were found.
    
    :param parts: Individual words in the name
    :returns: Two values: Given name, Family name
    """
    try:
        return _splitNameByAbbreviations(parts)
    except Exception:
        return ' '.join(parts[:-1]), parts[-1]

def _splitNameByAbbreviations(parts):
    """
    If a name contains abbreviations, then split so that first name is abbreviated parts and last name is parts that
    are not abbreviated.
    
    :param parts: Individual words in the name
    :raises: ValueError if parts cannot be partitioned into given and family name
    :returns: Two values: Given name, Family name
    """
    if len(parts[0]) == 1 or parts[0].endswith('.'):
        for i in range(1, len(parts)):
            if len(parts[i]) > 1 and not parts[i].endswith('.'):
                return ' '.join(parts[:i]), ' '.join(parts[i:])
    raise ValueError('Could not split name on abbreviations')
