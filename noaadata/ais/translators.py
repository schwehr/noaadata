#!/Usr/bin/env python
__version__ = '$Revision: 2068 $'.split()[1] # See man ident
__date__ = '$Date: 2006-05-02 08:17:59 -0400 (Tue, 02 May 2006) $'.split()[1]
__author__ = 'Kurt Schwehr'

__doc__='''
Codecs to handle encoding to and from BitVectors

@requires: U{BitVector<http://cheeseshop.python.org/pypi/BitVector>}
@requires: U{epydoc<http://epydoc.sourceforge.net/>} > 3.0alpha3

@bug: FIX: need some doctests
@bug: need some asserts
@todo: maybe decorators?

@author: '''+__author__+'''
@version: ''' + __version__ +'''
@copyright: 2006
@var __date__: Date of last svn commit
@undocumented: __version__ __author__ __doc__ myparser
'''

# Python standard library
import sys
from decimal import Decimal

# External libraries
from BitVector import BitVector

# Local
import aisstring
import binary
#import verbosity
#from verbosity import BOMBASTIC,VERBOSE,TRACE,TERSE,ALWAYS


######################################################################


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

######################################################################
if __name__=='__main__':
    from optparse import OptionParser
    myparser = OptionParser(usage="%prog [options]",
			    version="%prog "+__version__)
    myparser.add_option('--test','--doc-test',dest='doctest',default=False,action='store_true',
                        help='run the documentation tests')
#    verbosity.addVerbosityOptions(myparser)
    (options,args) = myparser.parse_args()

    success=True

    if options.doctest:
	import os; print os.path.basename(sys.argv[0]), 'doctests ...',
	sys.argv= [sys.argv[0]]
#	if options.verbosity>=VERBOSE: sys.argv.append('-v')
	import doctest
	numfail,numtests=doctest.testmod()
	if numfail==0: print 'ok'
	else:
	    print 'FAILED'
	    success=False

    if not success:
	sys.exit('Something Failed')
