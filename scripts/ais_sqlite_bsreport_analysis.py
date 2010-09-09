#!/usr/bin/env python

__author__    = 'Kurt Schwehr'
__version__   = '$Revision: 4799 $'.split()[1]
__revision__  = __version__ # For pylint
__date__ = '$Date: 2006-09-25 11:09:02 -0400 (Mon, 25 Sep 2006) $'.split()[1]
__copyright__ = '2009'
__license__   = 'GPL v3'
__contact__   = 'kurt at ccom.unh.edu'
__deprecated__ = 'what goes here?'

__doc__ ='''
Do an analysis of bs reports from an sqlite db.

@requires: U{Python<http://python.org/>} >= 2.5
@requires: U{epydoc<http://epydoc.sourceforge.net/>} >= 3.0.1
@requires: U{psycopg2<http://initd.org/projects/psycopg2/>} >= 2.0.6

@undocumented: __doc__
@since: 2009-Jun-09
@status: under development
@organization: U{CCOM<http://ccom.unh.edu/>} 
'''

import sqlite3
import datetime
import calendar # to make a unix utc timestamp

def main():
    '''
    FIX: document main
    '''
    from optparse import OptionParser
    parser = OptionParser(usage="%prog [options]",
                          version="%prog "+__version__+' ('+__date__+')')
    parser.add_option('-d','--database-file',dest='database_file',default='ais.db3',
                      help='Name of the python file to write [default: %default]')
    parser.add_option('-v', '--verbose', dest='verbose', default=False, action='store_true',
                      help='run the tests run in verbose mode')

    (options, args) = parser.parse_args()
    v = options.verbose

    cx = sqlite3.connect(options.database_file)
    cx.row_factory = sqlite3.Row 

    bs_list = [row['userid'] for row in cx.execute('SELECT DISTINCT(userid) FROM bsreport;')]

    print 'Total stations:',len(bs_list)
    o = file('bs_locations.xym','w')
    for bs in bs_list:
        x = []
        y = []
        for row in cx.execute('SELECT Position_longitude as lon, Position_latitude as lat FROM bsreport WHERE userid=:userid', {'userid':bs}):
            if row['lon'] > 180 or row['lat'] > 90:
                continue
            x.append(float(row['lon']))
            y.append(float(row['lat']))
        if len(x) < 10:
            continue
        x = sum(x) / len(x)
        y = sum(y) / len(y)
        print x,y,bs
        o.write('%f %f %s\n' % (x,y,str(bs)))


    
    if 1:

      dt_bs_uscg = []
      for row in cx.execute('SELECT * FROM bsreport;'):
        bsreport = dict(row)
        if row['Time_year'] == 0:
            continue
#        print 
#        for item in bsreport:
#            print '  ',item,bsreport[item]
        bs_time = datetime.datetime(row['Time_year'],row['Time_month'],row['Time_day'],
                                    row['Time_hour'],row['Time_min'],row['Time_sec']
                                    )
        cg_timestamp = datetime.datetime.utcfromtimestamp(row['cg_sec'])

        #get unix utc timestamp from datetime
        bs_sec = calendar.timegm((bs_time.year,bs_time.month,bs_time.day,
                                        bs_time.hour,bs_time.minute,bs_time.second))
        #print bs_time, cg_timestamp
        dt =  row['cg_sec'] - bs_sec
        print dt
        #if dt
        

######################################################################
# Code that runs when this is this file is executed directly
######################################################################
if __name__ == '__main__':
    main()
