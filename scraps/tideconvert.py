#!/usr/bin/env python
__author__    = 'Kurt Schwehr'
__version__   = '$Revision: 9833 $'.split()[1]
__revision__  = __version__ # For pylint
__date__ = '$Date: 2008-07-03 22:21:26 -0400 (Thu, 03 Jul 2008) $'.split()[1]
__copyright__ = '2008'
__license__   = 'GPL v3'
__contact__   = 'kurt at ccom.unh.edu'
__doc__ ='''
Process the data for summer Hydro 2008.

Comes in this format on tide2.schwehr.org in ~data/data/tide/tide-memma-2008-MM-DD

# START LOGGING UTC seconds since the epoch: 1213488002.45
# SPEED:       9600
# PORT:        /dev/ttyS0
# TIMEOUT:     300.0
# STATIONID:   memma
# DAEMON MODE: True
635  711  427,rmemma,1213488014.57
635  711  427,rmemma,1213488026.7
635  711  427,rmemma,1213488038.83
635  712  427,rmemma,1213488050.95
635  712  426,rmemma,1213488063.08
635  712  426,rmemma,1213488075.21
635  712  426,rmemma,1213488087.33
63

Caris seems to want...

----------- FORT POINT , NH:  8423898 -----------
--------------------- 8423898.tid ---------------------
--------------------- Time Zone:  UTC  ---------------------

--------------------- Invariant Fields ---------------------
Name             Type Size    Units Value
------------------------------------------------------------
station_id       CHAR    8     8423898
station_name     CHAR    15    FORT POINT , NH
data_product     CHAR    10   UNVERIFIED
start_time       INTG    4   seconds 2007/06/01 00:00:00
end_time         INTG    4   seconds 2007/06/11 19:30:00
file_date        INTG    4   seconds 2007/06/11 20:10:53
max_water_level  REAL    4   metres 03.21
min_water_level  REAL    4   metres -00.31
------------------------------------------------------------

---------------------- Variant Fields ----------------------
Name             Type Size    Units
------------------------------------------------------------
time             INTG    4   seconds
water_level      REAL    4   metres
std_dev          REAL    4   metres
------------------------------------------------------------

2007/06/01 00:00:00    1.18   0.008
2007/06/01 00:06:00    1.23   0.007
2007/06/01 00:12:00    1.28   0.007
2007/06/01 00:18:00    1.34   0.009
2007/06/01 00:24:00    1.41   0.009
2007/06/01 00:30:00    1.48   0.009
2007/06/01 00:36:00    1.55   0.010
2007/06/01 00:42:00    1.62   0.008

@see: http://pypi.python.org/pypi/tappy/ Is tappy useful for CCOM?
'''
import time
import datetime
import os
import sys

timeFmts = {
    'caris':'%Y/%m/%d %H:%M:%S'
    ,'matlab':'%Y\t%m\t%d\t%H\t%M\t%S\t'
}
timeTypes=timeFmts.keys()

# Coefficients for water level in meters
A=-1.008E-01
B=5.125E-03
C=7.402E-08
D=0

#os.system ('date')
#os.system ('date -u')
#now = time.time()
#datetime.datetime.utcfromtimestamp(now)


def processFile(infile,out,d,g=9.80665,stdDev=None, timeshift=0
                ,timeFormat=timeFmts['caris']
                ,datumOffset=0):
    '''
    @param d: water density in grams per cubic centimeters
    @param datumOffset: meters above the sensor for datum 0 level
    @param stddev: what the heck? 
    @param timeFormat: strftime \% format string
    '''

    #if stdDev is not float: 
    if stdDev is None: 
        #print 'coverting',stdDev
        stdDev = '0.000'
        #print 'after',stdDev
    elif type(stdDev) is float:
        #print 'before',stdDev
        stdDev = ('%0.3f' % stdDev)
        #print 'after',stdDev

    for line in infile:
        if '#' == line[0]: continue
        try:
            fields,station,timestamp = line.split(',')
        except:
            sys.stderr.write('bad line: '+line.strip()+'\n')
            sys.stderr.write('continuing...\n')
            continue

        timestamp = float(timestamp)
        if timeshift != 0:
            #print 'shifting from ',timestamp
            timestamp = timestamp+timeshift
            #print 'shifting to ',timestamp

        dTime = datetime.datetime.utcfromtimestamp(timestamp)
        timeStr = dTime.strftime(timeFormat)
        #timeStr = dTime.strftime('%Y/%m/%d %H:%M:%S') # caris
        # This is what Val has for matlab
        #timeStr = dTime.strftime('%Y\t%m\t%d\t%H\t%M\t%S\t')

        # N is raw pressure value
        try:
            stationId,N,rawTemp = fields.split()
            N = float(N)
        except:
            sys.stderr.write('bad line2: '+line.strip()+'\n')
            sys.stderr.write('continuing...\n')
            continue

        # water Level(m)=((A+BN+CN^2+DN^3)/d*g))
        
        waterlevel = A + B*N + C*(N**2.) + D*(N**3.)
        waterlevel = (waterlevel / d) * g 
        waterlevel -= datumOffset
        #print waterlevel, d*g, d, g
        #print waterlevel

        resultStr = timeStr+'    '+('%0.2f' % waterlevel)+'   ' + str(stdDev)
        out.write(resultStr+'\n')

def main():
    '''
    FIX: document main
    '''
    from optparse import OptionParser
    parser = OptionParser(usage="%prog [options] tide files",
                          version="%prog "+__version__+' ('+__date__+')')

    parser.add_option('-d','--density', dest='density', default=1.026
                      ,type='float'
                      ,help='density of water in grams per cubic centimeters.  [default: %default]')

    parser.add_option('-g','--gravity',dest='gravity', default = 9.80665, type='float'
                      ,help='gravity.  You probably do not want to change this [default: %default]')

    parser.add_option('-s','--stddev',dest='stddev', default = 0.010, type='float'
                      ,help='stddev fill in value.  This does not seem right [default: %default]')

    parser.add_option('-o','--output-file', dest='outFilename', default=None, 
                      help='What filename to write to [default: %default - stdout if None]')

    parser.add_option('-t','--timeshift', dest='timeshift', default=0
                      ,type='float'
                      ,help='in seconds.  You will need to shift time for data from 2008-06-15 and older by +/- 45 seconds [default: %default]')

    parser.add_option('-v', '--verbose', dest='verbose', default=False, action='store_true',
                      help='run the tests run in verbose mode')

    parser.add_option('-f','--format-time'
                      ,dest='timeFormat'
                      ,type='choice'
                      ,default='caris'
                      ,choices=timeTypes
                      ,help= 'One of ' + ', '.join(timeFmts)+ ' [default: %default] ')
    parser.add_option('-D','--datum-offset'
                      ,dest='datumOffset'
                      ,type='float'
                      ,default=0
                      ,help= 'Distance from the sensor up to the datum offset in meters (negative is below the sensor) [default: %default] ')


    (options, args) = parser.parse_args()

    out = sys.stdout
    if options.outFilename:
        out = file(options.outFilename,'a')

    sys.stderr.write( 'using density: %s\n' % options.density)
    sys.stderr.write( 'using gravity: %s\n' % options.gravity)

    for filename in args:
        processFile(file(filename),out
                    ,d=options.density
                    ,g=options.gravity
                    ,stdDev=options.stddev
                    ,timeshift=options.timeshift
                    ,timeFormat=timeFmts[options.timeFormat]
                    ,datumOffset=options.datumOffset)


######################################################################
# Code that runs when this is this file is executed directly
######################################################################
if __name__ == '__main__':
    main()
    sys.stderr.write ('all done converting\n')
