#!/usr/bin/env python

__version__ = '$Revision: 4791 $'.split()[1]
__date__ = '$Date: 2008-10-08 $'.split()[1]
__author__ = 'xmlbinmsg'

__doc__='''

Hand coded processing of ais msg 24

@requires: U{epydoc<http://epydoc.sourceforge.net/>} > 3.0alpha3
@requires: U{BitVector<http://cheeseshop.python.org/pypi/BitVector>}

@author: '''+__author__+'''
@version: ''' + __version__ +'''
@var __date__: Date of last svn commit
@undocumented: __version__ __author__ __doc__ parser
@status: under development
@license: Generated code has no license
@todo: FIX: put in a description of the message here with fields and types.
'''

import sys
from decimal import Decimal
from BitVector import BitVector

import binary, aisstring

# FIX: check to see if these will be needed
TrueBV  = BitVector(bitstring="1")
"Why always rebuild the True bit?  This should speed things up a bunch"
FalseBV = BitVector(bitstring="0")
"Why always rebuild the False bit?  This should speed things up a bunch"


fieldList = (
	'MessageID',
	'RepeatIndicator',
	'UserID',
	'partnum',
	'name',
        'shipandcargo',
        'vendorid',
        'callsign',
        'dimA',
        'dimB',
        'dimC',
        'dimD',
        'mothership',
        'spare',
)

fieldListPostgres = fieldList

toPgFields = {}
'''
Go to the Postgis field names from the straight field name
'''

fromPgFields = {}
'''
Go from the Postgis field names to the straight field name
'''

pgTypes = {}
'''
Lookup table for each postgis field name to get its type.
'''

def encode(params, validate=False):
	'''Create a b_staticdata

	Fields in params:
	  - MessageID(uint): AIS message number.  Must be 19 (field automatically set to "19")
	  - RepeatIndicator(uint): Indicated how many times a message has been repeated
	  - UserID(uint): Unique ship identification number (MMSI)
          - FIX... add the rest
	@param params: Dictionary of field names/values.  Throws a ValueError exception if required is missing
	@param validate: Set to true to cause checking to occur.  Runs slower.  FIX: not implemented.
	@rtype: BitVector
	@return: encoded binary message (for binary messages, this needs to be wrapped in a msg 8
	@note: The returned bits may not be 6 bit aligned.  It is up to you to pad out the bits.
	'''

	bvList = []
	bvList.append(binary.setBitVectorSize(BitVector(intVal=19),6))
	if 'RepeatIndicator' in params:
		bvList.append(binary.setBitVectorSize(BitVector(intVal=params['RepeatIndicator']),2))
	else:
		bvList.append(binary.setBitVectorSize(BitVector(intVal=0),2))
	bvList.append(binary.setBitVectorSize(BitVector(intVal=params['UserID']),30))

        assert False

	return binary.joinBV(bvList)

def decode(bv, validate=False):
	'''Unpack a b_staticdata

	Fields in params:
	  - MessageID(uint): AIS message number.  Must be 19 (field automatically set to "19")
	  - RepeatIndicator(uint): Indicated how many times a message has been repeated
	  - UserID(uint): Unique ship identification number (MMSI)
          - FIX: ... add the rest of the fields
	@type bv: BitVector
	@param bv: Bits defining a message
	@param validate: Set to true to cause checking to occur.  Runs slower.  FIX: not implemented.
	@rtype: dict
	@return: params
	'''

	if len(bv) not in (160,162,168): # 162 is 160 with 2 bits padding
		print 'warning... len is not 160 or 168.  Found',len(bv)

	r = {}
	r['MessageID']=24
	r['RepeatIndicator']=int(bv[6:8])
	r['UserID']=int(bv[8:38])
        r['partnum']=int(bv[38:40])
        assert r['partnum'] in (0,1)

        if 0 == r['partnum']: # Part A message
            r['name']=aisstring.decode(bv[40:160]).rstrip(' @')

        elif 1 == r['partnum']: # Part B message
            r['shipandcargo']=int(bv[40:48])
            r['vendorid']=aisstring.decode(bv[48:90]).rstrip(' @')
            r['callsign']=aisstring.decode(bv[90:132]).rstrip(' @')
            r['dimA']=int(bv[132:141])
            r['dimB']=int(bv[141:150])
            r['dimC']=int(bv[150:156])
            r['dimD']=int(bv[156:162])
            r['mothership']=int(bv[132:162])
            r['spare']=int(bv[162:168])
        elif 2 == r['partnum']: # Part C message - no such thing
            assert False
        elif 3 == r['partnum']: # Part D message - no such thing
            assert False

	return r

def decodeMessageID(bv, validate=False):
	return 24

def decodeRepeatIndicator(bv, validate=False):
	return int(bv[6:8])

def decodeUserID(bv, validate=False):
	return int(bv[8:38])

### Removed lots

def printFields(params, out=sys.stdout, format='std', fieldList=None, dbType='postgres'):
	'''Print a b_staticdata message to stdout.

	Fields in params:
	  - MessageID(uint): AIS message number.  Must be 19 (field automatically set to "19")
	  - RepeatIndicator(uint): Indicated how many times a message has been repeated
	  - UserID(uint): Unique ship identification number (MMSI)
	  - Spare(uint): Reseverd for definition by a compentent regional or local authority.  Should be set to zero. (field automatically set to "0")
	  - SOG(udecimal): Speed over ground
	  - PositionAccuracy(uint): Accuracy of positioning fixes
	  - longitude(decimal): Location of the vessel  East West location
	  - latitude(decimal): Location of the vessel  North South location
	  - COG(udecimal): Course over ground
	  - TrueHeading(uint): True heading (relative to true North)
	  - TimeStamp(uint): UTC second when the report was generated
	  - Spare2(uint): Not used.  Should be set to zero.  Researched for future use. (field automatically set to "0")
	  - name(aisstr6): Vessel name
	  - shipandcargo(uint): what
	  - dimA(uint): Distance from bow to reference position
	  - dimB(uint): Distance from reference position to stern
	  - dimC(uint): Distance from port side to reference position
	  - dimD(uint): Distance from reference position to starboard side
	  - fixtype(uint): Method used for positioning
	  - RAIM(bool): Receiver autonomous integrity monitoring flag
	  - DTE(uint): Data terminal ready
	  - Spare3(uint): Not used. Should be set to zero (field automatically set to "0")
	@param params: Dictionary of field names/values.
	@param out: File like object to write to
	@rtype: stdout
	@return: text to out
	'''

	if 'std'==format:
		out.write("b_staticdata:\n")
		if 'MessageID' in params: out.write("	MessageID:         "+str(params['MessageID'])+"\n")
		if 'RepeatIndicator' in params: out.write("	RepeatIndicator:   "+str(params['RepeatIndicator'])+"\n")
		if 'UserID' in params: out.write("	UserID:            "+str(params['UserID'])+"\n")
		if 'partnum' in params: out.write("	partnum:            "+str(params['partnum'])+"\n")
                if 0==params['partnum']:
                    out.write('\tname: \t%s\n' % (params['name'],) )
                elif 1==params['partnum']:
			out.write('''\tshipandcargo: {shipandcargo}
\tvendorid: {vendorid}
\tcallsign: {callsign}
\tdimA: {dimA}
\tdimB: {dimB}
\tdimC: {dimC}
\tdimD: {dimD}
\tmothership: {mothership}
\tspare: {spare}
'''.format(**params))
	elif 'sql'==format:
		sqlInsertStr(params,out,dbType=dbType)
	else:
		print "ERROR: unknown format:",format
		assert False

	return # Nothing to return

RepeatIndicatorEncodeLut = {
	'default':'0',
	'do not repeat any more':'3',
	} #RepeatIndicatorEncodeLut

RepeatIndicatorDecodeLut = {
	'0':'default',
	'3':'do not repeat any more',
	} # RepeatIndicatorEncodeLut

import ais.ais_msg_5

shipandcargoEncodeLut = ais.ais_msg_5.shipandcargoEncodeLut
shipandcargoDecodeLut = ais.ais_msg_5.shipandcargoDecodeLut

dimCEncodeLut = {
	'63 m or greater':'63',
	} #dimCEncodeLut

dimCDecodeLut = {
	'63':'63 m or greater',
	} # dimCEncodeLut

dimDEncodeLut = {
	'63 m or greater':'63',
	} #dimDEncodeLut

dimDDecodeLut = {
	'63':'63 m or greater',
	} # dimDEncodeLut


######################################################################
# SQL SUPPORT
######################################################################

dbTableName='b_staticdata'
'Database table name'

def sqlCreateStr(outfile=sys.stdout, fields=None, extraFields=None
		,addCoastGuardFields=True
		,dbType='postgres'
		):
	'''
	Return the SQL CREATE command for this message type
	@param outfile: file like object to print to.
	@param fields: which fields to put in the create.  Defaults to all.
	@param extraFields: A sequence of tuples containing (name,sql type) for additional fields
	@param addCoastGuardFields: Add the extra fields that come after the NMEA check some from the USCG N-AIS format
	@param dbType: Which flavor of database we are using so that the create is tailored ('sqlite' or 'postgres')
	@type addCoastGuardFields: bool
	@return: sql create string
	@rtype: str

	@see: sqlCreate
	'''
	# FIX: should this sqlCreate be the same as in LaTeX (createFuncName) rather than hard coded?
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
	c = sqlhelp.create(dbTableName,dbType=dbType)
	c.addPrimaryKey()
	if 'MessageID' in fields: c.addInt ('MessageID')
	if 'RepeatIndicator' in fields: c.addInt ('RepeatIndicator')
	if 'UserID' in fields: c.addInt ('UserID')
	if 'partnum' in fields: c.addInt ('partnum')
	if 'name' in fields: c.addVarChar('name',20)
	if 'shipandcargo' in fields: c.addInt ('shipandcargo')
	if 'callsign' in fields: c.addVarChar('callsign',7)
	if 'vendorid' in fields: c.addVarChar('vendorid',7)
	if 'dimA' in fields: c.addInt ('dimA')
	if 'dimB' in fields: c.addInt ('dimB')
	if 'dimC' in fields: c.addInt ('dimC')
	if 'dimD' in fields: c.addInt ('dimD')
	if 'mothership' in fields: c.addInt ('mothership')
	if 'spare' in fields: c.addInt ('Spare')

	if addCoastGuardFields:
		# c.addInt('cg_rssi')     # Relative signal strength indicator
		# c.addInt('cg_d')        # dBm receive strength
		# c.addInt('cg_T')        # Receive timestamp from the AIS equipment
		# c.addInt('cg_S')        # Slot received in
		# c.addVarChar('cg_x',10) # Idonno
		c.addVarChar('cg_r',15)   # Receiver station ID  -  should usually be an MMSI, but sometimes is a string
		c.addInt('cg_sec')        # UTC seconds since the epoch

		c.addTimestamp('cg_timestamp') # UTC decoded cg_sec - not actually in the data stream

	return c

def sqlInsertStr(params, outfile=sys.stdout, extraParams=None, dbType='postgres'):
	'''
	Return the SQL INSERT command for this message type
	@param params: dictionary of values keyed by field name
	@param outfile: file like object to print to.
	@param extraParams: A sequence of tuples containing (name,sql type) for additional fields
	@return: sql create string
	@rtype: str

	@see: sqlCreate
	'''
	outfile.write(str(sqlInsert(params,extraParams,dbType=dbType)))


def sqlInsert(params,extraParams=None,dbType='postgres'):
	'''
	Give the SQL INSERT statement
	@param params: dict keyed by field name of values
	@param extraParams: any extra fields that you have created beyond the normal ais message fields
	@rtype: sqlhelp.insert
	@return: insert class instance
	@todo: allow optional type checking of params?
	@warning: this will take invalid keys happily and do what???
	'''
	import sqlhelp
	i = sqlhelp.insert('b_staticdata',dbType=dbType)

	for key in params:
		if type(params[key])==Decimal: i.add(key,float(params[key]))
		else: i.add(key,params[key])

	if None != extraParams:
		for key in extraParams:
			i.add(key,extraParams[key])

	return i




######################################################################
# UNIT TESTING
######################################################################
import unittest
def testParams():
	'''Return a params file base on the testvalue tags.
	@rtype: dict
	@return: params based on testvalue tags
	'''
	params = {}

	return params

class Testb_staticdata(unittest.TestCase):
	'''Use testvalue tag text from each type to build test case the b_staticdata message'''
	def testEncodeDecode(self):

		pass

def addMsgOptions(parser):
	parser.add_option('-d','--decode',dest='doDecode',default=False,action='store_true',
		help='decode a "b_staticdata" AIS message')

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

	typeChoices = ('binary','nmeapayload','nmea') # FIX: what about a USCG type message?
	parser.add_option('-t','--type',choices=typeChoices,type='choice',dest='ioType'
		,default='nmeapayload'
		,help='What kind of string to write for encoding ('+', '.join(typeChoices)+') [default: %default]')


	outputChoices = ('std', 'sql')
	parser.add_option('-T','--output-type',choices=outputChoices,type='choice',dest='outputType'
		,default='std'
		,help='What kind of string to output ('+', '.join(outputChoices)+') [default: %default]')

	parser.add_option('-o','--output',dest='outputFileName',default=None,
			  help='Name of the python file to write [default: stdout]')

	parser.add_option('-f','--fields',dest='fieldList',default=None, action='append',
			  choices=fieldList,
			  help='Which fields to include in the output.  Currently only for csv output [default: all]')

	parser.add_option('-c','--sql-create',dest='sqlCreate',default=False,action='store_true',
			  help='Print out an sql create command for the table.')

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


	if options.sqlCreate:
		sqlCreateStr(outfile,options.fieldList,dbType=options.dbType)

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
