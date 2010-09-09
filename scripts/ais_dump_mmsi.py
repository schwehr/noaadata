#!/usr/bin/env python
__version__ = '$Revision: 7470 $'.split()[1]
__date__ = '$Date: 2007-11-06 10:31:44 -0500 (Tue, 06 Nov 2007) $'.split()[1]
__author__ = 'Kurt Schwehr'

__doc__='''
Try to get the mmsi info as fast as possible

@requires: U{epydoc<http://epydoc.sourceforge.net/>} >= 3.0alpha3
@requires: U{BitVector<http://cheeseshop.python.org/pypi/BitVector>} >= 1.2

@author: U{'''+__author__+'''<http://schwehr.org/>}
@version: ''' + __version__ +'''
@copyright: 2006
@var __date__: Date of last svn commit
@undocumented: __version__ __author__ __doc__ parser
@since: 2006-Dec
@status: under development
@organization: U{CCOM<http://ccom.unh.edu/>}
@license: GPL v2

@bug: Cheap hack
@todo: Add option to make sure the that the receive stations are the same for uscg N-AIS data
@todo: Option to check the AIVDM tags to make sure that the messages should be combined
'''

import sys
from ais import binary as binary
#from ais import ais_msg_1 as m1
# Going to do this by hand
from ais import aisstring as aisstring
from ais.BitVector import BitVector

######################################################################
if __name__=='__main__':
    from optparse import OptionParser
    parser = OptionParser(usage="%prog [options] file1 [file2 ...]",
			    version="%prog "+__version__)

    parser.add_option('-d','--dump-line',dest='dumpLine',default=False
                      ,action='store_true'
		      ,help='Append the nmea string after the line [default: do not print the line]')

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

