#!/usr/bin/env python

__version__ = '$Revision: 6398 $'.split()[1] # See man ident
__date__ = '$Date: 2007-06-20 13:42:04 -0400 (Wed, 20 Jun 2007) $'.split()[1] # FIX: pull out just the date
__author__ = 'Kurt Schwehr'
__doc__='''
Helper functions to create SQL statements.

@license: GPL
@todo: How do I assemble queries like this::

    SELECT COUNT(samplename) AS count FROM \\
        (SELECT DISTINCT(samplename) AS samplename FROM \\
         ams WHERE corenum=1 AND coretype='p');

@todo: subqueries
@todo: make a super class so that inserts and selects can verify based on the create str
@todo: take the super class info from the database?

@bug: FIX: write some doc tests!
@bug: had no protection from SQL injection attacks or quoting mistakes

@note: This is not as snazzy as SQLAlchemy or SQLObject, but it works and is simple

@author: '''+__author__+'''
@version: ''' + __version__ +'''
@copyright: 2006
@note: postgres is sort of case sensitive, so go all lowercase for fields and tables
@var __date__: Date of last svn commit

@undocumented: __version__ __author__ __doc__ myparser
'''

# Python standard libraries
import sys

from BitVector import BitVector

# Local modules
# import verbosity
# from verbosity import BOMBASTIC,VERBOSE,TRACE,TERSE,ALWAYS

BOMBASTIC= 4
VERBOSE  = 3
TRACE    = 2
TERSE    = 1
ALWAYS   = 0
NEVER    = 0 # Confusing, eh?
# Pass in 0 for NEVER from the user side


def addVerbosityOptions(parser):
    '''
    Added the verbosity options to a parser
    '''
    parser.add_option('-v','--verbose',action="count",dest='verbosity',default=0,
                        help='how much information to give.  Specify multiple times to increase verbosity')
    parser.add_option('--verbosity',dest='verbosity',type='int',
                        help='Specify verbosity.  Should be in the range of '
                        +str(ALWAYS)+'...'+str(BOMBASTIC)+' (None...Bombastic)')
    parser.add_option('--noisy',dest='verbosity', action='store_const', const=2*BOMBASTIC,
                        help='Go for the max verbosity ['+str(2*BOMBASTIC)+']')

######################################################################
import datetime
def sec2timestamp(utcsec):
    '''
    Convert a UTC sec time to a SQL timestamp

    >>> sec2timestamp(int(1169703371))
    '2007-01-25 05:36:11'

    '''

    d = datetime.datetime.utcfromtimestamp(utcsec)
    s = '%d-%02d-%02d %02d:%02d:%02d' % (d.year,d.month,d.day,d.hour,d.minute,d.second)
    return s

######################################################################
class select:
    '''
    Construct an sql select query

    Sometimes it just gets ugly having all that comma and WHERE AND
    logic in there.  This code takes care of that
    '''
    def __init__(self,dbType='postgres'):
        self.fields = []
        self.where = []
        self.limit = None
        self.from_tables = []
        self.orderby = None
        self.desc = False # descending sort if true
        return

    def setorderby(self,field,desc=False):
        "Make the returned rows come in some order"
        if str != type(field): print "ERROR: fix throw type exception"
        self.orderby = field
        self.desc = desc
        return

    def addfield(self,fieldname):
        "Add a field name to return"
        if str != type(fieldname): print "ERROR: fix throw type exception"
        self.fields.append(fieldname)
        return

    def addwhere(self,boolTest):
        " Add expressions to chain together with ANDs"
        if str != type(boolTest):
            print "ERROR: fix throw type exception"
        self.where.append(boolTest)
        return

    def addfrom(self,tableName):
        "Which tables the query will pull from"
        if str != type(tableName):
            print "ERROR: fix throw type exception"
        self.from_tables.append(tableName)
        return

    def setlimit(self,numOfItems):
        "Set the maximum number of items to return"
        if int != type(numOfItems):
            print "ERROR: fix throw type exception"
        self.limit = numOfItems
        return

    def __str__(self):
        "Return the query as a string"
        if len(self.fields) < 1: print "ERROR: Must specify at least one from!\n  FIX: throw some exception?"
        s = 'SELECT '
        #for i in range (len(self.fields)-1): s += self.fields[i]+','
        if dbType == 'postgres':
            s+=','.join([f.lower() for f in self.fields])
        else:
            s+=','.join(self.fields)
        s += self.fields[-1] + ' '

        if len(self.from_tables)<1: print "ERROR: fix throw some exception"
        s += 'FROM '
        for i in range (len(self.from_tables)-1):
            s += self.from_tables[i]+','
        s += self.from_tables[-1]

        if (len(self.where)>0): s += ' WHERE '
        for i in range (len(self.where)-1):
            s += self.where[i]+' AND '
        if (len(self.where)>0): s += self.where[-1]

        if (None != self.orderby):
            s += ' ORDER BY ' + self.orderby
            if self.desc: s += ' DESC'

        if (None != self.limit):
            s += ' LIMIT ' + str(self.limit)

        s += ';'
        return s

class create:
    '''
    Helper for building create SQL commands.

    FIX: add type checking - what did I mean by this???
    @todo: FIX - add a remove command to nuke a field
    '''

    def __init__(self,table,dbType='postgres'):
        '''Kick it off with no fields

        table - which table are we going to insert into'''
        self.table = table
        self.dbType = dbType
        self.fields = []
        self.types = []
        self.postgis = []; # Tuples of (field,typeName,dim,srid)
        return

    def add(self,field,typeStr):
        '''
        Unchecked field.  Provide the field and type all in one.  Use
        this if nothing matches what you need.

        e.g.:
        create.add('corenumber','INTEGER')
        create.add('username','VARCHAR(40)')
        create.add('id','INTEGER PRIMARY KEY')

	@param field: name of the field
	@param typeStr: the type of field

	@todo: Allow setting of primary key in a simple way
        '''
        self.fields.append(field)
        self.types.append(typeStr)
        return

    def addPrimaryKey(self,keyName='key'):
        '''
        Add a primary key based on the field name.
        @todo: FIX: complain if trying to add a second primary key
        '''

        self.fields.append(keyName)
        if   'sqlite'  ==self.dbType: self.types.append('INTEGER PRIMARY KEY')
        elif 'postgres'==self.dbType: self.types.append('SERIAL PRIMARY KEY')
        else:
            print 'Do not know how to construct a primary key for database type of',self.dbType
            assert False
        return

    def addInt(self,field):
	'''
	SQL integer field
	@param field: name of the field
	'''
        self.fields.append(field)
        self.types.append("INTEGER")

    def addReal(self,field):
	'''
	SQL floating point field
	@param field: name of the field
	'''

        self.fields.append(field)
        self.types.append("REAL")

    def addVarChar(self,field,length):
	'''
	SQL VARCHAR field... variable length up to a max size
	@param field: name of the field
	@param length: max length of the field
	'''
        self.fields.append(field)
        self.types.append("VARCHAR("+str(length)+")")


    def addBool(self,field):
	'''
	SQL Boolean field
	@param field: name of the field
	'''
        self.fields.append(field)
        self.types.append("BOOL")

    def addBitVarying(self,field,length):
	'''
	SQL Boolean field
	@param field: name of the field
	@param length: largest possible size
	'''
	assert (length>0)
        self.fields.append(field)
        self.types.append('BIT VARYING('+str(length)+')')


    def addDecimal(self,field,precision=5,scale=0):
	'''
	@param precision: overall digits including to right of decimal
	@param scale: number of digits to the right of decimal
	'''
	self.fields.append(field)
	self.types.append('DECIMAL('+str(precision)+','+str(scale)+')')

    def addTimestamp(self,field):
	'''SQL TIMESTAMP field
	@param field: name of the field
	'''
        self.fields.append(field)
        self.types.append("TIMESTAMP")
        return

    def addPostGIS(self,field,typeName,dimension,SRID='-1'):
        '''
        Add a spatial column to the table using the OpenGIS
        AddGeometryColumn function using current schema:

        AddGeometryColumn(<table_name>,<column_name>, <srid>, <type>, <dimension>)

        @param field: Name of the field in the db table
        @type field: str
        @param typeName: OpenGIS geometry type (e.g. POINT)
        @type typeName: str
        @param dimension: x,y would be 2
        @type dimension: int
        @param SRID: spatial referencing system identifier (FIX: give some more info!)
        @type SRID: int
        '''

        int(dimension) # Force this to be an int
        self.postgis.append((field,typeName,dimension,SRID))


    def __str__(self):
        '''Return the SQL string for the table creation
	@rtype: str'''
        assert (len(self.fields)>0)
        assert (len(self.types)>0)
        assert (len(self.fields)==len(self.types))
        cstr = 'CREATE TABLE '
        if 'postgres'==self.dbType:
            cstr += self.table.lower()+' ('
            for i in range(len(self.fields)-1):
                cstr += str(self.fields[i].lower())+' '+str(self.types[i])+', '
            cstr += str(self.fields[-1].lower())+' '+str(self.types[-1])
        else:
            cstr += self.table+' ( '
            for i in range(len(self.fields)-1):
                cstr += str(self.fields[i])+' '+str(self.types[i])+', '
            cstr += str(self.fields[-1])+' '+str(self.types[-1])
        cstr += ' ); '

        cmds=[]
        for postgisFields in self.postgis:
            table    = '\''+self.table.lower()+'\''
            field    = '\''+postgisFields[0].lower()+'\''
            typeName = '\''+postgisFields[1]+'\''
            dim      = str(postgisFields[2])
            SRID     = str(postgisFields[3])
            fieldStr = ','.join((table,field,SRID,typeName,dim))
            addCmd = 'SELECT AddGeometryColumn('+fieldStr+')'
            cmds.append(addCmd)

        retStr = cstr + ';'.join(cmds)
        if len(cmds)>0: retStr += ';'
        return retStr

class insert:
    '''
    Help create an SQL insert statement for injecting data into a database.  Wee!

    @todo: FIX: provide some sort of validation, maybe with the CREATE string or class?
    @todo: Put in a remove/delete call to pull a value out so that it is not inserted

    @todo: FIX:  MUST REWRITE THIS CLASS TO BE TYPE AWARE.
    '''
    def __init__(self,table,dbType='postgres'):
        '''Create an insert with no values

        @param table: which table are we going to insert into
        @param dbType: sqlite can not handle True/False keyworks (at version 3.2.8)
        '''
        self.table = table
        self.dbType = dbType
        self.fields = []
        self.values = []
        self.postGIS = []
        return

    def dump(self):
	'''Print out a safer dump to std out rather than str for debugging'''
	print '\n === dump insert for table',self.table,'==='
	for i in range(1,len(self.fields)):
	    print self.fields[i], self.values[i],'    (',type(self.fields[i]), type(self.values[i]),')'
	print

    def __str__(self):
        "Return the SQL string for the insert"
        if 0==len(self.fields):
            print "WARNING: empty insert.  returning empty string"
            return ""  # FIX: throw exception and a hissy fit

        s = 'INSERT INTO '

        if 'postgres'==self.dbType: s+= self.table.lower() + ' '
        else: s+= self.table + ' '

        assert(len(self.fields)==len(self.values))
        fields = None
        if 'postgres'==self.dbType:
            fields = [f.lower() for f in self.fields]
        else: fields = self.fields
        #s1 = ''
        #s2 = ''

        # FIX: insert the 1st without a leading ','
        #s1 += str(self.fields[0])
        #if str == type(self.values[0]): s2 += '"'+str(self.values[0])+'"'
        #else: s2 += str(self.values[0])

        # FIX: switch to join of strings for speed  AND SIMPLICITY!!
        #s1List=[]
        s2List=[]
        for i in range(len(fields)):
            #s1List.append(str(fields[i]))
	    if bool == type(self.values[i]):
                if 'sqlite'==self.dbType:
                    if self.values[i]: s2List.append('1')
                    else: s2List.append('0')
                else: s2List.append(str(self.values[i]))
	    elif isinstance(self.values[i],BitVector): s2List.append('\''+str(self.values[i])+'\'')
            elif str == type(self.values[i]):          s2List.append('\''+str(self.values[i])+'\'')
            elif type(self.values[i]) in (int, float): s2List.append(str(self.values[i]))

	    elif not self.values[i]:
                print 'FIX: what was I trying to accomplish with this?',fields[i],self.values[i]
		s2List.append('NULL')
            else:
                s2List.append(str(self.values[i]))

        s1List = fields
        for entry in self.postGIS:
            s1List.append(entry[0].lower())
            # FIX: this hard codes WGS 84.  Not good for a general library!
            s2List.append('GeomFromText(\'' + entry[1] + '\',4326)')

        s += '(' + ','.join(s1List) + ') VALUES (' + ','.join(s2List) + ');'
        return s

    def addPostGIS(self,field,value):
        '''
        Handle postGIS geometry
        '''
        self.postGIS.append((field,value))


    def add(self,field,value):
        '''Add a field value pair to the insert

        @note: Integers and floats should NOT be converted to strings.
	@param field: name of the field
	@param value: value to be assigned to that field.
        '''

        if type(value)==str:
	    # Prevent quotes from breaking out of a string/varchar.  "" is SQL for " in a character string
	    value = value.replace('"','""')
	self.fields.append(field)
        self.values.append(value)
        return



######################################################################
import datetime

def sqlInsertStrFromList (table,aList,dbType='postgres'):
    ''' Take a list and make an insert string.  This works with
    dictionaries too.  Here is a quick example:

    >>> aList = [('one',1),('2','two'),('threepoint',3.)]
    >>> sqlInsertStrFromList('myTable',aList,dbType='sqlite')
    "insert into myTable (one,2,threepoint) values (1,'two',3.0);"
    >>> sqlInsertStrFromList('myTable',aList)
    "insert into mytable (one,2,threepoint) values (1,'two',3.0);"

    @param table: Which table to insert into
    @type table: str
    @param aList: list of tubles pairs to insert - (name, value)
    @type aList(list)
    @return: complete SQL insert command
    @rtype: str
    '''

    if 'postgres'==dbType: table = table.lower()
    ins = "insert into " + table + " ("
    first = []
    if 'postgres'==dbType: first = [f[0].lower() for f in aList]
    else: first = [f[0] for f in aList]
    ins += ','.join(first) + ") values ("
    first=True
    for pair in aList:
        value = pair[1]
        if first: first=False
        else:     ins+=","
        # Make sure to quote all strings and timestamps
        # print type(value)
        # <type 'DateTime'>
        # What way is better to handle this?
        #if type(value) == str or type(value) == type(datetime()): ins+="'"
        if type(value)!=int and type(value)!=float: ins+="'"
        ins+=str(value)
        if type(value)!=int and type(value)!=float: ins+="'"
        #if type(value) == str or type(value) == type(datetime()): ins+="'"
    ins += ");"
    return ins



######################################################################
if __name__=='__main__':
    from optparse import OptionParser
    myparser = OptionParser(usage="%prog [options]",
			    version="%prog "+__version__)
    myparser.add_option('--test','--doc-test',dest='doctest',default=False,action='store_true',
                        help='run the documentation tests')

    addVerbosityOptions(myparser)
    (options,args) = myparser.parse_args()

    success=True

    if options.doctest:
	import os; print os.path.basename(sys.argv[0]), 'doctests ...',
	sys.argv= [sys.argv[0]]
	if options.verbosity>=TERSE: sys.argv.append('-v')
	import doctest
	numfail,numtests=doctest.testmod()
	if numfail==0: print 'ok'
	else:
	    print 'FAILED'
	    success=False

    if not success:
	sys.exit('Something Failed')
