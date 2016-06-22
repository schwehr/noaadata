#!/usr/bin/env python

__version__ = '$Revision: 2075 $'.split()[1] # See man ident
__date__ = '$Date: 2006-05-03 04:18:20 -0400 (Wed, 03 May 2006) $'.split()[1]
__author__ = 'Kurt Schwehr'

__doc__='''
AIS binary helper functions.

Code to convert AIS messages between binary BitVectors and strings.
They are usually encoded an ASCII 6-bit packing within NMEA
!AIVDM/!AIVDO messages.

@see: NMEA strings at U{http://gpsd.berlios.de/NMEA.txt}
@see: Wikipedia at U{http://en.wikipedia.org/wiki/Automatic_Identification_System}

@author: '''+__author__+'''
@version: ''' + __version__ +'''
@copyright: 2006


@todo: Flush out stuffBits and unstuffBits
@todo: bitvectorais6
@todo: test cases for ais6tobitvec

@var decode: cache of character to BitVector lookup
@var encode: cache of ais int value to charcter
@var __date__: Date of last svn commit
@undocumented: __version__ __author__ __doc__ myparser
@undocumented: buildLookupTables ais6tobitvecSLOW

@bug: code up stuffBits and unstuffBits
@bug: find an example needing bitstuffing
@undocumented: stuffBits unstuffBits
'''


# Python standard library
import sys

# Outside modules
from BitVector import BitVector
import struct

def float2bitvec(floatval):
    '''
    Get the IEEE floating point bits for a python float

    @bug: May have bite order backwards
    @type floatval: number
    @param floatval: number to convert to bits
    @rtype: BitVector
    @return: 32 bits
    @todo: Is there a faster way to do this?
    @see: U{struct module<http://www.python.org/doc/current/lib/module-struct.html>}
    '''
    s = struct.pack('!f',floatval)  # FIX: Is this the right bight order?  Could easily be wrong!!!!
    i = struct.unpack('!I',s)[0]
    #print 'unpacked:',i
    #return setBitVectorSize(BitVector(intVal=i),32)

    # Old way...  since BitVector can't encode large intVals (>2^31)
    # FIX: make this go in one step now that bitvector 1.3 is out.
    bvList = []
    for i in range(4):
        bv1 = setBitVectorSize(BitVector(intVal=ord(s[i])),8)
        #bv2 = BitVector(intVal=ord(s[i]),size=8)
        bvList.append(bv1)
    return joinBV(bvList)

def bitvec2float(bv):
    '''
    Convert a 32 bit bitvector representing an IEEE float into a python float
    @bug: May have bite order backwards
    @type bv: BitVector
    @param bv: 32 bits representing an IEEE float
    @rtype: float
    @return: the corresponing number
    @see: U{struct module<http://www.python.org/doc/current/lib/module-struct.html>}
    '''
    return struct.unpack('!f',chr(bv[0:8]) + chr(bv[8:16]) + chr(bv[16:24]) + chr(bv[24:32]))[0]


def joinBV(bvSeq):
    '''
    Combined a sequence of bit vectors into one large BitVector
    @param bvSeq: sequence of bitvectors
    @return: aggregated BitVector
    @bug: replace with a faster algorithm!
    '''
    bvTotal=BitVector(size=0)
    for bv in bvSeq:
        bvTotal = bvTotal + bv

    return bvTotal

def setBitVectorSize(bv,size=8):
    """Pad a BitVector with 0's on the left until it is at least the size specified

    @param bv: BitVector that needs to meet a minimim size
    @type bv: BitVector
    @param size: Minimum number of bits to make the new BitVector
    @type size: int
    @return: BitVector that is size bits or larger
    @rtype: BitVector

    @todo: What to do if the vector is larger than size?
    """
    pad=BitVector(bitlist=[0])
    while len(bv)<size: bv = pad + bv
    return bv


def addone(bv):
    '''
    Add one bit to a bit vector.  Overflows are silently dropped.

    @param bv: Add one to these bits
    @type bv: BitVector
    @return: Bits with one added
    @rtype: BitVector
    '''
    new = bv
    r = range(1,len(bv)+1)
    for i in r:
        index = len(bv)-i
        if 0==bv[index]:
            new[index]=1
            break
        new[index]=0
    return new

def subone(bv):
    '''
    Subtract one bit from a bit vector

    @param bv: Bits to add one bit to the right side
    @type bv: BitVector
    @rtype: BitVector
    '''
    new = bv
    r = range(1,len(bv)+1)
    for i in r:
        index = len(bv)-i
        if 1==bv[index]:
            new[index]=0
            break
        new[index]=1
    return new


def bvFromSignedInt(intVal,bitSize=None):
    '''
    Create a twos complement BitVector from a signed integer.  Not that 110 and 10 are both -2.

    Positives must have a '0' in the left hand position.

    Negative numbers must have a '1' in the left hand position.

    @param intVal: integer value to turn into a bit vector
    @type intVal: int
    @param bitSize: optional size to flush out the number of bits
    @type bitSize: int
    @return: A Bit Vector flushed out to the right size
    @rtype: BitVector
    '''
    bv = None
    if None==bitSize:
        bv = BitVector(intVal=abs(intVal))
    else:
        bv = setBitVectorSize(BitVector(intVal=abs(intVal)),bitSize-1)
        if (bitSize-1!=len(bv) and bv[0] != 1 and bv[-1] != 0):
            print 'ERROR: bitsize not right'
            print '  ',bitSize-1,len(bv)
            assert(False)
        if len(bv) == bitSize and bv[0] == 1: return bv
    if intVal>=0:
        bv = BitVector(intVal=0) + bv
    else:
        bv = subone(bv)
        bv = ~bv
        bv = BitVector(intVal=1) + bv
    return bv

def signedIntFromBV(bv):
    '''
    Interpret a bit vector as an signed integer.  int(BitVector)
    defaults to treating the bits as an unsigned int.  Assumes twos
    complement representation.

    U{http://en.wikipedia.org/wiki/Twos_complement}

    Positive values decode like so:

    Here are some negative integer examples:

    @param bv: Bits to treat as an signed int
    @type bv: BitVector
    @return: Signed integer
    @rtype: int

    @note: Does not know the difference between byte orders.
    '''
    if 0==bv[0]: return int(bv)
    # Nope, so it is negative
    val = int(addone(~(bv[1:])))
    if 0 != val: return -val
    return -(int(bv))

# This is a better thing to no than the craziness in the slow
#aisstr6_encode = [chr(i+64) for i in range(32)] + [chr(i+32) for i in range(32)]


def ais6chartobitvec(char6):
    '''
    Create a 6 bit BitVector for a single character

    x, y, and z will not appear.

    @param char6: character of an AIS message where each character represents 6 bits
    @type char6: str(1)
    @return: Decoded bits for one character (does not know about padding)
    @rtype: BitVector(6)
    @bug: need to cut down the doctest here and copy all of the current one to tests/test_binary.py
    '''
    c = ord(char6)
    val = c - 48
    if val>=40: val -= 8
    if 0==val: return(BitVector(size=6))
    return setBitVectorSize(BitVector(intVal=val),6)


def ais6tobitvecSLOW(str6):
    """Convert an ITU AIS 6 bit string into a bit vector.  Each character
    represents 6 bits.  This is for text sent within ais messages


    @note: If the original BitVector had ((len(bitvector) % 6 > 0),
    then there will be pad bits in the str6.  This function has no way
    to know how many pad bits there are.

    @bug: Need to add pad bit handling

    @param str6: ASCII that as it appears in the NMEA string
    @type str6: string
    @return: decoded bits (not unstuffed... what do I mean by
    unstuffed?).  There may be pad bits at the tail to make this 6 bit
    aligned.
    @rtype: BitVector
    """
    bvtotal = BitVector(size=0)

    for c in str6:
        c = ord(c)
        val = c - 48
        if val>=40: val -= 8
        bv = None
        #print 'slow: ',c,val
        if 0==val:
            bv = BitVector(size=6)
        else:
            bv = setBitVectorSize(BitVector(intVal=val),6)
            #bv = BitVector(intVal=val,size=6)  # FIX: I thought this would work, but it is more than 6 bits?
        bvtotal += bv
    return bvtotal




def buildLookupTables():
    '''
    @bug: rename the local encode/decode dictionaries so there is no shadowing
    '''
    decode={}
    #encode={}
    for i in range(127):
#    for i in range(64):  # FIX: is this the right range?
        if i<48: continue
        c = chr(i)
        bv = ais6tobitvecSLOW(c)
        val = int (bv)
        if val>=64: continue
        #encode[val] = c
        decode[c] = bv
        #print i, val, bv, "'"+str(c)+"'"
    #return encode,decode
    return decode

decode=buildLookupTables()
# X, Y, and Z are not in the table.
decode.pop('X')
decode.pop('Y')
decode.pop('Z')

encode = [chr(i+48) for i in range(40)] + [chr(i+96) for i in range(24)]
'''
Lookup the character representation for in an ais AIVDM message from
the 6-bit integer value.

@see: IEC-PAS 61162-100 Ed.1 IEC Page 26, Annex C, Table C-1
'''

def test_encode():
    if len(encode)!=64: return False

    if encode[ 0]!='0': return False # 000000
    if encode[16]!='@': return False # 010000
    if encode[17]!='A': return False # 010001
    if encode[39]!='W': return False # 100111

    if encode[40]!="`": return False # 101000
    if encode[41]!='a': return False # 101001
    if encode[51]!='k': return False # 110011
    if encode[63]!='w': return False # 111111

    if 'x' in encode: return False
    if 'X' in encode: return False
    if '[' in encode: return False
    if ']' in encode: return False

    return True

#assert (test_encode())

def ais6tobitvec(str6):
    '''Convert an ITU AIS 6 bit string into a bit vector.  Each character
    represents 6 bits.  This is the NMEA !AIVD[MO] message payload.

    @note: If the original BitVector had ((len(bitvector) % 6 > 0),
    then there will be pad bits in the str6.  This function has no way
    to know how many pad bits there are.

    @bug: Need to add pad bit handling

    @param str6: ASCII that as it appears in the NMEA string
    @type str6: string
    @return: decoded bits (not unstuffed... what do I mean by
    unstuffed?).  There may be pad bits at the tail to make this 6 bit
    aligned.
    @rtype: BitVector
    '''
    bvtotal = BitVector(size=6*len(str6))

    for pos in range(len(str6)):
        bv = decode[str6[pos]]
        start = pos*6
        for i in range(6):
            bvtotal[i+start] = bv[i]
    return bvtotal

def getPadding(bv):
    '''
    Return the number of bits that need to be padded for a bit vector

    @rtype: int
    @return: number of pad bits required for this bitvector to make it bit aligned to the ais nmea string
    '''
    pad = 6-(len(bv)%6)
    if 6==pad: pad = 0
    return pad

def bitvectoais6(bv,doPadding=True):
    """Convert bit vector int an ITU AIS 6 bit string.  Each character represents 6 bits

    @param bv: message bits (must be already stuffed)
    @type bv: BitVector
    @return: str6 ASCII that as it appears in the NMEA string
    @rtype: str, pad

    @todo: make a test base for needing padding
    @bug: handle case when padding needed
    """
    pad = 6-(len(bv)%6)
    if 6==pad: pad = 0
    strLen = len(bv)/6
    if pad>0: strLen+=1
    aisStrLst = []

    if pad!=0:
        if doPadding:
            print 'pad befaore',len(bv)
            bv = bv + BitVector(size=pad)
            print 'pad after',len(bv)
        else:
            print 'ERROR: What are you doing with a non-align entity?  Let me pad it!'
            assert False

    #else: # No pad needed
    for i in range(strLen):
        start = i*6
        end = (i+1)*6
        val = int(bv[start:end])
        c = encode[val]
        aisStrLst.append(c)

    aisStr = ''.join(aisStrLst)

    return aisStr, pad


def stuffBits(bv):
    """Apply bit stuffing - add extra bytes to long sequences

    @param bv: bits that may need padding
    @type bv: BitVector
    @return: new bits, possibly longer
    @rtype: BitVector

    @see: unstuffBits

    @todo: Add a nice description of how bit stuffing works
    @todo: Actually write the code
    """
    assert False

def unstuffBits(bv):
    """Undo bit stuffing - remove extra bytes to long sequences

    @param bv: bits that may have padding
    @type bv: BitVector
    @return: new bits, possibly longer
    @rtype: BitVector

    @todo: Actually write the code
    @see: stuffBits
    """
    assert False

if __name__ == '__main__':
    from optparse import OptionParser
    parser = OptionParser(usage="%prog [options]",version="%prog "+__version__)
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

    if not success:
        sys.exit('Something Failed')
