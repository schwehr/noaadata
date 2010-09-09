#!/usr/bin/env python
__author__    = 'Kurt Schwehr'
__version__   = '$Revision: 4799 $'.split()[1]
__revision__  = __version__ # For pylint
__date__ = '$Date: 2006-09-25 11:09:02 -0400 (Mon, 25 Sep 2006) $'.split()[1]
__copyright__ = '2008'
__license__   = 'GPL v3'
__contact__   = 'kurt at ccom.unh.edu'

__doc__ ='''
Output python code for BBM encode and decode for a particular binary message

@requires: U{Python<http://python.org/>} >= 2.5
@requires: U{epydoc<http://epydoc.sourceforge.net/>} >= 3.0.1
@undocumented: __doc__
@since: 2008-Mar-30
@status: under development
@organization: U{CCOM<http://ccom.unh.edu/>} 
@see: IEC-PAS 61162-100 Ed. 1 Page 19: BBM - AIS Broadcast Binary Message
'''

import sys
import os

import StringIO

import ais.nmea

def create(payload,fill_bits=0,prefix='xx',seq_msg_id=0, msg_type=8,ais_chan='A'):
    '''
    >>> create('FstG8N6Kw<3<P6P1=87l0@',fill_bits=4,prefix='EC')
    '!ECBBM,1,1,0,A,8,FstG8N6Kw<3<P6P1=87l0@,4*7A'
    '''
    assert msg_type in (8,) #(8,14)
    # FIX: handle msg 14
    assert seq_msg_id >= 0 and seq_msg_id < 10
    assert ais_chan in 'AB'
    assert len(payload) <= 58 # FIX: handle messages with more than 348 bits
    assert fill_bits>=0 and fill_bits<=5

    p = ['!'+prefix+'BBM',]
    p.append('1') # total sentences - FIX: handle multiline BBM messages
    p.append('1') # sentence number - FIX: handle multiline BBM messages
    p.append(str(seq_msg_id))
    p.append(ais_chan)
    p.append(str(msg_type))
    p.append(payload)
    p.append(str(fill_bits)+'*')
    s = ','.join(p)
    
    s+=ais.nmea.checksumStr(s)
    return s



    
def do_doctest(verbose=False):
    '''
    @return: success
    @rtype: bool
    '''
    success = True

    print os.path.basename(sys.argv[0]), 'doctests ...',
    argv_orig = sys.argv
    sys.argv = [sys.argv[0]]
    if verbose:
        sys.argv.append('-v')
    import doctest
    numfail, numtests = doctest.testmod()
    if numfail == 0:
        print 'ok  numtests:', numtests
    else: 
        print 'FAILED', numfail, 'tests out of', numtests
        success = False
    sys.argv = argv_orig # Restore the original args
    return success

def main():
    '''
    FIX: document main
    '''
    from optparse import OptionParser
    parser = OptionParser(usage="%prog [options]",
                          version="%prog "+__version__+' ('+__date__+')')
    parser.add_option('--doc-test', dest='doctest', default=False, action='store_true',
                      help='run the documentation tests')

    parser.add_option('-v', '--verbose', dest='verbose', default=False, action='store_true',
                      help='run the tests run in verbose mode')

    (options, args) = parser.parse_args()

    if options.doctest:
        if not do_doctest(options.verbose):
            sys.exit('Something Failed')

if __name__ == '__main__':
    main()
