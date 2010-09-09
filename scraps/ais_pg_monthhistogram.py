#!/usr/bin/env python

__version__ = '$Revision: 4791 $'.split()[1]
__date__ = '$Date: 2007-01-04 $'.split()[1]
__author__ = 'Kurt Schwehr'

__doc__="""
Count the transits by ship type for each month.  A transit is
associated with the first month that the vessel is observed.

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

import sys, os

categories=[
  'cargo_container'
# ,'fishing' # we are leaving out fishing for 2006.
 ,'passenger'
 ,'service_research'
 ,'tanker'
 ,'tug'
]


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
    defaultUser = os.getenv('USER') #os.getlogin()
    parser.add_option('-u','--database-user',dest='databaseUser',default=defaultUser,
                      help='Host name on which the database resides [default: %default]')
    parser.add_option('-r','--restrict-table',dest='table', default='summary2006'
                      ,help='SQL table to use for picking the ship type [default: %default]')
    parser.add_option('-R','--restrict-field',dest='field', default='catagory'
                      ,help='SQL field to use for picking the ship type [default: %default]')
    parser.add_option('--excel',dest='excel',default=False,action='store_true',
                      help='Write excel spreadsheet')

    parser.add_option('--distance',dest='distance',default=False,action='store_true',
                      help='Count distance in meters rather than number of transits')
    parser.add_option('--use-nm',dest='useNM',default=False,action='store_true',
                      help='Report distances in nautical miles rather than km')

    # FIX: utm zone not hardcoded would be good
    # UTM Zone 19... 
    #sql='SELECT AsText(Transform(track,32619)) FROM tpath'
    # --- EPSG 32610 : WGS 84 / UTM zone 10N
    #sql='SELECT AsText(Transform(track,32610)) FROM tpath'

    parser.add_option('-v','--verbose',dest='verbose',default=False,action='store_true',
                      help='Make the test output verbose')
    (options,args) = parser.parse_args()
    verbose = options.verbose

    if options.distance:
        if options.useNM:
            options.basename+='-dist-nm'
        else:
            options.basename+='-dist-km'
    else:
        if options.useNM:
            sys.exit('ERROR: can not specify nm units when not in distance mode')

    import psycopg2 as psycopg

    connectStr = "dbname='"+options.databaseName+"' user='"+options.databaseUser+"' host='"+options.databaseHost+"'"
    if verbose:
         sys.stderr.write('CONNECT: '+connectStr+'\n')
    cx = psycopg.connect(connectStr)
    cu = cx.cursor()

    # FIX: This should be one big database query, I am sure.
    catCounts={}
    for category in categories:
        if verbose: sys.stderr.write('Category: '+category+'\n')
        #print 'FIX: remove limit'
        # Yes, I know that I mispelled the field in the database
        cu.execute('SELECT DISTINCT(userid) FROM summary2006 WHERE catagory=\''+category+'\';')  # LIMIT 20;')
        ships = cu.fetchall()
        if verbose: sys.stderr.write('  Num ships: '+str(len(ships))+'\n')
        monthCounts = [0,]*13  # leave 0 well alone
        for ship in ships:
            if options.distance:
                q = 'SELECT t.id,startpos,length(Transform(track,32619)) FROM tpath'\
                           ',(SELECT id,startpos FROM transit WHERE userid=\''+str(ship[0])+'\') AS t '\
                           'WHERE tpath.id=t.id;'
                #if verbose:  sys.stderr.write('  q='+q+'\n')
                cu.execute(q)
                for row in cu.fetchall():
                    id,startpos,lengthMeters=row
                    cu.execute('SELECT cg_timestamp FROM position WHERE key=\''+str(startpos)+'\';')
                    ts = cu.fetchone()[0]
                    #print lengthMeters,ts
                    if options.useNM:
                        monthCounts[ts.month]+= (lengthMeters/1000.) * 0.539956803
                    else:
                        monthCounts[ts.month]+=lengthMeters/1000.
                    
                               
                #sys.exit('early')
            else: # do transit count
                cu.execute('SELECT p.cg_timestamp FROM position AS p, (SELECT startpos FROM transit WHERE userid=\''+str(ship[0])+'\') AS t WHERE key = startpos;')
                for start in cu.fetchall():
                    monthCounts[start[0].month]+=1
        
        if verbose:  sys.stderr.write('  '+str(monthCounts)+'\n')
        catCounts[category]=monthCounts

    #print catCounts
    # gnuplot 4.2 compatible file for histogram plots
    o = file(options.basename+'.dat','w')
    o.write('# Ship transit occurance by category and month\n')
    o.write('Category Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec\n')
    for category in categories:
        o.write(category)
        for i in range(1,13):
            o.write(' '+str(catCounts[category][i]))
        o.write('\n')

    del(o)

    # the above one plots backwards in gnuplot... maybe this one is better
    
    o = file(options.basename+'-2.dat','w')
    o.write('# Ship transit occurance by category and month\n')
    catList = [categories[i] for i in range(len(categories))]
    print catList
    o.write('- '+' '.join(catList)+'\n')
    monthNames = (None,'Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec')
    for i in range(1,13):
        o.write(monthNames[i])
        for category in categories:
            o.write(' '+str(catCounts[category][i]))
        o.write('\n')
    del(o)

    basename=options.basename
    gp=file(basename+'.gp','w')
    gp.write('''#!/usr/bin/env gnuplot
# Generated by ais_pg_monthhistogram.py from noaadata-py\n''')
    if options.distance:
        gp.write("set title 'Vessel Transit Distances'\n")
        if options.useNM:
            gp.write("set ylabel 'Distance (nm)'\n")
        else:
            gp.write("set ylabel 'Distance (km)'\n")
    else:
        gp.write("set title 'Vessel Transit Counts'\n")
        gp.write("set ylabel '# of transits'\n")

    gp.write("set xlabel 'Month'\n")

    gp.write('''set terminal pdf
set key left

set xtics nomirror rotate by -45
set style data linespoints
set datafile missing "-"

set output \''''+basename+'''.pdf\'
plot \''''+basename+'''-2.dat\' using 2:xtic(1) t 2, \
'' u 3 t 3,\
'' u 4 t 4,\
'' u 5 t 5,\
'' u 6 t 6

# Bar graph...
set output \''''+basename+'''-bars.pdf\'
set style data histogram
set style histogram cluster gap 1
set style fill solid border -1
set boxwidth 0.9
replot

# Stacked ...
set output \''''+basename+'''-stacked.pdf\'
set style data histogram
set style histogram rowstacked
set style fill solid border -1
set boxwidth 0.75

replot
''')
    del (gp)
    os.chmod(basename+'.gp',0755)



    if options.excel:
        import pyExcelerator as excel
        workbook = excel.Workbook()
        ws = workbook.add_sheet('Type Transits by Month')
        ws_row=0

        ws.write(ws_row,0,'Ship transits for each month broken down by ship type.  Fishing left out'); ws_row+=1
        if options.distance:
            if options.useNM:
                ws.write(ws_row,6,'Results in nautical miles (nm)'); ws_row+=1
            else:
                ws.write(ws_row,6,'Results in kilometers (km)'); ws_row+=1
        else:
            ws.write(ws_row,6,'Results in number of transits'); ws_row+=1
        col=0
        ws.write(ws_row,col,'Ship type'); col+=1
        ws.write(ws_row,col,'Jan'); col+=1
        ws.write(ws_row,col,'Feb'); col+=1
        ws.write(ws_row,col,'Mar'); col+=1
        ws.write(ws_row,col,'Apr'); col+=1
        ws.write(ws_row,col,'May'); col+=1
        ws.write(ws_row,col,'Jun'); col+=1
        ws.write(ws_row,col,'Jul'); col+=1
        ws.write(ws_row,col,'Aug'); col+=1
        ws.write(ws_row,col,'Sep'); col+=1
        ws.write(ws_row,col,'Oct'); col+=1
        ws.write(ws_row,col,'Nov'); col+=1
        ws.write(ws_row,col,'Dec'); #col+=1

        for category in categories:
            col=0
            ws_row+=1
            ws.write(ws_row,col,category); col+=1
            for i in range(1,13):
                # FIX: double check that we want to be using integers
                ws.write(ws_row,col,int(catCounts[category][i])); col+=1

        workbook.save(options.basename+'.xls')
        
        
