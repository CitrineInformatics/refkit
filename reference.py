"""
Functions for determining information about a referenced work.
"""

from refkit.lookup   import arxiv
from refkit.lookup   import crossref
from refkit.metadata import Metadata

from refkit.util.doi import extract

def getMetadata(input, autoSaveMinimum = crossref.defAutoSaveMinimum, autoSaveMaximum = crossref.defAutoSaveMaximum):
    """
    Gather metadata for a reference. In some cases it may be possible that multiple Metadata objects are returned.
    For example, if an arXiv reference is found, and it has a DOI associated with it, the metadata for the article
    with that DOI will also be returned. In all cases, the first item returned is the primary reference.
    
    :param input: String with the reference to extract metadata for
    :param autoSaveMinimum: Minimum value for overlap score to be valid without user intervention (0 - 1)
    :param autoSaveMaximum: Maximum ratio of the second best to best overlaps for a result to be valid without
                            user intervention (0 - 1)
    :returns: List of Metadata objects with the metadata that was gathered
    """
    return _getMetadataByLookup(input, autoSaveMinimum, autoSaveMaximum)

def _getMetadataByLookup(input, autoSaveMinimum, autoSaveMaximum):
    """
    Gather metadata for a reference by searching for information on lookup services.
    
    :param input: String with the reference to extract metadata for
    :param autoSaveMinimum: Minimum value for overlap score to be valid without user intervention (0 - 1)
    :param autoSaveMaximum: Maximum ratio of the second best to best overlaps for a result to be valid without
                            user intervention (0 - 1)
    :returns: List of Metadata objects with the metadata that was gathered
    """
    res  = _getMetadataFromArxiv(input)
    res += _getMetadataFromCrossref(input, res, autoSaveMinimum, autoSaveMaximum)
    return res

def _getMetadataFromArxiv(input):
    """
    Gather metadata for a reference from arXiv.org.
    
    :param input: String with the reference to extract metadata for
    :returns: Metadata object with the information that was gathered
    """
    try:
        return [ arxiv.search(input) ]
    except Exception:
        return []

def _getMetadataFromCrossref(input, existingMetadata, autoSaveMinimum, autoSaveMaximum):
    """
    Gather metadata for a reference from CrossRef.org. This function first tries to use metadata already gathered to
    search CrossRef.org, then uses the input string if metadata did not produce a result.
    
    :param input: String with the reference to extract metadata for
    :param existingMetadata: List of metadata objects already determined for input
    :param autoSaveMinimum: Minimum value for overlap score to be valid without user intervention (0 - 1)
    :param autoSaveMaximum: Maximum ratio of the second best to best overlaps for a result to be valid without
                            user intervention (0 - 1)
    :returns: Metadata object with the information that was gathered
    """
    for i in existingMetadata:
        try:
            return [ crossref.search(i.toUnformattedString(), autoSaveMinimum, autoSaveMaximum) ]
        except Exception, e:
            pass
    if len(existingMetadata) == 0:
        try:
            return [ crossref.search(input, autoSaveMinimum, autoSaveMaximum) ]
        except:
            pass
        return _promptForManualEntry(input)
    return []

def _promptForManualEntry(input):
    """
    Ask the user if they want to manual set the metadata for the object.
    
    :param input: String with the reference data being searched for.
    :returns: Metadata object with the information that was gathered or emtpy array.
    """
    print ''
    print 'LOOKUP STRING: ' + input
    return [] if _getResponse('Do you want to manually set the information [y/n]: ') == 'n' else _getDataFromUser()

def _getDataFromUser():
    """
    Ask the user whether they have a better lookup string.
    
    :returns: Metadata object with the information that was gathered or emtpy array.
    """
    print ''
    input = raw_input('Better lookup string: ')
    res = []
    if len(input) > 0:
        res = _getMetadataByLookup(input, crossref.defAutoSaveMinimum, crossref.defAutoSaveMaximum)
    if len(res) == 0:
        res = [ Metadata().getDataFromUser() ]
    return res

def _getResponse(message):
    """
    Get a y/n response from the user.
    
    :param message: Message to print to the user.
    :returns: Response from the user.
    """
    res = ''
    while res != 'y' and res != 'n':
        res = raw_input(message)
    return res
