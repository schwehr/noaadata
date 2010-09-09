#!/usr/bin/env python

__version__ = '$Revision: 7470 $'.split()[1]
__date__ = '$Date: 2007-11-06 10:31:44 -0500 (Tue, 06 Nov 2007) $'.split()[1]
__author__ = 'Kurt Schwehr'

__doc__='''

Split an USCG N-AIS log file into one file per receiving station.

@requires: U{epydoc<http://epydoc.sourceforge.net/>} > 3.0alpha3

@author: U{'''+__author__+'''<http://schwehr.org/>}
@version: ''' + __version__ +'''
@copyright: 2006
@var __date__: Date of last svn commit
@undocumented: __version__ __author__ __doc__ parser
@since: 2006-Sep-24
@status: under development
@organization: U{CCOM<http://ccom.unh.edu/>}
@license: GPL v2

@todo: add a link to generated doc string to bring up the html for the pretty version

@bug: NOT complete
@todo: make sure binary is only used in AIS ITU messages and not within the binary messages!
'''

import sys, os
#from decimal import Decimal
#from lxml import etree 

def getStation(msg,withR=True):
    '''
    Return the station/tower portion of the message
    @param withR: True keeps the leading r
    @rtype: str or None
    @return: Station name
    '''
    fields = msg.split(',')
    numFields = len(fields)
    #for i in range(numFields):
    for i in range(numFields-1,-1,-1):
	#curField = fields[numFields-i-1]
	curField = fields[i]
	if curField[0]=='r':
	    if withR: return curField
	    return curField[1:]
	if curField[1]=='*': # Checksum
	    return None
    return None


def towersplit(options, filenames):
    '''
    One file per receive station/tower

    The tower is specified in the USCG extensions after the checksum in the field starting with a 'r'.
    In this message, the station is r3669961.  This is not located in a fixed position.

    !AIVDM,1,1,,B,15MgF90017JWnghFFuLeJrW608D;,0*7C,x161434,s26256,d-109,T34.43128733,r3669961,1152921695
    '''
    #stations=set()
    subdir = options.subdir
    if options.useSubdir:
	if not os.access(subdir,os.X_OK):
	    os.mkdir(subdir)
	if subdir[-1]!='/': subdir += '/'
	print 'Using subdir ...',subdir
    else:
	subdir = ''
    
    unknown = None  # Where to write messages with no station
    stationFiles={}
    for filename in filenames:
	lineNum = 0
	for line in file(filename):
	    lineNum += 1
	    if lineNum % 20000 == 0: print 'line',lineNum
	    if line[0]=='#': continue # Allow for comments
	    station = getStation(line)
	    if None==station:
		print 'Line had no station:',line
		if None==unknown: unknown = file(subdir+'unknown','w')
		unknown.write(line)
	    if station not in stationFiles:
		stationFilename = subdir+station
		#print 'Creating station file',stationFilename,'for',station
		stationFiles[station] = file(stationFilename,'w')
	    #else: print 'already open'
	    #print 'writing line to file:',station
	    stationFiles[station].write(line)

######################################################################
if __name__=='__main__':
    from optparse import OptionParser
    parser = OptionParser(usage="%prog [options]",
			    version="%prog "+__version__)

    parser.add_option('--doc-test',dest='doctest',default=False,action='store_true',
                        help='run the documentation tests')

    parser.add_option('-v','--verbose',dest='verbose',default=False,action='store_true',
                        help='run the tests run in verbose mode')

    parser.add_option('-n','--nosubdir',dest='useSubdir',default=True,action='store_false',
                        help='Prevent use of a subdirectory.  Will make a mess.')

    parser.add_option('-s','--subdir',dest='subdir',default='towers',
                        help='Where to make the tower files [default: %default]')

    (options,args) = parser.parse_args()

    success=True

    if options.doctest:
	import os; print os.path.basename(sys.argv[0]), 'doctests ...',
	argvOrig = sys.argv
	sys.argv= [sys.argv[0]]
	if options.verbose: sys.argv.append('-v')
	import doctest
	numfail,numtests=doctest.testmod()
	if numfail==0: print 'ok'
	else: 
	    print 'FAILED'
	    success=False
	sys.argv = argvOrig # Restore the original args
	del argvOrig # hide from epydoc
	sys.exit() # FIX: Will this exit success?

    towersplit(options, args)
