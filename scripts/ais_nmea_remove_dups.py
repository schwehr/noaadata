#!/usr/bin/env python
__author__    = 'Kurt Schwehr'
__version__   = '$Revision: 4799 $'.split()[1]
__revision__  = __version__ # For pylint
__date__ = '$Date: 2006-09-25 11:09:02 -0400 (Mon, 25 Sep 2006) $'.split()[1]
__copyright__ = '2009'
__license__   = 'GPL v3'
__contact__   = 'kurt@ccom.unh.edu'
__deprecated__ = 'what goes here?'

__doc__ ='''
Take a normalized AIS NMEA stream of AIVDM and attempt to remove
duplicates.  Looks just at the payload... ignores USCG metadata

Purely based on if we have seen a payload that is the same in the last
batch of messages.

@requires: U{Python<http://python.org/>} >= 2.6
@requires: U{epydoc<http://epydoc.sourceforge.net/>} >= 3.0.1

@undocumented: __doc__
@since: 2009-Aug-01
@status: under development
@organization: U{CCOM<http://ccom.unh.edu/>} 

@see: U{Sean Gillies How to lay out Python project code http://sgillies.net/blog/845/how-to-lay-out-python-project-code/}
'''
import sys
import os


#lookback_dist = 1000
#received = {}  # Dict of FIFO's for each message type.


def remove_dups(in_file, outfile, lookback_dist=1000, pos_only=False, verbose = False):
    payloads = []
    if isinstance(in_file,str):
        in_file = file(in_file)
        
    o = outfile #file('unique.ais','w')

    dropped = 0
    for line_num, line in enumerate(in_file):
        if verbose and line_num % 10000 == 0:
            sys.stderr.write('line_num: %d dropped: %d\n' % (line_num, dropped))

        # Pass through non AIS traffic
        if '!AIVD' != line[:5]:
            o.write(line)
            continue

        payload = line.split(',')[5]

        if pos_only and payload[0] not in ('1','2','3'):
            o.write(line)
            continue

        if payload in payloads:
            dropped += 1
            continue

        if len(payloads) > lookback_dist:
            payloads.pop(0)

        payloads.append(payload)
        o.write(line)

def main():
    from optparse import OptionParser
    parser = OptionParser(usage="%prog [options]",
                          version="%prog "+__version__+' ('+__date__+')')
    parser.add_option('-l', '--lookback-dist', dest='lookback_dist', 
                      default=1000, type='int',
                      help='Number of message payloads to track for duplicates [default: %default]')
    parser.add_option('-p', '--pos-only', dest='pos_only', default=False, action='store_true',
                      help='Only apply the duplicate check to position messages')
    parser.add_option('-o','--output-file', dest='output', default=sys.stdout,
                       help='Where to write the results [default: stdout]')
    parser.add_option('-v', '--verbose', dest='verbose', default=False, action='store_true',
                      help='run the tests run in verbose mode')

    (options, args) = parser.parse_args()
    v = options.verbose

    if isinstance(options.output, str):
        options.output = file(options.output,'w')

    if len(args) == 0:
        args.append(sys.stdin)

    for in_file in args:
        remove_dups(in_file, options.output, options.lookback_dist, options.pos_only, v)

if __name__ == '__main__':
    main()
