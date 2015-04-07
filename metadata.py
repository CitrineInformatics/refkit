"""
This file defines that general storage object for a reference.
"""

import re
from refkit.format import author
from refkit.format import journal
from refkit.util   import arxivid

class Metadata(object):
    """
    Class to store information about a reference.
    """
    
    def __init__(self, asDictionary = None):
        """
        Default constructor.
        """
        self.setDefaults()
        if asDictionary is not None:
            self.doi       = asDictionary.get('doi',       self.doi)
            self.isbn      = asDictionary.get('isbn',      self.isbn)
            self.issn      = asDictionary.get('issn',      self.issn)
            self.url       = asDictionary.get('url',       self.url)
            self.author    = asDictionary.get('author',    self.author)
            self.editor    = asDictionary.get('editor',    self.editor)
            self.publisher = asDictionary.get('publisher', self.publisher)
            self.title     = asDictionary.get('title',     self.title)
            self.edition   = asDictionary.get('edition',   self.edition)
            self.journal   = asDictionary.get('journal',   self.journal)
            self.volume    = asDictionary.get('volume',    self.volume)
            self.issue     = asDictionary.get('issue',     self.issue)
            self.year      = asDictionary.get('year',      self.year)
            self.pageStart = asDictionary.get('pageStart', self.pageStart)
            self.pageEnd   = asDictionary.get('pageEnd',   self.pageEnd)
    
    def setDefaults(self):
        """
        Set the default values for the member variables of this object.
        """
        self.doi       = ''
        self.isbn      = ''
        self.issn      = ''
        self.url       = ''
        self.author    = []
        self.editor    = []
        self.publisher = ''
        self.title     = ''
        self.edition   = ''
        self.journal   = ''
        self.volume    = ''
        self.issue     = ''
        self.year      = ''
        self.pageStart = ''
        self.pageEnd   = ''
    
    def getDataFromUser(self):
        """
        Set the content of this object based on information from the user.
        """
        self.getValueFromUser('doi')
        self.getValueFromUser('isbn')
        self.getValueFromUser('issn')
        self.getValueFromUser('url')
        self.getValueFromUser('publisher')
        self.getValueFromUser('title')
        self.getValueFromUser('edition')
        self.getValueFromUser('journal')
        self.getValueFromUser('volume')
        self.getValueFromUser('issue')
        self.getValueFromUser('year')
        self.getValueFromUser('pageStart')
        self.getValueFromUser('pageEnd')
        self.getPeopleFromUser('author')
        self.getPeopleFromUser('editor')
        return self
    
    def getValueFromUser(self, field):
        """
        Prompt the user for a field value.
        
        :param field: Name of the field to get from the user.
        """
        setattr(self, field, raw_input(field + ': '))
    
    def getPeopleFromUser(self, field):
        """
        Prompt the user for a list of names.
        
        :param field: Name of the field to save the name in.
        """
        nameList = []
        while (True):
            res = self.getPersonFromUser(field)
            if res is None:
                break
            else:
                nameList.append(res)
        setattr(self, field, nameList)
    
    def getPersonFromUser(self, field):
        """
        Prompt the user for a name.
        
        :param field: Name of the field to save the name in.
        :returns: Dictionary with givenName and familyName or None if no value was entered.
        """
        res = {}
        res['givenName'] = raw_input(field + ' given name: ')
        res['familyName'] = raw_input(field + ' family name: ')
        return res if len(res['familyName']) != 0 else None
    
    def tidy(self):
        """
        Tidy values in self object by removing newlines and extra whitespace.
        """
        attributes = vars(self).keys()
        for i in attributes:
            setattr(self, i, self._tidyValue(getattr(self, i)))
        self._tidyByPublisher()
    
    def toReferenceString(self, maxAuthors = 0, abbreviateJournal = True, abbreviateNames = True, \
                          familyNameFirst = False, forceTitle = False, firstPageOnly = False):
        """
        Return a formatted version of the parameters in self object.
        
        :param maxAuthors: Maximum number of authors/editors to print. Value less than 2 to print all authors
        :param abbreviateJournal: True to abbreviate the name of a journal. False otherwise
        :param abbreviateNames: True to abbreviate the first names of authors/editors. False to keep full names
        :param familyNameFirst: True to print the last names of authors/editors first. False otherwise
        :param forceTitle: Force the printing of a title no matter the reference type
        :param firstPageOnly: True to show only the first page when a range is available. False otherwise
        :returns: String with the reference information
        """
        if len(self.journal) > 0:
            return self._journalToString(maxAuthors, abbreviateJournal, abbreviateNames, familyNameFirst, \
                                         forceTitle, firstPageOnly)
        else:
            try:
                arxivIdentifier = arxivid.extract(self.url)
                return self._arxivToString(arxivIdentifier, maxAuthors, abbreviateNames, familyNameFirst, \
                                           forceTitle, firstPageOnly)
            except Exception:
                return self._anyToString(maxAuthors, abbreviateNames, familyNameFirst, firstPageOnly)
    
    def toUnformattedString(self):
        """
        Return all of the parameters in self object as a single string.
        
        :returns: String with all of the information in this object
        """
        res = []
        self._addValueToList(res, 'doi')
        self._addValueToList(res, 'isbn')
        self._addValueToList(res, 'issn')
        self._addValueToList(res, 'url')
        self._addValueToList(res, 'publisher')
        self._addValueToList(res, 'title')
        self._addValueToList(res, 'edition')
        self._addValueToList(res, 'journal')
        self._addValueToList(res, 'volume')
        self._addValueToList(res, 'issue')
        self._addValueToList(res, 'year')
        self._addNamesToList(res, 'author')
        self._addNamesToList(res, 'editor')
        self._addPagesToList(res)
        return ', '.join(res)
    
    def _tidyValue(self, value):
        """
        Fix up to formatting of a value by removing newline characters and extra white space.
    
        :param value: String to format
        :returns: Formatted version of the value
        """
        if isinstance(value, (list, tuple)):
            return self._tidyList(value)
        elif isinstance(value, dict):
            return self._tidyDict(value)
        else:
            return self._tidyObject(value)
    
    def _tidyDict(self, values):
        """
        Fix up the values in a dictionary.
        
        :param values: Dictionary with the values to format
        :returns: Dictionary of formatted values
        """
        for key, value in values.iteritems():
            values[key] = self._tidyValue(value)
        return values
    
    def _tidyList(self, values):
        """
        Fix up a list of values.
        
        :param values: List of values to format
        :returns: List of formatted values
        """
        for i in range(len(values)):
            values[i] = self._tidyValue(values[i])
        return values
    
    def _tidyObject(self, value):
        """
        Format a single object.
        
        :param value: Object to format
        :returns: Formatted version of value
        """
        value = value.replace('\n', ' ')
        value = re.sub('\s+', ' ', value)
        value = value.strip()
        return value
    
    def _tidyByPublisher(self):
        """
        Try to fill out additional fields in self object based on saved data.
        """
        lookup = self.publisher.lower().replace(' ', '')
        if lookup.find('americanphysicalsociety') != -1:
            self._tidyForAps()
        elif lookup.find('naturepublishing') != -1:
            self._tidyForNature()
    
    def _tidyForAps(self):
        """
        Try to fill in values based on APS publishing information.
        """
        if (self.pageStart == '' or self.volume == '') and len(self.doi) > 0:
            try:
                parts = self.doi.split('/')[1].split('.')
                self.volume    = self.volume    if self.volume    != '' else parts[1]
                self.pageStart = self.pageStart if self.pageStart != '' else parts[2]
            except Exception:
                pass
    
    def _tidyForNature(self):
        """
        Try to fill in values based on APS publishing information.
        """
        if self.pageStart == '':
            try:
                self.pageStart = self.doi.split('/srep')[1]
            except Exception:
                pass
    
    def _journalToString(self, maxAuthors, abbreviateJournal, abbreviateNames, familyNameFirst, forceTitle, \
                         firstPageOnly):
        """
        Return a formatted version of the parameters in self object as a journal.
        
        :param maxAuthors: Maximum number of authors/editors to print. None to print all authors
        :param abbreviateJournal: True to abbreviate the name of a journal. False otherwise
        :param abbreviateNames: True to abbreviate the first names of authors/editors. False to keep full names
        :param familyNameFirst: True to print the last names of authors/editors first. False otherwise
        :param forceTitle: Force the printing of a title no matter the reference type
        :param firstPageOnly: True to show only the first page when a range is available. False otherwise
        :returns: String with the reference information
        """
        res = self._getAuthorsAsString(maxAuthors, abbreviateNames, familyNameFirst)
        if forceTitle and len(self.title) > 0:
            res.append(self.title + ',')
        if len(self.journal) > 0:
            res.append(journal.getAbbreviation(self.journal) if abbreviateJournal else self.journal)
        if len(self.volume) > 0:
            res.append(self.volume + ',')
        pages = self._getPagesAsString(firstPageOnly)
        if len(pages) > 0:
            res.append(pages)
        if len(self.year) > 0:
            res.append('(' + self.year + ')')
        return ' '.join(res)
    
    def _arxivToString(self, arxivIdentifier, maxAuthors, abbreviateNames, familyNameFirst, forceTitle, firstPageOnly):
        """
        Return a formatted version of the parameters in self object as an arXiv reference.
        
        :param arxivIdentifier: arXiv identifier for the article
        :param maxAuthors: Maximum number of authors/editors to print. None to print all authors
        :param abbreviateNames: True to abbreviate the first names of authors/editors. False to keep full names
        :param familyNameFirst: True to print the last names of authors/editors first. False otherwise
        :param forceTitle: Force the printing of a title no matter the reference type
        :param firstPageOnly: True to show only the first page when a range is available. False otherwise
        :returns: String with the reference information
        """
        res = self._getAuthorsAsString(maxAuthors, abbreviateNames, familyNameFirst)
        if forceTitle and len(self.title) > 0:
            res.append(self.title + ',')
        res.append('arXiv:' + arxivIdentifier)
        if len(self.year) > 0:
            res.append('(' + self.year + ')')
        return ' '.join(res)
    
    def _anyToString(self, maxAuthors, abbreviateNames, familyNameFirst, firstPageOnly):
        """
        Return a formatted version of the parameters in self object as an arbitrary type.
        
        :param maxAuthors: Maximum number of authors/editors to print. None to print all authors
        :param abbreviateNames: True to abbreviate the first names of authors/editors. False to keep full names
        :param familyNameFirst: True to print the last names of authors/editors first. False otherwise
        :param firstPageOnly: True to show only the first page when a range is available. False otherwise
        :returns: String with the reference information
        """
        res = []
        if len(self.author) > 0:
            res += self._getAuthorsAsString(maxAuthors, abbreviateNames, familyNameFirst)
        elif len(self.editor) > 0:
            res += self._getEditorsAsString(maxAuthors, abbreviateNames, familyNameFirst)
        if len(self.title) > 0:
            res.append(self.title + ',')
        if len(self.author) > 0 and len(self.editor) > 0:
            res += self._getEditorsAsString(maxAuthors, abbreviateNames, familyNameFirst)
        if len(self.publisher) > 0:
            res.append(self.publisher)
        if len(self.year) > 0:
            res.append('(' + self.year + ')')
        return ' '.join(res)
    
    def _getAuthorsAsString(self, maxAuthors, abbreviateNames, familyNameFirst):
        """
        Return a list of formatted authors.
        
        :param maxAuthors: Maximum number of authors/editors to print. None to print all authors
        :param abbreviateNames: True to abbreviate the first names of authors/editors. False to keep full names
        :param familyNameFirst: True to print the last names of authors/editors first. False otherwise
        :returns: String with the formatted list of authors
        """
        if len(self.author) > 0:
            return [ Metadata._formatNameString(self.author, maxAuthors, abbreviateNames, familyNameFirst) + ',' ]
        else:
            return []
    
    def _getEditorsAsString(self, maxAuthors, abbreviateNames, familyNameFirst):
        """
        Return a list of formatted editors.
        
        :param maxAuthors: Maximum number of authors/editors to print. None to print all authors
        :param abbreviateNames: True to abbreviate the first names of authors/editors. False to keep full names
        :param familyNameFirst: True to print the last names of authors/editors first. False otherwise
        :returns: String with the formatted list of editors
        """
        if len(self.editor) > 0:
            editorString = Metadata._formatNameString(self.editor, maxAuthors, abbreviateNames, familyNameFirst)
            return [ editorString + ' (Ed.),' if len(self.editor) == 1 else editorString + ' (Eds.),' ]
        else:
            return []
    
    @staticmethod
    def _formatNameString(names, maxAuthors, abbreviateNames, familyNameFirst):
        """
        Return a list of formatted names.
        
        :param names: List of names to format, each as a dictionary with 'familyName' and 'givenName' fields
        :param maxAuthors: Maximum number of authors/editors to print. None to print all authors
        :param abbreviateNames: True to abbreviate the first names of authors/editors. False to keep full names
        :param familyNameFirst: True to print the last names of authors/editors first. False otherwise
        :returns: String with the formatted list of names
        """
        res = []
        for i in range(len(names)):
            if maxAuthors > 1 and i == maxAuthors - 1 and i < len(names) - 1:
                res.append('et al.')
                break
            name = names[i]
            res.append(author.formatName(name['givenName'], name['familyName'], abbreviateNames, familyNameFirst))
        return ', '.join(res)
    
    def _addValueToList(self, values, key):
        """
        If the value of the attribute 'key' has some length, then add it to a list.
        
        :param values: List of values to add to
        :param key: Key of the attribute to add
        """
        value = getattr(self, key)
        if len(value) > 0:
            values.append(value)
    
    def _addNamesToList(self, values, key):
        """
        Add all names stored by self object to a list.
        
        :param values: List of values to add to
        :param key: Key of the attribute with the list of names
        """
        names = getattr(self, key)
        for i in names:
            values.append(i['givenName'] + ' ' + i['familyName'])
    
    def _addPagesToList(self, values):
        """
        Add pages stored by self object to a list of values.
        
        :param values: List of values to add to
        """
        pages = self._getPagesAsString(False)
        if len(pages):
            values.append(pages)
    
    def _getPagesAsString(self, firstPageOnly):
        """
        Format pages and return then as a string.
        
        :param firstPageOnly: True to show only the first page when a range is available. False otherwise
        :returns: String with pages in self object
        """
        if firstPageOnly and len(self.pageStart) > 0:
            return self.pageStart
        if len(self.pageStart) > 0 and len(self.pageEnd) > 0:
            return self.pageStart + '-' + self.pageEnd
        elif len(self.pageStart) > 0:
            return self.pageStart
        elif len(self.pageEnd) > 0:
            return self.pageEnd
        else:
            return ''
