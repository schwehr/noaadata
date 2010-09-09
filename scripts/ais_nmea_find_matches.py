#!/usr/bin/env python

__author__    = 'Kurt Schwehr'
__version__   = '$Revision: 12308 $'.split()[1]
__revision__  = __version__ # For pylint
__date__ = '$Date: 2009-07-22 17:22:17 -0400 (Wed, 22 Jul 2009) $'.split()[1]
__copyright__ = '2008'
__license__   = 'GPL v3'
__contact__   = 'kurt at ccom.unh.edu'

__doc__='''Find the messages in file2 that are contained in file1.
Write out the linenumber in the output.  Should let me see time jumps in USCG data if I have matching
data from a more coherent logger.

Trying to do better than ais_nmea_uptime*.py

@requires: U{epydoc<http://epydoc.sourceforge.net/>} > 3.0
@since: 2010-Mar-26
@var __date__: Date of last svn commit
@undocumented: __version__ __author__ __doc__ parser
@status: In progress
'''
import sys
from aisutils.uscg import uscg_ais_nmea_regex

use_line_num = True # else use timestamp

msg_lut = {}
for line_num, line in enumerate(file(sys.argv[1])):
    line = line.strip()
    try:
        match = uscg_ais_nmea_regex.search(line).groupdict()
    except:
        print 'ignoring line:',line.strip()
    if use_line_num:
        msg_lut[match['body']] = line_num + 1
    else:
        msg_lut[match['body']] = msg['timeStamp']
print 'msgs in lut:', len(msg_lut),'from',line_num+1,'lines'

#o = file(sys.argv[2]+'.inboth','w')
if use_line_num:
    o = file(sys.argv[2]+'.linenum','w')
else:
    o = file(sys.argv[2]+'.time','w')


matches = 0
for line_num, line in enumerate(file(sys.argv[2])):
    if line_num % 500 == 0: sys.stderr.write('line %d\n' % line_num)
    try:
        match = uscg_ais_nmea_regex.search(line).groupdict()
    except:
        print 'ignoring line:',line.strip()
    if match['body'] in msg_lut:
        matches += 1
        o.write( str(msg_lut[match['body']]) + ' ' + line )
    else:
        print 'no match for line:',line.strip()

print 'matches:',matches,'from',line_num+1,'lines'
