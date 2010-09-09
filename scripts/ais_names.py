#!/usr/bin/env python

__version__ = '$Revision: 7470 $'.split()[1]
__date__ = '$Date: 2007-11-06 10:31:44 -0500 (Tue, 06 Nov 2007) $'.split()[1]
__author__ = 'Kurt Schwehr'

__doc__='''

Get the name and mmsi (User ID) for each msg 5 identification message.

This program requires that the nmea strings be sorted such that the
2nd part of the message comes directly after the first.  You can do
this by grepping for the USCG N-AIS station name.  This will prevent
interleaving of msg 5 nmea strings.

@requires: U{epydoc<http://epydoc.sourceforge.net/>} > 3.0alpha3

@author: '''+__author__+'''
@version: ''' + __version__ +'''
@var __date__: Date of last svn commit
@undocumented: __version__ __author__ __doc__ parser
@status: under development
@license: GPL

@todo: is this a repeat of merge5?

'''

import sys, os

from ais import binary
from ais import ais_msg_5
from ais import aisstring

def getNameMMSI(logfile,outfile):
    for line in logfile: 
	fields = line.split(',')[:6]
	if '1'!=fields[2]: # Must be the start of a sequence
	    continue
	if len(fields[5])<39: continue
	bv = binary.ais6tobitvec(fields[5][:39]) # Hacked for speed

	mmsi = ais_msg_5.decodeUserID(bv)
	name = aisstring.unpad(ais_msg_5.decodename(bv))
	outfile.write(str(mmsi)+' '+str(name)+'\n')

if __name__=='__main__':
    from optparse import OptionParser
    parser = OptionParser(usage="%prog [options] logfile1 [logfile2 logfile3 ...] ", version="%prog "+__version__)
    parser.add_option('-o','--output',dest='outputFileName',default=None,
		      help='Name of the file to write [default: stdout]')

    (options,args) = parser.parse_args()
    
    outfile = sys.stdout
    if None!=options.outputFileName:
	print 'outfilename=',options.outputFileName
	outfile = file(options.outputFileName,'w')
    if 0==len(args):
	getNameMMSI(sys.stdin,outfile)
    else: 
	for filename in args:
	    getNameMMSI(file(filename),outfile)

