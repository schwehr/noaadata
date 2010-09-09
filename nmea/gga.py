#!/usr/bin/env python
__version__ = '$Revision: 2068 $'.split()[1]
__date__ = '$Date: 2006-05-02 08:17:59 -0400 (Tue, 02 May 2006) $'.split()[1]
__author__ = 'Kurt Schwehr'

__doc__='''
Generate/decode NMEA messages.  For now, this just supports ZDA time stamps.

@author: '''+__author__+'''
@version: ''' + __version__ +'''
@copyright: 2006

@var __date__: Date of last svn commit

@undocumented: __version__ __author__ __doc__ myparser
'''

# Python standard libraries
import time, sys

# Local
import nmea
#import verbosity
#from verbosity import BOMBASTIC,VERBOSE,TRACE,TERSE,ALWAYS
import calendar # to make the seconds since the epoch


timekeepers={
    'ZA': 'atomic clock',
    'ZC': 'chronometer',
    'ZQ': 'quartz',
    'ZV': 'radio update'
}
'list of the valide clock sources'

def zdaEpochSeconds(nmeaStr):
    '''
    Return the seconds since the Epoch 

    @todo: implement
    '''
    z = zdaDecode(nmeaStr)
    print z
    return calendar.timegm((z['year'],z['mon'],z['day'],z['hour'],z['min'],z['sec']))


def zdaDecode(nmeaStr):
    '''
    Decode quartz time nmea messages.

    >>> zdaDecode('$ZQZDA,110003.00,27,03,2006,-5,00*47')
    {'timekeeper': 'ZQ', 'localzonehour': -5, 'localzonemin': 0, 'hour': 11, 'min': 0, 'hsec': 0, 'sec': 3, 'mon': 3, 'year': 2006, 'day': 27}

    @param nmeaStr: ZDA message to decode
    @type nmeaStr: str
    @rtype: dict
    @return: name value pairs for the GMT time of the message
    '''
    # FIX: strip off new line here?
    assert(len(nmeaStr)>20)
    assert(nmeaStr[0] in ('$','!'))
    assert(nmeaStr[3:6]=='ZDA')
    #print nmeaStr, nmea.isChecksumValid(nmeaStr)
    #assert(nmea.isChecksumValid(nmeaStr))
    fields = nmeaStr.split(',')
    val={}
    val['timekeeper']=fields[0][1:3]
    val['hour']=int(fields[1][0:2])
    val['min']=int(fields[1][2:4])
    val['sec']=int(fields[1][4:6])
    assert(fields[1][6]=='.')
    val['hsec']=int(fields[1][7:9]) # hundredths of seconds
    val['day']=int(fields[2])
    val['mon']=int(fields[3])
    val['year']=int(fields[4])
    val['localzonehour']=int(fields[5])
    val['localzonemin']=int(fields[6][0:2])

    return val

def ggaDecode(nmeaStr,validate=False):
    '''
    Decode NMEA GPS FIX data

    $GPGGA,152009.00,3652.48059177,N,07620.02018248,W,1,11,0.8,3.669,M,-34.579,M,,*57

    @param nmeaStr: nmea string to decode
    '''
    if validate:
        assert(len(nmeaStr)>=71)
        assert(len(nmeaStr)<=78)
        assert(nmeaStr[0] in ('$','!'))
        assert(nmeaStr[3:6]=='GGA')
        #assert(nmea.isChecksumValid(nmeaStr))
    fields = nmeaStr.split(',')
    r={} # Results dict to be returned
    r['hour']=fields[1][0:2]
    r['min']=fields[1][2:4]
    r['sec']=fields[1][4:6]
    r['hsec']=fields[1][7:9] # hundreths of seconds
    r['lat']=float(fields[2][0:2]) + float(fields[2][2:])/60.
    if fields[3]=='S': r['lat']=-r['lat']

    # FIX: lon probably will fail for 
    lon = fields[4][:3]
    if lon[0]=='0': lon = lon[1:]
    r['lon']=float(lon) + float(fields[4][3:])/60.
    if fields[5]=='W': r['lon']=-r['lon']
    r['qual']=int(fields[6])
    r['sats']=int(fields[7])
    r['horz_dilution']=float(fields[8]) # meters
    r['alt']=float(fields[9]) # altitude in meters above the geoid, meters
    r['alt_units']=fields[10]
    r['geoidal_sep']=float(fields[11])
    r['geoidal_sep_units']=fields[12]
    try:
        r['age']=float(fields[13])
    except:
        r['age']=None
    r['diff_ref_station']=fields[14]
    return r

'''
GGA - Global Positioning System Fix Data
Time, Position and fix related data for a GPS receiver.

        1         2       3 4        5 6 7  8   9  10 |  12 13  14   15
        |         |       | |        | | |  |   |   | |   | |   |    |
 $--GGA,hhmmss.ss,llll.ll,a,yyyyy.yy,a,x,xx,x.x,x.x,M,x.x,M,x.x,xxxx*hh<CR><LF>

 Field Number: 
  1) Universal Time Coordinated (UTC)
  2) Latitude
  3) N or S (North or South)
  4) Longitude
  5) E or W (East or West)
  6) GPS Quality Indicator,
     0 - fix not available,
     1 - GPS fix,
     2 - Differential GPS fix
     (values above 2 are 2.3 features)
     3 = PPS fix
     4 = Real Time Kinematic
     5 = Float RTK
     6 = estimated (dead reckoning)
     7 = Manual input mode
     8 = Simulation mode
  7) Number of satellites in view, 00 - 12
  8) Horizontal Dilution of precision (meters)
  9) Antenna Altitude above/below mean-sea-level (geoid) (in meters)
 10) Units of antenna altitude, meters
 11) Geoidal separation, the difference between the WGS-84 earth
     ellipsoid and mean-sea-level (geoid), "-" means mean-sea-level
     below ellipsoid
 12) Units of geoidal separation, meters
 13) Age of differential GPS data, time in seconds since last SC104
     type 1 or 9 update, null field when DGPS is not used
 14) Differential reference station ID, 0000-1023
 15) Checksum

$GPGGA,152009.00,3652.48059177,N,07620.02018248,W,1,11,0.8,3.669,M,-34.579,M,,*57
'''

def zdaDict2TIMESTAMP(zdaDict):
    '''
    Make an SQL TIMESTAMP from the results of a zdaDecode

    >>> zdaDict2TIMESTAMP({'hour': 11, 'min': 0, 'hsec': 0, 'sec': 3, 'mon': 3, 'year': 2006, 'day': 27})
    '2006-03-27 11:00:03'

    @param zdaDict: output from zdaDecode
    @type zdaDict: dict
    @return: TIMESTAMP
    @rtype: str
    '''
    s=''
    s+=str(zdaDict['year'])
    s+='-'+('%02d' % zdaDict['mon'])
    s+='-'+('%02d' % zdaDict['day'])
    s+=' '+('%02d' % zdaDict['hour'])
    s+=':'+('%02d' % zdaDict['min'])
    s+=':'+('%02d' % zdaDict['sec'])
    return s


######################################################################

# if __name__=='__main__':
#     from optparse import OptionParser
#     myparser = OptionParser(usage="%prog [options]",
# 			    version="%prog "+__version__)
#     myparser.add_option('--test','--doc-test',dest='doctest',default=False,action='store_true',
#                         help='run the documentation tests')
#     verbosity.addVerbosityOptions(myparser)
#     (options,args) = myparser.parse_args()

#     success=True

#     if options.doctest:
# 	import os; print os.path.basename(sys.argv[0]), 'doctests ...',
# 	sys.argv= [sys.argv[0]]
# 	if options.verbosity>=VERBOSE: sys.argv.append('-v')
# 	import doctest
# 	numfail,numtests=doctest.testmod()
# 	if numfail==0: print 'ok'
# 	else: 
# 	    print 'FAILED'
# 	    success=False

#     if not success:
# 	sys.exit('Something Failed')
