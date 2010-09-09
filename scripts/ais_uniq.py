#!/usr/bin/env python
__version__ = '$Revision: 7470 $'.split()[1]
__date__ = '$Date: 2007-11-06 10:31:44 -0500 (Tue, 06 Nov 2007) $'.split()[1]
__author__ = 'Kurt Schwehr'

'''Find unique ais messages within a stream and give only those...

This would be wise to drop messages after a fixed set of time so
that the list of messages does not get too large.  Perhaps 30
minutes for 123 and 6 hours for msg 5?

@requires: U{epydoc<http://epydoc.sourceforge.net/>} > 3.0alpha3

@author: '''+__author__+'''
@version: ''' + __version__ +'''
@var __date__: Date of last svn commit
@undocumented: __version__ __author__ __doc__ parser
@status: under development
@license: GPL v2
@since: 2007-Jun-28

@todo: need a real ring buffer!
'''

import sys

if __name__=='__main__':
    from optparse import OptionParser
    parser = OptionParser(usage="%prog [options] file1.ais [file2.ais ...]",version="%prog "+__version__)

    parser.add_option('-l','--line-max',dest='maxLines'
                      ,type='int'
                      ,default=None
                      ,help='How many lines to keep in the table of known messages'
                      +'[default: unlimited (aka SLOW)]'
                      )

    parser.add_option('-i','--interval-check',dest='intervalCheck'
                      ,type='int'
                      ,default=100
                      ,help='How many lines to read before shrinking the known message buffer'
                      +'[default: %default]'
                      )


    parser.add_option('-v','--verbose',dest='verbose',default=False,action='store_true',
                      help='Make the program run output verbose')

    parser.add_option('-o','--outfile',dest='outFile',default=None,#default='normalized.ais',
                      help='Name of the AIS file to write [default: stdout]')

    (options,args) = parser.parse_args()
    verbose = options.verbose
    out = sys.stdout
    if options.outFile != None: 
        out = file(options.outFile,'w')

    for filename in args:
        if verbose: sys.stderr.write('FILE: '+filename+'\n')
        msgs=[]
        linenum=0
        dropcount=0
        for line in file(filename):
            linenum += 1
            if verbose and linenum % 1000==0:
                sys.stderr.write('line '+str(linenum)+'   dropcount: '+str(dropcount)+'  bufferlen:'+str(len(msgs))+ '\n')
            data = line.split(',')[5]
            if data not in msgs:
                out.write(line)
                msgs.append(data)
            else:
                dropcount += 1
                
            if options.maxLines!=None and linenum%options.intervalCheck==0 and len(msgs)>options.maxLines:
                overflow = len(msgs)-options.maxLines
                msgs=msgs[overflow:] # Chop from the front.  What is the fastest way to do this?

        sys.stderr.write('#   FILE: '+filename
                         +'   lines: '+str(linenum)
                         +'   dropcount: '+str(dropcount)
                         +'   bufferlen:'+str(len(msgs))
                         +'\n')
