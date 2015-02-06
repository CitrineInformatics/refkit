"""
Functions for working with the CrossRef.org rest api.
"""

import re
import sys
import urllib
import requests
import unicodedata
from operator        import itemgetter
from refkit.util     import doi
from refkit.util     import isbn
from refkit.util     import citation
from refkit.metadata import Metadata

# Default minimum value for overlap score to be valid without user intervention
defAutoSaveMinimum = 0.99

# Default maximum ratio of the second best to best overlaps for a result to be valid without user intervention
defAutoSaveMaximum = 0.7

def search(lookup, autoSaveMinimum = defAutoSaveMinimum, autoSaveMaximum = defAutoSaveMaximum):
    """
    Search for a reference on CrossRef.org given a lookup string. This function goes through the following steps in
    order to find a match:
    (1) Search the lookup string for a DOI. If one is found, then use that to obtain the reference metadata. If a DOI
        is not found, then continue to (2).
    (2) Use the lookup string as a query against the CrossRef.org search api. Results obtained from this query are
        processed in the following steps.
    [2.1] Rank the results by the number of words from lookup that appear in the citation string of each result.
    [2.2] If only one result is found then return it if the result of [2.1] is greater than autoSaveMinimum.
    [2.3] If only one result is found and [2.2] is not true, then prompt the user to decide if the result is valid.
    [2.4] If multiple results are found, return the best one if the result of [2.1] is greater than autoSaveMinimum
          and the ratio of the second best result from [2.1] the best one is less than autoSaveMaximum.
    [2.5] If multiple results are found and [2.4] is not true, then prompt the user to decide which result is
          the best one.
    
    :param lookup: String with the lookup to search for on CrossRef.org
    :param autoSaveMinimum: Minimum value for overlap score to be valid without user intervention (0 - 1)
    :param autoSaveMaximum: Maximum ratio of the second best to best overlaps for a result to be valid without
                            user intervention (0 - 1)
    :raises ValueError: If a reference with the specified lookup could not be found on CrossRef.org
    :returns: Metadata object with information about the reference that was identified
    """
    try:
        try:
            lookup = unicodedata.normalize('NFKD', lookup).encode('ascii', 'ignore')
        except:
            pass
        lookupDoi = _getDoi(lookup, autoSaveMinimum, autoSaveMaximum)
        crossRefData = _getMetadataFromDoi(lookupDoi)
        return _saveMetadata(crossRefData)
    except Exception, e:
        raise

def _getMetadataFromDoi(lookupDoi):
    """
    Lookup a citation by DOI. The DOI does not need to be formatted.

    :param lookupDoi: String with the DOI to search for
    :raises ValueError: If the DOI could not be found on CrossRef.org
    :returns: Dictionary with information that was obtained from CrossRef.org for the citation with the set DOI
    """
    try:
        rawDoi = doi.extract(lookupDoi)
        url = 'http://api.crossref.org/works/' + rawDoi
        return requests.get(url).json()
    except Exception:
        raise

def _getDoi(lookup, autoSaveMinimum, autoSaveMaximum):
    """
    Get the DOI for a lookup string.
    
    :param lookup: String with the lookup to search for on CrossRef.org
    :param autoSaveMinimum: Minimum value for overlap score to be valid without user intervention (0 - 1)
    :param autoSaveMaximum: Maximum ratio of the second best to best overlaps for a result to be valid without
                            user intervention (0 - 1)
    :raises ValueError: If a DOI could not be obtained for the lookup string
    :returns: DOI for the lookup string
    """
    try:
        resDoi = doi.extract(lookup)
        return resDoi
    except Exception:
        pass
    try:
        resDoi = _getDoiForCitation(lookup, autoSaveMinimum, autoSaveMaximum)
        return resDoi
    except Exception, e:
        raise

def _getDoiForCitation(lookup, autoSaveMinimum, autoSaveMaximum):
    """
    Search CrossRef.org for a given citation.
    
    :param lookup: String with the lookup to search for on CrossRef.org
    :param autoSaveMinimum: Minimum value for overlap score to be valid without user intervention (0 - 1)
    :param autoSaveMaximum: Maximum ratio of the second best to best overlaps for a result to be valid without
                            user intervention (0 - 1)
    :raises ValueError: If a DOI could not be obtained for the lookup string
    :returns: DOI for the lookup string
    """
    try:
        queryResults = _runQuery(lookup)
        try:
            bestResult = _getBestQueryResult(lookup, queryResults, autoSaveMinimum, autoSaveMaximum)
            return doi.extract(bestResult['doi'])
        except Exception, e:
            raise ValueError('Could not match citation to DOI')
    except Exception:
        raise

def _runQuery(value):
    """
    Run a free-form query.

    :param value: String with the citation to search for
    :returns: Dictionary with the results of the query
    """
    try:
        lowercaseCitation = value.lower()
        formattedCitation = urllib.quote_plus(lowercaseCitation)
        url = 'http://search.crossref.org/dois?q=' + formattedCitation + '&sort=score&page=1&rows=10'
        return requests.get(url).json()
    except Exception:
        raise

def _getBestQueryResult(lookup, queryResults, autoSaveMinimum, autoSaveMaximum):
    """
    Analyze results from a free-form query to determine the best match that was found.
    
    :param lookup: String with the lookup to search for on CrossRef.org
    :param queryResults: Json list with the query results to analyze
    :param autoSaveMinimum: Minimum value for overlap score to be valid without user intervention (0 - 1)
    :param autoSaveMaximum: Maximum ratio of the second best to best overlaps for a result to be valid without
                            user intervention (0 - 1)
    :returns: Best match that was found or None if a viable match was not found
    """
    results = [ (citation.overlap(lookup, i['fullCitation']), i) for i in queryResults ]
    results = sorted(results, key = itemgetter(0), reverse = True)
    if len(results) == 1 and results[0][0] >= autoSaveMinimum:
        return results[0][1]
    if len(results) > 1:
        if results[0][0] >= autoSaveMinimum and float(results[1][0]) / results[0][0] < autoSaveMaximum:
            return results[0][1]
    if len(results) > 0:
        return _askUserForBestResult(lookup, queryResults)
    return None

def _askUserForBestResult(lookup, queryResults):
    """
    Prompt the user to decide which in a list of query results is the correct match.
    
    :param lookup: String with the lookup to search for on CrossRef.org
    :param queryResults: Json list with the query results to analyze
    :returns: Best match that was supplied or None if a viable match was not found
    """
    while True:
        try:
            res = int(_promptForBestResult(lookup, queryResults))
            return None if res == 0 else queryResults[res - 1]
        except Exception:
            pass

def _promptForBestResult(lookup, queryResults):
    """
    Prompt the user to decide which in a list of query results is the correct match.
    
    :param lookup: String with the lookup to search for on CrossRef.org
    :param queryResults: Json list with the query results to analyze
    :returns: Value entered by the user
    """
    print ''
    print 'LOOKUP STRING: ' + lookup
    print 'QUERY RESULTS:'
    for i in range(len(queryResults)):
        print '[' + str(i + 1) + '] ' + queryResults[i]['fullCitation']
    try:
        return raw_input('ENTER NUMBER OF CORRECT RESULT (or 0 if no match): ')
    except KeyboardInterrupt:
        print ''
        sys.exit(1)

def _askForManualEntry(lookup):
    """
    Prompt the user to input the metadata themselves.
    
    :param lookup: String with the lookup being searched for.
    :returns: Object with the user entered information or None if they chose not to enter it.
    """

def _saveMetadata(data):
    """
    Extract and save the metadata from the dictionary returned from a CrossRef.org api call.
    
    :param data: Dictionary returned from a CrossRef.org api call
    :returns: Metadata object with information saved from the input dictionary
    """
    metadata = Metadata()
    message = data['message']
    _saveIsbn(metadata, message)
    _saveYear(metadata, message)
    _saveTitle(metadata, message)
    _savePages(metadata, message)
    _saveJournal(metadata, message)
    _saveValue(metadata, message, 'volume',          'volume')
    _saveValue(metadata, message, 'issue',           'issue')
    _saveValue(metadata, message, 'DOI',             'doi')
    _saveValue(metadata, message, 'ISSN',            'issn')
    _saveValue(metadata, message, 'URL',             'url')
    _saveValue(metadata, message, 'publisher',       'publisher')
    _saveNames(metadata, message, 'author',          'author')
    _saveNames(metadata, message, 'editor',          'editor')
    metadata.tidy()
    return metadata
    
def _saveValue(metadata, crossRefData, dictionaryKey, attributeName):
    """
    Save an attribute on metadata object if it exists in the dictionary.
    
    :param metadata: Metadata object to store results
    :param crossRefData: Dictionary returned from a CrossRef.org api call
    :param dictionaryKey: Key for the value to find in the dictionary
    :param attributeName: Name to assign to the attribute
    """
    try:
        value = crossRefData[dictionaryKey]
        if isinstance(value, list):
            setattr(metadata, attributeName, value[0])
        else:
            setattr(metadata, attributeName, value)
    except Exception:
        pass

def _saveIsbn(metadata, crossRefData):
    """
    Save the ISBN of a reference if it is available.
    
    :param metadata: Metadata object to store results
    :param crossRefData: Dictionary returned from a CrossRef.org api call
    """
    try:
        valuesToTest = crossRefData['ISBN']
        for i in valuesToTest:
            try:
                setattr(metadata, 'isbn', isbn.extract(i))
                return
            except Exception:
                pass
    except Exception:
        pass

def _saveYear(metadata, crossRefData):
    """
    Save the year of a reference if it is available.
    
    :param metadata: Metadata object to store results
    :param crossRefData: Dictionary returned from a CrossRef.org api call
    """
    try:
        setattr(metadata, 'year', str(crossRefData['issued']['date-parts'][0][0]))
    except Exception:
        pass

def _savePages(metadata, crossRefData):
    """
    Save start and end pages for a reference.
    
    :param metadata: Metadata object to store results
    :param crossRefData: Dictionary returned from a CrossRef.org api call
    """
    try:
        pages = crossRefData['page'].split('-')
        value = pages[0]
        if len(value) > 0:
            setattr(metadata, 'pageStart', value)
        value = pages[1]
        if len(value) > 0:
            setattr(metadata, 'pageEnd', value)
    except Exception:
        pass

def _saveTitle(metadata, crossRefData):
    """
    Save title for a reference.
    
    :param metadata: Metadata object to store results
    :param crossRefData: Dictionary returned from a CrossRef.org api call
    """
    title = []
    try:
        title.append(crossRefData['title'][0])
        title.append(crossRefData['subtitle'][0])
    except Exception:
        pass
    try:
        setattr(metadata, 'title', ': '.join(title))
    except Exception:
        pass

def _saveJournal(metadata, crossRefData):
    """
    Save the journal for a reference. This saves the journal with the longest name.
    
    :param metadata: Metadata object to store results
    :param crossRefData: Dictionary returned from a CrossRef.org api call
    """
    res = 0
    journals = crossRefData['container-title']
    for i in range(1, len(journals)):
        if len(journals[i]) > len(journals[res]):
            res = i
    try:
        setattr(metadata, 'journal', journals[res])
    except Exception:
        pass

def _saveNames(metadata, crossRefData, dictionaryKey, attributeName):
    """
    Save a list of authors to a metadata object if they exist in the dictionary.
    
    :param metadata: Metadata object to store results
    :param crossRefData: Dictionary returned from a CrossRef.org api call
    :param dictionaryKey: Key for the value to find in the dictionary
    :param attributeName: Name to assign to the attribute
    """
    try:
        names = crossRefData[dictionaryKey]
        setattr(metadata, attributeName, filter(len, [ _saveName(i) for i in names ]))
    except Exception:
        pass

def _saveName(name):
    """
    Put a name into a dictionary.
    
    :param name: Name to put into dictionary
    :returns: Dictionary with givenName and familyName
    """
    try:
        return {'givenName': name['given'], 'familyName': name['family']}
    except Exception:
        return {}
