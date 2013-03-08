#!/usr/bin/env python

__version__ = '$Revision: 13395 $'.split()[1]
__date__ = '$Date: 2010-04-06 11:11:59 -0400 (Tue, 06 Apr 2010) $'.split()[1]
__author__ = 'Kurt Schwehr'

__doc__='''
Handle creation and extraction of NMEA strings.  Maybe need a separate VDM class like ais-py?

@requires: U{lxml<http://codespeak.net/lxml/>} - For libxml2 ElementTree interface.  Not actually required for the template, but this is just a demo or requirements.
@requires: U{Python<http://python.org/>} >= 2.4
@requires: U{epydoc<http://epydoc.sourceforge.net/>} >= 3.0alpha3
@requires: BitVector

@author: U{'''+__author__+'''<http://schwehr.org/>}
@version: ''' + __version__ +'''
@copyright: 2006
@var __date__: Date of last svn commit
@undocumented: __version__ __author__ __doc__ parser
@since: 2006-Sep-26  FIX: replace with the file creation date
@status: under development
@organization: U{CCOM<http://ccom.unh.edu/>} - FIX: if not CCOM change the name and link

@license: GPL v2

@note: This package does not respence the maximum number of characters
per line that is required in the NMEA specification.

'''

# Python standard libraries
import time, sys

# Local Modules
import binary

import re

EOL = "\x0D\x0A"
'''
DOS style end-of-line (<cr><lf>) for talking to AIS base stations
'''


def checksumStr(data,verbose=False):
    """
    Take a NMEA 0183 string and compute the checksum.

    Checksum is calculated by xor'ing everything between ? or ! and the *

    >>> checksumStr("!AIVDM,1,1,,B,35MsUdPOh8JwI:0HUwquiIFH21>i,0*09")
    '09'

    >>> checksumStr("AIVDM,1,1,,B,35MsUdPOh8JwI:0HUwquiIFH21>i,0")
    '09'

    >>> checksumStr('$AIACA,0,,,,,,,,,5,2087,0,2088,0,0,0,I,1,000000*15')
    '15'

    This is an example I made up

    >>> checksumStr('$xxCAB,1,1,1,1*5D')
    '40'

    @param data: NMEA message.  Leading ?/! and training checksum are optional
    @type data: str
    @return: hexidecimal value
    @rtype: str

    """

    # FIX: strip off new line at the end too
    #if data[0]=='!' or data[0]=='?': data = data[1:]
    #if data[-1]=='*': data = data[:-1]
    #if data[-3]=='*': data = data[:-3]
    end = data.find('*') # FIX: would rfind be faster?
    start=0
    if data[0] in ('$','!'): start=1
    if -1 != end: data=data[start:end]
    else: data=data[start:]
    if verbose: print 'checking on:',start,end,data
    # FIX: rename sum to not shadow builting function
    sum=0
    for c in data: sum = sum ^ ord(c)
    sumHex = "%x" % sum
    if len(sumHex)==1: sumHex = '0'+sumHex
    return sumHex.upper()


######################################################################
# common variables
#nmeaChecksumRegExStr = r"""\,[0-9]\*[0-9A-F][0-9A-F]"""
#nmeaChecksumRegExStr = r"""\,[A-Za-z0-9]\*[0-9A-F][0-9A-F]"""
nmeaChecksumRegExStr = r"""\*[0-9A-F][0-9A-F]"""
nmeaChecksumRE = re.compile(nmeaChecksumRegExStr)

def isChecksumValid(nmeaStr, allowTailData=True,verbose=False):
    """Return True if the string checks out with the checksum


    >>> isChecksumValid("!AIVDM,1,1,,B,35MsUdPOh8JwI:0HUwquiIFH21>i,0*09")
    True

    Corrupted:

    >>> isChecksumValid("!AIVDM,11,1,,B,35MsUdPOh8JwI:0HUwquiIFH21>i,0*09")
    False

    >>> isChecksumValid('$AIACA,0,,,,,,,,,5,2087,0,2088,0,0,0,I,1,000000*15')
    True

    @param allowTailData: Permit handing of Coast Guard format with data after the checksum
    @param nmeaStr: NMEA message.  Leading ?/! are optional
    @type nmeaStr: str
    @return: True if the checksum matches
    @rtype: bool
    """

    if allowTailData:
	match = nmeaChecksumRE.search(nmeaStr)
	if not match:
            if verbose: print 'Match failed'
            return False
	nmeaStr = nmeaStr[:match.end()]
	#if checksum.upper()==checksumStr(nmeaStr[match.end()


    if nmeaStr[-3]!='*':
	print 'FIX: warning... bad nmea string'
	return False  # Bad string without proper checksum
    checksum=nmeaStr[-2:]
    if checksum.upper()==checksumStr(nmeaStr).upper():
        return True
    if verbose:
        print 'mismatch checksums:', checksum.upper(),checksumStr(nmeaStr).upper()
    return False

def buildNmea(aisBits,prefix='!',serviceType='AI',msgType='VDM',channelSeq=None,channel='A'):
    '''
    Create one long oversized nmea string for the bits
    @param aisBits: message payload
    @type aisBits: BitVector
    @param prefix: '!' or '$'  what is the difference?
    @param serviceType: 'can this be anything other than AI?
    @param msgType: VDM.  Should not be VDO (own ship)
    @param channelSeq: 1-9 or None
    @param channel: AIS channel A or B
    @todo: sync names of prefix and serviceType to NMEA spec.
    @see: reference the appropriate spec documents for all this stuff.
    '''

    rList = [prefix,serviceType,msgType,',1,1,']
    if None != channelSeq: rList.append(str(channelSeq))
    rList.append(',')
    rList.append(channel)
    rList.append(',')

    payloadStr,pad = binary.bitvectoais6(aisBits) #[0]
    rList.append(payloadStr)
    rList.append(','+str(pad))
    rStr = ''.join(rList)
    rStr += '*'+checksumStr(rStr)

    return rStr


######################################################################
def cabEncode(TransA=False, TransB=False, Restart=False, Reset=False, prefix='AI'):  # FIX: default to xx?
    '''
    CAB - Control AIS Base Station.  Defaults to a safe state with
    everything shutdown.  62320-1/CDV, 80/427/CDV, Page 77, A.1.7

    >>> cabEncode()
    '$AICAB,0,0,,*48'

    >>> cabEncode(prefix='xx')
    '$xxCAB,0,0,,*40'

    Note that xx is probably not valid in this next example, but it is used by L3

    Made up example:

    >>> cabEncode(True,True,True,True,prefix='xx')
    '$xxCAB,1,1,1,1*40'

    >>> cabEncode(True,True,prefix='L3')
    '$L3CAB,1,1,,*3F'

    @param TransA: Transmissions enabled on channel A
    @type TransA: bool
    @param TransB: Transmissions enabled on channel B
    @type TransB: bool
    @param Restart: If true, command AIS Base station to restart operations in last known configuration
    @type Restart: bool
    @param Reset:
    @type Reset: bool
    @param prefix: string to put between the $ and CAB
    @type prefix: str
    @return: A CAB NMEA string
    @rtype: str
    '''
    r = ['$'+prefix+'CAB']
    if TransA: r.append('1')
    else: r.append('0')
    if TransB: r.append('1')
    else: r.append('0')
    if Restart: r.append('1')
    else: r.append('')
    if Reset: r.append('1')
    else: r.append('')
    rStr = ','.join(r)
    return rStr+'*'+checksumStr(rStr)


def cabDecode(msg,validate=True):
    '''

    >>> cabDecode('$AICAB,,,,*48')
    {'Reset': False, 'nmeaPrefix': 'AI', 'nmeaCmd': 'CAB', 'TransB': False, 'TransA': False, 'Restart': False}

    Note that ZZ is probably not valid in this next example

    >>> cabDecode('$ZZCAB,1,1,1,1*40')
    {'Reset': False, 'nmeaPrefix': 'ZZ', 'nmeaCmd': 'CAB', 'TransB': True, 'TransA': True, 'Restart': True}

    @param msg: NMEA string of a CAB message
    @type msg: str
    @param validate: Set to False to turn off validation for speed.
    @type validate: bool
    @return: lookup table of key/values
    @rtype: dict

    @todo: How do I make stable doctests with dictionary returns
    @todo FIX: throw an exception if not valid
    '''
    if validate and not isChecksumValid(msg,verbose=True):
        print 'FIX: this should be an exception in cabDecode.  Bad checksum'
        return False
    fields=msg.split(',')
    if validate and len(fields) not in (5,6,7): # Allow for USCG station and timestamp
        # check for USCG log tail
        print 'FIX: this should be an exception in cabDecode.  wrong number of fields'
        return False

    # FIX: for validate... make sure that the other case from 1 is an empty string
    r = {}
    if '1'==fields[1]: r['TransA']=True
    else: r['TransA']=False
    if '1'==fields[2]: r['TransB']=True
    else: r['TransB']=False
    if '1'==fields[3]: r['Restart']=True
    else: r['Restart']=False
    if '1'==fields[4]: r['Reset']=True
    else: r['Reset']=False
    r['nmeaCmd']='CAB'
    r['nmeaPrefix']=fields[0][1:3]
    return r

def verQuery(prefix='xx',appendEOL=True):
    '''
    Ask for the version string from a base station

    >>> verQuery(appendEOL=False)
    '$xxBSQ,VER*2D'

    >>> verQuery('AI',appendEOL=False)
    '$AIBSQ,VER*25'

    '''

    rStr =  '$' + prefix+'BSQ,VER'
    rStr += '*' + checksumStr(rStr)

    if appendEOL: rStr += EOL
    return rStr

def encodeQuery(query, prefix='xx',appendEOL=True):
    '''
    Ask for the version string from a base station

    >>> encodeQuery('VER',appendEOL=False)
    '$xxBSQ,VER*2D'

    >>> encodeQuery('VER', prefix='L3', appendEOL=False)
    '$L3BSQ,VER*52'

    >>> encodeQuery('VER','AI',appendEOL=False)
    '$AIBSQ,VER*25'

    >>> encodeQuery('ACA',appendEOL=False)
    '$xxBSQ,ACA*2F'

    >>> encodeQuery('CBM',appendEOL=False)
    '$xxBSQ,CBM*20'

    >>> encodeQuery('DLM',appendEOL=False)
    '$xxBSQ,DLM*29'

    >>> encodeQuery('DLM', prefix='L3', appendEOL=False)
    '$L3BSQ,DLM*56'

    >>> encodeQuery('BCF', prefix='L3', appendEOL=False)
    '$L3BSQ,BCF*54'

    >>> encodeQuery('CAB', prefix='L3', appendEOL=False)
    '$L3BSQ,CAB*53'

    '''

#    >>> encodeQuery('SID',appendEOL=False)
#    '$xxBSQ,SID*32'


    rStr =  '$' + prefix+'BSQ,'+query
    rStr += '*' + checksumStr(rStr)

    if appendEOL: rStr += EOL
    return rStr


# FIX: generic encode query function goes here


txrxLUT={
    0: 'tx a and b, rx on a and b'
    ,1: 'tx a, rx a and b'
    ,2: 'tx b, rx a and b'
    ,3: 'no tx, rx a and b'
    ,4: 'no tx, rx a'
    ,5: 'no tx, no rx'
}
'''
Transmit and Received modes.  See Page 88 61993-2 and XXXX???
'''

acaInfoSrcLUT = {
    'A':'ITU-R M.1371 message 22: addressed message'
    ,'B':'ITU-R M.1371 message 22: broadcast message'
    ,'C':'IEC 61162-1 AIS Channel Assignment setence'
    ,'D':'DSC Channel 70 telecommand'
    ,'M':'Operator manual input'
    ,'I':'Why is the L-3 unit returning I???  It is not defined on page 88 or 61993-2'
}
''' Lookup table of codes to use in the Information Source of an ACA
message.  See acaEncode() and acaDecode()
'''

powerLUT={
    0: 'high',
    1: 'low'
    }

powerEncode={
    'high':0,
    'low':1
    }

def acaEncode(seqnum='',north='',east='',south='',west='',transitionSize=''
              ,chanA='2087',chanAbandwidth='0' # default to normal channel and 0 is default bandwidth
              ,chanB='2088',chanBbandwidth='0'
              ,txrxMode='' # '3' # Default to no tx, but rx both
              ,power='' # Default to low power
              ,infosrc='' # Should be empty when sent to an AIS unit
              ,timeinuse='' # Should be empty for sent to an AIS unit
              ,prefix='xx',appendEOL=True
              ,validate=True
              ):
    '''Encode an AIS Regional Channel Assignment Message.


    >>> acaEncode(appendEOL=False)
    '$xxACA,,,,,,,2087,0,2088,0,,,,*4C'

    Set to high power

    >>> acaEncode(power=powerEncode['high'],appendEOL=False)
    '$xxACA,,,,,,,2087,0,2088,0,,0,,*7C'

    Set to low power

    >>> acaEncode(power=powerEncode['low'],appendEOL=False)
    '$xxACA,,,,,,,2087,0,2088,0,,1,,*7D'

    @see: 61993-2 Page 87.
    @param seqnum:
    @type seqnum: int
    @param north: llll.ll northern boundary
    @type north: float string
    @param east: yyyyy.yy (perhaps y was a bad choice)
    @type east: float string
    @param south:
    @type south:float string
    @param west:yyyyy.yy (perhaps y was a bad choice)
    @type west:float string
    @param transitionSize: (nautical miles)
    @type transitionSize: int
    @param chanA: Channel A number
    @type chanA: int
    @param chanAbandwidth: 0 is the default, 1 is 12.5 kHz
    @type chanAbandwidth: int
    @param chanB: Channel B number
    @type chanB: int
    @param chanBbandwidth: 0 is the default, 1 is 12.5 kHz
    @type chanBbandwidth: int
    @param txrxMode: See txrxLUT for the numbers
    @type txrxMode: int
    @param power: 0 for high, 1 for low
    @type power: int
    @param infosrc: should be empty for sending to an AIS device.  See acaInfoSrcLUT
    @type infosrc: letter
    @param timeinuse: should be empty for sending to an AIS device.  Time in UTC that the device changed to this state
    @type timeinuse: hhmmss.ss
    @param prefix: Vendor specific prefix.  FIX: what should be used here?
    @type prefix: Two letters
    @param appendEOL: Do you want a DOS end of line appended?
    @type appendEOL: bool
    @param validate: Set to true to validate the message
    @type validate: bool
    '''
    if validate:
        if ''!=seqnum: assert int(seqnum) in range(10)
        if ''!=north:  assert float(north) >= -90.  and float(north<=90.)
        if ''!=south:  assert float(south) >= -90.  and float(south<=90.)
        if ''!=east:   assert float(east)  >= -180. and float(east<=180.)
        if ''!=west:   assert float(west)  >= -180. and float(west<=180.)

        if transitionSize!='': assert int(transitionSize) in range(1,9)
        if chanA         !='': assert int(chanA) > 2000 and int(chanA) <= 2290 # FIX: what is the real range or is this it?
        if chanAbandwidth!='': assert int(chanAbandwidth) in (0,1)
        if chanB         !='': assert int(chanB) > 2000 and int(chanB) <= 2290 # FIX: what is the real range or is this it?
        if chanBbandwidth!='': assert int(chanBbandwidth) in (0,1)

        if txrxMode!='': assert int(txrxMode) in range(6)
        if power!='': assert int(power) in (0,1)
        if infosrc!='': assert infosrc in ('A','B','C','D','M')  # Sorry L-3, but I does not appear to be valid
        if timeinuse!='':
            v = float(timeinuse)
            assert v>=0. and v<24.

    r = ['$'+prefix+'ACA',str(seqnum)
         ,str(north),str(east),str(south),str(west),str(transitionSize)
         ,str(chanA),str(chanAbandwidth)
         ,str(chanB),str(chanBbandwidth)
         ,str(txrxMode),str(power),str(infosrc),str(timeinuse)]

    rStr = ','.join(r)
    rStr += '*'+checksumStr(rStr)
    if validate: assert(len(rStr)<=81)
    if appendEOL: rStr+=EOL

    return rStr


def acaDecode(msg,validate=True):
    '''
    Decode AIS Regional Channel Assignment Message.


    This is an example of an unconfigured base station, plus there is a USCG timestamp at the end.

    >>> acaDecode('$AIACA,0,,,,,,,,,5,2087,0,2088,0,0,0,I,1,000000*15,1172786646.1')
    {'inuse': '1', 'north': None, 'txrxMode': '0', 'power': '0', 'nmeaPrefix': 'AI', 'timeinuse': '000000', 'seqnum': '0', 'chanBbandwidth': '0', 'nmeaCmd': 'ACA', 'chanAbandwidth': '0', 'west': None, 'transitionSize': '5', 'infosrc': 'I', 'east': None, 'chanA': '2087', 'south': None, 'chanB': '2088'}

    @see: 61993-2 Page 87.
    @todo: get a complete example to decode as a doctest
    '''
    if validate and not isChecksumValid(msg,verbose=True):
        print 'FIX: this should be an exception in acaDecode.  Bad checksum'
        return False
    #assert msg[0]=='$'
    fields = msg.split(',')
    r = {}
    r['nmeaCmd']='ACA'
    r['nmeaPrefix']=fields[0][1:3]
    r['seqnum'] = fields[1]
    if len(fields[2])>0:
        lat = float(fields[2])  # FIX: what format is this??
        assert len(fields[3])==1
        if fields[3]=='S': lat= -1 * lat
    else: lat = None # empty string
    r['north']=lat
    del lat

    if len(fields[4])>0:
        lon = float(fields[4])  # FIX: what format is this??
        assert len(fields[5])==1
        if fields[5]=='W': lat= -1 * lat
    else: lon = None # empty string
    r['east']=lon
    del lon

    if len(fields[6])>0:
        lat = float(fields[6])  # FIX: what format is this??
        assert len(fields[7])==1
        if fields[7]=='S': lat= -1 * lat
    else: lat = None # empty string
    r['south']=lat
    del lat

    if len(fields[8])>0:
        lon = float(fields[8])  # FIX: what format is this??
        assert len(fields[9])==1
        if fields[9]=='W': lat= -1 * lat
    else: lon = None # empty string
    r['west']=lon
    del lon

    r['transitionSize'] = fields[10]  # Transition zone size in nm
    r['chanA']          = fields[11]  # Should probably be 2087
    r['chanAbandwidth'] = fields[12] # 12.5 or 25 kHz
    r['chanB']          = fields[13]  # Should probably be 2087
    r['chanBbandwidth'] = fields[14] # 12.5 or 25 kHz
    r['txrxMode']       = fields[15] # See lookup table txrxLUT
    r['power']          = fields[16] # 0 low, 1 hight
    r['infosrc']        = fields[17] # See acaInfoSrcLUT, can also be null
    r['inuse']          = fields[18] # 0 is not in use, 1 in-use.  Can also be null
    r['timeinuse']      = fields[19].split('*')[0] # hhmmss.ss
    return r


def cbmDecode(msg,validate=True):
    '''
    Decode Configure Base Station Message Broadcast Reporting Rates message.


    >>> cbmDecode('$AICBM,61,76,35,2,60,999,100,999,52,999,1,60,999,100,999*55,1172787005.46')
    {'msg17chanAnumslots': '1', 'nmeaPrefix': 'AI', 'msg4slot': '61', 'msg17chanAslotinterval': '999', 'nmeaCmd': 'CBM', 'msg20chanAslotinterval': '999', 'msg20chanAstartslot': '60', 'msg17chanAstartslot': '52', 'msg22chanAslotinterval': '999', 'msg22chanAstartslot': '100'}

    @see: 62320-1/CDV 80/427/CDV page 78, A.1.8
    '''

    if validate and not isChecksumValid(msg,verbose=True):
        print 'FIX: this should be an exception in acaDecode.  Bad checksum'
        return False
    #assert msg[0]=='$'
    fields = msg.split(',')
    r = {}
    r['nmeaCmd']=fields[0][3:] # CBM
    r['nmeaPrefix']=fields[0][1:3]
    r['msg4slot'] = fields[1]
    i = 2
    r['msg17chanAstartslot'] = fields[i]; i+=1
    r['msg17chanAslotinterval'] = fields[i]; i+=1
    r['msg17chanAnumslots'] = fields[i]; i+=1
    r['msg20chanAstartslot'] = fields[i]; i+=1
    r['msg20chanAslotinterval'] = fields[i]; i+=1
    r['msg22chanAstartslot'] = fields[i]; i+=1
    r['msg22chanAslotinterval'] = fields[i]; i+=1

    r['msg17chanAstartslot'] = fields[i]; i+=1
    r['msg17chanAslotinterval'] = fields[i]; i+=1
    r['msg17chanAnumslots'] = fields[i]; i+=1
    r['msg20chanAstartslot'] = fields[i]; i+=1
    r['msg20chanAslotinterval'] = fields[i]; i+=1
    r['msg22chanAstartslot'] = fields[i]; i+=1
    r['msg22chanAslotinterval'] = fields[i].split('*')[0]; i+=1  # 15
    return r


ownershipLUT = {
    'L':'local'
    ,'R':'remote'
    ,'C':'clear reservation'
}

def dlmDecode(msg, validate=True):
    '''
    Decode Data Link Management slot allocation for Base Station nmea message


    >>> dlmDecode ('$AIDLM,0,A,L,0,2,7,540,L,4,1,7,250,L,2511,1,7,0,,,,,*40,1172787005.5')
    {'nmeaPrefix': 'AI', 'timeout3': '7', 'timeout2': '7', 'timeout1': '7', 'timeout4': '', 'startslot2': '4', 'startslot3': '2511', 'incr4': '*40', 'incr3': '0', 'incr2': '250', 'incr1': '540', 'aisChannel': 'A', 'seqNum': '0', 'startslot1': '0', 'startslot4': '', 'nmeaCmd': 'DLM', 'ownership4': '', 'ownership3': 'L', 'ownership2': 'L', 'ownership1': 'L', 'numslots4': '', 'numslots1': '2', 'numslots2': '1', 'numslots3': '1'}

    @see: 62320-1/CDV 80/427/CDV page 79, A.1.9

    '''

    if validate and not isChecksumValid(msg,verbose=True):
        print 'FIX: this should be an exception in acaDecode.  Bad checksum'
        return False
    #assert msg[0]=='$'
    fields = msg.split(',')
    r = {}
    r['nmeaCmd']=fields[0][3:] # CBM
    r['nmeaPrefix']=fields[0][1:3]
    i = 1

    r['seqNum'] = fields[i]; i+=1
    r['aisChannel'] = fields[i]; i+=1

    # reservations
    r['ownership1'] = fields[i]; i+=1   # See ownership
    r['startslot1'] = fields[i]; i+=1
    r['numslots1']  = fields[i]; i+=1
    r['timeout1']   = fields[i]; i+=1
    r['incr1']      = fields[i]; i+=1

    r['ownership2'] = fields[i]; i+=1
    r['startslot2'] = fields[i]; i+=1
    r['numslots2']  = fields[i]; i+=1
    r['timeout2']   = fields[i]; i+=1
    r['incr2']      = fields[i]; i+=1

    r['ownership3'] = fields[i]; i+=1
    r['startslot3'] = fields[i]; i+=1
    r['numslots3']  = fields[i]; i+=1
    r['timeout3']   = fields[i]; i+=1
    r['incr3']      = fields[i]; i+=1

    r['ownership4'] = fields[i]; i+=1
    r['startslot4'] = fields[i]; i+=1
    r['numslots4']  = fields[i]; i+=1
    r['timeout4']   = fields[i]; i+=1
    r['incr4']      = fields[i]; i+=1

    return r

def bbmEncode(totSent, sentNum, seqId, aisChan, msgId, data, numFillBits
              ,prefix='xx',appendEOL=True
              ,validate=True
              ):
    '''Encode a binary broadcast message.

    I have no idea what this message says...

    !AIVDM,1,1,,A,85NqMF1Kf=Vsdt`l;0bnfFjd<uQeT2p<vmIRTB=mM5mtIT;sUL2t,0*54,rs003669982,1172918061

    >>> bbmEncode(1,1,0,3,8,'Fs[Ifs?:=2h:ec]dc3?HKI0f3?eFHa4[MGAMO6I2vqG0g',4)
    '!xxBBM,1,1,0,3,8,Fs[Ifs?:=2h:ec]dc3?HKI0f3?eFHa4[MGAMO6I2vqG0g,4*32'


    Here are the test messages from 62320-1 80/427/CDV Page 58, 10.2.2.1.2:

    >>> bbmEncode(1,1,0,1,8,'7E3B3C3E7E',0,appendEOL=False)
    '!xxBBM,1,1,0,1,8,7E3B3C3E7E,0*1F'

    Make it go on both

    >>> bbmEncode(1,1,0,3,8,'7E3B3C3E7E',0,appendEOL=False)
    '!xxBBM,1,1,0,3,8,7E3B3C3E7E,0*1D'



    @todo: put in some doc tests with know messages and what would be received as the VDM message(s)
    @see: IEC-PAS 61162-100 80/330/PAS, Page 19
    @param totSent: Total number of sentences needed for the message (1-9)
    @type totSent: int
    @param sentNum: Which sentence is this in the series (1-9)
    @type sentNum: int
    @param seqId: need to increment this for each message??!?!?  (0-9)  Linked to ABK
    @type seqId: int
    @param aisChan: AIS channel to use to send the message
      0. No channel preference
      1. AIS Channel A
      2. AIS Channel B
      3. Broadcast on both A and B
    @type aisChan: str
    @param msgId: AIS message 8 (binary broadcast message) or 14 (safety related broadcast)
    @type msgId: int
    @param data: Content of the binary data.  First sentence must be 58 characters or less.
    The rest can be up to 60 characters.
    @param numFillBits: Number of bits of padding in the last character of the data (0-5)
    @type numFillBits: int
    @return: nmea string
    @rtype: str
    '''
    if validate:
        # obsesive error checking follows
        tot = int(totSent)
        assert (0<tot and tot<=9)
        num = int(sentNum)
        assert (0<num and num<=9)
        assert (num<=tot)
        seq = int(seqId)
        assert (0<=seq and seq <=9)
        assert (int(aisChan) in range(0,5))
        assert (int(msgId) in (8,14))
        #if num==1: assert(len(data)<=58)
        #else: assert(len(data)<=60)
        # FIX: add validation of the characters in the data string
        assert(int(numFillBits) in range(0,6))
    r = ','.join(('!'+prefix+'BBM',str(totSent),str(sentNum),str(seqId),str(aisChan),str(msgId),data,str(numFillBits)))

    r += '*'+checksumStr(r)
    if validate: assert(len(r)) <= 81  # Max nmea string length
    return r


def bbmDecode(msg,validate=True):
    '''
    Decode a binary broadcast message NMEA string

    >>> bbmDecode('!xxBBM,1,1,0,3,8,Fs[Ifs?:=2h:ec]dc3?HKI0f3?eFHa4[MGAMO6I2vqG0g,4*32')
    {'numFillBits': '4', 'nmeaPrefix': 'xx', 'msgId': '8', 'aisChan': '3', 'data': 'Fs[Ifs?:=2h:ec]dc3?HKI0f3?eFHa4[MGAMO6I2vqG0g', 'seqId': '0', 'nmeaCmd': 'BBM', 'sentNum': '1', 'totSent': '1'}

    @todo: make the doctest stable
    @todo: doctests with known messages
    @param msg: NMEA string of a CAB message
    @type msg: str
    @param validate: Set to False to turn off validation for speed.
    @type validate: bool
    @return: lookup table of key/values
    @rtype: dict
    @see: IEC-PAS 61162-100 80/330/PAS, Page 19
    '''
    if validate and not isChecksumValid(msg,verbose=True):
        print 'FIX: this should be an exception in bbmDecode.  Bad checksum'
        return False
    fields=msg.split(',')
    if validate and len(fields) < 8: # Allow for USCG station and timestamp
        print 'FIX: this should be an exception in bbmDecode.  wrong number of fields', len(fields)
        print '  ', msg
        return False

    fields = msg.split(',')
    r = {}
    r['nmeaCmd']=fields[0][3:] # CBM  # 0
    r['nmeaPrefix']=fields[0][1:3]
    i = 1
    # FIX: convert from strings or not??
    r['totSent'] = fields[1]; i+= 1
    r['sentNum'] = fields[2]; i+= 1
    r['seqId'] = fields[3]; i+= 1
    r['aisChan'] = fields[4]; i+= 1
    r['msgId'] = fields[5]; i+= 1
    r['data'] = fields[6]; i+= 1
    r['numFillBits'] = fields[7].split('*')[0]; i+= 1

    return r

def bcfDecode(msg,validate=True):
    '''
    Decode a General Base Station Configuration NMEA string.

    >>> bcfDecode('$AIBCF,12345,7,4731.0,N,05249.0,W,1,2087,2088,2087,2088,1,1,3,0,AI*51')
    {'posAccuracy': '1', 'nmeaPrefix': 'AI', 'TxChanB': '2088', 'mmsi': '12345', 'RepeatIndicator': '0', 'lon': -5249.0, 'PowerB': '1', 'posSrc': '7', 'nmeaCmd': 'BCF', 'PowerA': '1', 'BaseStationTalkerID': 'AI', 'RxChanB': '2088', 'lat': 4731.0, 'RxChanA': '2087', 'TxChanA': '2087', 'VDLretries': '3'}

    @see: 62320-1/CDV 80/427/CDV, Page 76, A.1.6
    @param msg: NMEA string of a CAB message
    @type msg: str
    @param validate: Set to False to turn off validation for speed.
    @type validate: bool
    @return: lookup table of key/values
    @rtype: dict
    '''

    if validate and not isChecksumValid(msg,verbose=True):
        print 'FIX: this should be an exception in bcfDecode.  Bad checksum'
        return False
    fields=msg.split(',')
    if validate and len(fields) < 16: # Allow for USCG station and timestamp
        print 'FIX: this should be an exception in bcfDecode.  wrong number of fields', len(fields)
        print '  ', msg
        return False

    fields = msg.split(',')
    r = {}
    r['nmeaCmd']=fields[0][3:] # Had better be BCF
    r['nmeaPrefix']=fields[0][1:3]
    i = 1
    r['mmsi'] = fields[i]; i+= 1  # AKA UserID
    r['posSrc'] = fields[i]; i+= 1

    lat=fields[i]; i+= 1
    latNS=fields[i]; i+= 1
    if lat == '': r['lat'] = ''
    else:
        lat = float(lat)
        if 'S'==latNS: lat = -lat
        r['lat']=lat

    lon   = fields[i]; i+= 1
    lonEW = fields[i]; i+= 1
    if lon == '': r['lon'] = ''
    else:
        lon = float(lon)
        if 'W'==lonEW: lon = -lon
        r['lon'] = lon

    r['posAccuracy'] = fields[i]; i+= 1
    r['RxChanA'] = fields[i]; i+= 1
    r['RxChanB'] = fields[i]; i+= 1
    r['TxChanA'] = fields[i]; i+= 1
    r['TxChanB'] = fields[i]; i+= 1
    r['PowerA'] = fields[i]; i+= 1
    r['PowerB'] = fields[i]; i+= 1
    r['VDLretries'] = fields[i]; i+= 1
    r['RepeatIndicator'] = fields[i]; i+= 1
    r['BaseStationTalkerID'] = fields[i].split('*')[0]

    return r


posSrcLUT = {
    0:'surveyed'
    ,1:'internal EPFD in use'
    ,2:'external EPFD in use'
    ,3:'internal EPFD in use with auto fallback to surveyed'
    ,4:'internal EPFD in use with auto fallback to external EPFD'
    ,5:'external EPFD in use with auto fallback to surveyed'
    ,6:'external EPFD in use with auto fallback to internal EPFD'
    ,7:'FIX: What exactly is 7 supposed to be... not in the source list in item 2.'
    }
'''
Position source used in a BCF message

@note: EPFD = el;ectronic position fixing device
@see: 62320-1  80/427/CDV Page 76 A.1.6
'''

def bcfEncode(mmsi='',posSrc=''
              ,lat='',latNS=''
              ,lon='',lonEW=''
              ,posAccuracy=''

              ,RxChanA='',RxChanB=''
              ,TxChanA='',TxChanB=''
              ,PowerA ='',PowerB =''

              ,VDLretries=''
              ,RepeatIndicator=''
              ,BaseStationTalkerID=''
              ,prefix='AI',appendEOL=True
              ,validate=True
              ):
    '''
    Enocde a General Base Station Configuation Message.  Defaults to not changing anything

    >>> bcfEncode(appendEOL=False)
    '!AIBCF,,,,,,,,,,,,,,,,AI*47'

    >>> bcfEncode(12345,7,4731.0,'N',5249.0,'W',1,2087,2088,2087,2088,1,1,3,0,'AI',appendEOL=False)
    '!AIBCF,12345,7,4731.0,N,5249.0,W,1,2087,2088,2087,2087,1,1,3,0,AI*6E'

    This is what the L-3 base station returns this.  I am not sure what the format of the position is.

    '$AIBCF,12345,7,4731.0,N,05249.0,W,1,2087,2088,2087,2088,1,1,3,0,AI*51'


    Set to low power:

    >>> bcfEncode(PowerA=powerEncode['low'],PowerB=powerEncode['low'],appendEOL=False)
    '!AIBCF,,,,,,,,,,,,1,1,,,AI*47'

    My MMSI that is registered for testing at UNH

    >>> bcfEncode(mmsi=338040883, appendEOL=False,prefix='L3')
    '!L3BCF,338040883,,,,,,,,,,,,,,,L3*78'


    @see: 62320-1/CDV 80/427/CDV, Page 76, A.1.6
    @param mmsi: UserID for the base station
    @type  mmsi: int
    @param posSrc: See posSrcLUT. 0..6
    @type  posSrc: int
    @param lat: Surveyed latitude position.  FIX: how is this encoded!!?!?!
    @type  lat: float
    @param latNS: N or S
    @type  latNS: str(1)
    @param lon: Suveyed longitude position.  FIX: how is this encoded!!?!?!
    @type  lon: float
    @param lonEW: E or W
    @type  lonEW: str(1)
    @param posAccuracy: 0 for low, 1 for hight
    @type  posAccuracy: int
    @param RxChanA: Receive channel to use (default is 2087)
    @type  RxChanA: int
    @param RxChanB: Receive channel to use (default is 2088)
    @type  RxChanB: int
    @param TxChanA: Transmit channel to use (default is 2087)
    @type  TxChanA: int
    @param TxChanB: Transmit channel to use (default is 2089)
    @type  TxChanB: int
    @param PowerA: Transmit power for channel A - 0 high (12.5 W), 1 low (Nominal 2 watts).
                   FIX: Seems there is a disagreement between specs on the power levels.
                   2 or 5 watts for low?  2..9 reservered
    @type  PowerA: int
    @param PowerB:Transmit power for channel A - 0 high (12.5 W), 1 low (Nominal 2 watts).
                   FIX: Seems there is a disagreement between specs on the power levels.
                   2 or 5 watts for low?  2..9 reservered
    @type  PowerB: int
    @param VDLretries: FIX: what does this mean?
    @type  VDLretries: int
    @param RepeatIndicator: ?
    @type  RepeatIndicator: int
    @param BaseStationTalkerID: Usually AI.  The prefix that does before NMEA string identifiers
    @type  BaseStationTalkerID: str(2)
    @param prefix: Vendor specific prefix.  FIX: what should be used here?
    @type  prefix: Two letters
    @param appendEOL: Do you want a DOS end of line appended?
    @type  appendEOL: bool
    @param validate: Set to true to validate the message
    @type  validate: bool
    '''

    if validate:
        #print 'FIX: write validation code'
        pass


    r = ('!'+prefix+'BCF',str(mmsi),str(posSrc)
         ,str(lat),str(latNS)
         ,str(lon),str(lonEW)
         ,str(posAccuracy)
         ,str(RxChanA),str(RxChanB)
         ,str(TxChanA),str(TxChanA)
         ,str(PowerA),str(PowerB)
         ,str(VDLretries),str(RepeatIndicator),str(prefix)
         )

    rStr = ','.join(r)
    rStr += '*'+checksumStr(rStr)
    if validate: assert(len(rStr)<=81)
    if appendEOL: rStr+=EOL

    return rStr


######################################################################
if __name__=='__main__':
    from optparse import OptionParser
    parser = OptionParser(usage="%prog [options]",
                          version="%prog "+__version__)
    parser.add_option('--test','--doc-test',dest='doctest',default=False,action='store_true',
                      help='run the documentation tests')
    parser.add_option('-v','--verbose',dest='verbose',default=False,action='store_true',
                      help='run the tests run in verbose mode')
    (options,args) = parser.parse_args()

    success=True

    if options.doctest:
	import os; print os.path.basename(sys.argv[0]), 'doctests ...',
	argvOrig = sys.argv
	sys.argv= [sys.argv[0]]
	if options.verbose: sys.argv.append('-v')
	import doctest
	numfail,numtests=doctest.testmod()
	if numfail==0: print 'ok'
	else:
	    print 'FAILED'
	    success=False
	sys.argv = argvOrig # Restore the original args
	del argvOrig # hide from epydoc

    if not success:
	sys.exit('Something Failed')

    del success # Hide success from epydoc
