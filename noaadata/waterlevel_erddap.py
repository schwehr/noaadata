#!/usr/bin/env python
__version__ = '$Revision: 4762 $'.split()[1]
__date__ = '$Date: 2006-09-19 14:56:22 -0400 (Tue, 19 Sep 2006) $'.split()[1]
__author__ = 'Kurt Schwehr'

__doc__='''
Retrieve 6 minute raw water level data from NOAA CO-OPS ERDDAP server.

@see: U{NOAA DODS/OPeNDAP page<http://opendap.co-ops.nos.noaa.gov/dods/>}
@requires: U{pydap/dap-py<http://pydap.org/>}
@requires: U{epydoc<http://epydoc.sourceforge.net/>}

@author: U{'''+__author__+'''<http://schwehr.org/>}
@license: Apache 2.0
@copyright: (C) 2006 Kurt Schwehr
'''

import pandas as pd

# FIX: document the datums
datumList = ['MLLW','MSL','MHW','STND','IGLD','NGVD','NAVD']
unitList = ['Meters','Feet']

import datetime

# Try to hang on to the dataset in case the user wants to do multiple requests
# FIX: how do I prevent epydoc from talking to the NOAA server when documentation is generated?
datasetURL='http://opendap.co-ops.nos.noaa.gov/dods/IOOS/Raw_Water_Level'
"OPeNDAP URL for NOAA CO-OPS database"
"This set only contains raw 6 minute water level data"
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

    startD = d + datetime.timedelta(minutes=-20)
    endD = d + datetime.timedelta(minutes=10)

    data = get_waterlevel(stationId,startD,endD,verbose=verbose, returnDict=returnDict,datum='MSL')
    return data

def get_waterlevel(stationId,start_date,end_date,verbose=False, returnDict=True,datum='MSL'):
    '''
    Use the NOAA COOS ERDDAP service to get 6 minute water levels:
    
    Maybe try erddap hint per https://groups.google.com/forum/#!topic/pydap/rQ82h3ARxkE
    
    '''
    import pandas as pd 
    
    beginDate = '{:04d}{:02d}{:02d}%20{:02d}:{:02d}'.format(start_date.year, start_date.month, start_date.day, start_date.hour, start_date.minute)
    endDate   = '{:04d}{:02d}{:02d}%20{:02d}:{:02d}'.format(end_date.year, end_date.month, end_date.day, end_date.hour, end_date.minute)
    
    # sample url='https://opendap.co-ops.nos.noaa.gov/erddap/tabledap/IOOS_Raw_Water_Level.csv?time%2CWL_VALUE%2CSIGMA%2CO%2CF%2CR%2CL&STATION_ID=%228638610%22&DATUM=%22NAVD%22&BEGIN_DATE=%2220171001%2000%3A00%22&END_DATE=%2220171005%2000%3A00%22'
    
    url = 'https://opendap.co-ops.nos.noaa.gov/erddap/tabledap/IOOS_Raw_Water_Level.csv?time%2CWL_VALUE%2CSIGMA%2CO%2CF%2CR%2CL&STATION_ID=%22{}%22&DATUM=%22{}%22&BEGIN_DATE=%22{}%22&END_DATE=%22{}%22'. format(
        stationId,datum,beginDate,endDate)
    
    df = pd.read_csv(url,index_col='time',parse_dates=True,skiprows=[1])  # skip the units row 
    return df




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
            try:
	        print station,':',getWaterLevelNow(station,options.verbose)
	        sys.stdout.flush() # Get the data out as soon as possible.  This get is SLOW!
            except:
                pass
    else:
	print getWaterLevelNow(options.station,options.verbose)

    if not success:
	sys.exit('Something Failed')

