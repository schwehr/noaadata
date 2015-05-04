#!/usr/bin/env python
"""Build a postgres/postgis database of the raw ais messages.

NOTE: this following sets up postgres totally open.  You need to use a
password and firewall on any deployment on the internet!

You may need to some intial setup: (examples assume mac osx + fink)
  - start postgres: sudo pgsql.sh start
  - create the database: sudo -u postgres createdb ais
  - Add your username to the db: sudo -u postgres createuser -U postgres -W $USER -P
      (FIX: update instructions for better security)
  - Might need to install plpgsql
      - createlang plpgsql ais
  - Install postgis into the database:
      - sudo -u postgres /sw/bin/psql-8.3 -f /sw/share/doc/postgis83/lwpostgis.sql -d ais
      - sudo -u postgres /sw/bin/psql-8.3 -f /sw/share/doc/postgis83/spatial_ref_sys.sql -d ais

@todo: Add an option to allow a prefix to the database table names.
"""

from decimal import Decimal
import os
import sys
import StringIO

from aisutils.BitVector import BitVector
from aisutils import binary
from aisutils import sqlhelp

import ais
import ais.ais_msg_1
import ais.ais_msg_2
import ais.ais_msg_3


def createTables(cx,verbose=False):
    '''
    param cx: database connection
    '''
    cu = cx.cursor()

    if verbose: print str(ais.ais_msg_1.sqlCreate())
    cu.execute(str(ais.ais_msg_1.sqlCreate()))

    # Skip 2 and 3 since they are also position messages

    if verbose: print str(ais.ais_msg_5.sqlCreate())
    cu.execute(str(ais.ais_msg_5.sqlCreate()))

    cu.execute(str(ais.ais_msg_4.sqlCreate()))

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

    import psycopg2 # For ProgrammingError exception


    counts = {1:0,2:0,3:0,5:0}

#    buf=[]


    for line in datafile:
	lineNum += 1
	if lineNum%1000==0:
	    print lineNum
# 	if lineNum%1000==0:
#             try:
#                 cu.execute('BEGIN;'+';'.join(buf)+'COMMIT;')
#             except psycopg2.ProgrammingError:
#                 # FIX: how do display the exception?
#                 print 'psycopg2.ProgrammingError:\n  ',line
#                 continue
#             buf=[]
#             cx.commit()

#	    if lineNum>3000:
#		print 'Early exit from load'
#		break

	if line[3:6] not in ('VDM|VDO'): continue # Not an AIS VHF message
	try:
	    msgNum = int(binary.ais6tobitvec(line.split(',')[5][0]))
	except:
	    print '# line would not decode',line
	    continue
	if verbose: print '# msgNum:',msgNum
	if msgNum not in (1,2,3,5):
	    if verbose: print '# skipping',line
	    continue
	
	payload = bv = binary.ais6tobitvec(line.split(',')[5])

# FIX: need to take padding into account ... right before the *
	if msgNum in (1,2,3):
#	    if len(bv) != 168:
	    if len(bv) < 168:
		print '# ERROR: skipping bad position message, line:',lineNum
		print '#  ',line,
		print '#   Got length',len(bv), 'expected', 168
		continue
	elif msgNum == 5:
#	    if len(bv) != 424:
	    if len(bv) < 424:
		print '# ERROR: skipping bad shipdata message, line:',lineNum
		print '#  ',line,
		print '#   Got length',len(bv), 'expected', 424
		continue



	fields=line.split(',')

	cg_sec = None
	cg_station   = None
	if uscg:
	    cg_sec = int(float(fields[-1])) # US Coast Guard time stamp.
            cg_timestamp = sqlhelp.sec2timestamp(cg_sec)
	    #print len(fields),fields
	    for i in range(len(fields)-1,5,-1):
		if 0<len(fields[i]) and 'r' == fields[i][0]:
		    cg_station = fields[i]
		    break # Found it so ditch the for loop

	#print station
	#sys.exit('stations please work')

	ins = None

        # FIX: redo this for all messages using the new aisutils structure
#	try:
        if True:
	    if   msgNum==1: ins = ais.ais_msg_1.sqlInsert(ais.ais_msg_1.decode(bv),dbType='postgres')
	    elif msgNum==2: ins = ais.ais_msg_2.sqlInsert(ais.ais_msg_2.decode(bv),dbType='postgres')
	    elif msgNum==3: ins = ais.ais_msg_3.sqlInsert(ais.ais_msg_3.decode(bv),dbType='postgres')
	    elif msgNum==5:
                params = ais.ais_msg_5.decode(bv)
                #print params
                # FIX: make this a command line option
                params['name'] = params['name'].replace('"','').replace('\\','').strip('@').strip()
                params['callsign'] = params['callsign'].replace('"','').replace('\\','').strip('@').strip()
                params['destination'] = params['destination'].replace('"','').replace('\\','').strip('@').strip()
                #params.callsign = params.callsign.strip()
                #params. = params..strip()
                ins = ais.ais_msg_5.sqlInsert(params,dbType='postgres')
            else:
		print '# Warning... not handling type',msgNum,'line:',lineNum
		continue
#	except:
#	    print '# ERROR:  some decode error?','line:',lineNum
#	    print '#  ',line
#	    continue

	counts[msgNum] += 1

	if uscg:
	    if None != cg_sec:       ins.add('cg_sec',       cg_sec)
            if None != cg_timestamp: ins.add('cg_timestamp', cg_timestamp)
	    if None != cg_station:   ins.add('cg_r',         cg_station)
	if verbose:
            print str(ins)
            print '# line:',line
        #print str(ins)
        try:
            cu.execute(str(ins))
            #buf.append(str(ins))
	except Exception, e:
            print params
#            # FIX: give a better error message
            print '# exception:',str(type(Exception)), str(e)
	    print '# ERROR: sql error?','line:',lineNum
	    print '#  ', str(ins)
	    print '#  ',line
            sys.exit('EARLY!!!')

        if lineNum%5000==0:
            if verbose:
                print '# committing batch'
            cx.commit()

    print counts
    #cu.execute('BEGIN;'+';'.join(buf)+'COMMIT;')

    cx.commit()


############################################################
if __name__=='__main__':
    from optparse import OptionParser
    parser = OptionParser(
        usage="%prog [options] file1.ais [file2.ais ...]",
        version='%prog ')

    parser.add_option('-d','--database-name',dest='databaseName',default='ais',
                      help='Name of database within the postgres server [default: %default]')
    parser.add_option('-D','--database-host',dest='databaseHost',default='localhost',
                      help='Host name of the computer serving the dbx [default: %default]')
    #defaultUser = os.genenv('USER')
    defaultUser = os.getlogin()
    parser.add_option('-u','--database-user',dest='databaseUser',default=defaultUser,
                      help='Host name of the to access the database with [default: %default]')

# FIX: add password

    parser.add_option('-C','--with-create',dest='createTables',default=False, action='store_true',
                      help='Do not create the tables in the database')

    parser.add_option('-U','--without-uscg',dest='uscgTail',default=True,action='store_false',
                      help='Do not look for timestamp and receive station at the end of each line [default: with-uscg]')

    parser.add_option('-v','--verbose',dest='verbose',default=False,action='store_true',
                      help='Make the test output verbose')

    (options,args) = parser.parse_args()

    import psycopg2 as psycopg
    #cx = psycopg.connect("dbname='"+options.databaseName+"' user='schwehr' host='localhost'")
    connectStr = "dbname='"+options.databaseName+"' user='"+options.databaseUser+"' host='"+options.databaseHost+"'"
    if options.verbose:
        print 'Connect string:',connectStr
    cx = psycopg.connect(connectStr)


    # FIX: what if we need to create the database?!?!?

    if options.createTables:
        createTables(cx,verbose=options.verbose)

    if len(args)==0:
        if options.verbose: print 'processing from stdin'
        loadData(cx,sys.stdin,verbose=options.verbose,uscg=options.uscgTail)
    else:
        for filename in args:
            print 'processing file:',filename
            loadData(cx,file(filename,'r'),verbose=options.verbose,uscg=options.uscgTail)

#cur = cx.cursor()
#cur.execute('INSERT INTO position (UserID,COG,SOG) Values (1234,2,3);')
#conn.commit()
#cur.execute('SELECT UserID,COG,SOG FROM position;')
#cur.fetchall()
