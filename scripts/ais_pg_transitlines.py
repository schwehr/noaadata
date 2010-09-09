#!/usr/bin/env python

__version__ = '$Revision: 7470 $'.split()[1]
__date__ = '$Date: 2007-11-06 10:31:44 -0500 (Tue, 06 Nov 2007) $'.split()[1]
__author__ = 'Kurt Schwehr'

__doc__="""
Create track lines for each transit from points in each line.

I did this in PL/pgsql, but gave up after a couple hours of the code
cranking on the 4.5 M points that I have.  Here is the code:

CREATE OR REPLACE FUNCTION aisTransitLines () RETURNS text
AS '
  DECLARE
       text_output TEXT := '' '';
       arow transit%ROWTYPE;
  BEGIN
       FOR arow IN SELECT * FROM transit LOOP
           text_output := text_output || arow.userid || ''\n'';

           INSERT INTO tpath 
           SELECT arange.id as id, arange.userid, setSRID(MakeLine(position),4326) AS track
                  FROM 
                  	    position,
                  	    (SELECT userid,startpos,endpos,id FROM transit WHERE transit.id=arow.id) AS arange 
                  WHERE 
                  	    position.key >= arange.startpos 
           	    and 
           	    position.key <= arange.endpos
           	    and
           	    position.userid = arange.userid
                  GROUP BY id,arange.userid
             ;
       END LOOP;
       RETURN text_output;
  END;
' LANGUAGE 'plpgsql';


@requires: U{epydoc<http://epydoc.sourceforge.net/>} > 3.0alpha3
@requires: U{psycopg2<http://initd.org/projects/psycopg2>}
@requires: U{postgreSQL<http://www.postgresql.org/>} => 8.2
@requires: U{postgis<http://postgis.org>} => 8.2

@author: """+__author__+"""
@version: """ + __version__ +"""
@var __date__: Date of last svn commit
@undocumented: __version__ __author__ __doc__ parser
@status: under development
@license: GPL v2
@since: 2007-Jul-01

@todo: find a pure sql way to do this on the server side.  This would be the run section of the SQL boo
"""


import os,sys

if __name__=='__main__':
    from optparse import OptionParser
    parser = OptionParser(usage="%prog [options]",version="%prog "+__version__)

    parser.add_option('-d','--database-name',dest='databaseName',default='ais',
                      help='Name of database within the postgres server [default: %default]')
    parser.add_option('-D','--database-host',dest='databaseHost',default='localhost',
			  help='Host name of the computer serving the dbx [default: %default]')
    defaultUser = os.getlogin()
    parser.add_option('-u','--database-user',dest='databaseUser',default=defaultUser,
                      help='Host name of the to access the database with [default: %default]')
# FIX: add password
    parser.add_option('-t','--table-name',dest='tableName',default='tpath',
                      help='Table name to use for the geometry [default: %default]')

    parser.add_option('-C','--with-create',dest='createTables',default=False, action='store_true',
                      help='Do not create the tables in the database')

    parser.add_option('-v','--verbose',dest='verbose',default=False,action='store_true',
                      help='Make the test output verbose')

    (options,args) = parser.parse_args()
    verbose = options.verbose
    import psycopg2 as psycopg
    import ais.sqlhelp as sqlhelp

    connectStr = "dbname='"+options.databaseName+"' user='"+options.databaseUser+"' host='"+options.databaseHost+"'"
    if verbose:
        print 'CONNECT:',connectStr
    cx = psycopg.connect(connectStr)
    cu = cx.cursor()

    if options.createTables:
        try:
            #cu.execute('drop table summary2006;')
            #cx.commit()
            #print 'table dropped'
            pass
        except:
            print 'table did not already exist'
        

        cu.execute('''
CREATE TABLE '''+options.tableName+'''
(
  id INTEGER NOT NULL REFERENCES transit(id),  -- transit id number from the transit table
  userid INTEGER NOT NULL 		-- primary mmsi
  -- geometry column created with a stored procedure
);
''')

        cu.execute("SELECT AddGeometryColumn('tpath','track',4326,'LINESTRING',2);")
        # FIX: add index on id or userid?
        # Add the non-btree index on the geometry so that it can be searched

        cx.commit()


    # Loop through each transit and create the line geometry in tpath
    cu.execute('SELECT * FROM transit;')
    cu2 = cx.cursor()
    rowNum=0
    for row in cu.fetchall():
        rowNum+=1

        id,userid,startpos,endpos=row

        cu2.execute('SELECT count(*)'
                    +' FROM position'
                    +' WHERE userid='+str(userid)+' AND key>='+str(startpos)+' AND key<='+str(endpos)+';')
        count=cu2.fetchone()[0]
        if verbose:
            sys.stderr.write('ROW # '+str(rowNum)+'  POSITIONS: '+str(count)+'\n')

        if count>20000:
            if verbose: sys.stderr.write('precommitting before large data operation\n')
            cx.commit()

        cu2.execute('SELECT MakeLine(position)'
                    +' FROM position'
                    +' WHERE userid='+str(userid)+' AND key>='+str(startpos)+' AND key<='+str(endpos)+';')
        if verbose: sys.stderr.write('makeline done\n')
        lineWKB = cu2.fetchone()
        if verbose: sys.stderr.write('fetch wkb done\n')
        cu2.execute('INSERT INTO '+options.tableName+' (id,userid,track) VALUES (%s,%s,%s);',(id,userid,lineWKB[0]))
        if verbose: sys.stderr.write('fetch insert done\n')

        if rowNum%100==0 or count>5000:
            cx.commit()

    cx.commit()
