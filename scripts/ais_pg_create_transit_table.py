#!/usr/bin/env python

__version__ = '$Revision: 7470 $'.split()[1]
__date__ = '$Date: 2007-11-06 10:31:44 -0500 (Tue, 06 Nov 2007) $'.split()[1]
__author__ = 'Kurt Schwehr'

__doc__='''
Talk to a postgres/postgis db to build the transit table

@requires: U{epydoc<http://epydoc.sourceforge.net/>} > 3.0alpha3
@requires: U{psycopg2<http://initd.org/projects/psycopg2>}
@requires: U{postgreSQL<http://www.postgresql.org/>} => 8.2
@requires: U{postgis<http://postgis.org>} => 8.2

@author: '''+__author__+'''
@version: ''' + __version__ +'''
@var __date__: Date of last svn commit
@undocumented: __version__ __author__ __doc__ parser
@status: under development
@license: GPL v2
@since: 2007-Jul-01

@todo: find a pure sql way to do this on the server side.  This would be the run section of the SQL boo
'''

import os,sys

if __name__=='__main__':
	from optparse import OptionParser
	parser = OptionParser(usage="%prog [options] ",version="%prog "+__version__)
	parser.add_option('-d','--database-name',dest='databaseName',default='ais',
			  help='Name of database within the postgres server [default: %default]')
	parser.add_option('-D','--database-host',dest='databaseHost',default='localhost',
			  help='Host name of the computer serving the dbx [default: %default]')
        defaultUser = os.getlogin()
	parser.add_option('-u','--database-user',dest='databaseUser',default=defaultUser,
			  help='Host name of the to access the database with [default: %default]')
# FIX: add password
	parser.add_option('-C','--with-create',dest='createTables',default=False, action='store_true',
			  help='Do not create the tables in the database')

	parser.add_option('-t','--delta-time',dest='deltaT'
                          ,default=60*60
                          ,type='int'
			  ,help='Time gap in seconds that determines when a new transit starts [default: %default]')

	(options,args) = parser.parse_args()

        import psycopg2 as psycopg

        deltaT = options.deltaT
        
        connectStr = "dbname='"+options.databaseName+"' user='"+options.databaseUser+"' host='"+options.databaseHost+"'"

        cx = psycopg.connect(connectStr)
        cu = cx.cursor()

        if options.createTables:
            print 'FIX: make start and end be foreign keys into position'
#            try:
#                cu.execute('DROP TABLE transit;')
#            except:
#                print 'unable to drop table'
            #cu.execute('''CREATE TABLE transit (id SERIAL PRIMARY KEY, startPos INTEGER, endPos INTEGER);''')
            cu.execute('''
CREATE TABLE transit
(
  id serial NOT NULL,
  userid integer NOT NULL,
  startpos integer NOT NULL,
  endpos integer NOT NULL,
  CONSTRAINT transit_pkey PRIMARY KEY (id)
);
''')
            cx.commit()

        cu.execute('SELECT DISTINCT(userid) FROM position;');
        ships= [ship[0] for ship in cu.fetchall()]
        #print ships
        #print 'FIX: hack... only one ship'
        #ships=[338029917]
        print ships
        for ship in ships:
            print 'Processing ship: ',ship
            cu.execute('SELECT key,cg_sec FROM position WHERE userid=%s ORDER BY cg_sec',(ship,))
            startKey,startTime=cu.fetchone()
            print startKey,startTime
            lastKey,lastTime=startKey,startTime
            needFinal=True
            # Now go through the rest of the ship position records
            for row in cu.fetchall():
                #print row
                needFinal=True
                key,time = row
                #print key,time,('%04d' % (time-lastTime)),  ('%01.3f' % ((time-lastTime)/3600.)),  ('%01.4f' % ((time-lastTime)/3600./24.))
                if time>lastTime+deltaT:
                    #print '\nNew transit found'
                    print  'FOUND',startKey,startTime,'->',lastKey,lastTime
                    cu.execute('INSERT INTO transit (userid,startPos,endPos) VALUES (%s,%s,%s);',(ship,startKey,lastKey))
                    startKey,startTime=key,time
                    needFinal=False
                lastKey,lastTime=key,time # Save for the next loop
                #sys.exit()

            if needFinal:
                print 'Final transit...'
                print 'FOUND',startKey,startTime,'->',lastKey,lastTime
                cu.execute('INSERT INTO transit (userid,startPos,endPos) VALUES (%s,%s,%s);',(ship,startKey,lastKey))
            cx.commit()
