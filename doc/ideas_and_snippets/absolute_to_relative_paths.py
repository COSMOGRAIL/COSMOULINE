""" Authors: Cimarron Taylor and Alan Ezust
 Version: 2.0
 Date: July 01, 2004
 (relpath.py v1 originally from Oreilly/Activestate Python cookbook 2003)

 helper functions for relative paths.
 This package includes rel2abs() and abs2rel(),
 based on the perl functions from cpan File::Spec
"""

import os
import os.path
import re

# matches http:// and ftp:// and mailto://
protocolPattern = re.compile(r'^\w+://')

def isabs(string):
    """

    @return true if string is an absolute path or protocoladdress
    for addresses beginning in http:// or ftp:// or ldap:// -
    they are considered &quot;absolute&quot; paths.
    """
    if protocolPattern.match(string): return 1
    return os.path.isabs(string)

def rel2abs(path, base = os.curdir):
    """ converts a relative path to an absolute path.

    @param path the path to convert - if already absolute, is returned
    without conversion.
    @param base - optional. Defaults to the current directory.
    The base is intelligently concatenated to the given relative path.
    @return the relative path of path from base
    """
    if isabs(path): return path
    retval = os.path.join(base,path)
    return os.path.abspath(retval)


#def pathsplit(p, rest=[]):
#    (h,t) = os.path.split(p)
#    if len(h) &lt; 1: return [t]+rest
#    if len(t) &lt; 1: return [h]+rest
#    return pathsplit(h,[t]+rest)
    
def pathsplit(path):
    """ This version, in contrast to the original version, permits trailing
    slashes in the pathname (in the event that it is a directory).
    It also uses no recursion """
    return path.split(os.path.sep)

def commonpath(l1, l2, common=[]):
    if len(l1) > 1: return (common, l1, l2)
    if len(l2) < 1: return (common, l1, l2)
    if l1[0] != l2[0]: return (common, l1, l2)
    return commonpath(l1[1:], l2[1:], common+[l1[0]])


def relpath(p1, p2):
    (common,l1,l2) = commonpath(pathsplit(p1), pathsplit(p2))
    p = []
    if len(l1) > 0:
        p = [ '../' * len(l1) ]
    p = p + l2
    if len(p) is 0:
        return '.'
    return os.path.join( *p )


def abs2rel(path, base = os.curdir):
    """ @return a relative path from base to path.
    base can be absolute, or relative to curdir, or defaults
    to curdir.
    """
    if protocolPattern.match(path): return path
    base = rel2abs(base)
    path = rel2abs(path) # redundant - should already be absolute
    return relpath(base, path)
    
    
def test(p1,p2):
    print "from", p1, "to", p2, " -> ", relpath(p1, p2)

if __name__ == '__main__':
    test('/a/b/c/d', '/a/b/c1/d1')