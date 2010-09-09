#!/usr/bin/env python
__version__ = '$Revision: 4762 $'.split()[1]
__date__ = '$Date: 2006-09-19 14:56:22 -0400 (Tue, 19 Sep 2006) $'.split()[1]
__author__ = 'Kurt Schwehr'

__doc__='''
Build the water level binary broadcast message for NOAA water level
stations.  Does NOT use the St Lawrence Seaway message format.

@todo: How do I sync the clocks on my computer to those at NOAA?

@see: U{NOAA DODS/OPeNDAP page<http://opendap.co-ops.nos.noaa.gov/dods/>}
@requires: U{pydap/dap-py<http://pydap.org/>}
@requires: U{epydoc<http://epydoc.sourceforge.net/>}

@author: U{'''+__author__+'''<http://schwehr.org/>}
@license: GPL v2
@copyright: (C) 2007 Kurt Schwehr
@version: ''' + __version__ +'''
@since: 04-Jan-2007

@var __date__: Date of last svn commit
@undocumented: __version__ __author__ __doc__ parser success 

'''

import sys, os
from decimal import Decimal
#import decimal.Decimal as Decimal

import noaadata.stations as Stations
import noaadata.waterlevel_dap as wl_dap
from ais.nmea import buildNmea

import ais.waterlevel as wl_ais
import ais.ais_msg_8 as msg8_ais
import ais.nmea
from BitVector import BitVector

stations = Stations.ActiveStations(forceCache=True)

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

def splitNoaaDateTime(datetimeStr):
    '''
    Splits a noaa utc time into fields that are more usable.

    >>> splitNoaaDateTime('Jan  4 2007  4:36PM')
    (2007,1,4,16,36)
    '''
    fields = datetimeStr.split()
    yr = fields[2]
    mo = monthLUT[fields[0]]
    da = fields[1]
    hr = int(fields[3].split(':')[0])
    if fields[3][-2]=='P': hr += 12
    mi = fields[3].split(':')[1][:2]
    return yr,mo,da,hr,mi


def noaawaterlevel2aisMsg8Nmea(stationID,mmsi,verbose=False,debug=False):
    '''
    Return one long NMEA string.  This will be oversized for the nmea spec.
    '''

    payloadBits = noaawaterlevel2aisBits(stationID,mmsi=mmsi,verbose=verbose,debug=debug)

    #params = {}
    #params['MessageID'] = 8
    #params['RepeatIndicator'] = 1
    #params['UserID'] = int(mmsi)
    #params['Spare'] = 0
    #params['BinaryData'] = payloadBits

    #msg8bits = msg8_ais.encode(params)
    #nmeaStr = buildNmea(msg8bits)

    nmeaStr = buildNmea(payloadBits)

    bbmPayloadBitsNoPad = payloadBits[40:]
    print 'lenpayload',len(bbmPayloadBitsNoPad)
#     padLen=6 - (len(bbmPayloadBitsNoPad)%6)
#     if 0!= padLen:
#         pad = BitVector( bitlist = [0,]*padLen )
#         bbmPayloadBits = bbmPayloadBitsNoPad + pad
#     else:
#         bbmPayloadBits = bbmPayloadBitsNoPad

    print bbmPayloadBitsNoPad
    bbmPayloadStr,padLen = ais.binary.bitvectoais6(bbmPayloadBitsNoPad)

    print bbmPayloadBitsNoPad
    print ais.binary.ais6


    print 'pad len',padLen

    bbmStr = ais.nmea.bbmEncode(1 # totSent=
                                ,1 # sentNum=
                                ,0 # seqId=
                                ,3 # aisChan=
                                ,8 # MsgId
                                , bbmPayloadStr #bbmPayloadBits # data=
                                ,padLen # numFillBits=
                                )


    s = bbmStr[1:-3]
    print bbmStr
    print s
    sum=0
    for c in s: sum = sum ^ ord(c)
    sumHex= "%x" % sum
    print 'checksum should be:', sumHex.upper()


    return nmeaStr,bbmStr

def noaawaterlevel2aisBits(stationID,mmsi,verbose=False,debug=False,datum='MSL'):
    '''
    Return an AIS string of the latest waterlevel.
    @param stationID: which station to query (e.g. '8639348')
    @type stationID: str
    @param verbose: Set to true for print messages
    @param debug: Do not actually fetch any real data (fast for debugging)
    @param datum: MSL,MLLW

    @return: bits for the message payload
    @rtype: BitVector
    '''
    wl = None
    if debug:
	print 'Using a testing dict for waterlevel'
	wl = {
	    '_STATION_ID': '8639348',
	    '_DATUM': datum, #'MLLW',
	    '_BEGIN_DATE': '20070104 16:24',
	    '_END_DATE': '20070104 16:54',
	    'DCP': '1',
	    'SENSOR_ID': 'A1',
	    'DATE_TIME': 'Jan  4 2007  4:36PM', 
	    'WL_VALUE': 0.674,
	    'SIGMA': 0.005,
	    'O': 0, # Samples outside of 3 sigma
	    'F': 0, # Flat Toler
	    'R': 0, # Rate toler exceeded
	    'L': 0, # Level infered
	    }
    else:
	wl = wl_dap.getWaterLevelNow(stationID,verbose,datum)
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
    yearDummy, monthDummy, dayDummy, hourDummy, minDummy = splitNoaaDateTime(wl['DATE_TIME'])
    params['month'] = int(monthDummy)
    params['day']   = int(dayDummy)
    params['hour']  = int(hourDummy)
    params['min']   = int(minDummy)
    params['sec']   = 0  # No seconds in timestamp
    params['stationid']     = wl['_STATION_ID']
    station = stations.getStation(stationID)
    params['longitude'] = Decimal(str(station.getLon()))
    params['latitude']  = Decimal(str(station.getLat()))
    params['waterlevel'] = int(float(wl['WL_VALUE'])*100) # Convert to CM
    print params['waterlevel'], wl['WL_VALUE']
    params['datum']      = int(wl_ais.datumEncodeLut[wl['_DATUM']])
    params['sigma']      = float(wl['SIGMA'])
    params['o']          = wl['O']

 


    #
    # FIX: I think I am missing some values in the returned data!
    # 

    if bool(wl['L']): params['levelinferred'] = True
    else:             params['levelinferred'] = False
    if bool(wl['F']): params['flat_tolerance_exceeded'] = True
    else:             params['flat_tolerance_exceeded'] = False
    if bool(wl['R']): params['rate_tolerance_exceeded'] = True
    else:             params['rate_tolerance_exceeded'] = False
    params['temp_tolerance_exceeded']  = False	# FIX: Where is the code for this???
    params['expected_height_exceeded'] = False  # FIX: Where is the code for this???
    params['link_down'] = False         

    # FIX: put in the timeLastMeastured

        
    #params['timeLastMeasured_month'] = params['timetag_month']
    #params['timeLastMeasured_day']   = params['timetag_day']
    #params['timeLastMeasured_hour']  = params['timetag_hour']
    #params['timeLastMeasured_min']   = params['timetag_min']
    #params['timeLastMeasured_sec']   = 0

    if verbose:
	wl_ais.printFields(params)
        print 'params dump:'
        for item in params.keys():
            print '  ',item,params[item]

    return wl_ais.encode(params)



if __name__ == '__main__':
    from optparse import OptionParser
    parser = OptionParser(usage="%prog [options]",version="%prog "+__version__)
    parser.add_option('-s','--station',dest='station',default='8639348'
                      ,help='Specify the station to print.  (Default is Money Point) [default: %default]')
    parser.add_option('-m','--mmsi',dest='mmsi',default='338040883'
                      ,help='Specify the station to print.  (Default MMSI belongs to Kurt) [default: %default]')

    parser.add_option('-o','--output',dest='outputFileName',default=None,
		      help='Name of the ais VDM nmea file to write [default: stdout]')

    parser.add_option('-O','--bbm-output',dest='bbmOutputFileName',default=None,
		      help='Name of the ais BBM file to write [default: stdout]')

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

    if not success: sys.exit('Something Failed')
    del success # Hide success from epydoc


    #print noaawaterlevel2ais(options.station,options.verbose,debug=True)
    #resultStr = noaawaterlevel2aisMsg8Nmea(options.station,options.mmsi,verbose=options.verbose)#,debug=True)
    vdmStr,bbmStr = noaawaterlevel2aisMsg8Nmea(options.station,options.mmsi,verbose=options.verbose)#,debug=True)

    outfile = sys.stdout
    if None!=options.outputFileName:
	outfile = file(options.outputFileName,'w')
    outfile.write(vdmStr)
    outfile.write('\n')

    outfile = sys.stdout
    if None!=options.bbmOutputFileName:
	outfile = file(options.bbmOutputFileName,'w')
    outfile.write(bbmStr)
    outfile.write('\n')
