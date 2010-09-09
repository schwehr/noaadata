#!/usr/bin/env python

__author__    = 'Kurt Schwehr'
__version__   = '$Revision: 12308 $'.split()[1]
__revision__  = __version__ # For pylint
__date__ = '$Date: 2009-07-22 17:22:17 -0400 (Wed, 22 Jul 2009) $'.split()[1]
__copyright__ = '2010'
__license__   = 'GPL v3'
__contact__   = 'kurt at ccom.unh.edu'

__doc__='''Calculate the distances for received messages.  Stores them
in an sqlite database.  Builds a historgram of receives.  Hoping to
have a spectrogram like view of the data by day.

Trying to do better than ais_nmea_uptime*.py

@requires: U{epydoc<http://epydoc.sourceforge.net/>} > 3.0
@since: 2010-Apr-25
@var __date__: Date of last svn commit
@undocumented: __version__ __author__ __doc__ parser
@status: In progress
'''

import ais
from ais import binary
from aisutils.uscg import uscg_ais_nmea_regex

import ais.binary
import ais
import datetime

from BitVector import BitVector

from optparse import OptionParser
import math
import sqlite3

from pyproj import Proj


import sys, os

def lon_to_utm_zone(lon):
    return int(( lon + 180 ) / 6) + 1


# Good luck if your station moves
station_locations = {
    'r003669945': (-70.7165857810977 , 42.1990684235934),
    'r003669946': (-70.632477 , 42.688824 ),
    'r003669947': (-70.2053363315039 , 42.0740521817588),
    }

class AisError(Exception):
    def __init__(self,msg):
        self.msg = msg
    def __str__(self):
        return 'AisError: ' + self.msg

class AisErrorBadNumBits(AisError):
    def __str__(self):
        return 'AisErrorBadNumBits: ' + self.msg

class AisErrorPositionTooFar(Exception):
    def __init__(self,msg):
        self.msg = msg
    def __str__(self):
        return 'AisErrorPositionTooFar: ' + self.msg


def distance_km_unit_sphere(lat1, long1, lat2, long2):
    return distance_m_unit_sphere(lat1, long1, lat2, long2) / 1000.

def dist (lon1, lat1, lon2, lat2):
    'calculate 2D distance.  Should be good enough for points that are close together'
    dx = (lon1-lon2)
    dy = (lat1-lat2)
    return math.sqrt(dx*dx + dy*dy)

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
    #dx = utm1[0]-utm2[0]
    #dy = utm1[1]-utm2[1]
    #return math.sqrt(dx*dx + dy*dy)


def distance_m_unit_sphere(lat1, long1, lat2, long2):
    'distance in meters between two points assuming unit sphere - very rough!'
    
    # phi = 90 - latitude
    phi1 = math.radians(90.0 - lat1)
    phi2 = math.radians(90.0 - lat2)
        
    # theta = longitude
    theta1 = math.radians(long1)
    theta2 = math.radians(long2)
        
    # Compute spherical distance from spherical coordinates.
    cos = (math.sin(phi1)*math.sin(phi2)*math.cos(theta1 - theta2) + 
           math.cos(phi1)*math.cos(phi2))
    arc = math.acos( cos )

    return arc * 6373000

def build_dist_database(database_filename, log_files, verbose=False):

    cx = sqlite3.connect(database_filename)

    print 'WARNING: not saving the station name'
    cx.execute('''
    CREATE TABLE IF NOT EXISTS distance (
       -- Save space, no key
       -- ts INTEGER, -- Save more space
       julian_day INTEGER,
       -- x REAL,
       -- y REAL,
       dist_km REAL
       --,
       --station VARCHAR(15)
       );
    ''')

    cu = cx.cursor()

    counts = {'nogps': 0}

    for filename in log_files:
        if verbose:
            print 'file:',filename
            sys.stdout.flush()
        for line_num, line in enumerate(file(filename)):
            if 'AIVDM,1,1' not in line: continue
            match = uscg_ais_nmea_regex.search(line).groupdict()
            message_id = match['body'][0] # First letter is the message type
            if message_id not in ('1','2','3'): continue

            if len(match['body']) != 28: # 6 bits per character
                raise AisErrorBadNumBits('expected 168, got %d' % len(match['body']) / 6)

            bits = binary.ais6tobitvec(match['body'][:20]) # Don't need any of the other bits, so do not waste time

            x = binary.signedIntFromBV(bits[61:89]) / 600000.
            y = binary.signedIntFromBV(bits[89:116]) / 600000.

            if x > 180 or y > 90:
                counts['nogps'] += 1
                continue

            station = match['station']
            
            julian_day = int(datetime.datetime.utcfromtimestamp(int(match['timeStamp'])).strftime('%j'))

            d_km =  dist_utm_km( (x,y), station_locations[station] )
            #cu.execute('INSERT INTO distance VALUES (:julian_day, :x, :y, :dist_km, :station)',
                       #{'julian_day': julian_day, 'x':x, 'y':y, 'dist_km': d_km, 'station':station} )
            #cu.execute('INSERT INTO distance VALUES (:julian_day, :x, :y, :dist_km)',
            #           {'julian_day': julian_day, 'x':x, 'y':y, 'dist_km': d_km, } )
            cu.execute('INSERT INTO distance VALUES (:julian_day, :dist_km)',
                       {'julian_day': julian_day, 'dist_km': d_km, } )
            if line_num % 10000 == 9999:
                cx.commit()


        cx.commit()

    if False:
        print 'Creating indexes'
        try:
            cx.execute('CREATE INDEX idx_dist_day ON distance(julian_day);')
            cx.execute('CREATE INDEX idx_dist_dist ON distance(dist_km);')
            #cx.execute('CREATE INDEX idx_dist_station ON distance(station);')
            cx.commit()
        except sqlite3.OperationalError:
            print 'Appears indexes were already created'

    return cx, counts
            
def get_parser():
    import magicdate

    parser = OptionParser(option_class=magicdate.MagicDateOption,
                          usage='%prog [options] file1 [file2] [file3] ...',
                          version='%prog '+__version__)
    
#    parser.add_option('-s', '--start-time', type='magicdate', default=None, help='Force a start time (magicdate) [default: use first timestamp in file]')
#    parser.add_option('-e', '--end-time',   type='magicdate', default=None, help='Force an end  time (magicdate) [default: use last timestamp in file]')

    parser.add_option('-d', '--database-filename', default='distances.db3', help='[ default: %default]')

    #parser.add_option('-b', '--build-database', default=False, action='store_true', help='Without this flag, this will assume there is a prebuild db')
    parser.add_option('-v', '--verbose', default=False, action='store_true', help='Run in chatty mode')
    return parser

class Histogram:
    'build up a histogram on point at a time.  Must know the range and bins needed'
    def __init__(self, min_val, max_val, num_bins):
        self.bins = [0,] * num_bins
        self.min_val = min_val
        self.max_val = max_val
        self.extent = max_val - min_val
        self.bin_size = self.extent / float(num_bins)
        print 'hist:',min_val,max_val, num_bins,self.extent,self.bin_size

    def add_value(self,value):
        assert value >= self.min_val and value <= self.max_val
        bin = int ( math.floor ( (value - self.min_val) / self.bin_size ) )
        #print 'bin:',value,'->',bin
        self.bins[bin] += 1

from numpy import array
import numpy

def main():    
    parser = get_parser()
    (options,args) = parser.parse_args()
    v = options.verbose

    max_dist_km = 200
    num_bins = 40 # 5 km bins

    if len(args) > 0:
        cx, counts = build_dist_database(options.database_filename, args, options.verbose)
        print counts
    else:
        cx = sqlite3.connect(options.database_filename)

    #cx.row_factory = sqlite3.Row # Allow access of fields by name

    days = [row[0] for row in cx.execute('SELECT DISTINCT(julian_day) FROM distance;')]
    print 'days:',days

    histograms = []

    min_bin_val = 999999999
    max_bin_val = -1
    for day in days:
        distances = array( [int(row[0]) for row in cx.execute('SELECT dist_km FROM distance WHERE julian_day=:julian_day AND dist_km<:max_dist_km',
                                                              {'julian_day':day, 'max_dist_km':max_dist_km})] )
        print day,distances.min(),distances.max(), numpy.average(distances)
        hist = Histogram(0,max_dist_km, num_bins)
        for d in distances:
            hist.add_value(d)
        print day, hist.bins
        bins = array(hist.bins)
        min_bin_val = min(min_bin_val,bins.min())
        max_bin_val = max(max_bin_val,bins.max())
        histograms.append(bins)    

    print min_bin_val, max_bin_val
    max_bin_val = math.log(max_bin_val)
    
    o = file('foo.pgm','w')
    o.write('P2\n')
    o.write('%d %d\n' % (num_bins, len(histograms)))
    o.write('255\n')
    for hist in histograms:
        for val in hist:
            if val==0:
                o.write('0 ')
            else:
                o.write('%d ' % int(255 * math.log(val)/max_bin_val))

        o.write('\n')
    

if __name__ == '__main__':
    main()
