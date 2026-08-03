#!/usr/bin/env python

"""Get the name and mmsi (User ID) for each msg 5 identification message.

This program requires that the nmea strings be sorted such that the
2nd part of the message comes directly after the first.  You can do
this by grepping for the USCG N-AIS station name.  This will prevent
interleaving of msg 5 nmea strings.

@requires: U{epydoc<http://epydoc.sourceforge.net/>} > 3.0alpha3

@author: '''+__author__+'''
@version: ''' + __version__ +'''
@var __date__: Date of last svn commit
@undocumented: __version__ __author__ __doc__ parser
@status: under development
@license: Apache 2.0

 TODO(schwehr):is this a repeat of merge5?
"""

import sys
from optparse import OptionParser

from ais import ais_msg_5
from aisutils import aisstring, binary


def getNameMMSI(logfile, outfile):
    for line in logfile:
        fields = line.split(",")[:6]
        if fields[2] != "1":  # Must be the start of a sequence
            continue
        if len(fields[5]) < 39:
            continue
        bv = binary.ais6tobitvec(fields[5][:39])  # Hacked for speed

        mmsi = ais_msg_5.decodeUserID(bv)
        name = aisstring.unpad(ais_msg_5.decodename(bv))
        outfile.write(str(mmsi) + " " + str(name) + "\n")


def main():
    parser = OptionParser(
        usage="%prog [options] logfile1 [logfile2 logfile3 ...] ",
        version="%prog " + __version__,
    )
    parser.add_option(
        "-o",
        "--output",
        dest="outputFileName",
        default=None,
        help="Name of the file to write [default: stdout]",
    )

    (options, args) = parser.parse_args()

    outfile = sys.stdout
    if options.outputFileName is not None:
        print("outfilename=", options.outputFileName)
        outfile = file(options.outputFileName, "w")
    if len(args) == 0:
        getNameMMSI(sys.stdin, outfile)
    else:
        for filename in args:
            getNameMMSI(file(filename), outfile)


if __name__ == "__main__":
    main()
