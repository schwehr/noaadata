#!/usr/bin/env python
__author__    = 'Kurt Schwehr'
__version__   = '$Revision: 4799 $'.split()[1]
__revision__  = __version__ # For pylint
__date__ = '$Date: 2006-09-25 11:09:02 -0400 (Mon, 25 Sep 2006) $'.split()[1]
__copyright__ = '2008'
__license__   = 'GPL v3'
__contact__   = 'kurt at ccom.unh.edu'

__doc__ ='''
Convert AIS messages from AIVDM binary to IVS C&C NMEA strings

!AIVDM,1,1,,B,15MvrUPP1DG?wfBE`;;IB?vT0<0o,0*03,x144329,b003669712,1224508882
!AIVDM,1,1,,B,181:Jf002AIGoB8?w2TUPTHV0@;Q,0*18,s23690,d-113,T00.60063558,r993669942,1224508880

@requires: U{Python<http://python.org/>} >= 2.5
@requires: U{epydoc<http://epydoc.sourceforge.net/>} >= 3.0.1

@undocumented: __doc__
@since: 2008-Oct-20
@status: under development
@organization: U{CCOM<http://ccom.unh.edu/>}


'''

import nmea.checksum
import uscg
import ais
from math import *
import datetime

def msg_1_to_cnc(nmea_str):
    match_obj = uscg.uscg_ais_nmea_regex.search(nmea_str.strip())
    if match_obj is None:
        # throw exception
        print 'no match!',nmea_str
        return None
    grp = match_obj.group

    bv = ais.binary.ais6tobitvec(grp('body'))
    body = ais.ais_msg_1.decode(bv)

    #ais.ais_msg_1.printFields(body)

    r = ['$C&C',]
    r.append(str(body['UserID'])) # Vehicle name
    r.append(datetime.datetime.utcfromtimestamp(float(grp('timeStamp'))).strftime('%H:%M:%S.0'))
    r.append(str(float(body['longitude'])))
    r.append(str(float(body['latitude'])))
    heading = body['TrueHeading']
    if 511==heading:
        heading = 0 # Unknown, so just point it north
    r.append(str(heading))
    r.append('0.0,0.0,0.0,0.0') # pitch, roll, height, altitude
    r = ','.join(r)
    checksum = nmea.checksum.checksumStr(r)
    return r+'*'+checksum

def test():
    lines='''!AIVDM,1,1,,B,15Mwq1WP01rB2crBh5G:6?v200Rj,0*59,s28057,d-095,T49.46179499,x91028,rRDSULI1,1224516422
'''
    import StringIO
    str_file = StringIO.StringIO(lines)
    for line in str_file.readlines():
        print 'LINE:',line
        cnc_str = msg_1_to_cnc(line)
        print 'cnc:   ',cnc_str
