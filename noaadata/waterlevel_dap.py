#!/usr/bin/env python
__version__ = '$Revision: 4762 $'.split()[1]
__date__ = '$Date: 2006-09-19 14:56:22 -0400 (Tue, 19 Sep 2006) $'.split()[1]
__author__ = 'Kurt Schwehr'

__doc__='''
Retrieve 6 minute raw water level data from NOAA CO-OPS server.

@see: U{NOAA DODS/OPeNDAP page<http://opendap.co-ops.nos.noaa.gov/dods/>}
@requires: U{pydap/dap-py<http://pydap.org/>}
@requires: U{epydoc<http://epydoc.sourceforge.net/>}

@author: U{'''+__author__+'''<http://schwehr.org/>}
@license: GPL v2
@copyright: (C) 2006 Kurt Schwehr
@version: ''' + __version__ +'''

@var __date__: Date of last svn commit
@undocumented: __version__ __author__ __doc__ parser success 

'''

import sys, httplib, dap.client
import urllib # FIX: remove this when pydap protects the seqReq

# FIX: document the datums
datumList = ['MLLW','MSL','MHW','STND','IGLD','NGVD','NAVD']
unitList = ['Meters','Feet']

import datetime

# Try to hang on to the dataset in case the user wants to do multiple requests
# FIX: how do I prevent epydoc from talking to the NOAA server when documentation is generated?
datasetURL='http://opendap.co-ops.nos.noaa.gov/dods/IOOS/Raw_Water_Level'
"OPeNDAP URL for NOAA CO-OPS database"
waterlevelDataset=dap.client.open(datasetURL)
"This set only contains raw 6 minute water level data"
waterlevelSeq = waterlevelDataset['WATERLEVEL_RAW_PX']
"This is a sequence containter for waterlevels"

stationsAll = {
    '8639348':'Money Point',
    '8638595':'South Craney Island',
    '8638610':'Sewells Point',
    'cb0402':'NSN LB 7',
    'cb0601':'Newport News Channel LB 14' ,
    '8638511':'Dom. Term. Assoc. Pier 11',
    '8638614':'Willoughby Degaussing Station',  # Is this in the right location on the map???
    'cb0301':'Thimble Shoal Channel LB 18',
    '8638863':'CBBT', 
    'cb0102':'Cape Henry LB 2CH',
    '8638999':'Cape Henry',
    'cb0201':'York Spit Channel LBB 22',
    '8632200':'Kiptopeke Beach',
    '8637611':'York River East Rear Range Light', 
    '8637689':'Yorktown USCG Training Center'
}

stationsWaterLevel = {
    '8638610':'Sewells Point',
    '8639348':'Money Point',
    '8638863':'CBBT', 
    '8632200':'Kiptopeke Beach',
    '8637689':'Yorktown USCG Training Center'
}


'''Convenience table.  Should really get the stations from the web,
soap, or dap.  These stations are in the Southern Chesapeake Bay.'''

def getWaterLevelNow(stationId,verbose=False, returnDict=True,datum='MSL'):
    '''
    Fetch the dictionary for the current water level

    @see: U{Southern Chesapeak Bay Stations<http://tidesandcurrents.noaa.gov/cbports/cbports_south.shtml?port=cs>}

    '''

    d = datetime.datetime.utcnow()

    #print 'FIX: do this in seconds space!!!!  This is crap!'

    startD = d + datetime.timedelta(minutes=-20)
    endD = d + datetime.timedelta(minutes=10)
    #startMin = int(d.minute) - 6 # or 5?
    #endMin = int(d.minute) + 1
    #if verbose: print startD,endD,d

    beginDate = str(startD.year)+('%02d' % startD.month)+('%02d' % startD.day)+' '+ ('%02d' % (startD.hour))+':'+('%02d' % (startD.minute))
    endDate = str(endD.year)+('%02d' % endD.month)+('%02d' % endD.day)+' '+ ('%02d' % (endD.hour))+':'+('%02d' % (endD.minute))

    if verbose:
        print 'range: %s -> %s' % (str(beginDate),str(endDate))

    reqStr = '_STATION_ID="'+str(stationId)+'"&_BEGIN_DATE="'+beginDate+'"&_END_DATE="'+endDate+'"&_DATUM="'+datum+'"'
    if verbose: 
        print 'plain text, then quoted'
        print 'getWaterLevelNow reqStr:\n  ',reqStr
    reqStr = urllib.quote(reqStr) # FIX: remove this step when pydap updated
    if verbose: 
        print 'getWaterLevelNow reqStr:\n  ',reqStr
    filt_seq=waterlevelSeq.filter(reqStr)
    if verbose: print 'sending data request...'
    data = filt_seq._get_data()
    #if len(data) != 1: print 'WARNING: retrieved more than one point!'
    if not returnDict: return data[-1][:]

    data = data[-1][:] # get just the row and drop the surrounding "[]"
    keys = filt_seq.keys()
    #print len(keys),':     ',keys
    #print len(data),':     ',data
    #print 
    assert len(keys) == len(data)
    r = {} # Results
    for i in range(len(keys)):
	r[keys[i]] = data[i]
    return r


def get_waterlevel(stationId,start_date,end_date,verbose=False, returnDict=True,datum='MSL'):
    '''
    Fetch the dictionary for the current water level

    FIX:.... in progress!
    '''

    beginDate = str(start_date.year)+('%02d' % start_date.month)+('%02d' % start_date.day)+' '+ ('%02d' % (start_date.hour))+':'+('%02d' % (start_date.minute))
    endDate = str(end_date.year)+('%02d' % end_date.month)+('%02d' % end_date.day)+' '+ ('%02d' % (end_date.hour))+':'+('%02d' % (end_date.minute))

    reqStr = '_STATION_ID="'+str(stationId)+'"&_BEGIN_DATE="'+beginDate+'"&_END_DATE="'+endDate+'"&_DATUM="'+datum+'"'
    if verbose: 
        print 'plain text, then quoted'
        print 'getWaterLevelNow reqStr:\n  ',reqStr
    reqStr = urllib.quote(reqStr) # FIX: remove this step when pydap updated
    if verbose: 
        print 'getWaterLevelNow reqStr:\n  ',reqStr
    filt_seq=waterlevelSeq.filter(reqStr)
    if verbose: print 'sending data request...'
    data = filt_seq._get_data()
    #if len(data) != 1: print 'WARNING: retrieved more than one point!'
    if not returnDict: return data[-1][:]

    data = data[-1][:] # get just the row and drop the surrounding "[]"
    keys = filt_seq.keys()
    #print len(keys),':     ',keys
    #print len(data),':     ',data
    #print 
    assert len(keys) == len(data)
    r = {} # Results
    for i in range(len(keys)):
	r[keys[i]] = data[i]
    return r


######################################################################

if __name__ == '__main__':
    from optparse import OptionParser
    parser = OptionParser(usage="%prog [options]",version="%prog "+__version__)
    parser.add_option('-a','--all-stations',dest='allStations',default=False,action='store_true',
                        help='print values for all the stations in the Southern Chesapeake Bay region')
    parser.add_option('-s','--station',dest='station',default='8639348',
                        help='Specify the station to print.  (Default is Money Point) [default: %default]')
    parser.add_option('--test','--doc-test',dest='doctest',default=False,action='store_true',
                        help='run the documentation tests')
    parser.add_option('-v','--verbose',dest='verbose',default=False,action='store_true',
		      help='Make the test output verbose')

    (options,args) = parser.parse_args()

    success=True

    if options.doctest:
	import os; print os.path.basename(sys.argv[0]), 'doctests ...',
	sys.argv= [sys.argv[0]]
	if options.verbose: sys.argv.append('-v')
	import doctest
	numfail,numtests=doctest.testmod()
	if numfail==0: print 'ok'
	else: 
	    print 'FAILED'
	    success=False

    if options.allStations:
	for station in stationsWaterLevel:
	    # FIX: probably better to pull all the stations together somehow
	    print station,':',getWaterLevelNow(station,options.verbose)
	    sys.stdout.flush() # Get the data out as soon as possible.  This get is SLOW!
    else:
	print getWaterLevelNow(options.station,options.verbose)

    if not success:
	sys.exit('Something Failed')

