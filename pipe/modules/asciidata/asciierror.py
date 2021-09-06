"""
Specific exception classes

@author: Martin Kuemmel, Jonas Haase
@organization: Space Telescope - European Coordinating Facility (ST-ECF)
@license: Gnu Public Licence
@contact: mkuemmel@eso.org
@since: 2005/09/13

$LastChangedBy: jhaase $
$LastChangedDate: 2006-10-13 18:38:13Z $
$HeadURL: http://astropy.scipy.org/svn/astrolib/trunk/asciidata/Lib/asciierror.py $
"""
__version__ = "Version 1.0 $LastChangedRevision: 113 $"

import string

class AsciiDataError(Exception):
    """
    A general exception class for the AsciiData object

    This class is the parent class for all specific
    Errors branched off it.
    """
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class ColumnError(AsciiDataError):
    """
    Exception if a column does not exist    
    """
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

class ColTypeError(AsciiDataError):
    """
    Exception if a column type is not valid
    """
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

class TypeTransError(AsciiDataError):
    """
    Exception if a column type is not valid
    """
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)
