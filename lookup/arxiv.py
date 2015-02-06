"""
Functions for working with the arXiv.org api.
"""

import urllib
import requests
from xml.etree       import ElementTree
from refkit.util     import arxivid
from refkit.metadata import Metadata
from refkit.format   import author

def search(lookup):
    """
    Search for a reference on arXiv.org given a lookup string. Since the arXiv.org api can return mutiple references
    for a single query, this function raises an error in the case that more than one reference was returned.
    
    :param lookup: String with the lookup to search for on arXiv.org
    :raises ValueError: If a reference with the specified lookup could not be found on arXiv.org
    :returns: Metadata object with information about the reference that was identified
    """
    try:
        id = arxivid.extract(lookup)
        arxivData = _getMetadataFromArxivId(id)
        return _saveMetadata(arxivData)
    except Exception:
        raise ValueError('Could not match query to arXiv')

def _getMetadataFromArxivId(id):
    """
    Get metadata from arXiv.org given an arXiv identifier.
    
    :param id: arXiv identifier to look up
    :returns: Result from arXiv api query
    """
    url = 'http://export.arxiv.org/api/query?id_list=' + id + '&start=0&max_results=2'
    return requests.get(url)

def _saveMetadata(data):
    """
    Convert the results of an arXiv api call to a Metadata object.
    
    :param data: Results of the arXiv api call
    :raises: ValueError if the metadata could not be saved
    :returns: Metadata object with the content of data
    """
    try:
        root = ElementTree.fromstring(data.content)
        entry = _getEntry(root)
        return _saveMetadataFromEntry(entry)
    except Exception:
        raise

def _getEntry(root):
    """
    Get the node in the xml data that contains the result from the query to save. If multiple entries are found
    in the query result, this function raises an error.
    
    :param root: Root of the XML data from the arXiv query
    :raises: ValueError is the entry cannot be extracted from the XML data
    :returns: Node that contains the results from the query
    """
    entry = None
    for i in root:
        if i.tag.endswith('entry'):
            if entry is not None:
                raise ValueError('Multiple entries in result')
            entry = i
    return entry

def _saveMetadataFromEntry(entry):
    """
    Save the metadata from an entry returned by an arXiv query.
    
    :param entry: Entry from which to save metadata
    :returns: Metadata object with the results in the entry
    """
    metadata = Metadata()
    metadata.publisher = 'arXiv.org'
    _saveValue(metadata, 'title', entry, 'title')
    _saveValue(metadata, 'url',   entry, 'id')
    _saveValue(metadata, 'doi',   entry, 'doi')
    _saveYear(metadata, entry)
    _saveAuthors(metadata, entry)
    metadata.tidy()
    return metadata

def _saveValue(metadata, attribute, entry, tag):
    """
    Extract a value from an XML object and save it in a Metadata object.
    
    :param metadata: Metadata object to save the value in
    :param attribute: Name of the attribute to save the value as in metadata
    :param entry: XML entry with the value to save
    :param tag: Tag of the value in entry to save
    """
    for i in entry:
        if i.tag.endswith(tag):
            try:
                setattr(metadata, attribute, i.text)
            except Exception,e:
                pass
            break

def _saveYear(metadata, entry):
    """
    Extract the year in which the article was last updated. arXiv api query results include both the published and
    updated dates. This function saves the updated year.
    
    :param metadata: Metadata object to save the year in
    :param entry: XML entry with the value to save
    """
    for i in entry:
        if i.tag.endswith('updated'):
            try:
                setattr(metadata, 'year', i.text.split('-')[0])
            except Exception:
                pass
            break

def _saveAuthors(metadata, entry):
    """
    Extract the authors from an XML object and convert them to given and family names.
    
    :param metadata: Metadata object to save the authors in
    :param entry: XML entry with the authors to save
    """
    for i in entry:
        if i.tag.endswith('author'):
            try:
                metadata.author.append(_getName(i))
            except Exception:
                pass

def _getName(entry):
    """
    Extract the name for an XML object.
    
    :param entry: XML entry with the name to save
    :raises: ValueError if a name cannot be found
    :returns: Dictionary with the given and family name in the entry
    """
    for i in entry:
        if i.tag.endswith('name'):
            try:
                return author.splitName(i.text)
            except Exception:
                raise
