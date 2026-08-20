#!/usr/bin/env python

__version__ = ["$Revision:", "2068", "$"][1]
__date__ = [
    "$Date:",
    "2006-05-02",
    "08:17:59",
    "-0400",
    "(Tue,",
    "02",
    "May",
    "2006)",
    "$",
][1]
__author__ = "Kurt Schwehr"

__doc__ = (
    """
Handle encoding and decoding AIS strings.

@bug: need some more interesting doctests!
@bug: needs to throw an exception if the character is not in the LUT
@bug: what to do about string with trailing @@@ or "   " (white space)

@var characterLUT: lookup table for decode to fetch characters faster
@type characterLUT: list

@var characterBits: lookup table for going from a single character to a 6 bit BitVector
@type characterBits: dict


@author: """
    + __author__
    + """
@version: """
    + __version__
    + """
@copyright: 2006

@var __date__: Date of last svn commit
@undocumented: __version__ __author__ __doc__ myparser
@undocumented: buildDict
"""
)


# python standard library
import sys

# External libs
from BitVector import BitVector

# Local
from . import binary

# import verbosity
# from verbosity import BOMBASTIC,VERBOSE,TRACE,TERSE,ALWAYS

characterLUT = [
    "@",
    "A",
    "B",
    "C",
    "D",
    "E",
    "F",
    "G",
    "H",
    "I",
    "J",
    "K",
    "L",
    "M",
    "N",
    "O",
    "P",
    "Q",
    "R",
    "S",
    "T",
    "U",
    "V",
    "W",
    "X",
    "Y",
    "Z",
    "[",
    "\\",
    "]",
    "^",
    "-",
    " ",
    "!",
    '"',
    "#",
    "$",
    "%",
    "&",
    "`",
    "(",
    ")",
    "*",
    "+",
    ",",
    "-",
    ".",
    "/",
    "0",
    "1",
    "2",
    "3",
    "4",
    "5",
    "6",
    "7",
    "8",
    "9",
    ":",
    ";",
    "<",
    "=",
    ">",
    "?",
]

characterDict = {
    "@": 0,
    "A": 1,
    "B": 2,
    "C": 3,
    "D": 4,
    "E": 5,
    "F": 6,
    "G": 7,
    "H": 8,
    "I": 9,
    "J": 10,
    "K": 11,
    "L": 12,
    "M": 13,
    "N": 14,
    "O": 15,
    "P": 16,
    "Q": 17,
    "R": 18,
    "S": 19,
    "T": 20,
    "U": 21,
    "V": 22,
    "W": 23,
    "X": 24,
    "Y": 25,
    "Z": 26,
    "[": 27,
    "\\": 28,
    "]": 29,
    "^": 30,
    "-": 31,
    " ": 32,
    "!": 33,
    '"': 34,
    "#": 35,
    "$": 36,
    "%": 37,
    "&": 38,
    "`": 39,
    "(": 40,
    ")": 41,
    "*": 42,
    "+": 43,
    ",": 44,
    "-": 45,
    ".": 46,
    "/": 47,
    "0": 48,
    "1": 49,
    "2": 50,
    "3": 51,
    "4": 52,
    "5": 53,
    "6": 54,
    "7": 55,
    "8": 56,
    "9": 57,
    ":": 58,
    ";": 59,
    "<": 60,
    "=": 61,
    ">": 62,
    "?": 63,
}
"""Fast lookup for the AIS int code for a character """
# The above illustrates the inline ways of documenting module variables


characterBits = {}
characterBits["@"] = binary.setBitVectorSize(BitVector.from_int(0), 6)
characterBits["A"] = binary.setBitVectorSize(BitVector.from_int(1), 6)
characterBits["B"] = binary.setBitVectorSize(BitVector.from_int(2), 6)
characterBits["C"] = binary.setBitVectorSize(BitVector.from_int(3), 6)
characterBits["D"] = binary.setBitVectorSize(BitVector.from_int(4), 6)
characterBits["E"] = binary.setBitVectorSize(BitVector.from_int(5), 6)
characterBits["F"] = binary.setBitVectorSize(BitVector.from_int(6), 6)
characterBits["G"] = binary.setBitVectorSize(BitVector.from_int(7), 6)
characterBits["H"] = binary.setBitVectorSize(BitVector.from_int(8), 6)
characterBits["I"] = binary.setBitVectorSize(BitVector.from_int(9), 6)
characterBits["J"] = binary.setBitVectorSize(BitVector.from_int(10), 6)
characterBits["K"] = binary.setBitVectorSize(BitVector.from_int(11), 6)
characterBits["L"] = binary.setBitVectorSize(BitVector.from_int(12), 6)
characterBits["M"] = binary.setBitVectorSize(BitVector.from_int(13), 6)
characterBits["N"] = binary.setBitVectorSize(BitVector.from_int(14), 6)
characterBits["O"] = binary.setBitVectorSize(BitVector.from_int(15), 6)
characterBits["P"] = binary.setBitVectorSize(BitVector.from_int(16), 6)
characterBits["Q"] = binary.setBitVectorSize(BitVector.from_int(17), 6)
characterBits["R"] = binary.setBitVectorSize(BitVector.from_int(18), 6)
characterBits["S"] = binary.setBitVectorSize(BitVector.from_int(19), 6)
characterBits["T"] = binary.setBitVectorSize(BitVector.from_int(20), 6)
characterBits["U"] = binary.setBitVectorSize(BitVector.from_int(21), 6)
characterBits["V"] = binary.setBitVectorSize(BitVector.from_int(22), 6)
characterBits["W"] = binary.setBitVectorSize(BitVector.from_int(23), 6)
characterBits["X"] = binary.setBitVectorSize(BitVector.from_int(24), 6)
characterBits["Y"] = binary.setBitVectorSize(BitVector.from_int(25), 6)
characterBits["Z"] = binary.setBitVectorSize(BitVector.from_int(26), 6)
characterBits["["] = binary.setBitVectorSize(BitVector.from_int(27), 6)
characterBits["\\"] = binary.setBitVectorSize(BitVector.from_int(28), 6)
characterBits["]"] = binary.setBitVectorSize(BitVector.from_int(29), 6)
characterBits["^"] = binary.setBitVectorSize(BitVector.from_int(30), 6)
characterBits["-"] = binary.setBitVectorSize(BitVector.from_int(31), 6)
characterBits[" "] = binary.setBitVectorSize(BitVector.from_int(32), 6)
characterBits["!"] = binary.setBitVectorSize(BitVector.from_int(33), 6)
characterBits['"'] = binary.setBitVectorSize(BitVector.from_int(34), 6)
characterBits["#"] = binary.setBitVectorSize(BitVector.from_int(35), 6)
characterBits["$"] = binary.setBitVectorSize(BitVector.from_int(36), 6)
characterBits["%"] = binary.setBitVectorSize(BitVector.from_int(37), 6)
characterBits["&"] = binary.setBitVectorSize(BitVector.from_int(38), 6)
characterBits["`"] = binary.setBitVectorSize(BitVector.from_int(39), 6)
characterBits["("] = binary.setBitVectorSize(BitVector.from_int(40), 6)
characterBits[")"] = binary.setBitVectorSize(BitVector.from_int(41), 6)
characterBits["*"] = binary.setBitVectorSize(BitVector.from_int(42), 6)
characterBits["+"] = binary.setBitVectorSize(BitVector.from_int(43), 6)
characterBits[","] = binary.setBitVectorSize(BitVector.from_int(44), 6)
characterBits["-"] = binary.setBitVectorSize(BitVector.from_int(45), 6)
characterBits["."] = binary.setBitVectorSize(BitVector.from_int(46), 6)
characterBits["/"] = binary.setBitVectorSize(BitVector.from_int(47), 6)
characterBits["0"] = binary.setBitVectorSize(BitVector.from_int(48), 6)
characterBits["1"] = binary.setBitVectorSize(BitVector.from_int(49), 6)
characterBits["2"] = binary.setBitVectorSize(BitVector.from_int(50), 6)
characterBits["3"] = binary.setBitVectorSize(BitVector.from_int(51), 6)
characterBits["4"] = binary.setBitVectorSize(BitVector.from_int(52), 6)
characterBits["5"] = binary.setBitVectorSize(BitVector.from_int(53), 6)
characterBits["6"] = binary.setBitVectorSize(BitVector.from_int(54), 6)
characterBits["7"] = binary.setBitVectorSize(BitVector.from_int(55), 6)
characterBits["8"] = binary.setBitVectorSize(BitVector.from_int(56), 6)
characterBits["9"] = binary.setBitVectorSize(BitVector.from_int(57), 6)
characterBits[":"] = binary.setBitVectorSize(BitVector.from_int(58), 6)
characterBits[";"] = binary.setBitVectorSize(BitVector.from_int(59), 6)
characterBits["<"] = binary.setBitVectorSize(BitVector.from_int(60), 6)
characterBits["="] = binary.setBitVectorSize(BitVector.from_int(61), 6)
characterBits[">"] = binary.setBitVectorSize(BitVector.from_int(62), 6)
characterBits["?"] = binary.setBitVectorSize(BitVector.from_int(63), 6)


def buildDict():
    """
    Helper to build the build the carachterBits and Dict tables

    Returns:
        test to stdout
    """
    print("characterDict={")
    for i, c in enumerate(characterLUT):
        if c == "\\":
            c = "\\\\"
        print("'" + c + "': " + str(i) + ",", end=" ")
        if (i + 1) % 6 == 0:
            print()
    print("}")

    print("characterBits={}")
    for i in range(len(characterLUT)):
        c = characterLUT[i]
        if c == "\\":
            c = "\\\\"
        print(
            "characterBits['"
            + c
            + "']"
            + "=binary.setBitVectorSize(BitVector.from_int("
            + str(i)
            + "),6)"
        )


def decode(bits: BitVector, dropAfterFirstAt: bool = False) -> str:
    """
    Decode bits as a string. Must be a multiple of 6 bits.

    Args:
        bits: n*6 bits that represent a string.
        dropAfterFirstAt: stop decoding at the first '@' pad character.
    Returns:
        str
    """
    numchar = len(bits) // 6
    bits_int = int(bits)
    s = []
    for i in range(numchar):
        shift = (numchar - 1 - i) * 6
        val = (bits_int >> shift) & 63
        if dropAfterFirstAt and val == 0:
            break
        s.append(characterLUT[val])

    return "".join(s)


def encode(string: str, bitSize: int | None = None) -> BitVector:
    """
    Encode an ASCII string into an AIS 6-bit BitVector.

    Args:
        string: python ascii string to encode.
        bitSize: optional size in bits (must be a multiple of 6).
    Returns:
        BitVector
    """
    if bitSize:
        assert bitSize % 6 == 0
    val = 0
    for char in string:
        val = (val << 6) | characterDict[char]
    total_bits = len(string) * 6

    if bitSize:
        if bitSize < total_bits:
            print(
                'ERROR:  string longer than specified bit count: "' + string + '"',
                bitSize,
                total_bits,
            )
            raise ValueError("Invalid payload or state")
        val <<= bitSize - total_bits
        total_bits = bitSize

    return binary.setBitVectorSize(BitVector.from_int(val), total_bits)


def unpad(string, removeBlanks=True):
    """
    Remove AIS string padding (@ and optionally trailing spaces).

    >>> unpad('@')
    ''
    >>> unpad('A@')
    'A'
    >>> unpad('ABCDEF1234@@@@@')
    'ABCDEF1234'
    >>> unpad('A@B')
    'A@B'
    >>> unpad(' ')
    ''
    >>> unpad('MY SHIP NAME    ')
    'MY SHIP NAME'
    >>> unpad('MY SHIP NAME    ',removeBlanks=False)
    'MY SHIP NAME    '

    Args:
        string: string to cleanup
        removeBlanks: set to true to strip spaces on the right
    Returns:
        str
    """
    string = string.rstrip("@")
    if removeBlanks:
        string = string.rstrip(" ")
    return string


def pad(string, length):
    """
    Pad a string out to the proper length with the @ character as required by the AIS spec.

    >>> pad('',0)
    ''
    >>> pad('',1)
    '@'
    >>> pad('A',1)
    'A'
    >>> pad('A',2)
    'A@'
    >>> pad('MY SHIP NAME',20)
    'MY SHIP NAME@@@@@@@@'

    Args:
        string: string to pad out
        length: number of characters that the string must be
    Returns:
        str of len length
    """
    return string.ljust(length, "@")


if __name__ == "__main__":
    from optparse import OptionParser

    myparser = OptionParser(usage="%prog [options]", version="%prog " + __version__)
    myparser.add_option(
        "--test",
        "--doc-test",
        dest="doctest",
        default=False,
        action="store_true",
        help="run the documentation tests",
    )
    #    verbosity.addVerbosityOptions(myparser)
    (options, args) = myparser.parse_args()

    success = True

    if options.doctest:
        import os

        print(os.path.basename(sys.argv[0]), "doctests ...", end=" ")
        sys.argv = [sys.argv[0]]
        #       if options.verbosity>=VERBOSE: sys.argv.append('-v')
        import doctest

        numfail, numtests = doctest.testmod()
        if numfail == 0:
            print("ok")
        else:
            print("FAILED")
            success = False

    if not success:
        sys.exit("Something Failed")
