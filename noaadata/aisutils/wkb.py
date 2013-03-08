#!/usr/bin/env python
__author__ = 'Kurt Schwehr'
__version__ = '$Revision: 8545 $'.split()[1]
__revision__  = __version__ # For pylint
__date__ = '$Date: 2008-02-06 17:37:24 -0500 (Wed, 06 Feb 2008) $'.split()[1]
__copyright__ = '2008'
__license__   = 'GPL v2'
__contact__   = 'kurt at ccom.unh.edu'

__doc__='''
AIS database utilities.

@status: under development
@since: 2008-Feb-07
@undocumented: __doc__ parser

@requires: U{GeoTypes<http://www.initd.org/tracker/psycopg/wiki/GeoTypes>} >= 0.7.0

@todo: Switch to GeoDjango so that this becomes irrelevant
'''

#@requires: U{psycopg2<http://http://initd.org/projects/psycopg2/>} >= 2.0.6
#import psycopg2
#import psycopg2.extensions
import GeoTypes

class convert:
    '''
    Simple wrapper to make decoding WKB Hex a lot simpler
    '''
    def __init__(self):
        self.factory = GeoTypes.OGGeoTypeFactory()
        self.parser = GeoTypes.HEXEWKBParser(factory)
    def decode(wkbhex):
        '''
        Convert a WKB Hex string to an object.  This is a factory, no?

        c = convert()
        c.decode("0020000001000010E6C051D30925D1DA0B4044A79AE924F228")

        @param wkbhex: HEX geometry
        @type wkbhex: str
        @return: Different geometry objects depending on what you give it.  e.g.
        @rtype: Geotypes object
        '''
        parser.parseGeometry(wkbhex)
        geom = factory.getGeometry()
        return geom
