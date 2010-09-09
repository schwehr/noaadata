#!/usr/bin/env python

__version__ = '$Revision: 4791 $'.split()[1]
__date__ = '$Date: 2006-09-24 14:01:41 -0400 (Sun, 24 Sep 2006) $'.split()[1]
__author__ = 'Kurt Schwehr'

__doc__='''

Build a wxpython interface that uses the aisxmlbinmsg2py generated file to create a message string.

aisxmlbinmsg2py was getting too long, so this functionality is completely broken out.

@requires: U{lxml<http://codespeak.net/lxml/>}
@requires: U{epydoc<http://epydoc.sourceforge.net/>} >= 3.0alpha3
@requires: U{BitVector<http://cheeseshop.python.org/pypi/BitVector>} >= 1.2

@author: U{'''+__author__+'''<http://schwehr.org/>}
@version: ''' + __version__ +'''
@copyright: 2006
@var __date__: Date of last svn commit
@undocumented: __version__ __author__ __doc__ parser
@since: 2006-Sep-24
@status: under development
@organization: U{CCOM<http://ccom.unh.edu/>}
@license: GPL v2

@bug: FIX: Handle text fields
@bug: FIX: deal with the name mangling flag in the xml?
'''


import sys, os
from lxml import etree 

def hasSubTag(et,subtag):
    '''
    @return: true if the tag a sub tag with name subtag
    '''
    if 0<len(et.xpath(subtag)): return True
    return False

def hasBoolField(et):
    '''
    @return: true there exists a bool type field
    @param et: message element tree
    '''
    if 0<len(et.xpath('field[@type="bool"]')): return True
    return False


def useChoice(field):
    '''
    @return: true if should use a wxChoice for this field
    @param field: Field element tree
    '''
    fieldType = field.attrib['type']
    if fieldType not in ['int','uint','bool']: 
	return False
    # FIX: check for arrays... what to do?
    if fieldType == 'bool': return True
    if int(field.attrib['numberofbits'])>4: return False
    if hasSubTag(field,'lookuptable'): return True
    return False

def createChoiceList(o,fieldET):
    '''Create the wx.Choice list of entries'''
    lookup    = fieldET.xpath('lookuptable')[0]
    name      = fieldET.attrib['name']
    fieldType = fieldET.attrib['type']
    if fieldType == 'int':
	assert False # FIX: write me!
    elif fieldType == 'uint':
	o.write('\t'+name+'List = [\n')
	lastVal=0
	for entry in lookup.xpath('entry'):
	    entryKey = int(entry.attrib['key'])
	    #print lastVal, entryKey, range(lastVal,entryKey)
	    for i in range(lastVal,entryKey):
		o.write('\t\t\''+str(i)+'\',\n')
	    lastVal = entryKey + 1 # Ready for the next key
	    o.write('\t\t\''+str(entryKey)+' - '+entry.text+'\',\n')
	o.write('\t\t]\n')
    elif fieldType == 'bool':
	pass # Just one bool list
    else:
	print 'ERROR: not handling the choice for ',name,fieldType
	#assert False


def generateWxPython(infile,outfile, prefixName=False,verbose=False):
    '''
    @param infile: xml ais binary message definition file
    @param outfile: where to dump the python code
    '''

    aisMsgsET = etree.parse(infile).getroot()

    o = file(outfile,'w')
    os.chmod(outfile,0755)

    print 'FIX: make the python command user selectable'
    o.write('''#!/usr/bin/env pythonw   # mac specific
# FIX: put some documentation here!

import wx
''')

    #for msgET in aisMsgsET.xpath('message'):
    #o.write('#import '+msgET.attrib['name']+' \t# FIX: turn this back on\n') 
    print 'FIX: make a more rebust determination of the module name'
    o.write('#import '+outfile.split('.')[0]+'\t# FIX: turn this back on\n') 

    # FIX: NUKE THIS HACK...
    o.write('''

testParams = {'COG': 34.5,
 'MessageID': 1,
 'NavigationStatus': 3,
 'PositionAccuracy': 1,
 'Position_latitude': 37.424458333333334,
 'Position_longitude': -122.16328055555556,
 'RAIM': False,
 'ROT': -2,
 'RegionalReserved': 0,
 'RepeatIndicator': 1,
 'SOG': 101.9,
 'Spare': 0,
 'TimeStamp': 35,
 'TrueHeading': 41,
 'UserID': 1193046,
 'slotoffset': 1221,
 'syncstate': 2}

''')

    for msgET in aisMsgsET.xpath('message'):
	#if msgET.tag != 'message': continue
	print msgET.tag, msgET.attrib['name']

	if len(msgET.xpath('include-struct')) > 0:
	    sys.exit("ERROR: cannot handle xml that still has include-struct tags.\n  Please use expandais.py.")
	buildWxPythonMsg(o,msgET,prefixName=prefixName,verbose=verbose)


def buildWxPythonMsg(o,msgET, verbose=False, prefixName=False):
    '''
    Write a class for the wx python.

    @param o: open file where resulting code will be written
    @param msgET: Element Tree starting at a message node

    @todo: for lookuptable/entry values, make it also print the decoded value.
    @todo: use a different name for message and field
    '''
    assert(msgET.tag=='message')
    msgName = msgET.attrib['name']


    className = 'MsgFrame'
    if prefixName: className = msgName+'MsgFrame'


    o.write('class '+className+'(wx.Frame):\n')
    o.write('''\t\'\'\'
	# FIX: write doc string here for the frame
	\'\'\' 

''')
    for field in msgET.xpath('field'):
	if verbose: print 'Does field',field.attrib['name'],'use choice ...',
	if useChoice(field):
	    createChoiceList(o,field)
	    if verbose: print 'yes'
	elif verbose: print 'no'

    # All bools use the same lookup list
    if hasBoolField(msgET): o.write('\tBoolList=[\'False\',\'True\']\n')


    o.write('''
	def __init__(self,parent,title,msgDict):
		\'\'\'
		@param msgDict: Default values to use.
			Overwritten with the return values.
			Values that are required will be ignored.
		@type msgDict: dict
		\'\'\'
		wx.Frame.__init__(self,parent,-1,title,size=(640,480)) # FIX: what size?
		self.msgDict = msgDict # Save this so we can edit and return valies in the incoming dict

		defaults = testParams # FIX: turn off this hack and use the unavailable values

		sizer=wx.FlexGridSizer(rows=1,cols=2, vgap=13, hgap=13)
		sizer.AddGrowableCol(1)
		self.SetSizer(sizer)

''')

    for field in msgET.xpath('field'):
	# FIX: does not cope with arrays of anything other than strings
	name      = field.attrib['name']
	fieldType = field.attrib['type']
	numBits = int(field.attrib['numberofbits'])

	o.write('\n\t\t############################ Field '+name+' - '+fieldType+'\n')
	o.write('\t\ttxt = wx.StaticText(self,label=\''+name+'\')\n')
	if hasSubTag(field,'required'):
	    o.write('\t\tself.'+name+'Widget=wx.StaticText(self,label=\''+field.xpath('required')[0].text+'\')\n')
	else:
	    o.write('\t\tvalue=str(defaults[\''+name+'\'])\n')
	    o.write('\t\tif \''+name+'\' in msgDict: value = str(msgDict[\''+name+'\'])\n')
	    o.write('\t\tself.'+name+'Widget=')  # Need to lookup what to do...
	    if 'uint'==fieldType: 
		if useChoice(field): 
		    o.write('wx.Choice(self,-1, choices = self.'+name+'List)\n')
		    o.write('\t\tself.'+name+'Widget.SetSelection(int(value))\n')
		else:                o.write('wx.SpinCtrl(self,value=value,min=0,max='+str(2**numBits - 1)+')\n')
	    elif 'int'==fieldType: 
		if useChoice(field): 
		    o.write('wx.Choice(self,-1, choices = self.'+name+'List)\n')
		    # FIX: need to figure out how to select choices when they could be negative
		    assert False
		else: o.write('wx.SpinCtrl(self,value=value,min='+str(2**(numBits-1))+',max='+str(2**(numBits-1) - 1)+')\n')
	    elif 'bool'==fieldType:  
		o.write('wx.Choice(self,-1, choices = self.BoolList)\n')
		o.write('\t\tif defaults[\''+name+'\']: self.'+name+'Widget.SetSelection(1)\n')
		o.write('\t\telse:  self.'+name+'Widget.SetSelection(0)\n')
	    elif fieldType in ['udecimal','decimal']:
		scale = float(field.xpath('scale')[0].text)
		if fieldType=='udecimal':
		    o.write('wx.Slider(self,-1,float(value),0,'+str((2**numBits -1) / scale))
		else:
		    #print name, numBits
		    #print 2**(numBits-1)
		    start = '-'+str((2**(numBits-1)) / scale)
		    end   = str((2**(numBits-1) - 1) / scale)
		    if hasSubTag(field,'range'):
			# FIX: need to also create a validator that allow min .. max plus the unavailable
			range = field.xpath('range')[0]
			start = float(range.attrib['min'])
			end   = float(range.attrib['max'])
			if hasSubTag(field,'unavailable'):
			    unavailable = float(field.xpath('unavailable')[0].text)
			    if unavailable < start: start = unavailable
			    if end < unavailable:   end   = unavailable
			    
		    #print 'decimal',start,end
		    o.write('wx.Slider(self,-1,float(value),'+str(start)+','+str(end))
		o.write(',style=wx.SL_HORIZONTAL|wx.SL_AUTOTICKS | wx.SL_LABELS)\n')


	    else:
		print 'Please follow the GPS navigation system over the cliff',name,fieldType
		assert(False)

	    o.write('\t\tdel value\n')

	o.write('\n')
	o.write('\t\tsizer.Add(item=txt); del txt\n')
	o.write('\t\tsizer.Add(self.'+name+'Widget,flag=wx.EXPAND)\n')

    o.write('''
    		#######
    		#######  FINISH UP __init__
    		#######
		btnDone = wx.Button(self,label='Done')
	
		sizer.Add((1,35),0,wx.ADJUST_MINSIZE,0)
		sizer.Add(item=btnDone)
		btnDone.Bind(wx.EVT_BUTTON,self.OnDone)

		self.Layout() # Get yourself organized
		self.Show()

	def OnDone(self,evt):
        	\'\'\'
		Put all values into msgDict so that they get returned to the caller
		\'\'\'
''')
    for field in msgET.xpath('field'):
	name      = field.attrib['name']
	fieldType = field.attrib['type']

	if hasSubTag(field,'required'):
	    # FIX: need to set the type right on the values
	    if fieldType in ['int','uint']:
		o.write('\t\tself.msgDict[\''+name+'\']='+field.xpath('required')[0].text+'\n')
	    else:
		print 'FIX: need to write this case!'
		assert False
	else:
	    if fieldType in ['int','uint','bool','udecimal','decimal']:
		if useChoice(field): o.write('\t\tself.msgDict[\''+name+'\']=self.'+name+'Widget.GetSelection()\n')
		else:                o.write('\t\tself.msgDict[\''+name+'\']=self.'+name+'Widget.GetValue()\n')
	    elif fieldType in ['decimal','udecimal']:
		print 'FIX: what do I do about decimals?'
		o.write('\t\t#FIX: handle '+name+' '+fieldType+'\n')
	    else:
		print 'FIX: need to write the other cases here', name, fieldType
		o.write('\t\t#FIX: handle '+name+' '+fieldType+'\n')
		assert False

    o.write('\t\tself.Close(True)\n')



    # FIX: put in command line interface here...
    # FIX: what if there is more than one message??
    o.write('''
if __name__=='__main__':
	app = wx.PySimpleApp()
	theData={}
	frame = MsgFrame(None,\''''+msgName.capitalize()+''' Message Editor',theData)
	app.MainLoop()

	print 'finishing up', theData
''')


######################################################################
if __name__=='__main__':
    from optparse import OptionParser
    parser = OptionParser(usage="%prog [options]",
			    version="%prog "+__version__)

    parser.add_option('-o','--output',dest='outputFileName',default=None,
			help='Name of the python file to write')
#			help='Name of the python file to write [default: stdout]')

    parser.add_option('-i','-x','--xml-definition',dest='xmlFileName',default=None,
			help='XML definition file for the msg to use')

    parser.add_option('--doc-test',dest='doctest',default=False,action='store_true',
                        help='run the documentation tests')

    parser.add_option('-p','--prefix',dest='prefix',default=False,action='store_true',
                        help='put the field name in front of all function names.'
			+'  Allows multiple messages in one file')

    parser.add_option('-v','--verbose',dest='verbose',default=False,action='store_true',
                        help='run the tests run in verbose mode')

    (options,args) = parser.parse_args()

    success=True

    if options.doctest:
	import os; print os.path.basename(sys.argv[0]), 'doctests ...',
	argvOrig = sys.argv
	sys.argv= [sys.argv[0]]
	if options.verbose: sys.argv.append('-v')
	import doctest
	numfail,numtests=doctest.testmod()
	if numfail==0: print 'ok'
	else: 
	    print 'FAILED'
	    success=False
	sys.argv = argvOrig # Restore the original args
	del argvOrig # hide from epydoc
	sys.exit() # FIX: Will this exit success?

    if None==options.xmlFileName:
	sys.exit('ERROR: must specify an xml definition file.')
    if None==options.outputFileName:
	sys.exit('ERROR: must specify an python file to write to.')
    generateWxPython(options.xmlFileName,options.outputFileName,prefixName=options.prefix
		     ,verbose=options.verbose)

    print '\nrecommend running pychecker like this:'
    print '  pychecker -q',options.outputFileName
