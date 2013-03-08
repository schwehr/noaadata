#!/usr/bin/env python
__version__ = '$Revision: 2275 $'.split()[1]
__date__ = '$Date: 2006-07-10 16:22:35 -0400 (Mon, 10 Jul 2006) $'.split()[1]
__author__ = 'Kurt Schwehr'

__doc__ = '''
Connect to a socket and forward what is received to another port.
Filter to a list of AIS receivers/basestations.

@author: '''+__author__+'''
@version: ''' + __version__ +'''
@copyright: 2006
@var __date__: Date of last svn commit
@undocumented: __version__ __author__ __doc__ myparser
@status: under development
@license: GPL v2
@since: Jan 2008

@todo: For speed, provide functions that only parse the timestamp, station, etc.
'''
import sys

#import datetime
import time
import datetime
import unittest

from BitVector import BitVector

import ais.sqlhelp # for sec2timestamp
import ais.binary
import ais.nmea

import re

######################################################################
# NEW Regular Expression Parsing Style

#FIX: make the field names be name1_name2 rather than camel case

# USCG has some receivers that emit corrupted fields, so loosen from this
#   | (,s(?P<s_rssi>\d*))
#   | (,d(?P<signal_strength>[-0-9]*))
#   | (,t(?P<t_recver_hhmmss>(?P<t_hour>\d\d)(?P<t_min>\d\d)(?P<t_sec>\d\d.\d*)))
#   | (,T(?P<time_of_arrival>[0-9.]*))
#   | (,x(?P<x_station_counter>[0-9]*))
#   | (,(?P<station>(?P<station_type>[rbB])[a-zA-Z0-9]*))

# AIVDO might not have a channel associated.
uscg_ais_nmea_regex_str = r'''[!$](?P<talker>AI)(?P<stringType>VD[MO])
,(?P<total>\d?)
,(?P<senNum>\d?)
,(?P<seqId>[0-9]?)
,(?P<chan>[AB]?)
,(?P<body>[;:=@a-zA-Z0-9<>\?\'\`]*)
,(?P<fillBits>\d)\*(?P<checksum>[0-9A-F][0-9A-F])
(
  (,S(?P<slot>\d*))
  | (,s(?P<s_rssi>\d*))
  | (,d(?P<signal_strength>[-0-9]*))
  | (,t(?P<t_recver_hhmmss>(?P<t_hour>\d\d)(?P<t_min>\d\d)(?P<t_sec>\d\d.\d*)))
  | (,T(?P<time_of_arrival>[^,]*))
  | (,x(?P<x_station_counter>[0-9]*))
  | (,(?P<station>(?P<station_type>[rbB])[a-zA-Z0-9_-]*))
)*
,(?P<timeStamp>\d+([.]\d+)?)?
'''
'''
Regular expression for parsing a USCG.

* s - receive signal strength indicator (RSSI)
* d - dBm
* S - slot number the message was received in
* x - index counter incremented for each sentence sent by remote site
* T - time of arrival with the minute.  Related to slot number
* r - receive station  r[^Bb] is a receiver, rR receiver, rB basestation, b is basestation
* t - HHMMSS.SS at the receiver (presume this is UTC from the local GPS)

@note: probably not complete
@todo: What is the x field?
@todo: make all fields explicit so errors do not parse
@bug: does not match this>???? !AIVDM,1,1,,B,85MwqdAKf=Wsd5sKUfl@u>DMk70JwpQ2hjnTHlbfcWj<2n<jRtHd,0*7E,x151038,r003669947,1222129826
@bug: is S missing a comma?
@bug: make this conform to the python coding style guides... time_stamp
'''

uscg_ais_nmea_regex = re.compile(uscg_ais_nmea_regex_str,  re.VERBOSE)
'''
Use this pre-comiled regular expression to parse USCG NMEA strings with the extended fields after the checksum
'''

def write_uscg_nmea_fields(nmea_str,out=sys.stdout,indent='\t'):
    '''
    Write out the fields of a USCG nmea string

    @param nmea_str: USCG style nmea string
    @param out: stream object to write to
    @param separator: string to put between each field
    @param indent: how to indent each field
    '''
    match_obj = uscg_ais_nmea_regex.search(nmea_str)
    write(out,indent+'         prefix = '+match_obj.group('prefix')+'\n')
    write(out,indent+'     stringType = '+match_obj.group('stringType')+'\n')
    write(out,indent+'          total = '+match_obj.group('total')+'\n')
    write(out,indent+'         senNum = '+match_obj.group('senNum')+'\n')
    write(out,indent+'          seqId = '+match_obj.group('seqId')+'\n')
    write(out,indent+'           chan = '+match_obj.group('chan')+'\n')
    write(out,indent+'           body = '+match_obj.group('body')+'\n')
    write(out,indent+'       fillBits = '+match_obj.group('fillBits')+'\n')
    write(out,indent+'       checksum = '+match_obj.group('checksum')+'\n')
    write(out,indent+'           slot = '+match_obj.group('slot')+'\n')
    write(out,indent+'              s = '+match_obj.group('s')+'\n')
    write(out,indent+'signal_strength = '+match_obj.group('signal_strength')+'\n')
    write(out,indent+'time_of_arrival = '+match_obj.group('time_of_arrival')+'\n')
    write(out,indent+'              x = '+match_obj.group('x')+'\n')
    write(out,indent+'        station = '+match_obj.group('station')+'\n')
    write(out,indent+'   station_type = '+match_obj.group('station_type')+'\n')
    write(out,indent+'      timeStamp = '+match_obj.group('timeStamp')+'\n')


######################################################################
# OLD Style


def get_station(nmeaStr):
    '''Return the station without doing anything else.  Try to be fast'''
    fields = nmeaStr.split(',')
    station = None
    for i in range(len(fields)-1,5,-1):
        if len(fields[i])==0:
            continue # maybe it should throw a parse exception instead?
        if fields[i][0] in ('b','r'):
            station = fields[i]
            continue
    return station

def get_contents(nmeaStr):
    '''Return the AIS msg string.  AIS goo'''
    return nmeaStr.split(',')[5]

class UscgNmea:
    def __init__(self,nmeaStr=None):
        '''
        Fields:
         - rssi ('s'): relative signal strength indicator
         - signalStrength ('d') - signal strendth in dBm
         - timeOfArrival ('T') - time of arrive from receiver - seconds within the minute
         - slotNumber ('S') - Receive slot number
         - station ('r' or 'b') - station name or id that received the message
         - stationTypeCode - first letter of the station name indicating 'b'asestation or 'r'eceive only (I think)
         - cg_sec - receive time of the message from the logging software.  Unix UTC second timestamp
         - timestamp - python datetime object in UTC derived from the cg_sec

        @todo: parse the other fields?

        @see: Maritime navigation and radiocommunication equipment and
              systems - Digital interfaces - Part 100: Single talker
              and multiple listeners - Extra requirements to IEC
              61162-1 for the UAIS. (80_330e_PAS) Draft...

        '''
        if None!=nmeaStr:
            #if len(nmeaStr)<6:
            #    # FIX: throw exception
            #    sys.stderr.write('Not a AIVDM... too short\n')

            fields = nmeaStr.split(',')
            self.cg_sec=float(fields[-1])
            self.timestamp = datetime.datetime.utcfromtimestamp(self.cg_sec)
            self.sqlTimestampStr = ais.sqlhelp.sec2timestamp(self.cg_sec)
            # See 80_330e_PAS
            #
            self.nmeaType=fields[0][1:]
            self.totalSentences = int(fields[1])
            self.sentenceNum = int(fields[2])
            tmp = fields[3]
            if len(tmp)>0:
                self.sequentialMsgId = int(tmp)
            else:
                self.sequentialMsgId = None
            # FIX: make an int if the above is set
            self.aisChannel = fields[4] # 'A' or 'B'
            self.contents = fields[5]
            self.fillbits = int(fields[6].split('*')[0])
            self.checksumStr = fields[6].split('*')[1] # FIX: this is a hex string.  Convert?

            if self.sentenceNum==1:
                self.msgTypeChar=fields[5][0]
            else:
                self.msgTypeChar=None

            for i in range(len(fields)-1,5,-1):
                if len(fields[i])==0:
                    continue # maybe it should throw a parse exception instead?
                f = fields[i]
                c = f[0] # first charater determines what the field is
		if c in ('b','r','B','R'):
		    self.station = f # FIX: think we want to keep the code in the first char
                    self.stationTypeCode = self.station[0]
                    continue
		    #break # Found it so ditch the for loop
                if c == 's':
                    self.rssi=int(f[1:])
                    continue
                if c == 'd':
                    self.signalStrength = int(f[1:])
                    continue
                if c == 'T':
                    try:
                        self.timeOfArrival = float(f[1:])
                    except:
                        #print 'warning: bogus time of arrival: %s' % (f[1:],)
                        pass
                    continue
                if c == 'S':
                    self.slotNumber = int(f[1:])
                    continue
                if c == 'x':
                    # I don't know what x is
                    self.x = int(f[1:])
                    continue
    def getBitVector(self):
        '''
        @return: bits for the payload (even if this is a multipart)
        @rtype: BitVector
        '''
        return ais.binary.ais6tobitvec(self.contents)

    def __eq__(self,other):
        # Try to be smart for speed
        if self.cg_sec != other.cg_sec: return False
        if self.sentenceNum != other.sentenceNum: return False
        if self.totalSentences != other.totalSentences: return False
        if self.sequentialMsgId != other.sequentialMsgId: return False
        if self.aisChannel != other.aisChannel: return False
        if self.checksumStr != other.checksumStr: return False
        if self.fillbits != other.fillbits: return False
        if self.station != other.station: return False
        if self.contents != other.contents: return False

        # FIX: probably should check for the existance of rssi, signalStrength, etc
        return True

    def __ne__(self,other):
        return not self.__eq__(other)

    def __str__(self):
        return self.buildNmea()

    def buildNmea(self):
        '''Use the values in this message to reconstruct a single line nmea string'''

        parts=['!'+self.nmeaType,str(self.totalSentences),str(self.sentenceNum)]
        if self.sequentialMsgId is None:
            parts.append('')
        else:
            parts.append(str(self.sequentialMsgId))
        parts.append(self.aisChannel)
        parts.append(self.contents)
        parts.append(str(self.fillbits)+'*'+self.checksumStr)

        if 'rssi' in self.__dict__: parts.append('s'+str(self.rssi))
        if 'signalStrength' in self.__dict__: parts.append('d'+str(self.signalStrength))
        if 'timeOfArrival' in self.__dict__: parts.append('T'+str(self.timeOfArrival))
        if 'slotNumber' in self.__dict__: parts.append('S'+str(self.slotNumber))
        if 'x' in self.__dict__: parts.append('x'+str(self.x))

        if self.station: parts.append(self.station)
        parts.append(str(self.cg_sec)) # Always last
        return ','.join(parts)

#    def getDriver(self):
#        '''
#        Return the python module that handles this message type
#        '''
        # FIX: where did I do this nicely?

class TestUscgNmea(unittest.TestCase):
    def testUscgNmea(self):
        un = UscgNmea('!AIVDM,1,1,,B,15Cjtd0Oj;Jp7ilG7=UkKBoB0<06,0*63,s1234,d-119,T12.34567123,r003669958,S4321,1085889680')

        self.failUnlessEqual(un.nmeaType,'AIVDM')
        self.failUnlessEqual(un.totalSentences,1)
        self.failUnlessEqual(un.sentenceNum,1)
        self.failUnlessEqual(un.sequentialMsgId,None)
        self.failUnlessEqual(un.aisChannel,'B')
        self.failUnlessEqual(un.fillbits,0)
        self.failUnlessEqual(un.checksumStr,'63')

        self.failUnlessEqual(un.rssi,1234)
        self.failUnlessEqual(un.signalStrength,-119)
        self.failUnlessEqual(un.timeOfArrival,12.34567123)
        self.failUnlessEqual(un.slotNumber,4321)
        self.failUnlessEqual(un.station,'r003669958')
        self.failUnlessEqual(un.stationTypeCode,'r')
        self.failUnlessEqual(un.cg_sec,float(1085889680))
        print un.timestamp
        print un.sqlTimestampStr  # Hmmm... they look the same


    def testEquality(self):
        m1 = UscgNmea('!AIVDM,1,1,,B,15Cjtd0Oj;Jp7ilG7=UkKBoB0<06,0*63,s1234,d-119,T12.34567123,r003669958,S4321,1085889680')
        m1same = UscgNmea('!AIVDM,1,1,,B,15Cjtd0Oj;Jp7ilG7=UkKBoB0<06,0*63,s1234,d-119,T12.34567123,r003669958,S4321,1085889680')
        # A whole bunch of mangled fields
        m2 = UscgNmea('!AIVDM,2,1,,B,15Cjtd0Oj;Jp7ilG7=UkKBoB0<06,0*63,s1234,d-119,T12.34567123,r003669958,S4321,1085889680')
        m3 = UscgNmea('!AIVDM,1,2,,B,15Cjtd0Oj;Jp7ilG7=UkKBoB0<06,0*63,s1234,d-119,T12.34567123,r003669958,S4321,1085889680')
        m4 = UscgNmea('!AIVDM,1,1,7,B,15Cjtd0Oj;Jp7ilG7=UkKBoB0<06,0*63,s1234,d-119,T12.34567123,r003669958,S4321,1085889680')
        m5 = UscgNmea('!AIVDM,1,1,,A,15Cjtd0Oj;Jp7ilG7=UkKBoB0<06,0*63,s1234,d-119,T12.34567123,r003669958,S4321,1085889680')
        m6 = UscgNmea('!AIVDM,1,1,,B,25Cjtd0Oj;Jp7ilG7=UkKBoB0<06,0*63,s1234,d-119,T12.34567123,r003669958,S4321,1085889680')
        m7 = UscgNmea('!AIVDM,1,1,,B,15Cjtd0Oj;Jp7ilG7=UkKBoB0<06,1*63,s1234,d-119,T12.34567123,r003669958,S4321,1085889680')
        m8 = UscgNmea('!AIVDM,1,1,,B,15Cjtd0Oj;Jp7ilG7=UkKBoB0<06,0*64,s1234,d-119,T12.34567123,r003669958,S4321,1085889680')
        #m9 = UscgNmea('!AIVDM,1,1,,B,15Cjtd0Oj;Jp7ilG7=UkKBoB0<06,0*63,s123,d-119,T12.34567123,r003669958,S4321,1085889680')
        #m10 = UscgNmea('!AIVDM,1,1,,B,15Cjtd0Oj;Jp7ilG7=UkKBoB0<06,0*63,s1234,d-120,T12.34567123,r003669958,S4321,1085889680')
        #m11 = UscgNmea('!AIVDM,1,1,,B,15Cjtd0Oj;Jp7ilG7=UkKBoB0<06,0*63,s1234,d-119,T11.34567123,r003669958,S4321,1085889680')
        m12 = UscgNmea('!AIVDM,1,1,,B,15Cjtd0Oj;Jp7ilG7=UkKBoB0<06,0*63,s1234,d-119,T12.34567123,r003669959,S4321,1085889680')
        #m13 = UscgNmea('!AIVDM,1,1,,B,15Cjtd0Oj;Jp7ilG7=UkKBoB0<06,0*63,s1234,d-119,T12.34567123,r003669958,S432,1085889680')
        m14 = UscgNmea('!AIVDM,1,1,,B,15Cjtd0Oj;Jp7ilG7=UkKBoB0<06,0*63,s1234,d-119,T12.34567123,r003669958,S4321,1085889681')
        self.failUnless(m1==m1)
        self.failUnless(m1==m1same)
        self.failUnless(m1!=m2)
        self.failUnless(m1!=m3)
        self.failUnless(m1!=m4)
        self.failUnless(m1!=m5)
        self.failUnless(m1!=m6)
        self.failUnless(m1!=m7)
        self.failUnless(m1!=m8)
        #self.failUnless(m1!=m9)
        #self.failUnless(m1!=m10)
        #self.failUnless(m1!=m11)
        self.failUnless(m1!=m12)
        #self.failUnless(m1!=m13)
        self.failUnless(m1!=m14)


############################################################
if __name__=='__main__':

    from optparse import OptionParser
    parser = OptionParser(usage="%prog [options]",
                          version="%prog "+__version__)

    parser.add_option('--doc-test',dest='doctest',default=False,action='store_true'
                      ,help='run the documentation tests')
    parser.add_option('--unit-test',dest='unittest',default=False,action='store_true'
                      ,help='run the unit tests')
    parser.add_option('-v','--verbose',dest='verbose',default=False,action='store_true'
                      ,help='Make the test output verbose')

    (options,args) = parser.parse_args()

    if options.doctest:
        success=True
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
	#del success # Hide success from epydoc

    if options.unittest:
        sys.argv = [sys.argv[0]]
        if options.verbose: sys.argv.append('-v')
        unittest.main()


def create_nmea(bits
                ,nmeaType='!AIVDM'
                #,nmeaType='$AIVDM'  # I think both are valid, but some parsers don't like it
                ,totalSentences=None
                ,sentenceNum=None
                ,sequentialMsgId=None
                ,aisChannel='A'
                ,station='runknown'
                ,cg_sec=None):
    '''
    Build a NMEA string for an AIS binary message payload.

    e.g. !AIVDM,1,1,,B,13UIAT001mmL=vhP1Sa:?8>l06A<,0*37,s24467,rNDBC46001,1202235568

    >>> bv=BitVector(bitstring='001000000101000010011000011000001100110001011011101111110011001010110001011011010111100111110010001100110011000001110100011001000000000000000000000000111001111000000000')
    >>> create_nmea(bv,cg_sec=1202235568)
    'AIVDM,1,1,,A,852HH<iKgk:iKG_j<k1lI0000qp0,0*13,runknown,1202235568'

    @type bits: BitVector
    @param cg_sec: seconds since the epoch in UTC or if None, the current time will be used
    @param totalSentences: defaults to 1.  Eventually will calculated for multi-line
    @type totalSentences: positive int
    @param sentences: defaults to 1.  Eventually will calculated for multi-line
    @type sentenceNum: positive int
    @param sequentialMsgId: the number 1..9 for this group of messages.  Defaults to blank
    @type sequentialMsgId: positive int

    @todo: handle the rest of the uscg fields
    @todo: handle multi-line messages
    '''
    bitLen=len(bits)
    assert (bitLen <= 168)  # If larger, this needs to be a multi-line set of nmea msgs
    if totalSentences is not None:
        # FIX: what is the right max number for a 5 slot message?
        assert(totalSentences < 5)
    else:
        # FIX: for multi-line, calculate this
        totalSentences=1
    if sentenceNum is not None:
        # FIX: should not be done here for multi-line
        assert(sentenceNum < totalSentences)
    else:
        sentenceNum=1

    if sequentialMsgId is not None:
        assert (sequentialMsgId<10)
        sequentialMsgId = str(sequentialMsgId)
    else:
        sequentialMsgId = ''

    pad = 6 - (bitLen%6)
    if 6==pad: pad=0
    if pad!=0: #bitLen%6!=0:
        #sys.stderr.write( 'padding '+str(pad)+'\n')
        bits = bits + BitVector(size=(6 - (bitLen%6)))  # Pad out to multiple of 6
    payload = ais.binary.bitvectoais6(bits)[0]

    fields=[nmeaType,]
    fields.append(str(totalSentences))
    fields.append(str(sentenceNum))
    fields.append(sequentialMsgId)
    fields.append(aisChannel)
    fields.append(payload)
    fields.append(str(pad))
    firstStr = ','.join(fields)
    checksum = ais.nmea.checksumStr(firstStr)
    fields = [firstStr+'*'+checksum,]
    fields.append(station)
    if cg_sec is None:
        cg_sec = time.time()
    fields.append(str(cg_sec))

    return ','.join(fields)


def test():
    #if options.doctest:
    #import os; print os.path.basename(sys.argv[0]),
    print 'doctests ...',
    #sys.argv= [sys.argv[0]]
    #if options.verbose: sys.argv.append('-v')
    import doctest
    numfail,numtests=doctest.testmod()
    if numfail==0:
        print 'ok'
    else:
        print 'FAILED'
        success=False

if __name__=='__main__':
    test()
