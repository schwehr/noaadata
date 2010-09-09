#!/usr/bin/env python

# Since 2010-Apr-22

# Try to decimate messages for ships

import math
from pyproj import Proj
import sqlite3
import datetime

import pytz
EST = pytz.timezone('EST')

def dist (lon1, lat1, lon2, lat2):
    'calculate 2D distance.  Should be good enough for points that are close together'
    dx = (lon1-lon2)
    dy = (lat1-lat2)
    return math.sqrt(dx*dx + dy*dy)

def lon_to_utm_zone(lon):
    return int(( lon + 180 ) / 6) + 1

def dist_utm_km (p1, p2):
    return dist_utm_m (p1[0],p1[1], p2[0],p2[1]) / 1000.

def dist_utm_m (lon1, lat1, lon2, lat2):
    'calculate 2D distance.  Should be good enough for points that are close together'
    zone = lon_to_utm_zone( (lon1 + lon2 ) / 2.) # Just don't cross the dateline!
    params = {'proj':'utm', 'zone':zone}
    proj = Proj(params)

    utm1 = proj(lon1,lat1)
    utm2 = proj(lon2,lat2)

    return dist(utm1[0],utm1[1],utm2[0],utm2[1])


class Decimate:
    def __init__(self,min_dist_m=200, min_time_s=600):
        '''min_dist: meters till we must emit
        min_time: 
        '''
        self.ship_status = {} # indexed by MMSI
        self.min_dist_m = min_dist_m
        self.min_time_s = min_time_s

    def add_pos(self,mmsi,x,y,timestamp):
        '''
        mmsi - ship ID number
        x - longitude
        y - latitude (decimal degrees)
        Return true if position should be emitted.  False, if redunant
        '''
        if mmsi not in self.ship_status:
            self.ship_status[mmsi] = {'x':x,'y':y, 'timestamp': timestamp}
            return True
        
        last = self.ship_status[mmsi]

        dt = timestamp - last['timestamp']
        if dt >= self.min_time_s:
            self.ship_status= {'x':x,'y':y, 'timestamp': timestamp}
            return True
        
        dist_m = dist_utm_m(x,y, last['x'], last['y'])
        if dist_m >= self.min_dist_m:
            self.ship_status= {'x':x,'y':y, 'timestamp': timestamp}
            return True

        return False

class Bbox:

    def __init__(self,x_min=None,y_min=None,x_max=None,y_max=None):
        self.bounds=(x_min,y_min,x_max,y_max)
    def is_inside(self,x,y):
        if self.bounds[0] is not None and self.bounds[0] > x: return False
        if self.bounds[2] is not None and self.bounds[2] < x: return False

        if self.bounds[1] is not None and self.bounds[1] > y: return False
        if self.bounds[3] is not None and self.bounds[3] < y: return False
        return True

    def is_outside(self,x,y):
        return not self.is_inside(x,y)
    

def main():
    from optparse import OptionParser
    parser = OptionParser(usage="%prog [options]")
    parser.add_option('-f','--database-file',default='ais.db3'
                      ,help='Name of the sqlite3 database file to write [default: %default]')

    parser.add_option('-t','--delta-time-sec', default=60*10, type='int', help='Time in seconds before requiring a report [default: %default (sec) ]')
    parser.add_option('-d','--delta-dist-m', default=200, type='int', help='Distant travel before requiring a report [default: %default (m) ]')


    parser.add_option('-x','--x-min', default=None,type='float', help='Geographic range (-180..180) [default: %default]')
    parser.add_option('-X','--X-max', default=None, type='float', help='Geographic range (-180..180) [default: %default]')

    parser.add_option('-y','--y-min', default=None, type='float', help='Geographic range (-90..90) [default: %default]')
    parser.add_option('-Y','--Y-max', default=None, type='float', help='Geographic range (-90..90) [default: %default]')
    parser.add_option('-m','--mmsi', default=None, type='int', help='Specify just one ship  [default: all ships]')

    parser.add_option('-v','--verbose', default=False, action='store_true', help='Make the test output verbose')

    (options,args) = parser.parse_args()
    verbose = options.verbose

    bbox = Bbox(options.x_min, options.y_min, options.X_max, options.Y_max)

    cx = sqlite3.connect(options.database_file)
    cx.row_factory = sqlite3.Row # Allow access of fields by name

    if options.mmsi is None:
        mmsi_list = [ row['userid'] for row in cx.execute('SELECT distinct(userid) FROM position;') ]
    else:
        mmsi_list = (options.mmsi,)
    print 'mmsi_list:',mmsi_list


    for mmsi in mmsi_list:

        decimate = Decimate(min_dist_m=options.delta_dist_m, min_time_s=options.delta_time_sec)
        if verbose: print 'Decimate options: %d m  and %d sec' % (options.delta_dist_m, options.delta_time_sec)
        keep_cnt = 0
        toss_cnt = 0
        outside_cnt = 0
        
        xymt = file(str(mmsi)+'.xymt','w')
        csv = file(str(mmsi)+'.csv','w')
        csv.write('mmsi,x,y,date/time UTC,date/time EST\n')
        
        print 'mmsi:',mmsi
        for row_num, row in enumerate (cx.execute('SELECT userid,longitude,latitude,cg_sec FROM position WHERE userid=%d AND latitude<90 ORDER by cg_sec;' % mmsi) ):
            if options.verbose and row_num % 10000 == 0: print row_num
            #print dict(row)
            x = float(row['longitude'])
            y = float(row['latitude'])
            if bbox.is_outside(x,y):
                outside_cnt += 1
                continue
            keep = decimate.add_pos(367314640, x, y, int(row['cg_sec']))
            if keep:
                keep_cnt += 1
                row = dict(row)
                #print row
                xymt.write('{longitude} {latitude} {UserID} {cg_sec}\n'.format(**row))
                d = datetime.datetime.utcfromtimestamp(row['cg_sec'])
                
                d_with_tz = datetime.datetime(d.year,d.month,d.day,d.hour,d.second, tzinfo=pytz.utc)
                d_est = d_with_tz.astimezone(EST)
                
                csv.write('{mmsi},{x},{y},{d},{d_est}\n'.format(mmsi=row['UserID'], x=x, y=y, d=d.strftime('%Y/%d/%m %H:%M:%S'), d_est=d_est.strftime('%Y/%d/%m %H:%M:%S')))
                #pass
            else:
                toss_cnt += 1

        print 'keep_cnt: ',keep_cnt
        print 'toss_cnt: ',toss_cnt
        print 'outside_cnt: ',outside_cnt


if __name__ == '__main__':
    main()
