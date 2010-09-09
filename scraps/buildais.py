#!/usr/bin/env python

__version__ = '$Revision: 4791 $'.split()[1]
__date__ = '$Date: 2006-09-24 14:01:41 -0400 (Sun, 24 Sep 2006) $'.split()[1]
__author__ = 'Kurt Schwehr'

__doc__='''

Use NMEA GGA and ZDA messages to construct a synthetic AIS track.

@requires: U{epydoc<http://epydoc.sourceforge.net/>} > 3.0alpha3
@requires: U{BitVector <http://>} 
@requires: U{pyproj <http://>} 
@requires: U{<http://>} 
@requires: U{<http://>} 

@author: U{'''+__author__+'''<http://schwehr.org/>}
@version: ''' + __version__ +'''
@copyright: 2006
@var __date__: Date of last svn commit
@undocumented: __version__ __author__ __doc__ parser
@since: 2006-Sep-24
@status: under development
@organization: U{CCOM<http://ccom.unh.edu/>}
@license: GPL v2

@todo: Calc ROT and make sure the Kurt coded ROT correctly in the message
@todo: Handle the comm state so that they make some sort of sense
'''

#timeshift = 0 # 27593333 # to get the transit to be the same time

import sys, calendar
from decimal import Decimal

from BitVector import BitVector

import nmea
import nmeamessages as nm
import ais.ais_msg_1 as m1
import ais.binary as binary

from pyproj import Proj
import math

#mmsi='999999'
#mmsi='369862000' # NOAA Bay Hydrographer


msg1Dict={
    'COG': Decimal("34.5"),
    'MessageID': 1,
    'NavigationStatus': 3,
    'PositionAccuracy': 1,
    'RAIM': False,
    'ROT': -2,
    'RegionalReserved': 0,
    'RepeatIndicator': 1,
    'SOG': Decimal("4.9"), # knots
    'Spare': 0,
    'TimeStamp': 35,
    'TrueHeading': 41,
    'UserID': 0,
    'latitude': None,
    'longitude': None,
    'state_slotoffset': 1221,
    'state_slottimeout': 0,
    'state_syncstate': 2
    }

def getDist (utm1,utm2):
    lon1, lat1 = utm1
    lon2, lat2 = utm2
    dx = (lon1-lon2)
    dy = (lat1-lat2)
    return math.sqrt(dx*dx + dy*dy)

def getHeading (utm1,utm2):
    'direction from utm1 to utm2'
    lon1, lat1 = utm1
    lon2, lat2 = utm2
    dx = (lon1-lon2)
    dy = (lat1-lat2)
    #print 'dx/dy:',dx,dy
    headingRad = math.atan2(dx,dy)
    headingDeg = math.degrees(headingRad)
    if 0>headingDeg: headingDeg+=360
    return headingDeg

if __name__=='__main__':

    from optparse import OptionParser

    parser = OptionParser(usage="%prog [options]", version="%prog "+__version__)

    parser.add_option('-m','--mmsi',dest='shipMMSI',type='int'
                      ,default=369862000
                      ,help='Ship MMSI for the ship to be tracked [default: %default (NOAA Bay Hydrographer)]')
    parser.add_option('-r','--receiver',dest='receiverMMSI'
                      ,type='string'
                      ,default='338040883'
                      ,help='Receiver station ID.  [default: %default (Kurt\'s MMSI)]')
    parser.add_option('-t','--timeshift',dest='timeshift',type='int'
                      ,default=0
                      ,help='How many seconds to shift the time in the ZDA strings [default: %default]')

    parser.add_option('-v','--verbose',dest='verbose',default=False,action='store_true'
                      ,help='Make the program be verbose')

    # FIX: add ais messages for Class B position reports... 24??
#    aisMsgNumbers=('1','2','3')
#    parser.add_option('-a','--ais-msg-num',dest='aisMsgNum'
#                      ,choices=aisMsgNumbers, default=1
#                      ,help='Which type of position report to use [default: %d].  Choices: '
#                      +' '.join([str(c) for c in aisMsgNumbers])
#                      )
                      
# Might as well always do the heading calculation
#    parser.add_option('-H','--no-heading',dest='computeHeading',default='False'
#                      ,action='store_true'
#                      ,help='Compute the headings for ships based on delta position'
#                      )

    parser.add_option('-o','--output',dest='outFile',type='string'
                      ,default=None
                      ,help='Where to write the resulting stream [default: stdout]')


    (options,args) = parser.parse_args()

    verbose = options.verbose

    msg1Dict['mmsi'] = options.shipMMSI

    # FIX: make the zone auto detect!
    params={'proj':'utm','zone':19} #int(options.zone)}
    proj = Proj(params)

    out = sys.stdout
    if options.outFile!=None: out = file(options.outFile,'w')

#    aisMsgNum = int(options.aisMsgNum)

    # FIX: Allow for stdin

    for filename in args:
        if verbose:
            sys.stderr.write('file: '+filename+'\n')
        timeBase=None
        linenum=0
        lastPos=None
        for line in file(filename):
            linenum+=1
            if verbose and linenum%1000==0:
                sys.stderr.write('line '+str(linenum)+'\n')
            if line[:6]=='$GPZDA':
                z = nm.zdaDecode(line)
                timeBase = (int(z['year']),int(z['mon']),int(z['day']))
            if line[:6]=='$GPGGA' and timeBase!=None:
                g = nm.ggaDecode(line)
                ts = calendar.timegm(timeBase+((g['hour'],g['min'],g['decimalsec'])))
                
                
                if None==lastPos:
                    utm = proj(float(g['lon']),float(g['lat']))
                    lastPos=(utm, ts)
                    continue # nothing to do on the first pos

                
                utmNew = proj(float(g['lon']),float(g['lat']))
                utmOld,tsOld = lastPos
                lastPos = (utmNew,ts)

                deltaT = ts - tsOld
                dist = getDist(utmOld,utmNew)
                if 0 != deltaT:
                    speedMetersPerSec = dist/deltaT
                else:
                    sys.stderr.write('zero delta T for line:\n  '+line)
                    speedMetersPerSec=0

                speedKnots = 1.9438445 * speedMetersPerSec
                heading = getHeading(utmOld,utmNew)
                
                ts += options.timeshift

                msg1Dict['longitude']=Decimal(str(g['lon']))
                msg1Dict['latitude']=Decimal(str(g['lat']))
                #print 'heading',heading
                #print msg1Dict['longitude'],msg1Dict['latitude']
                msg1Dict['COG'] = int(heading)
                msg1Dict['TrueHeading'] = int(heading)  # Force both COG and TrueHeading to point forward
                #if verbose:
                #    print 'speedKnots',speedKnots,'speedMetersPerSec',speedMetersPerSec,'FROM',dist,deltaT
                msg1Dict['SOG']=Decimal(str(speedKnots))

                bits = m1.encode(msg1Dict)
                pad = 6 - (len(bits)%6)
                if pad!=0: bits = bits + BitVector(size=(6 - (len(bits)%6)))

                aisPayloadStr = binary.bitvectoais6(bits)[0]

                aisStr = '!AIVDM,1,1,,A,'+aisPayloadStr+','+str(pad)+'*'
                aisStr += nmea.checksumStr(aisStr)
                out.write(aisStr+',r'+options.receiverMMSI+','+str(ts)+'\n')

