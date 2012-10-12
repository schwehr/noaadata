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
Adds commstate to the msg 4 definition

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

from ais_msg_4 import *


fieldList = (
	'MessageID',
	'RepeatIndicator',
	'UserID',
	'Time_year',
	'Time_month',
	'Time_day',
	'Time_hour',
	'Time_min',
	'Time_sec',
	'PositionAccuracy',
	'Position_longitude',
	'Position_latitude',
	'fixtype',
	'Spare',
	'RAIM',
) + commstate.sotdma_fields

def decode_aivdm(msg):
    bv = binary.ais6tobitvec(msg.split(',')[5])
    print decode(bv)

def decode(bv, validate=False):
	'''Unpack a bsreport message

	Fields in params:
	  - MessageID(uint): AIS message number.  Must be 4 (field automatically set to "4")
	  - RepeatIndicator(uint): Indicated how many times a message has been repeated
	  - UserID(uint): Unique ship identification number (MMSI)
	  - Time_year(uint): Current time stamp  year 1-9999
	  - Time_month(uint): Current time stamp  month 1..12
	  - Time_day(uint): Current time stamp  day of the month 1..31
	  - Time_hour(uint): Current time stamp  UTC hours 0..23
	  - Time_min(uint): Current time stamp  minutes
	  - Time_sec(uint): Current time stamp  seconds
	  - PositionAccuracy(uint): Accuracy of positioning fixes
	  - Position_longitude(decimal): Location of base station  East West location
	  - Position_latitude(decimal): Location of base station  North South location
	  - fixtype(uint): Method used for positioning
	  - Spare(uint): Not used.  Should be set to zero. (field automatically set to "0")
	  - RAIM(bool): Receiver autonomous integrity monitoring flag
	  - state_syncstate(uint): Communications State - SOTDMA  Sycronization state
	  - state_slottimeout(uint): Communications State - SOTDMA  Frames remaining until a new slot is selected
	  - state_slotoffset(uint): Communications State - SOTDMA  In what slot will the next transmission occur. BROKEN
	@type bv: BitVector
	@param bv: Bits defining a message
	@param validate: Set to true to cause checking to occur.  Runs slower.  FIX: not implemented.
	@rtype: dict
	@return: params
	'''

	#Would be nice to check the bit count here..
	#if validate:
	#	assert (len(bv)==FIX: SOME NUMBER)
	r = {}
	r['MessageID']=4
	r['RepeatIndicator']=int(bv[6:8])
	r['UserID']=int(bv[8:38])
	r['Time_year']=int(bv[38:52])
	r['Time_month']=int(bv[52:56])
	r['Time_day']=int(bv[56:61])
	r['Time_hour']=int(bv[61:66])
	r['Time_min']=int(bv[66:72])
	r['Time_sec']=int(bv[72:78])
	r['PositionAccuracy']=int(bv[78:79])
	r['Position_longitude']=Decimal(binary.signedIntFromBV(bv[79:107]))/Decimal('600000')
	r['Position_latitude']=Decimal(binary.signedIntFromBV(bv[107:134]))/Decimal('600000')
	r['fixtype']=int(bv[134:138])
	r['Spare']=0
	r['RAIM']=bool(int(bv[148:149]))
        r.update(commstate.sotdma_parse_bits(bv[-19:]))
        #r['commstate'] = commstate.sotdma_parse_bits(bv[-19:])
	#r['state_syncstate']=int(bv[149:151])
	#r['state_slottimeout']=int(bv[151:154])
	#r['state_slotoffset']=int(bv[154:168])
	return r


def sqlCreateStr(outfile=sys.stdout, fields=None, extraFields=None
		,addCoastGuardFields=True
		,dbType='postgres'
		):
	outfile.write(str(sqlCreate(fields,extraFields,addCoastGuardFields,dbType=dbType)))

def sqlCreate(fields=None, extraFields=None, addCoastGuardFields=True, dbType='postgres'):
	if None == fields: fields = fieldList
	import sqlhelp
	c = sqlhelp.create('bsreport',dbType=dbType)
	c.addPrimaryKey()
	if 'MessageID' in fields: c.addInt ('MessageID')
	if 'RepeatIndicator' in fields: c.addInt ('RepeatIndicator')
	if 'UserID' in fields: c.addInt ('UserID')
	if 'Time_year' in fields: c.addInt ('Time_year')
	if 'Time_month' in fields: c.addInt ('Time_month')
	if 'Time_day' in fields: c.addInt ('Time_day')
	if 'Time_hour' in fields: c.addInt ('Time_hour')
	if 'Time_min' in fields: c.addInt ('Time_min')
	if 'Time_sec' in fields: c.addInt ('Time_sec')
	if 'PositionAccuracy' in fields: c.addInt ('PositionAccuracy')
	if dbType != 'postgres':
		if 'Position_longitude' in fields: c.addDecimal('Position_longitude',8,5)
	if dbType != 'postgres':
		if 'Position_latitude' in fields: c.addDecimal('Position_latitude',8,5)
	if 'fixtype' in fields: c.addInt ('fixtype')
	if 'Spare' in fields: c.addInt ('Spare')
	if 'RAIM' in fields: c.addBool('RAIM')
	#if 'state_syncstate' in fields: c.addInt ('state_syncstate')
	#if 'state_slottimeout' in fields: c.addInt ('state_slottimeout')
	#if 'state_slotoffset' in fields: c.addInt ('state_slotoffset')

        commstate.sotdma_sql_fields(c)

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
		#--- EPSG 4326 : WGS 84
		#INSERT INTO "spatial_ref_sys" ("srid","auth_name","auth_srid","srtext","proj4text") VALUES (4326,'EPSG',4326,'GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],TOWGS84[0,0,0,0,0,0,0],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.01745329251994328,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4326"]]','+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs ');
		c.addPostGIS('Position','POINT',2,SRID=4326);

	return c

def printFields(params, out=sys.stdout, format='std', fieldList=None, dbType='postgres'):
	'''Print a bsreport message to stdout.

	Fields in params:
	  - MessageID(uint): AIS message number.  Must be 4 (field automatically set to "4")
	  - RepeatIndicator(uint): Indicated how many times a message has been repeated
	  - UserID(uint): Unique ship identification number (MMSI)
	  - Time_year(uint): Current time stamp  year 1-9999
	  - Time_month(uint): Current time stamp  month 1..12
	  - Time_day(uint): Current time stamp  day of the month 1..31
	  - Time_hour(uint): Current time stamp  UTC hours 0..23
	  - Time_min(uint): Current time stamp  minutes
	  - Time_sec(uint): Current time stamp  seconds
	  - PositionAccuracy(uint): Accuracy of positioning fixes
	  - Position_longitude(decimal): Location of base station  East West location
	  - Position_latitude(decimal): Location of base station  North South location
	  - fixtype(uint): Method used for positioning
	  - Spare(uint): Not used.  Should be set to zero. (field automatically set to "0")
	  - RAIM(bool): Receiver autonomous integrity monitoring flag
	  - state_syncstate(uint): Communications State - SOTDMA  Sycronization state
	  - state_slottimeout(uint): Communications State - SOTDMA  Frames remaining until a new slot is selected
	  - state_slotoffset(uint): Communications State - SOTDMA  In what slot will the next transmission occur. BROKEN
	@param params: Dictionary of field names/values.
	@param out: File like object to write to
	@rtype: stdout
	@return: text to out
	'''

	if 'std'==format:
		out.write("bsreport:\n")
		if 'MessageID' in params: out.write("	MessageID:           "+str(params['MessageID'])+"\n")
		if 'RepeatIndicator' in params: out.write("	RepeatIndicator:     "+str(params['RepeatIndicator'])+"\n")
		if 'UserID' in params: out.write("	UserID:              "+str(params['UserID'])+"\n")
		if 'Time_year' in params: out.write("	Time_year:           "+str(params['Time_year'])+"\n")
		if 'Time_month' in params: out.write("	Time_month:          "+str(params['Time_month'])+"\n")
		if 'Time_day' in params: out.write("	Time_day:            "+str(params['Time_day'])+"\n")
		if 'Time_hour' in params: out.write("	Time_hour:           "+str(params['Time_hour'])+"\n")
		if 'Time_min' in params: out.write("	Time_min:            "+str(params['Time_min'])+"\n")
		if 'Time_sec' in params: out.write("	Time_sec:            "+str(params['Time_sec'])+"\n")
		if 'PositionAccuracy' in params: out.write("	PositionAccuracy:    "+str(params['PositionAccuracy'])+"\n")
		if 'Position_longitude' in params: out.write("	Position_longitude:  "+str(params['Position_longitude'])+"\n")
		if 'Position_latitude' in params: out.write("	Position_latitude:   "+str(params['Position_latitude'])+"\n")
		if 'fixtype' in params: out.write("	fixtype:             "+str(params['fixtype'])+"\n")
		if 'Spare' in params: out.write("	Spare:               "+str(params['Spare'])+"\n")
		if 'RAIM' in params: out.write("	RAIM:                "+str(params['RAIM'])+"\n")
# 		if 'state_syncstate' in params: out.write("	state_syncstate:     "+str(params['state_syncstate'])+"\n")
# 		if 'state_slottimeout' in params: out.write("	state_slottimeout:   "+str(params['state_slottimeout'])+"\n")
# 		if 'state_slotoffset' in params: out.write("	state_slotoffset:    "+str(params['state_slotoffset'])+"\n")
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
		out.write("	<name>bsreport</name>\n")
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

	parser.add_option('--doc-test',dest='doctest',default=False,action='store_true',
		help='run the documentation tests')
	parser.add_option('--unit-test',dest='unittest',default=False,action='store_true',
		help='run the unit tests')
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


	if options.doEncode:
		# First make sure all non required options are specified
		if None==options.RepeatIndicatorField: parser.error("missing value for RepeatIndicatorField")
		if None==options.UserIDField: parser.error("missing value for UserIDField")
		if None==options.Time_yearField: parser.error("missing value for Time_yearField")
		if None==options.Time_monthField: parser.error("missing value for Time_monthField")
		if None==options.Time_dayField: parser.error("missing value for Time_dayField")
		if None==options.Time_hourField: parser.error("missing value for Time_hourField")
		if None==options.Time_minField: parser.error("missing value for Time_minField")
		if None==options.Time_secField: parser.error("missing value for Time_secField")
		if None==options.PositionAccuracyField: parser.error("missing value for PositionAccuracyField")
		if None==options.Position_longitudeField: parser.error("missing value for Position_longitudeField")
		if None==options.Position_latitudeField: parser.error("missing value for Position_latitudeField")
		if None==options.fixtypeField: parser.error("missing value for fixtypeField")
		if None==options.RAIMField: parser.error("missing value for RAIMField")
		if None==options.state_syncstateField: parser.error("missing value for state_syncstateField")
		if None==options.state_slottimeoutField: parser.error("missing value for state_slottimeoutField")
		if None==options.state_slotoffsetField: parser.error("missing value for state_slotoffsetField")
		msgDict={
			'MessageID': '4',
			'RepeatIndicator': options.RepeatIndicatorField,
			'UserID': options.UserIDField,
			'Time_year': options.Time_yearField,
			'Time_month': options.Time_monthField,
			'Time_day': options.Time_dayField,
			'Time_hour': options.Time_hourField,
			'Time_min': options.Time_minField,
			'Time_sec': options.Time_secField,
			'PositionAccuracy': options.PositionAccuracyField,
			'Position_longitude': options.Position_longitudeField,
			'Position_latitude': options.Position_latitudeField,
			'fixtype': options.fixtypeField,
			'Spare': '0',
			'RAIM': options.RAIMField,
			'state_syncstate': options.state_syncstateField,
			'state_slottimeout': options.state_slottimeoutField,
			'state_slotoffset': options.state_slotoffsetField,
		}

		bits = encode(msgDict)
		if 'binary'==options.ioType: print str(bits)
		elif 'nmeapayload'==options.ioType:
		    # FIX: figure out if this might be necessary at compile time
		    #print "bitLen",len(bits)
		    bitLen=len(bits)
		    if bitLen%6!=0:
			bits = bits + BitVector(size=(6 - (bitLen%6)))  # Pad out to multiple of 6
		    #print "result:",binary.bitvectoais6(bits)[0]
		    print binary.bitvectoais6(bits)[0]


		# FIX: Do not emit this option for the binary message payloads.  Does not make sense.
		elif 'nmea'==options.ioType:
		    #bitLen=len(bits)
                    #if bitLen%6!=0:
		    #	bits = bits + BitVector(size=(6 - (bitLen%6)))  # Pad out to multiple of 6
                    import aisutils.uscg as uscg
                    nmea = uscg.create_nmea(bits)
                    print nmea
                    #
                    #


                    #sys.exit("FIX: need to implement creating nmea capability")
		else: sys.exit('ERROR: unknown ioType.  Help!')


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
