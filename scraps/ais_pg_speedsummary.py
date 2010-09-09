#!/usr/bin/env python

__version__ = '$Revision: 4791 $'.split()[1]
__date__ = '$Date: 2007-01-04 $'.split()[1]
__author__ = 'Kurt Schwehr'

__doc__="""

Calculate speed and size parameters.  This uses the summary
spreadsheet parameters for size.  Units for distances will be in
kilometers.  Sorry.  No nautical miles.

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

@todo: catagory - yeah, it is mispelled.  bugger
"""

import sys, os, math
import datetime

from operator import add # For reduce

categories=[
  'cargo_container'
 ,'passenger'
 ,'service_research'
 ,'tanker'
 ,'tug'

# ,'fishing' # we are leaving out fishing for 2006.
]

def km2nm(km):
    return km*0.539956803

def knots2kph(knots):
    #knot = 1.85200 kph
    return knots*1.852

######################################################################
if __name__=='__main__':
    from optparse import OptionParser
    parser = OptionParser(usage="%prog [options]",version="%prog "+__version__)

    parser.add_option('-b','--basename',dest='basename'
                      ,default='speed-summary-km'
                      ,help='Base file name for output')
    parser.add_option('-d','--database-name',dest='databaseName',default='ais',
                      help='Name of database within the postgres server [default: %default]')
    parser.add_option('-D','--database-host',dest='databaseHost',default='localhost',
			  help='Host name of the computer serving the dbx [default: %default]')
    defaultUser = os.getenv('USER')
    parser.add_option('-u','--database-user',dest='databaseUser',default=defaultUser,
                      help='Host name on which the database resides [default: %default]')
    parser.add_option('-r','--restrict-table',dest='table', default='summary2006'
                      ,help='SQL table to use for picking the ship type [default: %default]')
    parser.add_option('-R','--restrict-field',dest='field', default='catagory'
                      ,help='SQL field to use for picking the ship type [default: %default]')

#    parser.add_option('--excel',dest='excel',default=False,action='store_true',
#                      help='Write excel spreadsheet')

#    parser.add_option('--use-nm',dest='useNM',default=False,action='store_true',
#                      help='Report distances in nautical miles rather than km')

    # FIX: utm zone not hardcoded would be good
    # UTM Zone 19... 
    #sql='SELECT AsText(Transform(track,32619)) FROM tpath'
    # --- EPSG 32610 : WGS 84 / UTM zone 10N
    #sql='SELECT AsText(Transform(track,32610)) FROM tpath'

    parser.add_option('-v','--verbose',dest='verbose',default=False,action='store_true',
                      help='Make the test output verbose')
    (options,args) = parser.parse_args()
    verbose = options.verbose

#    if options.useNM:
#        options.basename+='-dist-nm'
#    else:
#        options.basename+='-dist-km'

    import psycopg2 as psycopg

    connectStr = "dbname='"+options.databaseName+"' user='"+options.databaseUser+"' host='"+options.databaseHost+"'"
    if verbose:
         sys.stderr.write('CONNECT: '+connectStr+'\n')
    cx = psycopg.connect(connectStr)
    cu = cx.cursor()

    # FIX: This should be one big database query, I am sure.
    vesselCounts={}
    numberTransits={}
    transitDist={};
    for category in categories: transitDist[category]=0
    transitTime={}
    for category in categories: transitTime[category]=datetime.timedelta(0)
    meanLength={}
    lenStdErr={}
    meanDraught={}
    draughtStdErr={}

    meanMinSpeed={}
    meanMaxSpeed={}

    
    for category in categories:
        if verbose: sys.stderr.write('Category: '+category+'\n')

        minSpeeds=[]
        maxSpeeds=[]

        q = 'SELECT COUNT(id) FROM transit,(SELECT DISTINCT(userid) FROM summary2006 WHERE catagory=\''+category+'\') AS ships WHERE transit.userid=ships.userid;'
        cu.execute(q)
        transits=cu.fetchone()[0]
        if verbose: sys.stderr.write('  Num transits: '+str(transits)+'\n')
        numberTransits[category]=transits

        cu.execute('SELECT DISTINCT(userid) FROM summary2006 WHERE catagory=\''+category+'\';') #LIMIT 20;')
        ships = cu.fetchall()
        if verbose: sys.stderr.write('  Num ships: '+str(len(ships))+'\n')
        vesselCounts[category] = len(ships)
        monthCounts = [0,]*13  # leave 0 well alone
        shipCount=0
        for ship in ships:
            shipCount+=1
            if shipCount%20==0: print ' ',shipCount
            q = 'SELECT t.id,startpos,endpos,length(Transform(track,32619)) FROM tpath'\
                ',(SELECT id,startpos,endpos FROM transit WHERE userid=\''+str(ship[0])+'\') AS t '\
                'WHERE tpath.id=t.id;'
            cu.execute(q)
            for row in cu.fetchall():
                id,startpos,endpos,lengthMeters=row
                cu.execute('SELECT cg_timestamp FROM position WHERE key=\''+str(startpos)+'\';')
                ts = cu.fetchone()[0]
                #if options.useNM:
                #    transitDist[category]+= km2nm(lengthMeters/1000.)
                #else:
                transitDist[category]+=lengthMeters/1000.
                # Transit time
                q = 'SELECT cg_timestamp FROM position WHERE key IN ('+str(startpos)+','+str(endpos)+');'
                cu.execute(q)
                rows = cu.fetchall()
                #print rows
                dt = rows[1][0]-rows[0][0]
                #print dt
                transitTime[category]+=dt

                # Find the min and max speeds for this transit
                cu.execute('SELECT min(SOG),max(SOG) FROM position'\
                           ' WHERE userid='+str(ship[0])+\
                           ' AND key>='+str(startpos)+' AND key<= '+str(endpos)+' AND sog>0 AND SOG IS NOT NULL ;')

                minSOG,maxSOG = cu.fetchone()

                if minSOG is None or maxSOG is None:
                    sys.stderr.write('Ship '+str(ship[0])+' has a transit with no motion.  Not counting towards speed\n')
                else:
                    #print '  SOG range:',minSOG,maxSOG
                    minSpeeds.append(float(minSOG))
                    maxSpeeds.append(float(maxSOG))

        meanMinSpeed[category] = reduce(add, minSpeeds)/len(minSpeeds)
        meanMaxSpeed[category] = reduce(add, maxSpeeds)/len(maxSpeeds)
        if verbose:
            sys.stderr.write('  mean min/max speed: '+str(meanMinSpeed[category])+' ... '+str(meanMaxSpeed[category])+'\n')
                
        if verbose: sys.stderr.write('  calculating avg length\n')
        cu.execute('SELECT AVG(length) FROM summary2006 WHERE catagory=\''+category+'\';')
        curMeanLength=cu.fetchone()[0]
        meanLength[category] = curMeanLength

        # Compute standard error stderr = stddev/#samples.
        # Where stddev (aka sigma) is sqrt ( 1/N * sum [(xi - xave)^2 ] )
        cu.execute('SELECT length FROM summary2006 WHERE catagory=\''+category+'\' AND length IS NOT NULL;')
        sum = 0
        for length in cu.fetchall():
            sum += (length[0] - curMeanLength)**2
        cu.execute('SELECT count(length) FROM summary2006 WHERE catagory=\''+category+'\' AND length IS NOT NULL;')
        n = cu.fetchone()[0]
        print '  n:',n
        lenStdDev = math.sqrt ( sum / n)
        lenStdErr[category] = lenStdDev / math.sqrt (n)
        print '  curMeanLength:',curMeanLength
        print '  lenStdErr:',lenStdErr[category]

        del n
        del curMeanLength
        del lenStdDev
        
        cu.execute('SELECT (SUM(firstdraft)+SUM(lastdraft))/(COUNT(firstdraft)+COUNT(lastdraft))'\
                   'FROM summary2006 WHERE catagory=\''+category+'\' AND firstdraft IS NOT NULL AND lastdraft IS NOT NULL;')
        curMeanDraft=cu.fetchone()[0]
        print '  curMeanDraft:',curMeanDraft
        meanDraught[category] = curMeanDraft

        cu.execute('SELECT count(firstdraft) FROM summary2006'\
                   ' WHERE catagory=\''+category+'\' AND firstdraft IS NOT NULL;')
        n1 = cu.fetchone()[0]
        cu.execute('SELECT count(lastdraft) FROM summary2006'\
                   ' WHERE catagory=\''+category+'\' AND lastdraft IS NOT NULL;')
        n = n1 + cu.fetchone()[0]
        print '  n:',n
        
        cu.execute('SELECT firstdraft,lastdraft  FROM summary2006 WHERE catagory=\''+category+'\' '\
                   ' AND firstdraft IS NOT NULL AND lastdraft IS NOT NULL')
        sum = 0
        for draft in cu.fetchall():
            sum += (draft[0] - curMeanDraft)**2
        draughtStdDev = math.sqrt ( sum / n )
        draughtStdErr[category] = draughtStdDev / math.sqrt (n)
        print ' ',draughtStdErr[category]


    #print ' ',transitTime
    #for key in transitTime:
    #    print key,transitTime[key]
    
        
    if verbose: sys.stderr.write('\nwriting spreadsheet...\n')


    import pyExcelerator as excel
    workbook = excel.Workbook()
    ws = workbook.add_sheet('Vessel Types')
    ws_row=0

    ws.write(ws_row,0,'Vessel Type Table'); ws_row+=1
    ws.write(ws_row,0,'Fishing vessels left out'); ws_row+=1
    ws.write(ws_row,0,'Class A only'); ws_row+=1
    ws_row+=1
    
    col=0
    ws.write(ws_row,col,'Vessel type'); col+=1
    ws.write(ws_row,col,'# of vessels'); col+=1
    ws.write(ws_row,col,'# of transits'); col+=1
    ws.write(ws_row,col,'Tot transit distance (km)'); col+=1
    ws.write(ws_row,col,'Tot transit time (days)'); col+=1
    ws.write(ws_row,col,'Mean Vessel Length (m)'); col+=1
    ws.write(ws_row,col,'StdErr'); col+=1
    ws.write(ws_row,col,'Mean Vessel Draught (m)'); col+=1
    ws.write(ws_row,col,'StdErr'); col+=1
    ws.write(ws_row,col,'Mean Min Speed (kph)'); col+=1
    ws.write(ws_row,col,'Mean Max Speed (kph)'); col+=1

    for category in categories:
        ws_row+=1
        col=0
        ws.write(ws_row,col,category); col+=1
        ws.write(ws_row,col,vesselCounts[category]); col +=1
        #print numberTransits[category], type(numberTransits[category])
        ws.write(ws_row,col,int(numberTransits[category])); col +=1
        ws.write(ws_row,col,transitDist[category]); col +=1
        dt = transitTime[category]
        days = dt.days + dt.seconds / (3600*24.)
        print ' ',dt,"...",dt.days,dt.seconds,"->",days
        ws.write(ws_row,col,days); col +=1
        ws.write(ws_row,col,meanLength[category]); col +=1
        ws.write(ws_row,col,lenStdErr[category]); col +=1
        ws.write(ws_row,col,meanDraught[category]); col +=1
        ws.write(ws_row,col,draughtStdErr[category]); col +=1
        ws.write(ws_row,col,knots2kph(meanMinSpeed[category])); col +=1
        ws.write(ws_row,col,knots2kph(meanMaxSpeed[category])); col +=1
        #ws.write(ws_row,col,[category]); col +=1
        #ws.write(ws_row,col,[category]); col +=1

    workbook.save(options.basename+'.xls')
        
        
