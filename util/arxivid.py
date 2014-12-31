"""
Functions for working with arXiv identifier strings.
"""

import re
from sets import Set

def extract(value):
    """
    Attempt to extract an arXiv identifier from a string.
    
    :param value: String to extract arXiv identifier from
    :raises ValueError: If value does not contain an arXiv identifier
    :returns: String with the arXiv identifier that was extracted
    """
    res = _extractNewFormat(value)
    if res is None:
        res = _extractOldFormat(value)
    if res is None:
        raise ValueError('arXiv identifier could not be extracted from string')
    return res

def _extractNewFormat(value):
    """
    Attempt to extract a new format arXiv identifier from a string.
    
    :param value: String to extract arXiv identifier from
    :returns: String with the arXiv identifier that was extracted
    :returns: None if an arXiv identifier was not found
    """
    matches = _newPattern.finditer(value)
    for i in matches:
        if _validateStartOfFormat(value, i) and _validateEndOfFormat(value, i):
            return i.group('id')
    return None

def _validateStartOfFormat(value, match):
    """
    Make sure that characters preceding a matched arXiv identifier do not invalidate the match. The match is
    considered invalid if it is preceded by any alphanumeric character.
    
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

def _validateEndOfFormat(value, match):
    """
    Make sure that characters following a matched arXiv identifier do not invalidate the match. The match is
    considered invalid if it is followed by any alphanumeric character, unless that matches the pattern vI where
    I is an integer.
    
    :param value: String that was being searched
    :param match: MatchObject returned from regular expression function
    :returns: True if characters after match are valid
    :returns: False if characters after match are not valid
    """
    if match.end() < len(value):
        postString = value[match.end():]
        if re.match('\w', postString) is not None and re.match('[vV][0-9]', postString) is None:
            return False
    return True

def _extractOldFormat(value):
    """
    Attempt to extract an old format arXiv identifier from a string.
    
    :param value: String to extract arXiv identifier from
    :returns: String with the arXiv identifier that was extracted
    :returns: None if an arXiv identifier was not found
    """
    try:
        match = _oldPattern.search(value)
        if match is not None:
            id = match.group('id')
            if id.split('/')[0] in _subjects and _validateEndOfFormat(value, match):
                return id
        return None
    except:
        raise

# Regular expression to match new format of arXiv identifier
# This finds strings of the form IIII.IIII (where I are all integers) and saves the matching string as 'id'
_newPattern = re.compile('(?P<id>[0-9]{4}\.[0-9]{4})')

# Regular expression to match old format of arXiv identifier
# This find strings of the form [letters]letters/numbers where numbers is of length 7
_oldPattern = re.compile('(?P<id>[a-zA-Z][a-zA-Z\-\.]+/[0-9]{7})')

# List of arxiv subject areas
_subjects = Set([\
    'stat', 'stat.AP', 'stat.CO', 'stat.ML', 'stat.ME', 'stat.TH', 'q-bio', 'q-bio.BM', 'q-bio.CB', 'q-bio.GN', \
    'q-bio.MN', 'q-bio.NC', 'q-bio.OT', 'q-bio.PE', 'q-bio.QM', 'q-bio.SC', 'q-bio.TO', 'cs', 'cs.AR', 'cs.AI', \
    'cs.CL', 'cs.CC', 'cs.CE', 'cs.CG', 'cs.GT', 'cs.CV', 'cs.CY', 'cs.CR', 'cs.DS', 'cs.DB', 'cs.DL', 'cs.DM', \
    'cs.DC', 'cs.GL', 'cs.GR', 'cs.HC', 'cs.IR', 'cs.IT', 'cs.LG', 'cs.LO', 'cs.MS', 'cs.MA', 'cs.MM', 'cs.NI', \
    'cs.NE', 'cs.NA', 'cs.OS', 'cs.OH', 'cs.PF', 'cs.PL', 'cs.RO', 'cs.SE', 'cs.SD', 'cs.SC', 'nlin', 'nlin.AO', \
    'nlin.CG', 'nlin.CD', 'nlin.SI', 'nlin.PS', 'math', 'math.AG', 'math.AT', 'math.AP', 'math.CT', 'math.CA', \
    'math.CO', 'math.AC', 'math.CV', 'math.DG', 'math.DS', 'math.FA', 'math.GM', 'math.GN', 'math.GT', 'math.GR', \
    'math.HO', 'math.IT', 'math.KT', 'math.LO', 'math.MP', 'math.MG', 'math.NT', 'math.NA', 'math.OA', 'math.OC', \
    'math.PR', 'math.QA', 'math.RT', 'math.RA', 'math.SP', 'math.ST', 'math.SG', 'astro-ph', 'cond-mat', \
    'cond-mat.dis-nn', 'cond-mat.mes-hall', 'cond-mat.mtrl-sci', 'cond-mat.other', 'cond-mat.soft', \
    'cond-mat.stat-mech', 'cond-mat.str-el', 'cond-mat.supr-con', 'gr-qc', 'hep-ex', 'hep-lat', 'hep-ph', \
    'hep-th', 'math-ph', 'nucl-ex', 'nucl-th', 'physics', 'physics.acc-ph', 'physics.ao-ph', 'physics.atom-ph', \
    'physics.atm-clus', 'physics.bio-ph', 'physics.chem-ph', 'physics.class-ph', 'physics.comp-ph', \
    'physics.data-an', 'physics.flu-dyn', 'physics.gen-ph', 'physics.geo-ph', 'physics.hist-ph', 'physics.ins-det', \
    'physics.med-ph', 'physics.optics', 'physics.ed-ph', 'physics.soc-ph', 'physics.plasm-ph', 'physics.pop-ph', \
    'physics.space-ph', 'quant-ph'])
