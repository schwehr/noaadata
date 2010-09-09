#!/usr/bin/env python

__version__ = '$Revision: 13270 $'.split()[1]
__date__ = '$Date: 2010-03-11 14:50:30 -0500 (Thu, 11 Mar 2010) $'.split()[1]
__author__ = 'Kurt Schwehr'

__doc__="""
Create a grid from ais transit lines.  Rewrite of the gridding code
in a separate grid class such that it might actually work correctly.

@requires: U{epydoc<http://epydoc.sourceforge.net/>} > 3.0alpha3
@requires: U{psycopg2<http://initd.org/projects/psycopg2>}
@requires: U{postgreSQL<http://www.postgresql.org/>} => 8.2
@requires: U{postgis<http://postgis.org>} => 8.2
@requires: U{pyproj<>}
@requires: grid.py

@author: """+__author__+"""
@version: """ + __version__ +"""
@var __date__: Date of last svn commit
@undocumented: __version__ __author__ __doc__ parser
@status: under development
@license: GPL v3
@since: 2007-Jul-20

"""

import math,sys,os


def utmZoneToEpsg(cx,zone):
    '''
    Fetch the EPSG number from the PostGIS by UTM zone.
    @param cx: database connection
    @param zone: UTM zone number
    @return: EPSG number for use with PostGIS
    '''
    zone = int(zone) # make sure the zone is a valid in.
    # FIX: what is the right number of UTM zones?
    assert(zone>=0)
    assert(zone<=36)

    cu = cx.cursor()
    sql='SELECT srid FROM spatial_ref_sys WHERE srtext LIKE \'%UTM zone '+str(zone)+'%\';'
    #cu.execute('SELECT srid FROM spatial_ref_sys WHERE srtext like ''\%UTM zone %s\%\';',zone)
    cu.execute(sql)
    
    
######################################################################
if __name__=='__main__':
    from optparse import OptionParser
    parser = OptionParser(usage="%prog [options]",version="%prog "+__version__)

    parser.add_option('-b','--basename',dest='basename'
                      #,default='occupancy-grid'
                      ,default='tmp'
                      ,help='Base file name for output')

    parser.add_option('-x','--x-min'
                      ,dest='xMin'
                      ,default=-70.7
                      ,type='float'
                      ,help='Geographic range (-180..180) [default: %default]')
    parser.add_option('-X','--X-max'
                      ,dest='xMax'
                      ,default=-69.9
                      ,type='float'
                      ,help='Geographic range (-180..180) [default: %default]')

    parser.add_option('-y','--y-min'
                      ,dest='yMin'
                      ,default=42.0
                      ,type='float'
                      ,help='Geographic range (-90..90) [default: %default]')
    parser.add_option('-Y','--Y-max'
                      ,dest='yMax'
                      ,default=42.9
                      ,type='float'
                      ,help='Geographic range (-90..90) [default: %default]')
    parser.add_option('-s','--step'
                      ,dest='step'
                      ,default=1852 # 1 nautical mile
                      ,type='float'
                      ,help='cell size in meters [default: %default (1 nautical mile)]')

    parser.add_option('-d','--database-name',dest='databaseName',default='ais',
                      help='Name of database within the postgres server [default: %default]')
    parser.add_option('-D','--database-host',dest='databaseHost',default='localhost',
			  help='Host name of the computer serving the dbx [default: %default]')
    defaultUser = os.getlogin()
    parser.add_option('-u','--database-user',dest='databaseUser',default=defaultUser,
                      help='Host name on which the database resides [default: %default]')
    # FIX: add password
    parser.add_option('-z','--zone',dest='zone',type='int', default=19,
                        help='UTM Zone (19 for UNH) [default: %default]')

    parser.add_option('-l','--limit',dest='limit',type='int', default=None,
                        help='Limit the number of tracks returned from the db for testing [default: %default]')

    parser.add_option('-v','--verbose',dest='verbose',default=False,action='store_true',
                      help='Make the test output verbose')


    parser.add_option('--dry-run',dest='dryRun',default=False,action='store_true',
                      help='Print the SQL query and quit.')


    parser.add_option('--start-date',dest='startDate',default=None,
                      help='Restrict query to begin at this date [default: None]')
    parser.add_option('--end-date',dest='endDate',default=None,
                      help='Restrict date to not extent to more recent than this date [default: None]')

    ########################################

    parser.add_option('-r','--restrict-table',dest='table', default='summary2006'
                      ,help='SQL table to use for picking the ship type [default: %default]')

    # Probably need to do better than hard code these!!
    # FIX: whoops misspelled the table name.  crap
    #parser.add_option('-R','--restrict-field',dest='field', default='category'
    parser.add_option('-R','--restrict-field',dest='field', default='catagory'
                      ,help='SQL field to use for picking the ship type [default: %default]')

    categories={
 0: 'cargo_container'
 ,1: 'fishing'
 ,2: 'passenger'
 ,3: 'service_research'
 ,4: 'tanker'
 ,5: 'tug'
        }
    catStr='0: '+categories[0]
    for i in range(1,len(categories)):
        catStr+=', '+str(i)+': '+categories[i]

    parser.add_option('-c','--category',dest='category', default=None, type='int'
                      ,help='Which ship category to use as a subset [default: %default] '
                      + catStr
                      )



    (options,args) = parser.parse_args()
    verbose = options.verbose

    import aisutils.grid as grid
    import psycopg2 as psycopg
    from pyproj import Proj

    assert options.xMin < options.xMax
    assert options.yMin < options.yMax

    params={'proj':'utm','zone':int(options.zone)}
    proj = Proj(params)

    ll = proj(options.xMin,options.yMin)
    ur = proj(options.xMax,options.yMax)

    connectStr = "dbname='"+options.databaseName+"' user='"+options.databaseUser+"' host='"+options.databaseHost+"'"
    if verbose:
        print 'CONNECT:',connectStr
    cx = psycopg.connect(connectStr)
    cu = cx.cursor()

    step = options.step

    g = grid.Grid(ll[0],ll[1], ur[0],ur[1],stepSize=step, verbose=verbose)
    basename=options.basename
    g.writeLayoutGnuplot(basename+'-grd.dat')

    #sys.stderr.write('FIX: remove limit\n')

    print 'FIX: do not hard code the projection!'
    # UTM Zone 19... 
    sql='SELECT AsText(Transform(track,32619)) FROM tpath'
    # --- EPSG 32610 : WGS 84 / UTM zone 10N
    #sql='SELECT AsText(Transform(track,32610)) FROM tpath'
    

    if options.category!=None:
        s=',(SELECT userid FROM '+options.table+' WHERE '+options.field+'=\''+categories[options.category]
        s+='\') AS ships'
        sql += s

    if options.startDate or options.endDate:
        print 'constraining'
        s=',('
        s+= 'SELECT id FROM position,transit WHERE startpos=key '
        if options.startDate:
            s+= 'AND cg_timestamp > \''+options.startDate+'\' '
        if options.endDate:
            s+= 'AND cg_timestamp < \''+options.endDate+'\' '
        s+=') AS track_id'
        sql+=s

    if options.category!=None or options.startDate or options.endDate:
        sql +=' WHERE '
    if options.category!=None:
        sql +=' ships.userid=tpath.userid'
    if options.category!=None and ( options.startDate!=None or options.endDate!=None):
        sql += ' AND '
    if options.startDate!=None or options.endDate!=None:
        sql +=' tpath.id=track_id.id'

        
    if options.limit != None: sql+=' LIMIT '+str(options.limit)
    sql+=';'
    if options.dryRun:
        print sql
        sys.exit()

    if verbose:
        print sql
    cu.execute(sql)

    tracksFile = file(basename+'-tracks.dat','w')
    trackNum = 0
    for trackline in cu.fetchall():
        trackNum+=1
        if trackNum % 50 == 0:
            sys.stderr.write('track '+str(trackNum)+'\n')

        track = trackline[0];           #print track
        trackseq = grid.wktLine2list(track);  #print trackseq
        if verbose:
            print 'len',len(trackseq)
            if len(trackseq)<2:
                print 'TOO SHORT: ',track
                sys.exit('crap')
        for pt in trackseq:
            tracksFile.write(str(pt[0])+' '+str(pt[1])+' 0\n')
        #cells = getMultiSegLineCells(bbox,step,trackseq,verbose)
        #print cells
        g.addMultiSegLine(trackseq)
        
    tracksFile.write('\n')

    g.writeCellsGnuplot(basename+'-cells.dat')
    g.writeArcAsciiGrid(basename+'-grd.asc')

    
