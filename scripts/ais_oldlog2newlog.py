#!/usr/bin/env python

__version__ = '$Revision: 7470 $'.split()[1]
__date__ = '$Date: 2007-11-06 10:31:44 -0500 (Tue, 06 Nov 2007) $'.split()[1]
__author__ = 'Kurt Schwehr'

__doc__='''

Convert the old ais-py log format with ZDA nmea strings to the USCG log format

@requires: U{epydoc<http://epydoc.sourceforge.net/>} > 3.0alpha3

@author: U{'''+__author__+'''<http://schwehr.org/>}
@version: ''' + __version__ +'''
@copyright: 2007
@var __date__: Date of last svn commit
@undocumented: __version__ __author__ __doc__ parser
@since: 2007-Jun-20
@status: under development
@organization: U{CCOM<http://ccom.unh.edu/>}
@license: GPL v2

'''


import sys, calendar

#import nmea
#import nmeamessages as nm
import nmea.zda

if __name__=='__main__':

    from optparse import OptionParser

    parser = OptionParser(usage="%prog [options]", version="%prog "+__version__)
    parser.add_option('-s','--station-name',dest='station'
                      ,type='string'
                      ,default='unknown'
                      ,help='Receiver station name.  [default: %default]')
    
    parser.add_option('-o','--output',dest='outFile',type='string'
                      ,default=None
                      ,help='Where to write the resulting stream [default: stdout]')
    
    parser.add_option('-v','--verbose',dest='verbose',default=False,action='store_true'
                      ,help='Make the program be verbose')

    (options,args) = parser.parse_args()
    verbose = options.verbose

    out = sys.stdout
    if options.outFile!=None: out = file(options.outFile,'w')

    for filename in args:
        linenum=0
        curTime=None
        for line in file(filename):
            linenum+=1
            if verbose and linenum%1000==0:
                sys.stderr.write('line '+str(linenum)+'\n')
            if '#'==line[0]:
                continue # Skip comments
            if line[3:6]=='ZDA':
                z = nmea.zda.zdaDecode(line)
                timeTuple = (int(z['year']),int(z['mon']),int(z['day']),int(z['hour']),int(z['min']),z['decimalsec'])
                curTime = calendar.timegm(timeTuple)
                continue
            if line[1:6] in ('AITXT','AIVDM') and None!=curTime:
                out.write(line.strip()+',r'+options.station+','+str(curTime)+'\n')
                continue

            print 'WARNING: unknown line...',line,
