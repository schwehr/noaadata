#!/usr/bin/env python

__version__ = '$Revision: 7731 $'.split()[1]
__date__ = '$Date: 2007-12-01 17:50:19 -0500 (Sat, 01 Dec 2007) $'.split()[1]
__author__ = 'Kurt Schwehr'

__doc__="""
Purely graph the vessels per day.  Vessels seen per day

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
@since: 2007-Nov-24

@todo: calculate the day of the year for each date and writeout value number
"""

import os
import sys
import datetime

######################################################################
if __name__=='__main__':
    from optparse import OptionParser
    parser = OptionParser(usage="%prog [options]",version="%prog "+__version__)

    parser.add_option('-b','--basename',dest='basename'
                      ,default='month-summaries'
                      ,help='Base file name for output')
    parser.add_option('-d','--database-name',dest='databaseName',default='ais',
                      help='Name of database within the postgres server [default: %default]')
    parser.add_option('-D','--database-host',dest='databaseHost',default='localhost',
			  help='Host name of the computer serving the dbx [default: %default]')
    defaultUser = os.getenv('USER')
    parser.add_option('-u','--database-user',dest='databaseUser',default=defaultUser,
                      help='Host name on which the database resides [default: %default]')


    parser.add_option('-s','--start-date','--begin-date',dest='startDate',default=None,
                      help='Start date of the report (e.g. 2006-01-01) [default: oldest db record]')
    parser.add_option('-e','--end-date',dest='endDate',default=None,
                      help='Start date of the report (e.g. 2007-01-01) [default: youngest db record]')

    parser.add_option('-o','--out-file',dest='outFile',default='dailvessels.dat',
                      help='Start date of the report (e.g. 2007-01-01) [default: %d]')

    parser.add_option('-v','--verbose',dest='verbose',default=False,action='store_true',
                      help='Make the test output verbose')
    (options,args) = parser.parse_args()
    verbose = options.verbose

    import psycopg2 as psycopg

    connectStr = "dbname='"+options.databaseName+"' user='"+options.databaseUser+"' host='"+options.databaseHost+"'"
    if verbose:
         sys.stderr.write('CONNECT: '+connectStr+'\n')
    cx = psycopg.connect(connectStr)
    cu = cx.cursor()
    
    if options.startDate is not None:
        startFields = options.startDate.split('-')
        dt = datetime.datetime(int(startFields[0]),int(startFields[1]),int(startFields[2]))

    if options.endDate is not None:
        endFields = options.endDate.split('-')
        dtend = datetime.datetime(int(endFields[0]),int(endFields[1]),int(endFields[2]))


    if options.startDate is None or options.endDate is None:
        cu.execute(' SELECT min(cg_timestamp),max(cg_timestamp) FROM position;')
        minTS,maxTS = cu.fetchone()
        if verbose: sys.stderr.write('Date range found: '+str(minTS)+' TO '+str(maxTS)+'\n');
        if options.startDate is None: dt    = datetime.datetime(minTS.year,minTS.month,minTS.day)
        if options.endDate   is None: dtend = datetime.datetime(maxTS.year,maxTS.month,maxTS.day)
        del minTS
        del maxTS


    if verbose: sys.stderr.write('Using date range: '+str(dt)+' to '+str(dtend)+'\n')

    doy = 1 # day of the set (can be day of year if starting from 2xxx-01-01)
    oneDay = datetime.timedelta(1)
    o = file(options.outFile,'w')
    dow = [0,]*7
    dowCount = [0,]*7
    while dt < dtend:
        dateStr1 = ('%d-%02d-%02d' % (dt.year, dt.month, dt.day))
        if verbose and doy%20==0: sys.stderr.write(str(doy)+' '+dateStr1+'\n')
        dtnext = dt + oneDay
        dateStr2 = ('%d-%02d-%02d' % (dtnext.year, dtnext.month, dtnext.day))
        q = "SELECT count(distinct(userid)) FROM position"\
            " WHERE cg_timestamp >= '"+dateStr1+"' AND cg_timestamp <= '"+dateStr2+"';"
        cu.execute(q)
        numVessels = cu.fetchone()[0]
        o.write(str(doy)+' '+str(numVessels)+' '+dateStr1+'\n')
        dow[dt.weekday()] += numVessels
        dowCount[dt.weekday()] += 1
        dt = dtnext
        doy += 1

    del o
    
    o = file('dow.dat','w')
    # Monday = 0, Sunday = 6
    dayNames = ('Mon','Tue','Wed','Thu','Fri','Sat','Sun')
    for day in range(7):
        o.write(str(day) +' '+ str(dow[day]/float(dowCount[day])) +' '+ dayNames[day]+'\n')
