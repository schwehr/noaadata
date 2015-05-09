#!/usr/bin/env python

"""Try to get the mmsi info as fast as possible.

@bug: Cheap hack
 TODO(schwehr):Add option to make sure the that the receive stations are the same for uscg N-AIS data
 TODO(schwehr):Option to check the AIVDM tags to make sure that the messages should be combined
"""

from optparse import OptionParser
import sys

from aisutils import binary
from aisutils import aisstring
from aisutils.BitVector import BitVector


if __name__=='__main__':

    parser = OptionParser(usage="%prog [options] file1 [file2 ...]",
                          version="%prog ")

    parser.add_option(
        '-d','--dump-line',dest='dumpLine',default=False,
        action='store_true',
        help='Append the nmea string after the line [default: do not print the line]')

    parser.add_option('-o','--output',dest='outputFilename',default=None,
                      help='Name of the file to write [default: stdout]')

    (options,args) = parser.parse_args()
    o = sys.stdout
    if None != options.outputFilename: o = open(options.outFilename,'w')


    print args
    for filename in args:
        print filename
        for line in file(filename):
            if line[0]=='#':
                continue
	    fields = line.split(',')[:6]
	    if '1'!=fields[2]: # Must be the start of a sequence
		continue
	    if len(fields[5])<7: continue
	    bv = binary.ais6tobitvec(fields[5][:7]) # Hacked for speed
            int(bv[8:38])
	    mmsi = str(int(bv[8:38]))
	    o.write (mmsi)
            if options.dumpLine:
                o.write(' '+line.strip())
	    o.write ('\n')
