#!/usr/bin/env python
'''

@todo: turn this into a real test runner for everything in the test subdir.
'''
import sys
from aisutils.BitVector import BitVector
from aisutils import binary
import ais_msg_1
import ais_msg_8
import sls.waterlevel


if __name__=='__main__':

    # Try to parse some binary message
    if False:
        nmeaStr='!AIVDM,1,1,,A,85OpLV1Kf98p96dWWPLSViUfJlU@SV>cDF2Wq5>`=u8CnEFGCIOq,0*70,r003669983,1165795916'

        msgPayload = nmeaStr.split(',')[5]
        print 'nmea string:    ',nmeaStr
        print 'message payload:',msgPayload
        bv = binary.ais6tobitvec(msgPayload)
        print len(bv), bv

        msgDict = ais_msg_8.bin_broadcastDecode(bv)
        ais_msg_8.bin_broadcastPrintFields(msgDict)

        bv = bv[39:]

        print               'dac: ',bv[:10],int(bv[:10])
        bv = bv[10:]; print 'fid: ',bv[: 6],int(bv[: 6])
        bv = bv[ 6:]; print 'bits:',bv[:16],int(bv[:10])
        bv = bv[10:]; print 'len: ',len(bv)

    # Position message
    if False:
        nmeaStr = '!AIVDM,1,1,,B,15Mt9B001;rgAFhGKLaRK1v2040@,0*2A'
        msgPayload = nmeaStr.split(',')[5]
        print 'nmea string:    ',nmeaStr
        print 'message payload:',msgPayload
        bv = binary.ais6tobitvec(msgPayload)
        msgDict = ais_msg_1.positionDecode(bv)
        ais_msg_1.positionPrint(msgDict)


    # SLS try for waterlevel
    if True:
        bvStr = '010111101000001000100101000001010100110101001100011000001000000000110001100101110101000000001001010011101101000000000000001000000100000000000000'
        bv = BitVector(bitstring=bvStr)
        print type(bv)
        msgDict= sls.waterlevel.decode(bv)
        sls.waterlevel.printFields(msgDict)
