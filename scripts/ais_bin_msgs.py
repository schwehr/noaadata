#!/usr/bin/env python

__author__    = 'Kurt Schwehr'
__version__   = '$Revision: 12533 $'.split()[1]
__revision__  = __version__ # For pylint
__date__ = '$Date: 2009-08-31 23:34:01 -0400 (Mon, 31 Aug 2009) $'.split()[1]
__copyright__ = '2008'
__license__   = 'GPL v3'
__contact__   = 'kurt at ccom.unh.edu'

__doc__='''
Beginnings of code to handle AIS binary messages

@since: 2009-09-07

@var __date__: Date of last svn commit
@undocumented: __version__ __author__ __doc__ parser
@status: Works, but not complete
'''

import sys
import traceback
import datetime
import exceptions

from decimal import Decimal
from BitVector import BitVector
import StringIO

import ais.binary    as binary

from aisutils.uscg import uscg_ais_nmea_regex

def parse_msgs(infile, verbose=False):
    for line in infile:
        try:
            match = uscg_ais_nmea_regex.search(line).groupdict()
        except AttributeError:
            continue

        msg_type = match['body'][0]
        if msg_type not in ('6', '8'):
            continue
        #print line,
        if msg_type == '6' and len(match['body']) < 15:
          continue
        if msg_type == '8' and len(match['body']) < 10:
          continue

        try:
          bv = binary.ais6tobitvec(match['body'][:15])
        except ValueError:
          sys.stderr.write('bad msg: %s\n' % line.strip())
          continue
	r = {}
	r['MessageID']=int(bv[0:6])
	r['UserID']=int(bv[8:38])

        if '6' == msg_type:
            dac = int(bv[72:82])
            fi = int(bv[82:88])
        elif '8' == msg_type:
          dac = int(bv[40:50])
          fi = int(bv[50:56])
        elif verbose:
          print 'not a bbm:', line

        if verbose:
            print msg_type, dac, fi, r['UserID'], line.rstrip()
        else:
            print msg_type, dac, fi, r['UserID'], match['station']


def main():
    from optparse import OptionParser
    parser = OptionParser(usage="%prog [options] file1.ais [file2.ais ...]",version="%prog "+__version__)

    parser.add_option('-v','--verbose',default=False,action='store_true',
                      help='Make program output more verbose info as it runs')

    (options,args) = parser.parse_args()
    for filename in args:
        parse_msgs(file(filename), verbose = options.verbose)

if __name__=='__main__':
    main()
