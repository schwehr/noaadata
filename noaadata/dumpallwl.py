#!/usr/bin/env python2.4


__version__ = '$Revision: 6041 $'.split()[1]
__date__ = '$Date: 2007-04-23 11:22:18 -0400 (Mon, 23 Apr 2007) $'.split()[1]
__author__ = ''

__doc__=''' 
Create AIS NMEA strings for NOAA CO-OPS tide data. Try to pull all the
water level messages for a station over a long time period

fugly code

@requires: U{Python<http://python.org/>} >= 2.4
@requires: U{epydoc<http://epydoc.sourceforge.net/>} >= 3.0beta1
@requires: U{lxml}
@requires: U{soappy}

@author: U{'''+__author__+'''<http://schwehr.org/>}
@version: ''' + __version__ +'''
@copyright: 2007
@var __date__: Date of last svn commit
@undocumented: __version__ __author__ __doc__ parser success
@since: 2007-Apr-23
@status: Intial working version.  Still needs development
@organization: U{CCOM<http://ccom.unh.edu/>}

@license: GPL v2

'''

import sys
from SOAPpy import SOAPProxy
#import pysqlite2.dbapi2 as sqlite
#import pysqlite2.dbapi2

#import make_waterlevel_ais as wl_ais
import ais.waterlevel as wl_ais
import ais.ais_msg_8 as msg8_ais
from ais.nmea import buildNmea
import noaadata.stations as Stations
from decimal import Decimal
import calendar

stations = Stations.ActiveStations(forceCache=True)

url ='http://opendap.co-ops.nos.noaa.gov/axis/services/WaterLevelRawSixMin'
namespace='urn:WaterLevelRawSixMin' # This really can be anything.  It is ignored

daysPerMon=[-1,31,28,31,30,31,30,31,31,30,31,30,31]
monthLUT = {
    'Jan':1,
    'Feb':2,
    'Mar':3,
    'Apr':4,
    'May':5,
    'Jun':6,
    'Jul':7,
    'Aug':8,
    'Sep':9,
    'Oct':10,
    'Nov':11,
    'Dec':12
}
def splitNoaaDateTimeSoap(datetimeStr):
    '''
    Splits a noaa utc time into fields that are more usable.

    #>>> splitNoaaDateTime('Jan  4 2007  4:36PM')
    #(2007,1,4,16,36)

    >>> splitNoaaDateTime('2007-01-31 00:06:00.0')
    (2007,1,13,00,06)

    '''
    fields = datetimeStr.split()
    yr,mo,da=fields[0].split('-')

    hr,mi,sec, = fields[1].split(':')

    return yr,mo,da,hr,mi

def noaawaterlevel2aisMsg8Nmea(stationID,mmsi,datum,wl,verbose=False,debug=False):
    '''
    Return one long NMEA string.  This will be oversized for the nmea spec.
    '''
    #print 'noaawaterlevel2aisMsg8Nmea\n  ',wl
    payloadBits = noaawaterlevel2aisBits(stationID,mmsi=mmsi,datum=datum,wl=wl,verbose=verbose,debug=debug)

    nmeaStr = buildNmea(payloadBits)

    ts=wl.timeStamp
    fields = ts.split()
    yr,mo,da=fields[0].split('-')
    hr,mi,sec = fields[1].split(':')
    sec=sec.split('.')[0]
    if sec[0]=='0': sec=sec[1:]
    timestamp = calendar.timegm((int(yr),int(mo),int(da),int(hr),int(mi),int(sec)))
    nmeaStr += ',r'+str(mmsi)+','+str(timestamp)

    return nmeaStr

def noaawaterlevel2aisBits(stationID,mmsi,datum,wl,verbose=False,debug=False):
    '''
    Return an AIS string of the latest waterlevel.
    @param stationID: which station to query (e.g. '8639348')
    @type stationID: str
    @param wl: one entry from a soap query
    @param verbose: Set to true for print messages
    @param debug: Do not actually fetch any real data (fast for debugging)
    @param datum: MSL,MLLW

    @return: bits for the message payload
    @rtype: BitVector
    '''
    #wl = None
    #wl = wl_dap.getWaterLevelNow(stationID,verbose,datum)
    if verbose: print 'water level dict:',wl

    # FIX: check for link down state and return a link down packet

    params = {}

    # Beginning of AIS message 8 BBM
    # MessageID
    params['RepeatIndicator'] = 1
    params['UserID'] = int(mmsi)
    # Spare

    # Commented params are those that are required by the spec and do not need to be set.
    # params['dac'] = 366  # params['fid'] = 1  # params['efid'] = 1
    yearDummy, monthDummy, dayDummy, hourDummy, minDummy = splitNoaaDateTimeSoap(wl.timeStamp)
    params['month'] = int(monthDummy)
    params['day']   = int(dayDummy)
    params['hour']  = int(hourDummy)
    params['min']   = int(minDummy)
    params['sec']   = 0  # No seconds in timestamp
    params['stationid']     = str(stationID)
    station = stations.getStation(str(stationID))
    params['longitude'] = Decimal(str(station.getLon()))
    params['latitude']  = Decimal(str(station.getLat()))
    params['waterlevel'] = int(float(wl.WL)*100) # Convert to CM
    if verbose:
        print params['waterlevel'], wl.WL
    params['datum']      = int(wl_ais.datumEncodeLut[datum])
    params['sigma']      = float(wl.sigma)
    params['o']          = int(wl.O)
    
    if params['o']<0:
        print 'wl.O',wl.O, params['o'],'FIX: what does this mean?  Forcing O to be positive'
        params['o'] = -params['o']
    

    if bool(wl.L): params['levelinferred'] = True
    else:          params['levelinferred'] = False
    if bool(wl.F): params['flat_tolerance_exceeded'] = True
    else:          params['flat_tolerance_exceeded'] = False
    if bool(wl.R): params['rate_tolerance_exceeded'] = True
    else:          params['rate_tolerance_exceeded'] = False
    params['temp_tolerance_exceeded']  = False	# FIX: Where is the code for this???
    params['expected_height_exceeded'] = False  # FIX: Where is the code for this???
    params['link_down'] = False         

    if verbose:
	wl_ais.printFields(params)
        print 'params dump:'
        for item in params.keys():
            print '  ',item,params[item]

    return wl_ais.encode(params)

if __name__=='__main__':

    from optparse import OptionParser

    parser = OptionParser(usage="%prog [options] [file1] [file2] ...",
                          version="%prog "+__version__+' ('+__date__+')')

    parser.add_option('-y','--year',dest='year',default='2006'
                      ,help='Year of the water levels  (Default is Money Point) [default: %default]')

    parser.add_option('-m','--month-start',dest='monthStart',default='1',type='int'
                      ,help='Starting month (Default is Money Point) [default: %default]')
    parser.add_option('-M','--month-end',dest='monthEnd',default='12',type='int'
                      ,help='Ending month (Default is Money Point) [default: %default]')

    parser.add_option('-s','--station',dest='station',default='8639348'
                      ,help='Specify the station to print.  (Default is Money Point) [default: %default]')
    parser.add_option('--mmsi',dest='mmsi',default='338040883'
                      ,help='Specify the station to print.  (Default MMSI belongs to Kurt) [default: %default]')
    parser.add_option('-o','--output',dest='outputFileName',default=None,
		      help='Name of the python file to write [default: stdout]')

    # FIX: make choice...
    parser.add_option('-d','--datum',dest='datum',default='MSL',
		      help='What reference datum to use for the water levels [default: %default]')


    parser.add_option('-v','--verbose',dest='verbose',default=False,action='store_true',
		      help='Make the test output verbose')

    (options,args) = parser.parse_args()

    verbose = options.verbose
    stationId=options.station
    mmsi = options.mmsi
    #stationId=8638610
    #mmsi=338040883

    o=sys.stdout
    if options.outputFileName!=None:
        o = file(options.outputFileName,'w')


    server = SOAPProxy(url,namespace)

#     for mon in range(1,13):
#         beginDate='2006'+('%02d' % mon )+'01'
#         endDate='2006'+('%02d' % mon )+str(daysPerMon[mon])
#         print beginDate,'...',endDate
#         response = server.getWaterLevelRawSixMin(stationId=str(stationId),beginDate=beginDate,endDate=endDate,datum='MSL',unit=0,timeZone=0)
#         print len(response.item)
#         #print response


    for mon in range(options.monthStart,options.monthEnd+1):
        #print mon
        beginDate=str(options.year)+('%02d' % mon )+'01'
        endDate=str(options.year)+('%02d' % mon )+str(daysPerMon[mon])
        #if verbose:
        print beginDate,'...', endDate
        response = server.getWaterLevelRawSixMin(stationId=str(stationId)
                                                 ,beginDate=beginDate,endDate=endDate,
                                                 datum=options.datum
                                                 ,unit=0
                                                 ,timeZone=0)
        for wl in  response.item:
            #if verbose:
            #    print wl
            try:
                wlStr = noaawaterlevel2aisMsg8Nmea(stationId,mmsi,datum=options.datum,wl=wl)
            except:
                print 'ERROR: something with this line'
                print wl
                continue
            #if verbose: print wlStr
            o.write( wlStr + '\n' )

    if False:
        beginDate='20070401'
        endDate='20070401'
        #datum='MSL'
        #print beginDate,'...',endDate
        response = server.getWaterLevelRawSixMin(stationId=str(stationId),beginDate=beginDate,endDate=endDate,datum=options.datum,unit=0,timeZone=0)
        #print len(response.item)
        #wl = response.item[1]
        for wl in response.item:
            #print wl
            wlStr = noaawaterlevel2aisMsg8Nmea(stationId,mmsi,datum=options.datum,wl=wl)
            if verbose: 
                print wlStr
            o.write( wlStr + '\n' )

