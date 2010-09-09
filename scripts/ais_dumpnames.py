#!/usr/bin/env python
__version__ = '$Revision: 10020 $'.split()[1]
__date__ = '$Date: 2008-08-05 07:47:54 -0400 (Tue, 05 Aug 2008) $'.split()[1]
__author__ = 'Kurt Schwehr'

__doc__='''
Pull out names from msg 5 packages as fast as possible.  Dirty trick
version with no error checking.

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
from ais import ais_msg_5 as ais_msg_5
from ais import aisstring as aisstring
from ais.BitVector import BitVector

from aisutils.uscg import uscg_ais_nmea_regex

######################################################################
if __name__=='__main__':
    from optparse import OptionParser
    parser = OptionParser(usage="%prog [options] file1 [file2 ...]",
			    version="%prog "+__version__)
    parser.add_option('-o','--output',dest='outputFilename',default=None,
		      help='Name of the file to write [default: stdout]')
    parser.add_option('-v','--verbose',dest='verbose',default=False
                      ,action='store_true'
		      ,help='Name of the file to write [default: stdout]')

    (options,args) = parser.parse_args()
    o = sys.stdout
    if None != options.outputFilename: 
        o = open(options.outputFilename,'w')

    verbose = options.verbose
        
    #print args
    for filename in args:
	print filename
        linenum=1
	for line in file(filename):
            if linenum%1000==0:
                print 'line',linenum
            linenum += 1

            #try:
            
            match_obj = uscg_ais_nmea_regex.search(line)
            if match_obj is None:
                sys.stderr.write(line)
                continue
            station = match_obj.group('station')
            
            #except:
            #    sys.stderr.write('bad line: %s\n' %line)
            #    continue


	    fields = line.split(',')[:6]
	    if '1'!=fields[2]: # Must be the start of a sequence
                #if verbose:
                #    print 'skipping based on field 2',line
		continue
	    if len(fields[5])<39: 
                #if verbose:
                #    print 'skipping',line
                continue
	    bv = binary.ais6tobitvec(fields[5][:39]) # Hacked for speed
	    #print int(bv[8:38]),aisstring.decode(bv[112:232],True)
	    name = aisstring.decode(bv[112:232],True).strip('@ ')
	    mmsi = str(int(bv[8:38]))
            imo = str(int(bv[40:70]))
	    #if len(name)<1 or name[0]=='X': print 'TROUBLE with line:',line
	    if len(name)<1: print 'TROUBLE with line:',line
	    o.write (mmsi+' '+imo+' '+station+' '+name+'\n')

