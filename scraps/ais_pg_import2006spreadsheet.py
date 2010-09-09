#!/usr/bin/env python

__version__ = '$Revision: 4791 $'.split()[1]
__date__ = '$Date: 2007-01-04 $'.split()[1]
__author__ = 'Kurt Schwehr'

__doc__='''
Import the CSV from the 2006 ship AIS data

Column W

cargo_container
fishing
passenger
service_research
tanker
tug

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
    parser = OptionParser(usage="%prog [options]",version="%prog "+__version__)

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

    (options,args) = parser.parse_args()

    import psycopg2 as psycopg
    import ais.sqlhelp as sqlhelp

    connectStr = "dbname='"+options.databaseName+"' user='"+options.databaseUser+"' host='"+options.databaseHost+"'"

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
CREATE TABLE summary2006
(
  id serial NOT NULL,
  userid integer NOT NULL, 	-- primary mmsi
  userid2 integer, 		-- mmsi in the case where the ship had 2 mmsi values.  Mostly null
  imo_no integer, 		-- null if not available.
  numTransits integer NOT NULL,
  jan integer,			-- Number of transits within this month
  feb integer,			-- Number of transits within this month
  mar integer,			-- Number of transits within this month
  apr integer,			-- Number of transits within this month
  may integer,			-- Number of transits within this month
  jun integer,			-- Number of transits within this month
  jul integer,			-- Number of transits within this month
  aug integer,			-- Number of transits within this month
  sep integer,			-- Number of transits within this month
  oct integer,			-- Number of transits within this month
  nov integer,			-- Number of transits within this month
  dec integer,			-- Number of transits within this month
  timeInRegion REAL,		-- Hours
  posCountAIS integer,		-- Number of 1,2,3 AIS packages received
  name varchar(40),		-- Vessel Name
  shiptype varchar(50),		-- From msg 5
  cargotype varchar(50),	-- From msg 5
  catagory varchar(40) NOT NULL,-- Vessel Catagory... **V** 6 possible (pass, fishing, cargo_contr, serv_rese, tanker, tug)
  vesseltype varchar(50),	-- vessel type (w)
  vcargo varchar(50),		-- X
  length REAL,			-- m??
  beam REAL,
  firstDraft REAL,
  lastDraft REAL,
  grossTonnage integer,
  yearBuilt integer,
  flag varchar(40),
  missingData int,
  photoURL varchar,
  notes varchar,
  CONSTRAINT summary2006_pkey PRIMARY KEY (id)
);
''')

        cu.execute('CREATE INDEX summary2006_userid_idx ON summary2006(userid);')
        cu.execute('CREATE INDEX summary2006_userid2_idx ON summary2006(userid2);')
        cu.execute('CREATE INDEX summary2006_catagory_idx ON summary2006(catagory);')
        cx.commit()

    for filename in args:
        linenum=0
        for line in file(filename):
            linenum+=1
            print 'LINE:', linenum
            if line[0]=='P':
                continue # Skip first line
            fields = line.split(',')
            if len (fields[0]) == 0:
                continue # skip summary line
            ins = sqlhelp.insert('summary2006',dbType='postgres')

            i = 0
            ins.add('userid', int(fields[i])); i+=1
            if len(fields[i])>0: ins.add('userid2', int(fields[i]));
            i+=1
            if len(fields[i])>0 and fields[i]!='NA': ins.add('imo_no', int(fields[i]));
            i+=1
            ins.add('numTransits', int(fields[i])); i+=1

            for mon in ('jan','feb','mar','apr','may','jun','jul','aug','sep','oct','nov','dec'):
                if len(fields[i])>0: ins.add(mon, int(fields[i]));
                else: ins.add(mon,0)
                i+=1
            
            ins.add('timeInRegion',float(fields[i])); i+=1
            ins.add('posCountAIS', int(fields[i])); i+=1
            name = fields[i].replace("'"," ")  # NOR'EASTER causes trouble
            ins.add('name',name);
            i+=1
            ins.add('shiptype',fields[i]); i+=1
            ins.add('cargotype',fields[i]); i+=1
            ins.add('catagory',fields[i]); i+=1
            ins.add('vesseltype',fields[i]); i+=1
            ins.add('vcargo',fields[i]); i+=1
            if len(fields[i])>0: ins.add('length',float(fields[i]));
            i+=1
            if len(fields[i])>0: ins.add('beam',float(fields[i]));
            i+=1
            if len(fields[i])>0 and fields[i]!='NA': ins.add('firstDraft',float(fields[i]));
            i+=1
            if len(fields[i])>0 and fields[i]!='NA': ins.add('lastDraft',float(fields[i]));
            i+=1
            if len(fields[i])>0 and fields[i]!='NA': ins.add('grossTonnage',float(fields[i]));
            i+=1
            if len(fields[i])>0 and fields[i]!='NA': ins.add('yearBuilt', int(fields[i]));
            i+=1
            if len(fields[i])>0: ins.add('flag',fields[i]);
            i+=1
            if len(fields[i])>0: ins.add('missingData', int(fields[i]));
            i+=1
            if len(fields[i])>0: ins.add('photoURL',fields[i]);
            i+=1
            if len(fields[i])>0: ins.add('notes',fields[i].replace("'"," "));
            #i+=1
            print str(ins)
            cu.execute(str(ins))

        cx.commit()
        
