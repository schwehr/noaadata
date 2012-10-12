#!/usr/bin/env python

__version__ = '$Revision: 5231 $'.split()[1]
__date__ = '$Date: 2006-12-20 08:54:50 -0500 (Wed, 20 Dec 2006) $'.split()[1]
__author__ = 'Kurt Schwehr'

__doc__='''
Create a basic field for an ais message

Here is one of the simplest possible examples of an integer that goes
from 0 to 255:

FIX: how do I do epydoc indented text?

./aisfield.py -n MyName -t uint -d "My unsigned integer field"

<field name="MyName" numberofbits="8" type="uint">
<description>My unsigned integer field</description>
</field>



@author: U{'''+__author__+'''<http://xenon.stanford.edu/~schwehr/>}
@version: ''' + __version__ +'''
@copyright: 2006
@var __date__: Date of last svn commit
@undocumented: __version__ __author__ __doc__ myparser
@since: 2006-Sep-21
@status: under development
@organization: U{CCOM<http://ccom.unh.edu/>}
@license: GPL
'''

import sys

######################################################################
# Module Variables
######################################################################

typeBitsGuess = { 'bool':1,
		  'uint':8, 'sint':8,
		  'udecimal':8, 'sdecimal':8,
		  'float':32, 'double':64,   # These are mandatory
		  'aisstr6':6, 'ascii7':7,   # These are mandatory
}
'''
Best initial guess for each type size.  The floating point and
string values must be these sizes.
'''

typeChoices = ['bool','uint','sint','udecimal','sdecimal','float','double','aisstr6','ascii7']
'''
List of all the available types that may be used to fill an AIS message.
'''

# FIX: should bool be in here?
numberTypes = ['uint','sint','udecimal','sdecimal','float','double']
'''
Subset of typeChoices that only has the numeric types
'''

######################################################################
def tag(outfile,tagName,value,indent=''):
    '''
    Write out one complete tag
    @param outfile: open file to write to
    @param tagName: string containing the xml tag
    @param value: what to put between the begin and end tag.  Converts to a string
    @param indent: how much to indent the tag
    '''
    outfile.write(indent+'<'+tagName+'>'+str(value)+'</'+tagName+'>\n')

######################################################################
def getStubFieldDict():
    '''
    Convenience for thos that just want to tweak one or two things
    @return: example dictionary that can then be added to.
    '''

    return  {'maxRange': None, 'outputFile': None, 'lut': None,
	     'description': None, 'notes': None, 'required': None,
	     'minRange': None, 'numberOfBits': 1, 'units': None,
	     'scale': None, 'arrayLength': None, 'completeXml': False,
	     'decimalPlaces': None, 'unavailable': None,
	     'type': 'bool', 'name': None}

######################################################################
def makeField(options,out=sys.stdout):
    '''
    Write out one field of xml.  Here is a sample options dict

    {'maxRange': None, 'outputFile': None, 'lut': None, 'description': None, 'notes': None, 'required': None, 'minRange': None, 'numberOfBits': 1, 'units': None, 'scale': None, 'arrayLength': None, 'completeXml': False, 'decimalPlaces': None, 'unavailable': None, 'type': 'bool', 'name': None}

    @param options: dict of all the required fields

    '''
    o = options
    #out = sys.stdout

    if o.completeXml:
	out.write('<?xml version="1.0" encoding="utf-8"?>\n')
	out.write('<ais-binary-messages version="1.0">\n')
	out.write('<!-- FIX: add date -->\n')
	out.write('<!-- FIX: add user  -->\n')
	out.write('<!-- Produced by aisfield.py -->\n')
	out.write('<!-- Options: '+str(options)+'  -->\n')

    indent='\t'
    out.write(indent+'<field name="'+o.name+'" ')
    if options.arrayLength: out.write('arraylength="'+str(o.arrayLength)+'" ')
    out.write('numberofbits="'+str(o.numberOfBits)+'" type="'+o.type+'">\n')

    if True:
	indent+='\t'

	out.write(indent+'<description>'+o.description+'</description>\n')
	if o.notes:
	    for note in o.notes:
		out.write(indent+'<note>'+note+'</note>\n')

	if o.minRange: out.write(indent+'<range min="'+str(o.minRange)+'" max="'+str(o.maxRange)+'">\n')
	if o.unavailable: tag(out,'unavailable',o.unavailable,indent)
	if o.scale: tag(out,'scale',o.scale,indent)

	if o.decimalPlaces: tag(out,'decimalplaces',o.decimalPlaces,indent)
	if o.units: tag(out,'units',o.units,indent)

	if o.required: tag(out,'required',o.required,indent)

	if o.lut:
	    out.write(indent+'<lookuptable>\n')
	    indent += '\t'

	    for i in range(len(o.lut)):
		out.write(indent+'<entry key="'+str(i)+'">'+str(o.lut[i])+'</entry>\n')
	    indent=indent[:-1]
	    out.write(indent+'</lookuptable>\n')

	indent=indent[:-1]

    out.write(indent+'</field>\n')

    if o.completeXml:
	out.write('</ais-binary-messages>\n')

    return

######################################################################
def validate(options,notify=True):
    '''
    Check all of the options to make sure they work
    @param options: dict with all option fields
    @param notify: if true, emit error messages to stdout
    @return: True if options all ok
    '''
    o = options
    ok=True
    if not o.name:
	ok=False
	if notify: print 'Must specify the "name" of the variable'
    # FIX: check the name field, maybe with a regex

    if o.arrayLength and o.arrayLength<2:
	ok=False
	if notify: print 'Array length must be 2 or more'

    if (not o.numberOfBits) or (o.numberOfBits<1) or (o.numberOfBits>64):
	ok=False
	if notify: print 'Invalid number of bits:',o.numberOfBits

    if not o.description:
	ok=False
	if notify: print 'Must give a description'

    if o.unavailable and (o.type in numberTypes):
	try:
	    float(o.unavailable)
	except ValueError:
	    ok=False
	    if notify: print 'unavailable must be an number'

    # If unavailable and a string type , make sure that the string length fills the whole buffer
    if o.scale:
	try:
	    float(o.scale)
	except ValueError:
	    ok=False
	    if notify: print 'Scale must be an number'

    if o.lut and (o.type not in ['bool','uint']): #,'sint']):
	ok=False
	if notify: print 'Lookup tables must be an unsigned integer'

    # If int and no scale, can't specify decimal places

    return ok



######################################################################
if __name__=='__main__':
    from optparse import OptionParser
    myparser = OptionParser(usage="%prog [options]",
			    version="%prog "+__version__)


    myparser.add_option('-o','--output',dest='outputFile',default=None,
			help='Name of the xml file to write.  Opens for appending [default: stdout]')

    myparser.add_option('-c','--complete',dest='completeXml',default=False,action='store_true',
			help='Write out a complete xml file for a message.'
			+'Not really good for an ais message')

    myparser.add_option('-n','--name',dest='name',default=None,type='string',
			help='Name of the field [required]')

    myparser.add_option('-a','--array-length',dest='arrayLength',type='int',default=None,
			help='How many items to have or string length [default: not an array]')

    myparser.add_option('-N','--number-of-bits',dest='numberOfBits',type='int',default=None,
			help='Number of bits for each element in a field.'
			+'  ints and decimal can be in the range of 1..32.  [default: best guess]  ('+
			(''.join([choice+':'+str(typeBitsGuess[choice])+' ' for choice in typeBitsGuess])[:-1])
			+')')

    myparser.add_option('-t','--type',dest='type', type='choice', default='bool',
			choices=typeChoices,
			help='What type of data will the option represent? "u" for unsigned, "s" for signed. ('+
			(''.join([choice +' ' for choice in typeChoices]))[:-1]+')'
			)

    myparser.add_option('-d','--description',dest='description',default=None,type='string',
			help='Description of the field [required]')
    myparser.add_option('--note',dest='notes',action='append',type='string',default=None,
			help='0 or more notes to attach to the field')

    myparser.add_option('-r','--min-range',dest='minRange',default=None,type='float',
			help='Minimum possible value for a field.  [default: none]')
    myparser.add_option('-R','--max-range',dest='maxRange',default=None,type='float',
			help='Minimum possible value for a field.  [default: none]')


    myparser.add_option('-u','--unavailable',dest='unavailable',default=None,type='string',
			help='Value to use for when none is known.  [default: none]')

    #myparser.add_option('-s','--scale',dest='scale',default=None,type='float',
    # FIX: validate that the scale is actually a valid number
    myparser.add_option('-s','--scale',dest='scale',default=None,type='string',
			help='Value scale natural value to transmitted value.  [default: none]')

    myparser.add_option('-D','--decimal-places',dest='decimalPlaces',default=None,type='int',
			help='Decimal places to keep after undoing scale.  [default: none]')

    myparser.add_option('-U','--units',dest='units',default=None,type='string',
			help='What units are for the values.  [default: none]')

    myparser.add_option('--required',dest='required',default=None,type='float',
			help='TRY NOT TO USE THIS ONE accept for dac, fid, and efid.  '
			+'Specify manditory value if the field can not change.  [default: none]')

    myparser.add_option('-l','--lookup-table',dest='lut',default=None,action='append',type='string',
			help='Specify multiple entries in a lookup table.  Starts with 0.')

    (options,args) = myparser.parse_args()

    if not options.numberOfBits:
	options.numberOfBits = typeBitsGuess[options.type]

    # print options

    if not validate(options):
	sys.exit('ERROR: Options not ok.')

    if options.outputFile:
	makeField(options,file(options.outputFile,'a'))
    else:
	makeField(options)
