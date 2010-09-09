#!/usr/bin/env python

__version__ = '$Revision: 8197 $'.split()[1]
__date__ = '$Date: 2008-01-11 10:57:46 -0500 (Fri, 11 Jan 2008) $'.split()[1]
__author__ = 'Kurt Schwehr'

__doc__='''

Dump a waterlevel message from the nmea msg 8.  This should be built
in to the binary messages.  They need to be able to handle themselves.

@requires: U{epydoc<http://epydoc.sourceforge.net/>} > 3.0alpha3
@requires: U{BitVector<http://cheeseshop.python.org/pypi/BitVector>}

@author: '''+__author__+'''
@version: ''' + __version__ +'''
@var __date__: Date of last svn commit
@undocumented: __version__ __author__ __doc__ parser
@status: under development
@license: GPL v2
'''

import sys
from decimal import Decimal
from BitVector import BitVector

import ais.binary    as binary
import ais.aisstring as aisstring


############################################################
if __name__=='__main__':

	from optparse import OptionParser
	parser = OptionParser(usage="%prog [options]",
		version="%prog "+__version__)

	parser.add_option('--doc-test',dest='doctest',default=False,action='store_true',
		help='run the documentation tests')
	parser.add_option('--unit-test',dest='unittest',default=False,action='store_true',
		help='run the unit tests')
	parser.add_option('-v','--verbose',dest='verbose',default=False,action='store_true',
		help='Make the test output verbose')

	inputChoices = ('binary','nmeapayload','nmea') # FIX: what about a USCG type message?
	parser.add_option('-t','--input=type',choices=inputChoices,type='choice',dest='inputType'
		,default='nmea'
		,help='What kind of string to expect ('+', '.join(inputChoices)+') [default: %default]')

	outputChoices = ('std','html','xml')
	parser.add_option('-T','--output-type',choices=outputChoices,type='choice',dest='outputType'
		,default='std'
		,help='What kind of string to output ('+', '.join(outputChoices)+') [default: %default]')

	parser.add_option('-o','--output',dest='outputFileName',default=None,
		      help='Name of the python file to write [default: stdout]')

	(options,args) = parser.parse_args()
	success=True

	if options.doctest:
		import os; print os.path.basename(sys.argv[0]), 'doctests ...',
		sys.argv= [sys.argv[0]]
		if options.verbose: sys.argv.append('-v')
		import doctest
		numfail,numtests=doctest.testmod()
		if numfail==0: print 'ok'
		else: 
			print 'FAILED'
			success=False

	if not success: sys.exit('Something Failed')
	del success # Hide success from epydoc

	if options.unittest:
		sys.argv = [sys.argv[0]]
		if options.verbose: sys.argv.append('-v')
		unittest.main()


	outfile = sys.stdout
	if None!=options.outputFileName:
		outfile = file(options.outputFileName,'w')

	bv=None
	for msg in args:
	    if   'binary'      == options.inputType:  bv = BitVector(bitstring=msg)
	    elif 'nmeapayload' == options.inputType:  bv = binary.ais6tobitvec(msg)
	    elif 'nmea'        == options.inputType:  bv = binary.ais6tobitvec(msg.split(',')[5])
	    else: sys.exit('ERROR: unknown inputType.  Help!')

	    #import ais.ais_msg_8 as m8
	    #m8dict = m8.decode(bv)
	    import ais.waterlevel as wl
	    
            #wl.printFields(wl.decode(m8dict['BinaryData']),out=outfile,format=options.outputType)
            wl.printFields(wl.decode(bv),out=outfile,format=options.outputType)
	
