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
#import ais.aisstring as aisstring

#import ais

#import aisutils.database

#import ais.ais_msg_1_handcoded
#import ais.ais_msg_2_handcoded
#import ais.ais_msg_3_handcoded
#import ais.ais_msg_4_handcoded
#import ais.ais_msg_5
#import ais.ais_msg_18
#import ais.ais_msg_19
from aisutils.uscg import uscg_ais_nmea_regex

def parse_msgs(infile, verbose=False):
    for line in infile:
        try:
            match = uscg_ais_nmea_regex.search(line).groupdict()      
        except AttributeError:
            continue
        #if not match: continue

        if match['body'][0]!='8':
            continue
        #print line,
        bv = binary.ais6tobitvec(match['body'])
	r = {}
	r['MessageID']=int(bv[0:6])
	r['RepeatIndicator']=int(bv[6:8])
	r['UserID']=int(bv[8:38])
	r['Spare']=int(bv[38:50])
	#r['BinaryData']=bv[40:]
	r['dac']=int(bv[40:50])
	r['fid']=int(bv[50:56])

        #if 34==r['fid']:
        if verbose:
            print r['dac'], r['fid'], r['UserID'], line.rstrip()
        else:
            print r['dac'], r['fid'], r['UserID'], match['station']


        

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
