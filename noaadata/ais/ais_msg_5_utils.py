#!/usr/bin/env python

__version__ = '$Revision: 4791 $'.split()[1]
__date__ = '$Date: 2007-02-26 $'.split()[1]
__author__ = ''

__doc__='''

Hand coded utilities for ais ship and cargo messages (msg #5).

The main goal for the initial version is to help decode the
complicated type of ship and cargo 8 bit table (Table 18 in ITU-R M.1371-1).

@requires: U{epydoc<http://epydoc.sourceforge.net/>} > 3.0alpha3

@author: U{'''+__author__+'''<http://schwehr.org/>}
@version: ''' + __version__ +'''
@var __date__: Date of last svn commit
@undocumented: __version__ __author__ __doc__ parser
@status: under development
@license: GPL v2
@since: 2007-Mar-04
'''


def isTanker(value):
    '''
    Is the vessel classified as a tanker?  This is true if the first digit is 8.
    @rtype: bool
    '''
    if str(value)[0]=='8': return True
    return False
