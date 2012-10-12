#!/usr/bin/env python

__version__ = '$Revision: 8143 $'.split()[1]
__date__ = '$Date: 2008-01-07 19:19:20 -0500 (Mon, 07 Jan 2008) $'.split()[1]
__author__ = 'Kurt Schwehr'

__doc__='''
Normalize AIS messages so that each message takes exactly one line.  Works
like a Queue.  Messages must use the uscg format.

Rewrite from the command line only ais_normalize

@requires: U{epydoc<http://epydoc.sourceforge.net/>} > 3.0alpha3
@requires: U{BitVector<http://cheeseshop.python.org/pypi/BitVector>}

@author: U{'''+__author__+'''<http://schwehr.org/>}
@version: ''' + __version__ +'''
@var __date__: Date of last svn commit
@undocumented: __version__ __author__ __doc__ parser
@status: under development
@license: GPL v2
@since: 2008-Jan-30
@organization: U{CCOM<http://ccom.unh.edu/>}
@see: U{Queue<http://www.python.org/doc/current/lib/QueueObjects.html>}
'''

import sys
import Queue
import uscg
import ais.nmea
#from decimal import Decimal
#from BitVector import BitVector
#import StringIO


#from ais.nmea import isChecksumValid,checksumStr # Needed for checksums
#import ais.nmea

class Normalize(Queue.Queue):
    '''
    Provide a channel that normalizes messages.  Try to model it like a Queue.
    '''
    def __init__(self,maxsize=0,ttl=30,verbose=False):
        '''
        param ttl: number of seconds that a message fragment can live
        '''
        Queue.Queue.__init__(self,maxsize)
        self.mostRecentTime=0 # Seconds from UTC epoch
        self.ttl=ttl
        self.stations={}  # Buffer by station
        self.v=verbose

    def cull(self):
        '''
        Drop messages older than the ttl
        '''
        pass

    def put(self,uscgNmeaStr,block=True,timeout=None):

        cgMsg = uscg.UscgNmea(uscgNmeaStr)
        if self.mostRecentTime<cgMsg.cg_sec:
            self.mostRecentTime = cgMsg.cg_sec


        # single line message needs no help
        if 1 == cgMsg.totalSentences:
            Queue.Queue.put(self,uscgNmeaStr,block,timeout)
            return

        if cgMsg.sentenceNum!=cgMsg.totalSentences:
            station = cgMsg.station
            if station not in self.stations:
                self.stations[station] = [cgMsg,]
            else:
                #print 'self.stations[station]',station,type(self.stations[station])
                self.stations[station].append(cgMsg)
            self.cull()  # Clean house so the buffers do not get too large
            return

        # We have a final sentence, so construct the whole deal

        # Only can happen the first time we see a station and have not seen the first sentence
        if cgMsg.station not in self.stations:
            sys.stderr.write('dropping dangling fragment\n')
            return

        cgMsgFinal = cgMsg
        stationList = self.stations[cgMsgFinal.station]

        parts=[]
        payloads=[]

        del cgMsg

        for msg in stationList:
            if (msg.aisChannel == cgMsgFinal.aisChannel
                and msg.sequentialMsgId == cgMsgFinal.sequentialMsgId
                ):
                if msg.sentenceNum==1:
                    cgMsgFinal.cg_sec=msg.cg_sec # Save the first timestamp
                parts.append(msg)
                payloads.append(msg.contents)#.getBitVector)
                assert(msg.fillbits==0)

        #print 'num parts',len(parts)

        #print 'before',len(stationList)
        for cgMsg in parts:
            stationList.remove(cgMsg)
        #print 'after',len(stationList)

        if len(parts)!=cgMsgFinal.totalSentences-1:
            if self.v: sys.stderr.write('partial message.  Discarding\n')
            return

        payloads.append(cgMsgFinal.contents)
        #print 'payloads:', payloads

        # The fill bits will not change
        #bv = payloads[0]
        payload = ''.join(payloads)
        #print payload
        #parts.append(cgMsgFinal.getBitVector)

        cgMsgFinal.totalSentences=1
        cgMsgFinal.sentenceNum=1
        cgMsgFinal.contents = payload
        cgMsgFinal.checksumStr = ais.nmea.checksumStr(payload)
        newNmeaStr = cgMsgFinal.buildNmea()
        #print 'queuing',newNmeaStr
        Queue.Queue.put(self,newNmeaStr,block,timeout)
