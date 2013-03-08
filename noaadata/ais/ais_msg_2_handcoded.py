#!/usr/bin/env python

__author__    = 'Kurt Schwehr'
__version__   = '$Revision: 4799 $'.split()[1]
__revision__  = __version__ # For pylint
__date__ = '$Date: 2006-09-25 11:09:02 -0400 (Mon, 25 Sep 2006) $'.split()[1]
__copyright__ = '2009'
__license__   = 'GPL v3'
__contact__   = 'kurt at ccom.unh.edu'
__deprecated__ = 'what goes here?'

__doc__ ='''
Adds SOTDMA commstate to messages 1 and 2

@undocumented: __doc__
@since: 2009-Jul-21
@status: under development
@organization: U{CCOM<http://ccom.unh.edu/>}
'''

import sys
from decimal import Decimal
from BitVector import BitVector

import binary, aisstring
import commstate
import sqlhelp

#import copy
# FIX: can I do this better with copy.deepcopy?

from ais_msg_1 import *

fieldList = (
	'MessageID',
	'RepeatIndicator',
	'UserID',
	'NavigationStatus',
	'ROT',
	'SOG',
	'PositionAccuracy',
	'longitude',
	'latitude',
	'COG',
	'TrueHeading',
	'TimeStamp',
	'RegionalReserved',
	'Spare',
	'RAIM',
) + commstate.sotdma_fields

def decode_aivdm(msg):
    bv = binary.ais6tobitvec(msg.split(',')[5])
    print decode(bv)

def decode(bv, validate=False):
	r = {}
	r['MessageID']=int(bv[:6])
	r['RepeatIndicator']=int(bv[6:8])
	r['UserID']=int(bv[8:38])
	r['NavigationStatus']=int(bv[38:42])
	r['ROT']=binary.signedIntFromBV(bv[42:50])
	r['SOG']=Decimal(int(bv[50:60]))/Decimal('10')
	r['PositionAccuracy']=int(bv[60:61])
	r['longitude']=Decimal(binary.signedIntFromBV(bv[61:89]))/Decimal('600000')
	r['latitude']=Decimal(binary.signedIntFromBV(bv[89:116]))/Decimal('600000')
	r['COG']=Decimal(int(bv[116:128]))/Decimal('10')
	r['TrueHeading']=int(bv[128:137])
	r['TimeStamp']=int(bv[137:143])
	r['RegionalReserved']=0
	r['Spare']=0
	r['RAIM']=bool(int(bv[148:149]))
	r.update(commstate.sotdma_parse_bits(bv[-19:]))
	return r

def sqlCreateStr(outfile=sys.stdout, fields=None, extraFields=None
		,addCoastGuardFields=True
		,dbType='postgres'
		):
	outfile.write(str(sqlCreate(fields,extraFields,addCoastGuardFields,dbType=dbType)))


def sqlCreate(fields=None, extraFields=None, addCoastGuardFields=True, dbType='postgres'):
	'''
	Return the sqlhelp object to create the table.

	@param fields: which fields to put in the create.  Defaults to all.
	@param extraFields: A sequence of tuples containing (name,sql type) for additional fields
	@param addCoastGuardFields: Add the extra fields that come after the NMEA check some from the USCG N-AIS format
	@type addCoastGuardFields: bool
	@param dbType: Which flavor of database we are using so that the create is tailored ('sqlite' or 'postgres')
	@return: An object that can be used to generate a return
	@rtype: sqlhelp.create
	'''
	if None == fields: fields = fieldList
	import sqlhelp
	c = sqlhelp.create('position',dbType=dbType)
	c.addPrimaryKey()
	if 'MessageID' in fields: c.addInt ('MessageID')
	if 'RepeatIndicator' in fields: c.addInt ('RepeatIndicator')
	if 'UserID' in fields: c.addInt ('UserID')
	if 'NavigationStatus' in fields: c.addInt ('NavigationStatus')
	if 'ROT' in fields: c.addInt ('ROT')
	if 'SOG' in fields: c.addDecimal('SOG',4,1)
	if 'PositionAccuracy' in fields: c.addInt ('PositionAccuracy')
	if dbType != 'postgres':
		if 'longitude' in fields: c.addDecimal('longitude',8,5)
	if dbType != 'postgres':
		if 'latitude' in fields: c.addDecimal('latitude',8,5)
	if 'COG' in fields: c.addDecimal('COG',4,1)
	if 'TrueHeading' in fields: c.addInt ('TrueHeading')
	if 'TimeStamp' in fields: c.addInt ('TimeStamp')
	if 'RegionalReserved' in fields: c.addInt ('RegionalReserved')
	if 'Spare' in fields: c.addInt ('Spare')
	if 'RAIM' in fields: c.addBool('RAIM')

        commstate.sql_fields(c) # Include both itdma and sotdma so we have one position table

	if addCoastGuardFields:
		# c.addInt('cg_s_rssi')     # Relative signal strength indicator
		# c.addInt('cg_d_strength')        # dBm receive strength
		# c.addVarChar('cg_x',10) # Idonno
		c.addInt('cg_t_arrival')        # Receive timestamp from the AIS equipment 'T'
		c.addInt('cg_s_slotnum')        # Slot received in
		c.addVarChar('cg_r',15)   # Receiver station ID  -  should usually be an MMSI, but sometimes is a string
		c.addInt('cg_sec')        # UTC seconds since the epoch

		c.addTimestamp('cg_timestamp') # UTC decoded cg_sec - not actually in the data stream

	if dbType == 'postgres':
		c.addPostGIS('Position','POINT',2,SRID=4326);

	return c

def printFields(params, out=sys.stdout, format='std', fieldList=None, dbType='postgres'):

	if 'std'==format:
		out.write("position:\n")
		if 'MessageID' in params: out.write("	MessageID:          "+str(params['MessageID'])+"\n")
		if 'RepeatIndicator' in params: out.write("	RepeatIndicator:    "+str(params['RepeatIndicator'])+"\n")
		if 'UserID' in params: out.write("	UserID:             "+str(params['UserID'])+"\n")
		if 'NavigationStatus' in params: out.write("	NavigationStatus:   "+str(params['NavigationStatus'])+"\n")
		if 'ROT' in params: out.write("	ROT:                "+str(params['ROT'])+"\n")
		if 'SOG' in params: out.write("	SOG:                "+str(params['SOG'])+"\n")
		if 'PositionAccuracy' in params: out.write("	PositionAccuracy:   "+str(params['PositionAccuracy'])+"\n")
		if 'longitude' in params: out.write("	longitude:          "+str(params['longitude'])+"\n")
		if 'latitude' in params: out.write("	latitude:           "+str(params['latitude'])+"\n")
		if 'COG' in params: out.write("	COG:                "+str(params['COG'])+"\n")
		if 'TrueHeading' in params: out.write("	TrueHeading:        "+str(params['TrueHeading'])+"\n")
		if 'TimeStamp' in params: out.write("	TimeStamp:          "+str(params['TimeStamp'])+"\n")
		if 'RegionalReserved' in params: out.write("	RegionalReserved:   "+str(params['RegionalReserved'])+"\n")
		if 'Spare' in params: out.write("	Spare:              "+str(params['Spare'])+"\n")
		if 'RAIM' in params: out.write("	RAIM:               "+str(params['RAIM'])+"\n")

                for field in commstate.sotdma_fields:
                    fieldname = '\t'+(field+':').ljust(30)
                    if field in params:
                        out.write(fieldname + str(params[field]) + '\n')
                    else:
                        out.write(fieldname + 'n/a\n')

	elif 'csv'==format:
		if None == options.fieldList:
			options.fieldList = fieldList
		needComma = False;
		for field in fieldList:
			if needComma: out.write(',')
			needComma = True
			if field in params:
				out.write(str(params[field]))
			# else: leave it empty
		out.write("\n")
	elif 'html'==format:
		printHtml(params,out)
	elif 'sql'==format:
		sqlInsertStr(params,out,dbType=dbType)
	elif 'kml'==format:
		printKml(params,out)
	elif 'kml-full'==format:
		out.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n")
		out.write("<kml xmlns=\"http://earth.google.com/kml/2.1\">\n")
		out.write("<Document>\n")
		out.write("	<name>position</name>\n")
		printKml(params,out)
		out.write("</Document>\n")
		out.write("</kml>\n")
	else:
		print "ERROR: unknown format:",format
		assert False

	return # Nothing to return

def main():
	from optparse import OptionParser
	parser = OptionParser(usage="%prog [options]",
		version="%prog "+__version__)

	parser.add_option('-v','--verbose',dest='verbose',default=False,action='store_true',
		help='Make the test output verbose')

	# FIX: remove nmea from binary messages.  No way to build the whole packet?
	# FIX: or build the surrounding msg 8 for a broadcast?
	typeChoices = ('binary','nmeapayload','nmea') # FIX: what about a USCG type message?
	parser.add_option('-t','--type',choices=typeChoices,type='choice',dest='ioType'
		,default='nmeapayload'
		,help='What kind of string to write for encoding ('+', '.join(typeChoices)+') [default: %default]')


	outputChoices = ('std','html','csv','sql' , 'kml','kml-full')
	parser.add_option('-T','--output-type',choices=outputChoices,type='choice',dest='outputType'
		,default='std'
		,help='What kind of string to output ('+', '.join(outputChoices)+') [default: %default]')

	parser.add_option('-o','--output',dest='outputFileName',default=None,
			  help='Name of the python file to write [default: stdout]')

	parser.add_option('-f','--fields',dest='fieldList',default=None, action='append',
			  choices=fieldList,
			  help='Which fields to include in the output.  Currently only for csv output [default: all]')

	parser.add_option('-p','--print-csv-field-list',dest='printCsvfieldList',default=False,action='store_true',
			  help='Print the field name for csv')

	parser.add_option('-c','--sql-create',dest='sqlCreate',default=False,action='store_true',
			  help='Print out an sql create command for the table.')

	parser.add_option('--latex-table',dest='latexDefinitionTable',default=False,action='store_true',
			  help='Print a LaTeX table of the type')

	parser.add_option('--text-table',dest='textDefinitionTable',default=False,action='store_true',
			  help='Print delimited table of the type (for Word table importing)')
	parser.add_option('--delimt-text-table',dest='delimTextDefinitionTable',default='\t'
			  ,help='Delimiter for text table [default: \'%default\'](for Word table importing)')


	dbChoices = ('sqlite','postgres')
	parser.add_option('-D','--db-type',dest='dbType',default='postgres'
			  ,choices=dbChoices,type='choice'
			  ,help='What kind of database ('+', '.join(dbChoices)+') [default: %default]')

	addMsgOptions(parser)

	(options,args) = parser.parse_args()

	outfile = sys.stdout
	if None!=options.outputFileName:
		outfile = file(options.outputFileName,'w')

	if options.sqlCreate:
		sqlCreateStr(outfile,options.fieldList,dbType=options.dbType)

	if options.latexDefinitionTable:
		latexDefinitionTable(outfile)

	# For conversion to word tables
	if options.textDefinitionTable:
		textDefinitionTable(outfile,options.delimTextDefinitionTable)

	if options.printCsvfieldList:
		# Make a csv separated list of fields that will be displayed for csv
		if None == options.fieldList: options.fieldList = fieldList
		import StringIO
		buf = StringIO.StringIO()
		for field in options.fieldList:
			buf.write(field+',')
		result = buf.getvalue()
		if result[-1] == ',': print result[:-1]
		else: print result

	if options.doDecode:
		if len(args)==0: args = sys.stdin
		for msg in args:
			bv = None

			if msg[0] in ('$','!') and msg[3:6] in ('VDM','VDO'):
				# Found nmea
				# FIX: do checksum
				bv = binary.ais6tobitvec(msg.split(',')[5])
			else: # either binary or nmeapayload... expect mostly nmeapayloads
				# assumes that an all 0 and 1 string can not be a nmeapayload
				binaryMsg=True
				for c in msg:
					if c not in ('0','1'):
						binaryMsg=False
						break
				if binaryMsg:
					bv = BitVector(bitstring=msg)
				else: # nmeapayload
					bv = binary.ais6tobitvec(msg)

			printFields(decode(bv)
				    ,out=outfile
				    ,format=options.outputType
				    ,fieldList=options.fieldList
				    ,dbType=options.dbType
				    )

############################################################
if __name__=='__main__':
    main()
