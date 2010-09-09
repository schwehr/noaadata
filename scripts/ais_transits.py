#!/usr/bin/env python

__version__ = '$Revision: 12383 $'.split()[1]
__date__ = '$Date: 2009-08-03 09:41:06 -0400 (Mon, 03 Aug 2009) $'.split()[1]
__author__ = ''

__doc__='''
Calculate ship transits from AIS data.

Here is a quick way to make the xymt format:

ais_build_sqlite.py -d ais.db3 --with-create positions-123.ais 

sqlite3 ais.db3 'SELECT longitude,latitude,UserID,cg_sec FROM position' | tr '|' ' ' > ais.xymt

This program is getting a bit out of control.  Perhaps the best thing
to do in the long run would be to create a sqlite database of transits
and write many different types of reports based on that.

to create an animated gif, try this (with imagemagick installed)

convert -delay 200 -loop  100 2006-01-31.xymt*.gif anim.gif

@requires: U{Python<http://python.org/>} >= 2.4
@requires: U{epydoc<http://epydoc.sourceforge.net/>} >= 3.0beta1
@requires: U{pyExcelerator<http://pyexcelerator.sourceforge.net/>}
@requires: U{shapely<http://pypi.python.org/pypi/Shapely/>}
@requires: U{pyproj<http://code.google.com/p/pyproj/>}

@author: U{'''+__author__+'''<http://schwehr.org/>}
@version: ''' + __version__ +'''
@copyright: 2007
@var __date__: Date of last svn commit
@undocumented: __version__ __author__ __doc__ parser success
@since: 2007-Apr-21
@status: Intial working version.  Still needs development
@organization: U{CCOM<http://ccom.unh.edu/>}

@license: GPL v2


@todo: Allow the code to pull data from sqlite and postgis
@todo: Optional bounding box or polygon decimation
@todo: Speadup by using a C++ ais decoder
@todo: Try putting a background image in the gnuplot
@todo: Let the user specify the gnuplot plotting range
@todo: Allow user to specify local time zone rather than hard coding the local one configured by the os
@todo: Add GMT output to parallel what I am doing with gnuplot.  Probably better to do it off of a transit db?
@todo: KML... put a ship info popup for the beginning of each track.

@warning: This assumes that ship track data is sorted by time
'''

import sys
import os
import pyExcelerator as excel
from datetime import datetime

from pyproj import Proj
import shapely.geometry

def lon_to_utm_zone(lon):
   return int(( float(lon) + 180 ) / 6) + 1


def detectTransits(inFile, basename, options):
   '''
   @param inFile: open file like object containing data
   @param basename: prepend this str to filenames written
   @param options: FIX... list options

   @todo: detect if the input is AIS VDM or XYMT messages
   '''
   ships={}

   for line in inFile:
       x,y,m,t = line.split()
       if m not in ships:
           ships[m] = [(x,y,t),]
           continue
       ships[m].append((x,y,t))

   # FIX: maybe not the best way to pick UTM zone
   utm_zone = lon_to_utm_zone(x)
   #sys.stderr.write
   print 'utm_zone:',utm_zone
   params = {'proj':'utm','zone':utm_zone}
   proj = Proj(params)

   transitsFile = None
   transitsFilename=basename+'.transits'
   if options.transitData:
      transitsFile = file(transitsFilename,'w') # Points for the transit
   if options.gmtMultiSeg:
      gmtMultiSegFile = file(basename+'.transits.psxy.multiseg','w')

   summaryFile=None
   if options.transitFile:
      summaryFile = file(basename+'.transits.summary.txt','w') # Summary list of transits

   if options.gnuplot:
      gp = file(basename+'.gp','w')
      os.chmod(basename+'.gp',0755)
      gp.write('#!/usr/bin/env gnuplot\n')
      gp.write('\n# Requires gnuplot 4.2 or newer\n')
      gp.write('# Written by ais_transits.py\n\n')
      if options.transitData:
         gp.write('set title "'+basename+' transits plot"\n')
         gp.write('set xlabel "Longitude"\n')
         gp.write('set ylabel "Latitude"\n')
         gp.write('set key off\n')
         gp.write('set grid x\n')
         gp.write('set grid y\n')
         gp.write('\n')
         gp.write('# set yrange [42:43]\n')
         gp.write('# set xrange [-70.75:-69.75]\n')
         gp.write('\n')
         gp.write('set xtics .25\n')
         gp.write('set ytics .25\n')
         gp.write('\n')
         gp.write('\n')
         gp.write('set terminal pdf\n')
         gp.write('set output "'+basename+'.pdf"\n')

         gp.write('plot "'+transitsFilename+'" with l')
         if options.gpFiles:
            for filename in options.gpFiles:
               gp.write(' \\\n  ,"'+filename+'" with l title "'+filename+'"')
         if options.gpPointFiles:
            for filename in options.gpPointFiles:
               gp.write(' \\\n  ,"'+filename+'" with p title "'+filename+'"')
         gp.write('\n')

         gp.write('set terminal gif\n')
         gp.write('set output "'+basename+'.gif"\n')
         gp.write('replot\n')
      gp.write('\n')

   if options.excel:
      workbook = excel.Workbook()
      ws_summary = workbook.add_sheet('Transit Summary')
      ws_summary_row = 0
      ws_transits = workbook.add_sheet('Transits')
      ws_transits_row = 0

      dateTimeStyle = excel.XFStyle()
      dateTimeStyle.num_format_str = 'M/D/YY h:mm:ss'

      ws_summary.write(ws_summary_row,0,'Summary of transits for each ship')
      ws_summary_row += 1

      ws_summary.write(ws_summary_row,0,basename)
      ws_summary_row += 1

      col=0
      ws_summary.write(ws_summary_row,col,'MMSI'); col += 1
      ws_summary.write(ws_summary_row,col,'Num transits'); col += 1
      ws_summary.write(ws_summary_row,col,'Time in region (hours)'); col += 1
      ws_summary.write(ws_summary_row,col,'AIS Position Count'); col += 1
      ws_summary_row += 1


      ws_transits.write(ws_transits_row,0,'Vessel Transits based on AIS data produced by ais_transits.py')
      ws_transits_row += 1

      ws_transits.write(ws_transits_row,0,basename)
      ws_transits_row += 1

      col = 0
      #ws_transits.write(row,col,'Key');col+=1
      ws_transits.write(ws_transits_row,col,'MMSI');col+=1
      ws_transits.write(ws_transits_row,col,'Transit');col+=1
      ws_transits.write(ws_transits_row,col,'Transit_ID');col+=1
      ws_transits.write(ws_transits_row,col,'Start (UTC sec)');col+=1
      ws_transits.write(ws_transits_row,col,'Start (UTC)');col+=1
      ws_transits.write(ws_transits_row,col,'Start (EDT/local)');col+=1
      ws_transits.write(ws_transits_row,col,'End (UTC sec)');col+=1
      ws_transits.write(ws_transits_row,col,'End (UTC)');col+=1
      ws_transits.write(ws_transits_row,col,'End (EDT/local)');col+=1
      ws_transits.write(ws_transits_row,col,'Transit Duration (hours)');col+=1
      ws_transits.write(ws_transits_row,col,'Transit Length (km)');col+=1
      ws_transits.write(ws_transits_row,col,'AIS Position Count');col+=1
      ws_transits_row += 1

   totalTransits=0

   shipList = ships.keys()
   shipList=[int(s) for s in shipList]
   shipList.sort()
   shipList=[str(s) for s in shipList]

   #for ship in ships:
   for ship in shipList:
      shipTransitFile=None
      if options.separateShips: shipTransitFile = file(basename+'.'+ship,'w') # shipTransitFile 

      transits=[]  # List of start_time,end_time,# of points
      start=None # Time the current transit started
      samples=0 # How many samples in the current transit

      shipTransits=1
      t = None
      print ship
      if transitsFile: transitsFile.write('# '+ship+'\n')   
      if options.gmtMultiSeg: gmtMultiSegFile.write('>\n') # This is the segment separator default character
      if options.separateShips: shipTransitFile.write('# '+ship+'\n')   

      max_delta_t = 0  # maximum time between samples

      for pt in ships[ship]:
         x = pt[0]
         y = pt[1]
         newT = int(pt[2])
         #max_delta_t = 0

         if None==start:
            start = newT

         if t != None:
            dt = newT - t
            print dt, max_delta_t
            if dt > max_delta_t:
               #print 'setting!'
               max_delta_t = dt
               #print max_delta_t

            if newT>t+3600:
               shipTransits+=1
               if transitsFile: transitsFile.write('\n\n#Begin transit # '+str(shipTransits)+'\n')
               if options.gmtMultiSeg: gmtMultiSegFile.write('>\n') # This is the segment separator default character
               if options.separateShips: shipTransitFile.write('\n\n#Begin transit # '+str(shipTransits)+'\n')
               transits.append((start,t,samples,max_delta_t))
               samples = 0
               start = newT
         samples += 1
         t = newT

         if transitsFile: transitsFile.write(pt[0]+' '+pt[1]+' '+ship+' '+pt[2]+'\n')
         if options.gmtMultiSeg: gmtMultiSegFile.write(pt[0]+' '+pt[1]+'\n') # This is the segment separator default character
         if options.separateShips: shipTransitFile.write(pt[0]+' '+pt[1]+' '+ship+' '+pt[2]+'\n')

      print 'max_delta_t',max_delta_t
      transits.append((start,t,samples,max_delta_t))  # Catch the last transit

      if options.gnuplot and options.separateShips:
         #gpShip = file(basename+'.'+ship+'.gp','w')
         gp.write('\n######################################################################\n')
         gp.write('# Ship '+ship+'\n')
         gp.write('\n')
         gp.write('set title "Transits for MMSI '+ship+'"\n')
         gp.write('set key on\n')
         gp.write('\n')
         gp.write('set terminal gif\n')
         gp.write('set output "'+basename+'.'+ship+'.gif"\n')

         gp.write('plot "'+basename+'.'+ship+'" with l title "'+ship+'"')
         if options.gpFiles:
            for filename in options.gpFiles:
               gp.write(' \\\n  ,"'+filename+'" with l title "'+filename+'"')
         if options.gpPointFiles:
            for filename in options.gpPointFiles:
               gp.write(' \\\n  ,"'+filename+'" with p title "'+filename+'"')
         gp.write('\n')

         gp.write('\n')
         gp.write('set terminal pdf\n')
         gp.write('set output "'+basename+'.'+ship+'.pdf"\n')
         gp.write('replot\n')

      if options.excel: 
         totalTime = 0  # Track total time by ship in region
         totalSamples =0 # What was the total number of AIS position messages from this ship?
         transitCount=0 # What transit number for THIS ship
         for tr in transits:
            transitCount+=1
            start = tr[0]
            end = tr[1]
            samples = tr[2]
            totalSamples += samples
            dt_start = datetime.utcfromtimestamp(start)
            dt_start_local = datetime.fromtimestamp(start)
            dt_end = datetime.utcfromtimestamp(end)
            dt_end_local = datetime.fromtimestamp(end)
            totalTime += end-start
            col = 0

            print 'transit:',tr

         # Excel does not seem to be able to handle large numbers
            ws_transits.write(ws_transits_row,col,str(ship));col+=1
            ws_transits.write(ws_transits_row,col,transitCount);col+=1
            ws_transits.write(ws_transits_row,col,ship+'_'+str(start));col+=1
            ws_transits.write(ws_transits_row,col,int(start));col+=1
            ws_transits.write(ws_transits_row,col,dt_start,dateTimeStyle);col+=1
            ws_transits.write(ws_transits_row,col,dt_start_local,dateTimeStyle);col+=1
            ws_transits.write(ws_transits_row,col,int(end));col+=1
            ws_transits.write(ws_transits_row,col,dt_end,dateTimeStyle);col+=1
            ws_transits.write(ws_transits_row,col,dt_end_local,dateTimeStyle);col+=1
            ws_transits.write(ws_transits_row,col,(int(end)-int(start))/3600.);col+=1
            ws_transits.write(ws_transits_row,col,samples);col+=1

            ws_transits_row += 1
         col=0
         ws_summary.write(ws_summary_row,col,str(ship)); col += 1
         ws_summary.write(ws_summary_row,col,len(transits)); col += 1
         ws_summary.write(ws_summary_row,col,totalTime/3600.); col += 1
         ws_summary.write(ws_summary_row,col,totalSamples); col += 1
         #ws_summary.write(ws_summary_row,col,); col += 1
         ws_summary_row += 1
         
      #print transits

      if None != summaryFile:
         summaryFile.write(ship+' '+str(shipTransits)+'\n')
      if transitsFile: transitsFile.write('\n\n')
      if shipTransitFile: shipTransitFile.close()

      totalTransits+=shipTransits

  
   if transitsFile: transitsFile.write('#total transits = '+str(totalTransits)+'\n')
   print 'Total transits =',totalTransits
   if options.excel:
      workbook.save(basename+'.xls')
   

######################################################################
# Code that runs when this is this file is executed directly
######################################################################
if __name__ == '__main__':
    from optparse import OptionParser

    parser = OptionParser(usage="%prog [options] [file1] [file2] ...",
                          version="%prog "+__version__+' ('+__date__+')')

    parser.add_option('-b','--basename',dest='basename'
                      ,default=None
                      ,help='Base name to use for all generated products.  '
                      +'Defaults to the filenames')

    parser.add_option('-g','--gnuplot',dest='gnuplot'
                      ,default=False, action='store_true'
                      ,help='Write gnuplot file that will make a million little plots')

    parser.add_option('-G','--additional-gnuplot',dest='gpFiles'
                      ,action='append'
                      ,help='Additional data files to plot in gnuplot')

    parser.add_option('-p','--point-gnuplot',dest='gpPointFiles'
                      ,action='append'
                      ,help='Additional data files to plot in gnuplot as points')

#    parser.add_option('-k','--kml',dest='kml'
#                      ,default=False, action='store_true'
#                      ,help='Create a Google Earth KML report')

    parser.add_option('-e','--excel',dest='excel'
                      ,default=False, action='store_true'
                      ,help='Write out a report to a MS Excel file')

    parser.add_option('-c','--csv',dest='csv'
                      ,default=False, action='store_true'
                      ,help='Write out the report as a comma separated file')

    parser.add_option('-F','--transits-file',dest='transitFile'
                      ,default=False, action='store_true'
                      ,help='Write out a summary/master file will all transits')

    parser.add_option('-f','--transits-data',dest='transitData'
                      ,default=False, action='store_true'
                      ,help='Write out one file with all transits separate by blank lines')

    parser.add_option('-s','--separate-ships',dest='separateShips'
                      ,default=False, action='store_true'
                      ,help='Write out each ship to a separate file with transits separated by blank lines')

    parser.add_option('-n','--keep-nmea',dest='keepNeme'
                      ,default=False, action='store_true'
                      ,help='Cause the ship track files to stay in AIS NMEA format')

    parser.add_option('-t','--transit-time',dest='transitTime'
                      ,default=3600,type='int'
                      ,help='Time in seconds that define a new transit if the ship is not seen [default: %default]')

    parser.add_option('--gmt-multisegment',dest='gmtMultiSeg'
                      ,default=False,action='store_true'
                      ,help='Write a GMT multi segment file for psxy with -M')

    parser.add_option('-v','--verbose',dest='verbose',default=False,action='store_true'
                      ,help='run the tests run in verbose mode')

    (options,args) = parser.parse_args()

    if len(args)==0:
       if options.basename==None:
          options.basename='transit_log'
       detectTransits(sys.stdin, options.basename, options)
    else:
       for filename in args:
          basename=options.basename
          if None==basename:
             basename=filename
          detectTransits(file(filename), basename, options)

    del options
    del args
