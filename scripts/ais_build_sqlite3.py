#!/usr/bin/env python

__author__    = 'Kurt Schwehr'
__version__   = '$Revision: 10403 $'.split()[1]
__revision__  = __version__ # For pylint
__date__ = '$Date: 2008-09-24 22:44:22 -0400 (Wed, 24 Sep 2008) $'.split()[1]
__copyright__ = '2008'
__license__   = 'GPL v3'
__contact__   = 'kurt at ccom.unh.edu'

__doc__='''

Create or add to a database.  First attempt.  This could be made better/faster.
Assumes that all ais messages have been "normalized" - messages are one line only.

Only works with sqlite3 and python 2.5.  Uses the internal python sqlite db interface.

@see: U{Using adapters to tore additinal Python types in SQLite databases <http://docs.python.org/lib/node347.html>}
@requires: U{python <http://python.org/>} >= 2.5
@requires: U{sqlite3 <http://www.sqlite.org/>} >= 2.5
@requires: U{epydoc<http://epydoc.sourceforge.net/>} >= 3.0
@requires: U{BitVector<http://cheeseshop.python.org/pypi/BitVector>}

@var __date__: Date of last svn commit
@undocumented: __version__ __author__ __doc__ parser
@status: Works, but underdevelopment
@since: 2007-Dec-17
@organization: U{CCOM<http://ccom.unh.edu/>}
@todo: Can I merge messages 1-3 and 18 together?

@bug: seems to fail where pysqlite2 does not

INSERT INTO position (RegionalReserved,NavigationStatus,COG,SOG,TimeStamp,RepeatIndicator,UserID,RAIM,longitude,state_slottimeout,Spare,state_syncstate,PositionAccuracy,MessageID,latitude,TrueHeading,ROT,state_slotoffset,cg_timestamp) VALUES (0,15,285.3,0.0,59,0,316005624,0,-123.060903333,0,0,0,0,1,49.29086,511,-128,2304,2008-02-11 00:00:00);
Traceback (most recent call last):
  File "/Users/schwehr/projects/src/noaadata/scripts/ais_build_sqlite3.py", line 267, in <module>
    loadData(cx,file(filename,'r'),verbose=options.verbose,uscg=options.uscgTail)
  File "/Users/schwehr/projects/src/noaadata/scripts/ais_build_sqlite3.py", line 202, in loadData
    cu.execute(str(ins))
sqlite3.OperationalError: near "00": syntax error
'''

import sys
from decimal import Decimal
from BitVector import BitVector
import StringIO

import ais.binary    as binary
#import ais.aisstring as aisstring

import ais.ais_msg_1
import ais.ais_msg_2
import ais.ais_msg_3
import ais.ais_msg_4
import ais.ais_msg_5
import ais.ais_msg_18 # Class B position report
import ais.ais_msg_19 # Class B position and shipdata
#import ais.ais_msg_8
#import ais.ais_msg_21

#import pysqlite2.dbapi2 as sqlite
#import pysqlite2.dbapi2

import sqlite3
import datetime, time

def createTables(cx,verbose=False):
    '''
    param cx: database connection
    '''
    cu = cx.cursor()

    if verbose: print str(ais.ais_msg_1.sqlCreate(dbType='sqlite'))
    try:
        cu.execute(str(ais.ais_msg_1.sqlCreate(dbType='sqlite')))
    except:
        print 'Warning: position table already exists'

    # Skip 2 and 3 since they are also position messages
    
    if verbose: print str(ais.ais_msg_4.sqlCreate(dbType='sqlite'))
    cu.execute(str(ais.ais_msg_4.sqlCreate(dbType='sqlite')))

    if verbose: print str(ais.ais_msg_5.sqlCreate(dbType='sqlite'))
    cu.execute(str(ais.ais_msg_5.sqlCreate(dbType='sqlite')))

    cu.execute(str(ais.ais_msg_18.sqlCreate(dbType='sqlite')))
    cu.execute(str(ais.ais_msg_19.sqlCreate(dbType='sqlite')))

    cx.commit()

def loadData(cx,datafile,verbose=False
	     , uscg=True):
    '''
    Try to read data from an open file object.  Not yet well tested.

    @param cx: database connection
    @param verbose: pring out more if true
    @param uscg: Process uscg tail information to get timestamp and receive station
    @rtype: None
    @return: Nothing

    @note: can not handle multiline AIS messages.  They must be normalized first.
    '''
    cu = cx.cursor()
    lineNum = 0

    #counts = {1:0,2:0,3:0,4:0,5:0}
    counts = {}
    countsTotal = {} # Includes ignored messages

    for i in range(64):
        counts[i]=0
        countsTotal[i]=0

    for line in datafile:
	lineNum += 1
	if lineNum%1000==0:
	    print lineNum
	    cx.commit()
#	    if lineNum>3000:
#		print 'Early exit from load'
#		break

	if line[3:6] not in ('VDM|VDO'):
#            if verbose:
#                sys.stderr.write
            continue # Not an AIS VHF message
	try:
	    msgNum = int(binary.ais6tobitvec(line.split(',')[5][0]))
	except:
	    print 'line would not decode',line
	    continue

        countsTotal[msgNum]+=1
        
	if verbose: print 'msgNum:',msgNum
#	if msgNum not in (1,2,3,4,5): 
#	    if verbose: print 'skipping',line
#	    continue
	
	payload = bv = binary.ais6tobitvec(line.split(',')[5])

# FIX: need to take badding into account ... right before the *
	if msgNum in (1,2,3):
#	    if len(bv) != 168:
	    if len(bv) < 168:
		print 'ERROR: skipping bad position message, line:',lineNum
		print '  ',line,
		print '   Got length',len(bv), 'expected', 168
		continue
#	elif msgNum == 4:
	elif msgNum == 5:
#	    if len(bv) != 424:
	    if len(bv) < 424:
		print 'ERROR: skipping bad shipdata message, line:',lineNum
		print '  ',line,
		print '   Got length',len(bv), 'expected', 424
		continue
	    
		

	fields=line.split(',')

	cg_timestamp = None
	cg_station   = None
	if uscg:
            try:
                cg_sec = int(float(fields[-1])) # US Coast Guard time stamp.
                print 'cg_sec:',cg_sec,type(cg_sec)
                cg_timestamp = datetime.datetime.utcfromtimestamp(float(cg_sec))
            except:
                print 'ERROR getting timestamp for',lineNum,line
	    #print len(fields),fields
	    for i in range(len(fields)-1,5,-1):
		if 0<len(fields[i]) and 'r' == fields[i][0]:
		    cg_station = fields[i]
		    break # Found it so ditch the for loop

	#print station
	#sys.exit('stations please work')

	ins = None

	try:
	    if   msgNum==1: ins = ais.ais_msg_1.sqlInsert(ais.ais_msg_1.decode(bv),dbType='sqlite')
	    elif msgNum==2: ins = ais.ais_msg_2.sqlInsert(ais.ais_msg_2.decode(bv),dbType='sqlite')
	    elif msgNum==3: ins = ais.ais_msg_3.sqlInsert(ais.ais_msg_3.decode(bv),dbType='sqlite')
	    elif msgNum==4: ins = ais.ais_msg_4.sqlInsert(ais.ais_msg_4.decode(bv),dbType='sqlite')
	    elif msgNum==5: ins = ais.ais_msg_5.sqlInsert(ais.ais_msg_5.decode(bv),dbType='sqlite')

	    elif msgNum==18: ins = ais.ais_msg_18.sqlInsert(ais.ais_msg_18.decode(bv),dbType='sqlite')
	    elif msgNum==19: ins = ais.ais_msg_19.sqlInsert(ais.ais_msg_19.decode(bv),dbType='sqlite')
            else:
                if verbose:
                    print 'Warning... not handling type',msgNum,'line:',lineNum
		continue
	except:
	    print 'ERROR:  some decode error?','line:',lineNum
	    print '  ',line
	    continue

	counts[msgNum] += 1

	if uscg:
            # FIX: make cg_timestamp work
	    if None != cg_timestamp: ins.add('cg_timestamp',cg_timestamp)
	    if None != cg_station:   ins.add('cg_r',        cg_station)
	if verbose: print str(ins)

        # FIX: redo this correctly???
	#try:
        print str(ins)
        cu.execute(str(ins))
        #except:
        #    sys.stderr.write('FIX: write some sort of exception handler\n')
#         except pysqlite2.dbapi2.OperationalError, params:
# 	#except OperationalError,  params:
#             if -1 != params.message.find('no such table'):
#                 print 'ERROR:',params.message
#                 sys.exit('You probably need to run with --with-create')
#             print 'params',params
#             print type(params)
# 	    print 'ERROR: sql error?','line:',lineNum
# 	    print '  ', str(ins)
# 	    print '  ',line

#             if False:
#                 # Give some debugging flexibility
#                 from IPython.Shell import IPShellEmbed
#                 ipshell = IPShellEmbed(argv=[])
#                 ipshell() 
#                 sys.exit('Gave up')

    #print counts
    print '\nMessages found:'
    for key in countsTotal:
        if countsTotal[key]>0:
            print str(key)+':',countsTotal[key]

    print '\nMessages processed:'
    for key in counts:
        if counts[key]>0:
            print str(key)+':',counts[key]
    cx.commit()
	

############################################################
if __name__=='__main__':
    from optparse import OptionParser
    parser = OptionParser(usage="%prog [options] file1.ais [file2.ais ...]",version="%prog "+__version__)

    parser.add_option('-d','--database-file',dest='databaseFilename',default='ais.db3'
                      ,help='Name of the sqlite3 database file to write [default: %default]')
    parser.add_option('-C','--with-create',dest='createTables',default=False, action='store_true'
                      ,help='Create the tables in the database')

    parser.add_option('--without-uscg',dest='uscgTail',default=True,action='store_false'
                      ,help='Do not look for timestamp and receive station at the end of each line [default: with-uscg]')

    parser.add_option('-v','--verbose',dest='verbose',default=False,action='store_true'
                      ,help='Make program output more verbose info as it runs')

    (options,args) = parser.parse_args()
    cx = sqlite3.connect(options.databaseFilename)

    print 'FIX: cg_sec and cg_timestamp are currently broken'

    if options.createTables:
        createTables(cx,verbose=options.verbose)

    if len(args)==0:
        print 'processing from stdin'
    
        loadData(cx,sys.stdin,verbose=options.verbose,uscg=options.uscgTail)
    else:
        for filename in args:
            print 'processing file:',filename
            loadData(cx,file(filename,'r'),verbose=options.verbose,uscg=options.uscgTail)
