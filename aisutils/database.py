#!/usr/bin/env python
__author__ = 'Kurt Schwehr'
__version__ = '$Revision: 12372 $'.split()[1]
__revision__  = __version__ # For pylint
__date__ = '$Date: 2009-08-01 16:02:01 -0400 (Sat, 01 Aug 2009) $'.split()[1]
__copyright__ = '2008'
__license__   = 'Apache 2.0'
__contact__   = 'kurt at ccom.unh.edu'

__doc__='''
AIS database utilities.

@status: under development
@since: 2008 Jan 09
@undocumented: __doc__ parser

@todo: need to keep a cache of vessel names
@todo: probably lots that can be added here
@todo: createtables for the binary messages
@todo: use logging or sys.stderr rather than print
@see: U{WKT<http://dev.mysql.com/doc/refman/5.0/en/gis-wkt-format.html>}
'''

import os
import sys
import datetime
import traceback
import psycopg2 as psycopg

import ais

def checkpoint():
    import inspect
    f = inspect.currentframe().f_back
    print '%s:%d: Function %s CHECKPOINT' % (__file__,f.f_lineno,f.f_code.co_name)



dbTypes=(
    'postgres' # AKA postgis
    ,'sqlite' # Only sqlite3.  Time to ditch sqlite2
)
'''
The choices of databases that are supported.
'''

def stdCmdlineOptions(parser,dbType='postgres',verbose=False):
    '''
    Standard command line options
    @param parser: OptionParser parser that will get the additional options
    @param dbType: 'postgres' or 'sqlite'
    '''
    if dbType != 'all' and dbType not in dbTypes:
        # FIX: throw a database type exception
        sys.exit('unknown database type: '+dbType)

    if dbType in ('all','postgres'):
        if verbose: sys.stderr.write('Adding postgres options\n')
        parser.add_option('-d','--database-name',dest='databaseName',default='ais'
                          ,help='Name of database within the postgres server [default: %default]')
        parser.add_option('-D','--database-host',dest='databaseHost',default='localhost'
                          ,help='Host name of the computer serving the dbx [default: %default]')
        #defaultUser = os.genenv('USER')
        defaultUser = os.getlogin()
        parser.add_option('-u','--database-user',dest='databaseUser',default=defaultUser
                          ,help='Host name of the to access the database with [default: %default]')

        parser.add_option('-p','--database-passwd',dest='databasePasswd',default=None
                          ,help='Password to access the database with [default: None]')

    if dbType in ('all','sqlite'):
        if verbose: sys.stderr.write('Adding sqlite options\n')
        parser.add_option('-f','--database-file',dest='databaseFilename',default='ais.db3'
			  ,help='Name of the sqlite3 database file to write [default: %default]')

payload_table_sql = '''
CREATE TABLE payload (
       key INTEGER, -- Points to the key in the relevant table
       msg_num INTEGER,
       encoded_text VARCHAR(200) -- NMEA ecoded text payload in field 6 of the normalized AIVDM
);'''
'Table to track payloads as a sort of checksum'



def createTables(cx,dbType='sqlite',includeList=None, excludeList=None,verbose=False):
    '''
    @param cx: database connection
    @type cx: db API 2.0 object
    @param dbType: postgres or sqlite
    @type dbType: str
    @param includeList: If a list of message numbers is passed, only these are created
    @type includeList: list of integers
    @param excludeList: If a list of message numbers is passed, all but these are created
    @type excludeList: list of integers
    '''
    cu = cx.cursor()

    tables=[]
    for msgNum in ais.msgModByNumber:
        if excludeList is not None and msgNum in excludeList: continue
        if includeList is not None and msgNum not in includeList: continue

        aisMod = ais.msgModByNumber[msgNum]

        if aisMod.dbTableName in tables:
            if verbose: sys.stderr.write(str(msgNum)+' ... skipping - already in the db -'+str(aisMod.dbTableName)+'\n')
        else:
            if verbose:
                print msgNum,' ... adding '+aisMod.dbTableName+' table to db'
            cu.execute(str(aisMod.sqlCreate(dbType=dbType)))
            tables.append(aisMod.dbTableName)

    cx.commit()

def dropTables(cx,includeList=None, excludeList=None,verbose=False):
    '''
    Kiss your data goodbye

    @param cx: database connection
    @type cx: db API 2.0 object
    @param dbType: postgres or sqlite
    @type dbType: str
    @param includeList: If a list of message numbers is passed, only these are created
    @type includeList: list of integers
    @param excludeList: If a list of message numbers is passed, all but these are created
    @type excludeList: list of integers
    '''
    cu = cx.cursor()

    tables=[]
    for msgNum in ais.msgModByNumber:
        if excludeList is not None and msgNum in excludeList: continue
        if includeList is not None and msgNum not in includeList: continue

        aisMod = ais.msgModByNumber[msgNum]

        if aisMod.dbTableName in tables:
            if verbose:
                print msgNum,' ... skipping - already dropped from the db -',aisMod.dbTableName
        else:
            if verbose:
                print msgNum,' ... dropping '+aisMod.dbTableName+' table to db'
            cu.execute('DROP TABLE '+aisMod.dbTableName+';')
            tables.append(aisMod.dbTableName)

    cx.commit()




def connect(options,dbType=None):
    '''
    options must include the above standard options
    '''
    verbose = options.verbose
    if dbType is None:
        dbType = options.dbType

    cx = None

    if dbType=='sqlite':
        import sqlite3
        cx = sqlite3.connect(options.databaseFilename)

    elif dbType=='postgres':
        #import psycopg2 as psycopg
        # FIX: add password support
        connectStr = "dbname='"+options.databaseName+"' user='"+options.databaseUser+"' host='"+options.databaseHost+"'"

        if options.verbose:
            print 'Connect string:',connectStr
        cx = psycopg.connect(connectStr)

    else:
        sys.exit('Must specify a database type')

    if verbose:
        sys.stderr.write('connected to db\n')
    return cx


def rebuild_track_lines(cx,vessels=None
                        ,limitPoints=50
                        ,trackTable='track_lines'
                        ,trackKey='ogc_fid'
                        ,startTime=None
                        ,verbose=False):
    '''
    @param vessels: if None, do all vessels in the tables, otherwise a set of MMSI values
    @param trackTable: the database table where to put the lines
    @param limitPoints: max number of points in a track line
    @param startTime: oldest timestamp to allow in the track lines
    @type startTime: datetime
    '''
    v = verbose
    cu = cx.cursor()

    if v:
        sys.stderr.write('\nREBUILD_TRACK_LINES\n')
    #
    # position table - Class A
    #
    vesselsUpdated=0
    if vessels is None:
        if startTime:
            sql = 'SELECT distinct(userid) FROM position WHERE cg_timestamp > %s;'
            print 'FIX remove sql == ',sql
            sys.stderr.write('FIX: remove  startTime: %s   now: %s \n' % (str(startTime),str(datetime.datetime.utcnow())))
            cu.execute(sql,(startTime,))
        else:
            cu.execute('SELECT distinct(userid) FROM position;')
        vessels = set()
        for v in cu.fetchall():
            vessels.add(v[0])

    if v:
        sys.stderr.write('\nrebuild_track_lines\n')
        #sys.stderr.write('  vessels %s\n' % str(vessels))
        sys.stderr.write('  Number of vessels %d\n' % len(vessels))
        sys.stderr.write('  startTime: %s   now: %s \n' % (str(startTime),str(datetime.datetime.utcnow())))

    for vessel in vessels:

        query='SELECT AsText(position) FROM position WHERE userid=%s'
        if startTime is not None:
            query += ' AND cg_timestamp > %s'
        query+=' ORDER BY cg_sec DESC'
        if limitPoints is not None: query+=' LIMIT '+str(limitPoints)
        query+=';'

        #print 'startTime should be set',startTime
        if startTime is not None:
            #print 'FIX: q', (query % (vessel,startTime))
            cu.execute(query,(vessel,startTime))
        else:
            sys.exit ('NO!!!')
            cu.execute(query,(vessel,))
        linePoints=[]
        #lineLen=0
        for row in cu.fetchall():
            #lineLen+=1
            #print 'A point on the line',row[0]
            x,y = row[0].split()
            x = x.split('(')[1]
            y = y.split(')')[0]
            #print 'x,y',x,y
            if x=='181' and y=='91':
                if v:
                    sys.stderr.write('skipping point with no position: %s %s\n' % (vessel,row))
                continue
            linePoints.append(row[0].split('(')[1].split(')')[0])
        if len(linePoints)<2:#lineLen<2:
            if v:
                sys.stderr.write('Line needs at least 2 points for vessel %s\n' % vessel)
            cu.execute ('SELECT '+trackKey+' FROM '+trackTable+' WHERE userid = %s;',( vessel,))
            row = cu.fetchall()
            if len(row)>0:
                if v:
                    sys.stderr.write('dropping vessel %s from track\n' % vessel)
                cu.execute('DELETE FROM '+trackTable+' WHERE userid = %s;',(vessel,))
            continue
        lineWKT='LINESTRING('+','.join(linePoints)+')'
        if v:
            sys.stderr.write(str(len(linePoints))+' points used for vessel '+str(vessel)+'\n')
        # Get the most recent vessel name
        #if v: print 'Getting name...'
        cu.execute('SELECT name FROM shipdata WHERE userid='+str(vessel)+' LIMIT 1')

        # Always strip the junk off the name
        name = cu.fetchall()
        if len(name)==1:
            name=name[0][0].strip('@ ')
        else:
            name=str(vessel)

        if name=="":
            name=str(vessel)
        #sys.stderr.write('a NAME for '+str(vessel)+' is "'+name+'"\n')

        cu.execute('SELECT '+trackKey+' FROM '+trackTable+' WHERE userid='+str(vessel)+'\n')
        track_keys = cu.fetchall()
        #print 'track_keys',track_keys
        now = datetime.datetime.utcnow()
        if len(track_keys)==0:
            # Does not exist in the database, so insert a new line
            query = 'INSERT INTO track_lines (userid,name,track,update_timestamp) VALUES (%s,%s,GeomFromText(%s,4326),%s);'
            try:
                cu.execute(query,(vessel,name,lineWKT,now))
            except psycopg.ProgrammingError,inst:
                sys.stderr.write('psycopg2 execute flailed: '+str(inst)+'\n')
                traceback.print_exc(file=sys.stderr)
            else:
                vesselsUpdated += 1
        elif len(track_keys)==1:
            # Need to replace an existing row
            query = 'UPDATE track_lines SET name = %s, track = GeomFromText(%s,4326), update_timestamp = %s WHERE '+trackKey+' = %s'
            key = track_keys[0][0]
            try:
                cu.execute(query,(name,lineWKT,now,key))
            except psycopg.ProgrammingError,inst:
                sys.stderr.write('psycopg2 execute flailed: '+str(inst)+'\n')
                traceback.print_exc(file=sys.stderr)
            else:
                vesselsUpdated += 1
        else:
            # How did this happen???
            sys.stderr.write('ERROR: database corrupted ... too many track lines for '+str(vessel)+'\n')

    if vesselsUpdated>0:
        cx.commit()
        if v: sys.stderr.write('Updated tracks ... '+str(vesselsUpdated)+' tracks updated\n')

    #
    # Handle class B reports here
    #

    if startTime is not None:
        #cu2 = cx.cursor()
        print '*** Removing track_lines older than', startTime
        #checkpoint()
        cu.execute('SELECT COUNT(userid) FROM track_lines;')
        #checkpoint()
        count = cu.fetchone()
        #checkpoint()
        print 'COUNT track_lines "%s"' % count

        #checkpoint()

        import traceback

        sql = 'DELETE FROM track_lines WHERE userid IN (SELECT userid FROM track_lines WHERE update_timestamp < %s);'
        #try:
        #    checkpoint()
        cu.execute(sql,(startTime,))
        #checkpoint()
        #try:
        cx.commit()
        #except psycopg.ProgrammingError,inst:
        #    sys.stderr.write('psycopg2 execute flailed: '+str(inst)+'\n')
        #    traceback.print_exc(file=sys.stderr)

        #checkpoint()

        cu.execute('SELECT COUNT(userid) FROM track_lines;')
        #checkpoint()
        print 'AFTER COUNT track_lines',cu.fetchone()[0]

        print 'done cleaning track_lines based on startTime'


    if v:
        sys.stderr.write('Leaving REBUILD_TRACK_LINES\n')


def rebuild_last_position(cx
                          ,vesselsClassA=None
                          ,vesselsClassB=None
                          ,lastPosTable='last_position'
                          ,posKey='key'
                          ,startTime=None
                          ,verbose=False):
    '''
    This is to speed up the redrawing of the most recent position drawing in mapserver

    @param vessels: if None, do all vessels in the tables, otherwise a set of MMSI values
    @param trackTable: the database table where to put the lines
    @param startTime: oldest timestamp to allow in the last_position table
    @type startTime: datetime
    '''
    v = verbose
    cu = cx.cursor()

    #
    # position table - Class A
    #
    if v:
        sys.stderr.write ('REBUILD_LAST_POSITION: (%s to %s)\n' % ( str(startTime), str(datetime.datetime.utcnow()) ) )

    vesselsUpdated=0
    if vesselsClassA is None:
        if startTime:
            sql = 'SELECT distinct(userid) FROM position WHERE cg_timestamp > %s;'
            print 'FIX: sql last pos - ',sql
            cu.execute(sql,(startTime,))
        else:
            cu.execute('SELECT distinct(userid) FROM position;')
        vesselsClassA = set()
        for v in cu.fetchall():
            vesselsClassA.add(v[0])

    if v:
        sys.stderr.write ('  num class A vessels: %s\n' % len(vesselsClassA))

    for vessel in vesselsClassA:

        query='SELECT position,cog,sog,cg_timestamp FROM position WHERE userid=%s ORDER BY cg_sec DESC LIMIT 1;'
        #if startTime is not None:
        #    query += ' AND cg_timestamp > %s'
        #query+=' ORDER BY cg_sec DESC LIMIT 1;'
        #if startTime is not None:
        #    #print 'FIX: q', (query % (vessel,startTime))
        #    cu.execute(query,(vessel,startTime))
        #else:
        cu.execute(query,(vessel,));

        rows = cu.fetchall()
        if len(rows)==0: continue
        row = rows[0]
        position = row[0] # Already in WKB
        cog = int(row[1])  # convert from decimal
        sog = float(row[2])  # convert from decimal
        cg_timestamp = row[3]

        # FIX: why are we getting a date object here?
        if isinstance(startTime,datetime.date):
            sys.stderr.write('WARNING: unexpected date object.  converting to a datetime\n')
            startTime=datetime.datetime(startTime.year,startTime.month,startTime.day)

        if startTime is not None and cg_timestamp < startTime:
            cu.execute ('SELECT '+posKey+' FROM '+lastPosTable+' WHERE userid = %s;',( vessel,))
            row = cu.fetchall()
            if len(row)>0:
                if v:
                    sys.stderr.write('dropping vessel %s from last_position\n' % vessel)
                q = 'DELETE FROM '+lastPosTable+' WHERE userid = %s;'
                #sys.stderr.write('delete cmd: %s %s\n' % (q,str(vessel)))
                cu.execute(q,(vessel,))
                cx.commit()
            continue

        cu.execute('SELECT name,shipandcargo FROM shipdata WHERE userid='+str(vessel)+' LIMIT 1')
        name = cu.fetchall()
        if len(name)==1:
            name=name[0][0].strip('@ ')
        else:
            name=str(vessel)

        if name=="":
            sys.stderr.write("Bad ship with empty name: %d\n" % vessel)
            name=str(vessel)

        sys.stderr.write('b NAME for '+str(vessel)+' is "'+name+'"\n')

        # FIX: set color based on shipandcargo

        cu.execute('SELECT '+posKey+' FROM '+lastPosTable+' WHERE userid=%s\n', (vessel,))
        lastpos_keys = cu.fetchall()

        if len(lastpos_keys)==0:
            # Does not exist in the database, so insert a new line
            if v:
                print 'inserting...',vessel,name,cog,cg_timestamp,position
            query = 'INSERT INTO '+lastPosTable+' (userid,name,cog,sog,cg_timestamp,position) VALUES (%s,%s,%s,%s,%s,%s);'
            try:
                #print query
                #if v:
                #    sys.stderr.write('SQL insert to last pos %s\n' % query)
                cu.execute(query,(vessel,name,cog,sog,cg_timestamp,position))
            except psycopg.ProgrammingError,inst:
                sys.stderr.write('psycopg2 execute flailed: '+str(inst)+' for\n  ')
                sys.stderr.write(query+'\n')
                traceback.print_exc(file=sys.stderr)
            else:
                vesselsUpdated += 1
        elif len(lastpos_keys)==1:
            # Need to replace an existing row

            query = 'UPDATE '+lastPosTable+' SET name = %s, cog = %s, sog = %s, cg_timestamp=%s, position = %s WHERE '+posKey+' = %s'
            key = lastpos_keys[0][0]
            try:
                cu.execute(query,(name,cog,sog,cg_timestamp,position,key))
            except psycopg.ProgrammingError,inst:
                sys.stderr.write('psycopg2 execute flailed: '+str(inst)+' for\n  ')
                sys.stderr.write(query+'\n')
                traceback.print_exc(file=sys.stderr)
            else:
                vesselsUpdated += 1

        else:
            # How did this happen???
            sys.stderr.write('ERROR: database corrupted ... too many positions for '+str(vessel)+'\n')

    if vesselsUpdated>0:
        cx.commit()
        if v: sys.stderr.write('Updated tracks ... '+str(vesselsUpdated)+' tracks updated\n')

    if vesselsClassB is not None:
        print 'FIX: class B not yet implemented'

    if startTime is not None:
        print '*** Removing positions older than', startTime

        cu.execute('SELECT COUNT(key) FROM position;')
        print 'COUNT position',cu.fetchone()

        cu.execute('SELECT COUNT(key) FROM last_position;')
        print 'COUNT last_position',cu.fetchone()

        # Remove old points to keep the database lean... go back a few days
        sql = 'DELETE FROM position WHERE key IN (SELECT key FROM position WHERE cg_timestamp < %s);'
        when = startTime - datetime.timedelta(days=4)
        cu.execute(sql,(when,))

        sql = 'DELETE FROM last_position WHERE key IN (SELECT key FROM last_position WHERE cg_timestamp < %s);'
        cu.execute(sql,(startTime,))

        cx.commit()

        cu.execute('SELECT COUNT(key) FROM position;')
        print 'AFTER COUNT position',cu.fetchone()

        cu.execute('SELECT COUNT(key) FROM last_position;')
        print 'AFTER COUNT last_position',cu.fetchone()

        print 'done cleaning position and last_position based on startTime'


# FIX: unittests here?
