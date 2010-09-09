#!/usr/bin/env python

'''
Run a water level message from NMEA to decoded
'''

import sys
from BitVector import BitVector
import binary
import ais_msg_8
#import sls.header
import sls.waterlevel

if __name__=='__main__':

    print 'FIX: broken'
    vdm='!AIVDM,1,1,4,A,8030ot1?0@>PSpPPPC<2<oURAU=>T08f@02PSpPPP3C3<oU=d5<U00BH@02PSpPPP3C3EoU:A5<TwPPO@02PSpPPP2hk<oRWU5;si0Pl@02O<0PPPP3D<oPPEU;M418g@02PSpPPP2hlEoRQgU;j@17p@00,2*32'
    msg=vdm.split(',')[5]
    bvMsg = binary.ais6tobitvec(msg)

    msg8 = ais_msg_8.decode(bvMsg)
    bvMsg8 = msg8['BinaryData']
    del msg8['BinaryData']
    ais_msg_8.printFields(msg8)

    print

    # Now deal with the St Lawrence Seaway Header
    slsHdr = sls_header.decode(bvMsg8)
    bvHdr = slsHdr['BinaryData']
    del slsHdr['BinaryData']
    sls_header.printFields(slsHdr)

    #print slsHdr.keys()
    print

    wl = sls_waterlevel.decode(bvHdr)
    sls_waterlevel.printFields(wl)
