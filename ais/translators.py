#!/Usr/bin/env python
"""Codecs to handle encoding to and from BitVectors."""

import sys
from decimal import Decimal
from optparse import OptionParser

from aisutils.BitVector import BitVector

from aisutils import aisstring
from aisutils import binary


encode={}
'''use this table to get the functions to go from usable values in python to bitvectors'''
decode={}
'''use this table to get the functions to go from bitvectors to usable values in python'''


######################################################################

def unsigned_int_enc(val,bitSize):
    '''@rtype: BitVector'''
    bv = BitVector(intVal=val)
    return binary.setBitVectorSize(bv,bitSize)
def unsigned_int_dec(bv):
    '''@rtype: int'''
    return int(bv)

encode['unsigned int']=unsigned_int_enc
decode['unsigned int']=unsigned_int_dec


def int_enc(val,bitSize):
    '''@rtype: BitVector'''
    return binary.bvFromSignedInt(int(val),bitSize)
def int_dec(bv):
    '''@rtype: int'''
    return int(binary.signedIntFromBV(bv))

encode['int']=int_enc
decode['int']=int_dec


def bool_enc(val,bitSize):
    '''@rtype: BitVector'''
    assert(bitSize==1)
    if val: return BitVector(bitString="0")
    return BitVector(bitString="1")
def bool_dec(bv):
    '''@rtype: bool'''
    assert(len(bv)==1)
    if bv[0]==0: return False
    return True

encode['bool']=bool_enc
decode['bool']=bool_dec


def unsigned_decimal_enc(val,bitSize):
    '''@rtype: BitVector'''
    # FIX: make sure there is no remainder
    bv = BitVector(intVal=int(val))
    return binary.setBitVectorSize(bv,bitSize)
def unsigned_decimal_dec(bv):
    '''@rtype: Decimal'''
    return Decimal(int(bv))

encode['unsigned decimal']=unsigned_decimal_enc
decode['unsigned decimal']=unsigned_decimal_dec


def decimal_enc(val,bitSize):
    '''@rtype: BitVector'''
    # FIX: make sure there is no remainder
    return binary.bvFromSignedInt(int(val),bitSize)
def decimal_dec(bv):
    '''@rtype: Decimal'''
    return Decimal(binary.signedIntFromBV(bv))

encode['decimal']=decimal_enc
decode['decimal']=decimal_dec


# floats suck... these have xml encode/decode fields
def float_enc(val,bitSize):
    '''@rtype: BitVector'''
    bv = binary.bvFromSignedInt(int(val),bitSize)
    return binary.setBitVectorSize(bv,bitSize)
def float_dec(bv):
    '''@rtype: float'''
    return float(binary.signedIntFromBV(bv))

encode['float']=float_enc
decode['float']=float_dec


encode['string']=aisstring.encode
decode['string']=aisstring.decode


if __name__=='__main__':
    myparser = OptionParser(usage="%prog [options]")
    options, args = myparser.parse_args()

    # TODO(schwehr): Call something or delete this main or file.
