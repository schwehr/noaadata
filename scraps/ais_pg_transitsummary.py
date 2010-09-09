#!/usr/bin/env python

__version__ = '$Revision: 4791 $'.split()[1]
__date__ = '$Date: 2007-01-04 $'.split()[1]
__author__ = 'Kurt Schwehr'

__doc__="""
Create a table of statistics for the SBNMS traffic analysis

@requires: U{epydoc<http://epydoc.sourceforge.net/>} > 3.0alpha3
@requires: U{psycopg2<http://initd.org/projects/psycopg2>}
@requires: U{postgreSQL<http://www.postgresql.org/>} => 8.2
@requires: U{postgis<http://postgis.org>} => 8.2

@author: """+__author__+"""
@version: """ + __version__ +"""
@var __date__: Date of last svn commit
@undocumented: __version__ __author__ __doc__ parser
@status: under development
@license: GPL v3
@since: 2007-Jul-11

"""

import os,sys
import datetime
import pytz

utc = pytz.utc
datefmt = '%Y-%m-%d'
timefmt = '%H:%M:%S'

def mark_utc(dt):
    '''Take a datetime object in UTC without timezone set and return one with utc marked'''
    #print dt
    return datetime.datetime(dt.year,dt.month,dt.day, dt.hour, dt.minute, dt.second, tzinfo=utc)

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

    parser.add_option('-m','--max-speed',dest='maxSpeed',default=102.19
                      ,type='float'
                      ,help='102.3 is technically the undefined value for speed, but some venders do not agree [default: %default]')
    parser.add_option('-t','--threshold-speed',dest='thresholdSpeed',default=12.
                      ,type='float'
                      ,help='102.3 is technically the undefined value for speed, but some venders do not agree [default: %default]')

    parser.add_option('--mmsi',dest='mmsi', default=None, type='int'
                      ,help='Restrict the summary to just one vessel')

    parser.add_option('--timezone',dest='timezone', default='UTC'
                      ,help='What timezone to use, e.g. EST.  None is UTC [default: %default]')

    parser.add_option('-v','--verbose',dest='verbose',default=False,action='store_true',
                      help='Make the test output verbose')

    (options,args) = parser.parse_args()
    verbose = options.verbose

    # By putting imports here, help is available even 
    import psycopg2 as psycopg
    import pyExcelerator as excel
    import pytz
    import datetime

    options.timezone = pytz.timezone(options.timezone)

    connectStr = "dbname='"+options.databaseName+"' user='"+options.databaseUser+"' host='"+options.databaseHost+"'"
    if verbose:
        sys.stderr.write( 'CONNECT: %s' % connectStr )
    cx = psycopg.connect(connectStr)
    cu = cx.cursor()

    workbook = excel.Workbook()
    ws = workbook.add_sheet('Transit Stats')
    ws_row = 0

    d = datetime.datetime.now()
    ws.write(ws_row,0,'Stats for each transit/skipped transits are single point issues')
    ws_row += 1

    ws.write(ws_row,0,'Analysis done on %d-%02d-%02d' % (d.year, d.month, d.day))
    ws_row += 1

    # Give a time range summary
    cu.execute('select min(startpos),max(endpos) from transit;')
    start,stop = cu.fetchone()
    
    cu.execute('SELECT cg_timestamp FROM position WHERE key=%s or key=%s;',(start,stop))
    start = mark_utc(cu.fetchone()[0])
    stop  = mark_utc(cu.fetchone()[0])

    col = 0
    ws.write(ws_row,col,'Time range (UTC):'); col+=1
    ws_row += 1

    col = 0
    ws.write(ws_row,col,'Start:'); col+=1
    ws.write(ws_row,col,start.strftime(datefmt)); col+=1
    ws.write(ws_row,col,start.strftime(timefmt)); col+=1
    ws.write(ws_row,col,'Stop:'); col+=1
    ws.write(ws_row,col,stop.strftime(datefmt)); col+=1
    ws.write(ws_row,col,stop.strftime(timefmt)); col+=1
    ws_row+=1

    if options.timezone!=pytz.timezone('UTC'):
        start = start.astimezone(options.timezone)
        stop  =  stop.astimezone(options.timezone)

        col = 0
        ws.write(ws_row,col,'Time range ('+options.timezone.zone+'):'); col+=1
        ws_row += 1

        col = 0
        ws.write(ws_row,col,'Start:'); col+=1
        ws.write(ws_row,col,start.strftime(datefmt)); col+=1
        ws.write(ws_row,col,start.strftime(timefmt)); col+=1
        ws.write(ws_row,col,'Stop:'); col+=1
        ws.write(ws_row,col,stop.strftime(datefmt)); col+=1
        ws.write(ws_row,col,stop.strftime(timefmt)); col+=1
        ws_row+=1

    del start
    del stop

    col=0
    ws.write(ws_row,col,'Transit ID'); col+=1
    ws.write(ws_row,col,'MMSI(UserID)'); col+=1
    ws.write(ws_row,col,'StartKey'); col+=1
    ws.write(ws_row,col,'EndKey'); col+=1

    ws.write(ws_row,col,'Start Date ('+str(options.timezone)+')'); col+=1
    ws.write(ws_row,col,'Start Time ('+str(options.timezone)+')'); col+=1
    ws.write(ws_row,col,'End Date ('+str(options.timezone)+')'); col+=1
    ws.write(ws_row,col,'End Time ('+str(options.timezone)+')'); col+=1

    ws.write(ws_row,col,'Length(km)'); col+=1
    ws.write(ws_row,col,'Min SOG(kts)'); col+=1
    ws.write(ws_row,col,'Max SOG(kts)'); col+=1
    ws.write(ws_row,col,'time > '+str(options.thresholdSpeed)+' kts (sec)'); col+=1
    ws.write(ws_row,col,'total Time (sec)'); col+=1
    ws.write(ws_row,col,'% time > '+str(options.thresholdSpeed)+' kts'); col+=1
    ws.write(ws_row,col,'aisPos Count'); col+=1
    ws.write(ws_row,col,'aisPos Used'); col+=1
    ws.write(ws_row,col,'aisPos > '+str(options.thresholdSpeed)+' kts'); col+=1
    ws_row+=1


    if options.mmsi != None:
        if verbose:
            sys.stderr.write('Selecting transits for only one vessel...\n')
        cu.execute('SELECT * FROM transit WHERE userid=\''+str(options.mmsi)+'\';')
    else: # Was the default None
        if verbose:
            sys.stderr.write('Selecting transits for all vessels...\n')
        cu.execute('SELECT * FROM transit ORDER BY id;')

    rowcount=0
    skip_notice=False
    for rowcount,transit in enumerate(cu.fetchall()):
       
#        if rowcount<1360:
#            if not skip_notice:
#                print 'skip!!!!!!!!'
#                skip_notice = True
#            continue

        if rowcount%50==0: sys.stderr.write('rowcount %d\n' % rowcount)

        print transit

        t_id,userid,startkey,endkey = transit
#        if t_id>35:
#            print 'EARLY BREAK FIX:'
#            break

        if startkey==endkey:
            if verbose:
                sys.stderr.write('skipping transit id='+str(t_id)+' ... only one point\n')
            col=0
            ws.write(ws_row,col,t_id); col+=1
            ws.write(ws_row,col,str(userid)); col+=1
            ws.write(ws_row,col,startkey); col+=1
            ws.write(ws_row,col,endkey); col+=1
            ws.write(ws_row,col,'Start and end are the same position message'); col+=1
            ws_row += 1
            continue
        # 32619 is UTM 19N WGS84
        cu.execute('SELECT Length(Transform(track,32619))/1000. as length_km from tpath WHERE id=%s;',(t_id,));
        try:
            length_km = cu.fetchone()[0]
        except:
            sys.stderr.write('length_km failed for %s\n' % t_id)
            length_km = -9999
        cu.execute('SELECT MIN(sog),MAX(sog) FROM position WHERE key>=%s AND key<=%s AND userid=%s AND sog<%s;'
                   ,(startkey,endkey,userid,options.maxSpeed))
        minSog,maxSog = cu.fetchone()
        #print minSog,type(minSog)
        if None == minSog or None==maxSog:
            print 'HELP... FIX me... why is this none for this ship?',transit
            col=0
            ws.write(ws_row,col,t_id); col+=1
            ws.write(ws_row,col,str(userid)); col+=1
            ws.write(ws_row,col,startkey); col+=1
            ws.write(ws_row,col,endkey); col+=1
            ws.write(ws_row,col,'Min or max sog not available'); col+=1
            ws_row+=1
            continue
         
        minSog=float(minSog)
        maxSog=float(maxSog)


        time_range_sql = 'SELECT MIN(cg_timestamp),MAX(cg_timestamp) FROM position WHERE userid=%d AND key>=%d AND key<=%d;' % (userid,startkey,endkey)
        cu.execute(time_range_sql)
        startTime,endTime = cu.fetchone()

        
        cu.execute('SELECT MIN(cg_sec),MAX(cg_sec) FROM position WHERE userid=%d AND key>=%d AND key<=%d;' % (userid,startkey,endkey))
        minT,maxT = cu.fetchone()

        totalT = int(maxT)-int(minT)

        cu.execute('SELECT sog,cg_sec FROM position WHERE key>=%s AND key<=%s AND userid=%s;'
                   ,(startkey,endkey,userid))

        lastSOG,lastSEC = cu.fetchone()
        lastSOG=float(lastSOG)
        threshold=options.thresholdSpeed # knots
        totalSecAbove=0
        pointCount=0

        aisPosUsed=0
        if lastSOG<options.maxSpeed:
            aisPosUsed+=1

        for row in cu.fetchall():
            pointCount+=1
            sog,sec = row
            sog=float(sog)

            if lastSEC==sec:
                if verbose:
                    sys.stderr.write('skipping transit point for '+str(t_id)+' ... adjacents points within the same second\n')
                    sys.stderr.write('  '+str(pointCount)+': '+str(sog)+' '+str(lastSEC)+' '+str(sec)+'\n')
                continue

            aisPosUsed+=1
            
            if lastSOG<threshold and sog<threshold:
                lastSOG,lastSEC=sog,sec
                continue

            #if lastSOG>=102.29:
            if lastSOG>=options.maxSpeed:
                sys.stderr.write('a - skipping transit point for '+str(t_id)+' ... 102.3 is an undefined speed for vessel '+str(userid)+'\n')
                sys.stderr.write('  '+str(pointCount)+': '+str(sog)+' '+str(lastSEC)+' '+str(sec)+'\n')
#                if sog<102.29:
                if sog<options.maxSpeed:
                    lastSOG,lastSEC=sog,sec
                continue
#            elif sog>=102.29:
            elif sog>=options.maxSpeed:
                sys.stderr.write('b - skipping transit point for '+str(t_id)+' ... 102.3 is an undefined speed for vessel '+str(userid)+'\n')
                sys.stderr.write('  '+str(pointCount)+': '+str(sog)+' '+str(lastSEC)+' '+str(sec)+'\n')
                # no point in updating the lastSOG, lastSEC
                continue

            # y = mx+b
            if sog>=threshold and lastSOG>=threshold:
                totalSecAbove += sec-lastSEC
            else:
                # Do linear interpolation of where the ship dropped below threshold (12) knots.
                m = (sog-lastSOG)/float(sec-lastSEC)
                t12 = (threshold-lastSOG)/m + lastSEC
                if sog>lastSOG:
                    totalSecAbove += sec-t12
                else:
                    totalSecAbove += t12-lastSEC
            lastSOG,lastSEC=sog,sec

            

        cu.execute('SELECT COUNT(*) FROM position WHERE key>=%s AND key<=%s AND userid=%s;',(startkey,endkey,userid));
        aisPosCount=cu.fetchone()[0];
        aisPosCount=int(aisPosCount)

        cu.execute('SELECT COUNT(*) FROM position WHERE key>=%s AND key<=%s AND userid=%s AND sog>=%s;'
                   ,(startkey,endkey,userid,threshold));
        aisPosAboveThresh=cu.fetchone()[0];
        aisPosAboveThresh=int(aisPosAboveThresh)

        if totalT != 0:
            percentOverThresh = (totalSecAbove / totalT)*100
        else:
            sys.stderr.write('totalT is zero for vessel '+str(userid)+'\n')
            percentOverThresh = -9999
        #print t_id,userid,startkey,endkey,length_km,minSog,maxSog,totalSecAbove, totalT, percentOverThresh
        col=0
        ws.write(ws_row,col,t_id); col+=1
        ws.write(ws_row,col,str(userid)); col+=1
        ws.write(ws_row,col,startkey); col+=1
        ws.write(ws_row,col,endkey); col+=1

        if options.timezone!=pytz.timezone('UTC'):
            #before = startTime
            startTime = mark_utc(startTime).astimezone(options.timezone)
            #print before,' converts to ',startTime
            endTime   = mark_utc(  endTime).astimezone(options.timezone)

        ws.write(ws_row,col,startTime.strftime(datefmt)); col+=1
        ws.write(ws_row,col,startTime.strftime(timefmt)); col+=1

        ws.write(ws_row,col,endTime.strftime(datefmt)); col+=1
        ws.write(ws_row,col,endTime.strftime(timefmt)); col+=1

        ws.write(ws_row,col,length_km); col+=1
        ws.write(ws_row,col,minSog); col+=1
        ws.write(ws_row,col,maxSog); col+=1

        ws.write(ws_row,col,totalSecAbove); col+=1
        ws.write(ws_row,col,totalT); col+=1

        ws.write(ws_row,col,percentOverThresh); col+=1
        ws.write(ws_row,col,aisPosCount); col+=1

        ws.write(ws_row,col,aisPosUsed); col+=1
        ws.write(ws_row,col,aisPosAboveThresh); col+=1
        ws_row+=1


    now = datetime.datetime.now()
    workbook.save('results-'+now.strftime('%Y-%m-%d_%H%M')+'.xls') # FIX - command line option

