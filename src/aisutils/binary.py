#!/usr/bin/env python

__version__ = ["$Revision:", "2075", "$"][1]  # See man ident
__date__ = [
    "$Date:",
    "2006-05-03",
    "04:18:20",
    "-0400",
    "(Wed,",
    "03",
    "May",
    "2006)",
    "$",
][1]
__author__ = "Kurt Schwehr"

__doc__ = (
    """
AIS binary helper functions.

Code to convert AIS messages between binary BitVectors and strings.
They are usually encoded an ASCII 6-bit packing within NMEA
!AIVDM/!AIVDO messages.

@see: NMEA strings at U{http://gpsd.berlios.de/NMEA.txt}
@see: Wikipedia at U{http://en.wikipedia.org/wiki/Automatic_Identification_System}

@author: """
    + __author__
    + """
@version: """
    + __version__
    + """
@copyright: 2006


@todo: Flush out stuffBits and unstuffBits
@todo: bitvectorais6
@todo: test cases for ais6tobitvec

@var decode: cache of character to BitVector lookup
@var encode: cache of ais int value to character
@var __date__: Date of last svn commit
@undocumented: __version__ __author__ __doc__ myparser
@undocumented: buildLookupTables ais6tobitvecSLOW

@bug: code up stuffBits and unstuffBits
@bug: find an example needing bitstuffing
@undocumented: stuffBits unstuffBits
"""
)


# Python standard library
import struct
import sys

# Outside modules
from BitVector import BitVector


def float2bitvec(floatval):
    """
    Get the IEEE floating point bits for a python float

    Args:
        floatval: number to convert to bits
    Returns:
        BitVector (32 bits)
    """
    s = struct.pack("!f", floatval)
    i = int.from_bytes(s, byteorder="big")
    return setBitVectorSize(BitVector.from_int(i), 32)


def bitvec2float(bv):
    """
    Convert a 32 bit bitvector representing an IEEE float into a python float

    Args:
        bv: 32 bits representing an IEEE float
    Returns:
        float corresponding number
    """
    raw_bytes = int(bv).to_bytes(4, byteorder="big")
    return struct.unpack("!f", raw_bytes)[0]


def joinBV(bvSeq):
    """
    Combined a sequence of bit vectors into one large BitVector
    Args:
        bvSeq: sequence of bitvectors
    Returns:
        aggregated BitVector
    @bug: replace with a faster algorithm!
    """
    bvTotal = BitVector(size=0)
    for bv in bvSeq:
        bvTotal = bvTotal + bv

    return bvTotal


def setBitVectorSize(bv, size=8):
    """Pad a BitVector with 0's on the left until it is at least the size specified

    Args:
        bv: BitVector that needs to meet a minimum size
    @type bv: BitVector
        size: Minimum number of bits to make the new BitVector
    @type size: int
    Returns:
        BitVector that is size bits or larger
        BitVector

    @todo: What to do if the vector is larger than size?
    """
    if len(bv) < size:
        bv = BitVector(size=size - len(bv)) + bv
    return bv


def addone(bv):
    """Add one bit to a bit vector. Overflows are silently dropped."""
    val = (int(bv) + 1) & ((1 << len(bv)) - 1)
    return setBitVectorSize(BitVector.from_int(val), len(bv))


def subone(bv):
    """Subtract one bit from a bit vector."""
    val = (int(bv) - 1) & ((1 << len(bv)) - 1)
    return setBitVectorSize(BitVector.from_int(val), len(bv))


def bvFromSignedInt(intVal, bitSize=None):
    """Create a twos complement BitVector from a signed integer."""
    if intVal >= 0:
        if bitSize is None:
            return BitVector.from_int(intVal)
        return setBitVectorSize(BitVector.from_int(intVal), bitSize)

    if bitSize is None:
        bitSize = intVal.bit_length() + 1

    unsigned_val = (1 << bitSize) + intVal
    if unsigned_val < 0 or unsigned_val >= (1 << bitSize):
        raise ValueError("intVal cannot fit into the specified bitSize")
    return setBitVectorSize(BitVector.from_int(unsigned_val), bitSize)


def signedIntFromBV(bv):
    """Interpret a bit vector as a signed integer using twos complement."""
    val = int(bv)
    if len(bv) > 0 and bv[0] == 1:
        return val - (1 << len(bv))
    return val


# This is a better thing to no than the craziness in the slow
# aisstr6_encode = [chr(i+64) for i in range(32)] + [chr(i+32) for i in range(32)]


def ais6chartobitvec(char6):
    """
    Create a 6 bit BitVector for a single character

    x, y, and z will not appear.

    Args:
        char6: character of an AIS message where each character represents 6 bits
    @type char6: str(1)
    Returns:
        Decoded bits for one character (does not know about padding)
        BitVector(6)
    @bug: need to cut down the doctest here and copy all of the current one to tests/test_binary.py
    """
    c = ord(char6)
    val = c - 48
    if val >= 40:
        val -= 8
    if val == 0:
        return BitVector(size=6)
    return setBitVectorSize(BitVector.from_int(val), 6)


def ais6tobitvecSLOW(str6):
    """Convert an ITU AIS 6 bit string into a bit vector.  Each character
    represents 6 bits.  This is for text sent within ais messages


    @note: If the original BitVector had ((len(bitvector) % 6 > 0),
    then there will be pad bits in the str6.  This function has no way
    to know how many pad bits there are.

    @bug: Need to add pad bit handling

    Args:
        str6: ASCII that as it appears in the NMEA string
    @type str6: string
    Returns:
        decoded bits (not unstuffed... what do I mean by
    unstuffed?).  There may be pad bits at the tail to make this 6 bit
    aligned.
        BitVector
    """
    bvtotal = BitVector(size=0)

    for c in str6:
        c = ord(c)
        val = c - 48
        if val >= 40:
            val -= 8
        bv = None
        # print 'slow: ',c,val
        if val == 0:
            bv = BitVector(size=6)
        else:
            bv = setBitVectorSize(BitVector.from_int(val), 6)
            # bv = BitVector.from_int(val, size=6)  # FIX: I thought this would work, but it is more than 6 bits?
        bvtotal += bv
    return bvtotal


def buildLookupTables():
    """
    @bug: rename the local encode/decode dictionaries so there is no shadowing
    """
    decode = {}
    # encode={}
    for i in range(127):
        #    for i in range(64):  # FIX: is this the right range?
        if i < 48:
            continue
        c = chr(i)
        bv = ais6tobitvecSLOW(c)
        val = int(bv)
        if val >= 64:
            continue
        # encode[val] = c
        decode[c] = bv
        # print i, val, bv, "'"+str(c)+"'"
    # return encode,decode
    return decode


decode = buildLookupTables()
# X, Y, and Z are not in the table.
decode.pop("X")
decode.pop("Y")
decode.pop("Z")

decode_int = {c: int(bv) for c, bv in decode.items()}

encode = [chr(i + 48) for i in range(40)] + [chr(i + 96) for i in range(24)]
"""
Lookup the character representation for in an ais AIVDM message from
the 6-bit integer value.

@see: IEC-PAS 61162-100 Ed.1 IEC Page 26, Annex C, Table C-1
"""


def test_encode():
    if len(encode) != 64:
        return False

    if encode[0] != "0":
        return False  # 000000
    if encode[16] != "@":
        return False  # 010000
    if encode[17] != "A":
        return False  # 010001
    if encode[39] != "W":
        return False  # 100111

    if encode[40] != "`":
        return False  # 101000
    if encode[41] != "a":
        return False  # 101001
    if encode[51] != "k":
        return False  # 110011
    if encode[63] != "w":
        return False  # 111111

    if "x" in encode:
        return False
    if "X" in encode:
        return False
    if "[" in encode:
        return False
    return "]" not in encode


# assert (test_encode())


def ais6tobitvec(str6):
    """Convert an ITU AIS 6 bit string into a bit vector.  Each character
    represents 6 bits.  This is the NMEA !AIVD[MO] message payload.

    Args:
        str6: ASCII that as it appears in the NMEA string
    Returns:
        BitVector
    """
    val = 0
    for char in str6:
        val = (val << 6) | decode_int[char]
    return setBitVectorSize(BitVector.from_int(val), 6 * len(str6))


def getPadding(bv):
    """
    Return the number of bits that need to be padded for a bit vector

    Returns:
        int
        number of pad bits required for this bitvector to make it bit aligned to the ais nmea string
    """
    pad = 6 - (len(bv) % 6)
    if pad == 6:
        pad = 0
    return pad


def bitvectoais6(bv, doPadding=True):
    """Convert bit vector into an ITU AIS 6 bit string. Each character represents 6 bits

    Args:
        bv: message bits
        doPadding: whether to pad to 6-bit alignment
    Returns:
        str, pad
    """
    pad = 6 - (len(bv) % 6)
    if pad == 6:
        pad = 0

    if pad != 0:
        if doPadding:
            bv = bv + BitVector(size=pad)
        else:
            raise ValueError("Invalid payload or state")

    strLen = len(bv) // 6
    bv_int = int(bv)
    aisStrLst = []

    for i in range(strLen):
        shift = (strLen - 1 - i) * 6
        val = (bv_int >> shift) & 63
        aisStrLst.append(encode[val])

    return "".join(aisStrLst), pad


def bit_count(bv: BitVector) -> int:
    """Count set bits in a BitVector using int.bit_count()."""
    return int(bv).bit_count()


def parity(bv: BitVector) -> int:
    """Compute parity (0 or 1) of a BitVector using int.bit_count()."""
    return int(bv).bit_count() & 1


def stuffBits(bv):
    """Apply bit stuffing - add extra bytes to long sequences

    Args:
        bv: bits that may need padding
    @type bv: BitVector
    Returns:
        new bits, possibly longer
        BitVector

    @see: unstuffBits

    @todo: Add a nice description of how bit stuffing works
    @todo: Actually write the code
    """
    raise ValueError("Invalid payload or state")


def unstuffBits(bv):
    """Undo bit stuffing - remove extra bytes to long sequences

    Args:
        bv: bits that may have padding
    @type bv: BitVector
    Returns:
        new bits, possibly longer
        BitVector

    @todo: Actually write the code
    @see: stuffBits
    """
    raise ValueError("Invalid payload or state")


if __name__ == "__main__":
    from optparse import OptionParser

    parser = OptionParser(usage="%prog [options]", version="%prog " + __version__)
    parser.add_option(
        "--test",
        "--doc-test",
        dest="doctest",
        default=False,
        action="store_true",
        help="run the documentation tests",
    )
    parser.add_option(
        "-v",
        "--verbose",
        dest="verbose",
        default=False,
        action="store_true",
        help="Make the test output verbose",
    )
    (options, args) = parser.parse_args()

    success = True

    if options.doctest:
        import os

        print(os.path.basename(sys.argv[0]), "doctests ...", end=" ")
        sys.argv = [sys.argv[0]]
        if options.verbose:
            sys.argv.append("-v")
        import doctest

        numfail, numtests = doctest.testmod()
        if numfail == 0:
            print("ok")
        else:
            print("FAILED")
            success = False

    if not success:
        sys.exit("Something Failed")
