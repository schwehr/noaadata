#!/usr/bin/env python

__version__ = '$Revision: 7470 $'.split()[1]
__date__ = '$Date: 2007-11-06 10:31:44 -0500 (Tue, 06 Nov 2007) $'.split()[1]
__author__ = 'Kurt Schwehr'

__doc__='''

Split USCG N-AIS messages into separate stations

@requires: U{epydoc<http://epydoc.sourceforge.net/>} > 3.0alpha3

@author: '''+__author__+'''
@version: ''' + __version__ +'''
@var __date__: Date of last svn commit
@undocumented: __version__ __author__ __doc__ parser
@status: under development
@license: GPL
'''

import sys, os

def getStation(line, withR=False):
    fields=line.split(',')
    foundChecksum=False
    for f in fields:
	# must come after the checksum field
	if len(f)<1: continue
	if not foundChecksum:
	    if -1==f.find('*'): continue  # FIX: Is this sufficient to make sure this is a checksum?
	    #if '0'==f[0]: continue
	    foundChecksum=True
	    continue
        if len(f)<2: continue
        if f[0] != 'r': continue
        if withR: return f
	return f[1:]
    return None


def splitstations(logfile, subdir=None, basename=None, withR=False, verbose=False, stationSubdirs=False):
    '''
    @param logfile: file like object to read from
    @param subdir: put the files in a subdirectory
    @param withR: keep the r in front of the station name
    @param verbose: be loud
    '''
    if subdir!=None and not os.access(subdir,os.X_OK): #F_OK):
	os.mkdir(subdir)
    else: subdir='.'
	
    stations={}
    for line in logfile:
	station = getStation(line)
	if None==station: continue

	# Handle opening the file if have not seen the station before
	if station not in stations:
	    if verbose: print 'New station:',station
	    filename = subdir + '/' + station
	    if stationSubdirs:
		if not os.access(filename,os.X_OK): os.mkdir(filename)
		filename += '/log.ais'
	    stations[station] = file(filename,'a')

	stations[station].write(line)


    if verbose:
	print 'Finished file.  Station count =',len(stations)


if __name__=='__main__':
    
	from optparse import OptionParser
	parser = OptionParser(usage="%prog [options]", version="%prog "+__version__)

#	parser.add_option('--doc-test',dest='doctest',default=False,action='store_true',
#		help='run the documentation tests')
#	parser.add_option('--unit-test',dest='unittest',default=False,action='store_true',
#		help='run the unit tests')
	parser.add_option('-b','--base-name',dest='basename',default=None,
		help='prepend to each station name [default: %default]')
	parser.add_option('-s','--subdir',dest='subdir',default=None,
		help='Put all the stations in a subdirectory [default: %default]')
	parser.add_option('-S','--with-station-subdirs',dest='withStationSubdirs',default=False,action='store_true',
		help='Make the station name be a subdir with log.ais as the filename')
	parser.add_option('-r','--with-r',dest='withR',default=False,action='store_true',
		help='Keep the r in the station name')
	parser.add_option('-v','--verbose',dest='verbose',default=False,action='store_true',
		help='Make the test output verbose')

	(options,args) = parser.parse_args()
	success=True

	for filename in args:
	    if options.verbose: print 'Processing file:',filename
	    logfile = open(filename)
	    splitstations(logfile, options.subdir, options.basename, options.withR, options.verbose,options.withStationSubdirs)

