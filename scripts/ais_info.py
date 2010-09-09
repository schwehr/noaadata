#!/usr/bin/env python

__author__    = 'Kurt Schwehr'
__version__   = '$Revision: 12308 $'.split()[1]
__revision__  = __version__ # For pylint
__date__ = '$Date: 2009-07-22 17:22:17 -0400 (Wed, 22 Jul 2009) $'.split()[1]
__copyright__ = '2010'
__license__   = 'GPL v3'
__contact__   = 'kurt at ccom.unh.edu'

__doc__=''' Summarize AIS traffic.  Calculate distances of receives.
Time ranges, gaps, etc.  To calculate per receiver stats or per day,
you will need run this per day log file.  Times must be monotonically
increasing, sorry.

Trying to do better than ais_nmea_uptime*.py

@requires: U{epydoc<http://epydoc.sourceforge.net/>} > 3.0
@since: 2010-Mar-26
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
#from numpy import array

import sys, os

day_sec = 24*60*60.
'seconds in a day'

def get_sec_to_end_of_day(timestamp):
    'For a unix timestamp, how many seconds until the end of the day?'
    d1 = datetime.datetime.utcfromtimestamp(timestamp)
    d2 = datetime.datetime(year=d1.year,month=d1.month, day=d1.day, hour=23, minute=59, second=59)
    delta = d2 - d1
    return delta.seconds

def date_generator(start_date, end_date):
    cur_date = start_date
    dt = datetime.timedelta(days=1)
    while cur_date < end_date:
        yield cur_date
        cur_date += dt

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

class Histogram:
    'build up a histogram on point at a time.  Must know the range and bins needed'
    def __init__(self, min_val, max_val, num_bins):
        self.bins = [0,] * num_bins
        self.min_val = min_val
        self.max_val = max_val
        self.extent = max_val - min_val
        self.bin_size = self.extent / float(num_bins)
        print 'hist:',min_val,max_val, num_bins,self.extent,self.bin_size

    def add_point(self,value):
        assert value >= self.min_val and value <= self.max_val
        bin = int ( math.floor ( (value - self.min_val) / self.bin_size ) )
        #print 'bin:',value,'->',bin
        self.bins[bin] += 1
        
class  Uptime:
    'Calculated as downtime and then flipped.  Questionable which way makes more sense to calculate things'
    def __init__(self, min_gap_sec=2, min_gap_neg_sec=-1, dt_raw_filename=None, verbose=True):
        '''
        WARNING/FIX: assumes times are integer seconds
        
        @param min_gap_sec: minimum number of seconds to consider offline
        @param dt_raw_file: filename to write dt or None for no file.'''
        self.min_gap_sec = min_gap_sec
        print 'Uptime min_gap_sec:',min_gap_sec
        self.min_gap_neg_sec = min_gap_neg_sec
        self.verbose = verbose
        if verbose: print 'min_gap_sec:',min_gap_sec
        self.gap_counts_raw={} # Count all dt, even 0 and 1 sec
        self.gap_counts={}  # Positive only
        self.gap_counts_neg={}
        self.old_sec = None	# Only monotonic increasing?
        self.old_sec_raw = None # To track negative dt's from the USCG
        self.min_sec = None
        self.max_sec = None
        if dt_raw_filename is not None:
            self.dt_raw_file = file(dt_raw_filename,'w')
        self.time_count = 0

        self.tot_by_julian_yrday = {}  # Track downtime by year & julian day


    def set_start_time(self, timestamp):
        self.min_sec = self.max_sec = self.old_sec = self.old_sec_raw = timestamp
        
    def set_end_time(self, timestamp):
        'like add_time, but does not imply the system was working'
        julian_yrday = int(datetime.datetime.utcfromtimestamp(self.max_sec).strftime('%Y%j'))

        if self.max_sec >= timestamp: return # no updating needed

        dt = timestamp - self.max_sec
        #print 'end_dt:',dt, dt/day_sec, dt - day_sec, 'from',datetime.datetime.utcfromtimestamp(self.max_sec)

        dt_first = get_sec_to_end_of_day(self.max_sec)
        dt_rest  = dt - dt_first # This is what we add on to the next day

        if dt >= self.min_gap_sec:
            self.gap_counts[dt] = (1 if dt not in self.gap_counts     else self.gap_counts[dt] + 1)
        self.gap_counts_raw[dt] = (1 if dt not in self.gap_counts_raw else self.gap_counts_raw[dt] + 1)

        if dt >= self.min_gap_sec:
            self.tot_by_julian_yrday[julian_yrday]   = (dt_first if julian_yrday   not in self.tot_by_julian_yrday else self.tot_by_julian_yrday[julian_yrday  ] + dt_first)
            self.tot_by_julian_yrday[julian_yrday+1] = (dt_rest  if julian_yrday+1 not in self.tot_by_julian_yrday else self.tot_by_julian_yrday[julian_yrday+1] + dt_rest)

        self.max_sec = timestamp
         

    def add_time(self,timestamp):
        '''@param timestamp: UNIX UTC timestamp
        The timestamps had better be monotonic increasing!
        '''
        timestamp = int(timestamp) # Force rounding
        self.time_count += 1
        if self.time_count % 1000000 == 0:
            sys.stderr.write('line: %d M\n' % (self.time_count / 1000000) )

        # Monotonic assumption... but that does not really work with the uscg!
        #assert self.max_sec is None or self.max_sec <= timestamp
        if self.verbose and self.max_sec is not None and self.max_sec > timestamp:
            print 'WARNING: Non-monotonic timestamp'
            print '  ',self.max_sec,'>',timestamp,'    ',timestamp - self.max_sec, '\t\t',datetime.datetime.utcfromtimestamp(timestamp)

        if self.min_sec is None: self.min_sec = timestamp
        self.max_sec = timestamp

        # Track all time going backwards ... USCG
        if self.old_sec_raw == None:
            self.old_sec_raw = timestamp
        else:
            dt_raw = timestamp - self.old_sec_raw
            if self.dt_raw_file is not None:
                self.dt_raw_file.write('%d %d %d\n' % (timestamp, self.time_count, dt_raw))
            if dt_raw <= self.min_gap_neg_sec:
                if self.verbose:
                    print 'neg_gap:',dt_raw,timestamp,self.old_sec_raw,'\t',datetime.datetime.utcfromtimestamp(timestamp)
                if dt_raw not in self.gap_counts_neg:
                    self.gap_counts_neg[dt_raw] = 1
                else:
                    self.gap_counts_neg[dt_raw] += 1
            self.old_sec_raw = timestamp
            
        if self.old_sec == None:
            self.old_sec = timestamp
            return
            
        dt = timestamp - self.old_sec
        self.gap_counts_raw[dt] = (1 if dt not in self.gap_counts_raw else self.gap_counts_raw[dt] + 1)

        #
        # If the delta time is too small, stop here
        #

        if dt < self.min_gap_sec:
            self.old_sec = timestamp
            return
            
        if dt not in self.gap_counts:
            self.gap_counts[dt] = 1
        else:
            self.gap_counts[dt] += 1

        d = datetime.datetime.utcfromtimestamp(self.old_sec)
        d2 = datetime.datetime.utcfromtimestamp(timestamp)
        julian_yrday = int(d.strftime('%Y%j'))


        if d.day == d2.day:
            #print '+++++++ ', julian_yrday, dt, self.min_gap_sec
            if julian_yrday not in self.tot_by_julian_yrday:
                self.tot_by_julian_yrday[julian_yrday] = dt
            else:
                self.tot_by_julian_yrday[julian_yrday] += dt
        else:
            # Must partition between the end of the first day and the rest.
            dt_first = get_sec_to_end_of_day(self.old_sec)
            dt_rest  = dt - dt_first
            #print 'partitioning across day boundaries:',dt_first,dt_rest
            cur_day = (dt_first if julian_yrday   not in self.tot_by_julian_yrday else self.tot_by_julian_yrday[julian_yrday  ] + dt_first)
            nxt_day = (dt_rest  if julian_yrday+1 not in self.tot_by_julian_yrday else self.tot_by_julian_yrday[julian_yrday+1] + dt_rest)
            #print '======== tot_by_julian_yrday updates:',cur_day,nxt_day
            self.tot_by_julian_yrday[julian_yrday]   = cur_day
            self.tot_by_julian_yrday[julian_yrday+1] = nxt_day
            
        if self.verbose and abs(dt) > 30:
            print 'gap>30:',dt,'at',timestamp,'\t', datetime.datetime.utcfromtimestamp(timestamp)

        self.old_sec = timestamp
            
    def total_gap(self,min_gap_for_total=5*60):
        tot = 0
        for key in self.gap_counts:
            if key < min_gap_for_total:
                continue
            tot += key * self.gap_counts[key]
        tot_neg = 0
        for key in self.gap_counts_neg:
            tot_neg += key * self.gap_counts_neg[key]

        return tot, tot_neg

#    def total_gap_yrday(self):
    def up_time(self):
        '''Return a list of days and the % time uptime for that day... convert downtime to uptime to not confuse people.
        Works only on a per day basis.
        '''

        #print 'final self.tot_by_julian_yrday:',self.tot_by_julian_yrday
        keys = self.tot_by_julian_yrday.keys()
        keys.sort()

        start_date = datetime.datetime.utcfromtimestamp(self.min_sec)
        end_date   = datetime.datetime.utcfromtimestamp(self.max_sec)

        results = []
        carry_over = 0
        #print 'date_range:',start_date,end_date
        for a_date in date_generator(start_date,end_date):
            key = int(a_date.strftime('%Y%j'))
            try:
                current = self.tot_by_julian_yrday[key] + carry_over
                #print 'self.tot_by_julian_yrday[key]:',self.tot_by_julian_yrday[key]
                #carry_over = 0
            except:
                current = carry_over

            #print 'current:',a_date,current,'s  ','%.2f' % (current/day_sec),'days  carry_over',carry_over

            if current > day_sec:
                results.append((key,0)) # No uptime
                carry_over = current - day_sec
                if self.verbose: print 'carry_over:', a_date, key, 100, carry_over, '%.2f' % (carry_over / day_sec)
                continue
            
            carry_over = 0
            uptime =  100 - (100 * current / day_sec)  # Flip it to uptime
            results.append((key,uptime))
            #print 'no_carry_over:',a_date, key, r

        return results


def distance_km_unit_sphere(lat1, long1, lat2, long2):
    return distance_m_unit_sphere(lat1, long1, lat2, long2) / 1000.

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

class BoundingBox:
    def __init__(self, ):
        '''@param station_location: the lon, lat of the receiver
        @param max_dist_km: threshold beyond with to just drop points as bad'''
        self.x_min = None
        self.x_max = None
        self.y_min = None
        self.y_max = None

    def add_point(self,x,y):
        if self.x_min == None or self.x_min > x: self.x_min = x
        if self.x_max == None or self.x_max < x: self.x_max = x
        if self.y_min == None or self.y_min > y: self.y_min = y
        if self.y_max == None or self.y_max < y: self.y_max = y
        #print x,y,'->', str(self)
        

    def __str__(self):
        return 'bounding_box: x %.4f to %.4f  y %.4f to %.4f' % (self.x_min,self.x_max, self.y_min, self.y_max)

class AisPositionStats:
    def __init__(self, station_location = None, max_dist_km = 500):
        self.positions = []
        self.bbox = BoundingBox()
        self.station_location = station_location
        self.max_dist_km = max_dist_km
        self.dist_hist = Histogram(0,500,50) # in km


        # Counts of packets
        self.count_no_gps = 0
        self.count_bad_pos = 0
        self.count_bad_num_bits = 0
        
    def add_message(self, ais_msg_dict, bits):
        '''Takes a USCG message dict pulled with the regex and a bit vector
        FIX... optionally ingest class b messages
        '''
        #match = uscg_ais_nmea_regex.search(line).groupdict()
        message_id = ais_msg_dict['body'][0] # First letter is the message type
        if message_id in ('1','2','3'):
            if len(bits) != 168:
                print 'bad_bit_count_for_pos:',len(bits)
                self.count_bad_num_bits += 1
                raise AisErrorBadNumBits('expected 168, got 54')
                #return
            
            x = lon = binary.signedIntFromBV(bits[61:89]) / 600000.
            y = lat = binary.signedIntFromBV(bits[89:116]) / 600000.

            #
            # Check for bad messages
            #
            if lon > 180 or lat > 90:
                self.count_no_gps += 1
                return

            if self.station_location is not None:
                dist = distance_km_unit_sphere(x,y,self.station_location[0], self.station_location[1])
                #print 'dist:', dist
                if self.max_dist_km < dist:
                    #print 'bbox_dropping_point:',x,y,dist,'km'
                    self.count_bad_pos += 1
                    raise AisErrorPositionTooFar('%.2f %.2f -> %.2f km' % (x,y,dist))
                    #return 

                self.dist_hist.add_point(dist)

            self.positions.append((lon,lat))
            self.bbox.add_point(lon,lat)
            

    def __str__(self):
        return 'hi'

class AisStreamInfo:
    def __init__(self, station_location = None, max_dist_km = 500,
                 dt_raw_filename=None, min_gap_sec = 2, verbose=False):
        # intialize all counts to 0 for major numbers
        #print 'AisStreamInfo min_gap_sec:',min_gap_sec
        self.msgs_counts = dict([(val,0) for val in ais.binary.encode])
        self.up = Uptime(dt_raw_filename = dt_raw_filename,
                         min_gap_sec=min_gap_sec, verbose=verbose)
        if station_location is not None:
            self.pos_stats = AisPositionStats(station_location, max_dist_km)
        else:
            self.pos_stats = AisPositionStats()
        

    def add_file(self, filename):
        for line_num, line in enumerate(file(filename)):
            if len(line) < 10 or line[0] == '#':
                continue
            line = line.rstrip()
            #if line_num > 100:
            #    break
            #if line_num % 5000 == 0:
            #    print '%s: line %d' % (filename,line_num)
            try:
                timestamp = float(line.split(',')[-1])
            except:
                sys.stderr.write('skipping line: %s\n' % (line, ) )
                continue
            
            self.up.add_time(timestamp)

            if False:

                match = uscg_ais_nmea_regex.search(line).groupdict()
                if match['senNum'] != '1':
                    #print 'skipping senNum',match['senNum'],line.strip()
                    continue # later sentences in an un-normalized stream
                bits = binary.ais6tobitvec(match['body'])

                try:
                    self.pos_stats.add_message(match, bits)
                except AisErrorPositionTooFar, e:
                    print 'ERROR: too far', str(e)
                    print '  Line:', line.rstrip()
                    continue
                except AisErrorBadNumBits, e:
                    print 'ERROR: bad bit count', str(e)
                    print '  Line:', line.rstrip()
                    continue

        #print self.pos_stats.positions
        #print str(self.pos_stats.bbox)
        
def get_parser():
    import magicdate

    parser = OptionParser(option_class=magicdate.MagicDateOption,
                          usage='%prog [options] file1 [file2] [file3] ...',
                          version='%prog '+__version__)
    
    parser.add_option('--min-gap-sec', default=60*6, type='int', help='Suggest 21 seconds for a busy area with a basestation [default: %default]')
    parser.add_option('-s', '--start-time', type='magicdate', default=None, help='Force a start time (magicdate) [default: use first timestamp in file]')
    parser.add_option('-e', '--end-time',   type='magicdate', default=None, help='Force an end  time (magicdate) [default: use last timestamp in file]')
    parser.add_option('--gap-file', default=None, help='base file name to store gap file [ default: %default ]')

    parser.add_option('--up-time-file', default=None, help='Where to write the uptime per day [default: file1.uptime]')
    parser.add_option('-v', '--verbose', default=False, action='store_true', help='Run in chatty mode')
    
    return parser

import calendar
def datetime2unixtimestamp(a_datetime):
    if not isinstance(a_datetime, datetime.datetime):
        #print 'converting... date to datetime'
        a_datetime = datetime.datetime(a_datetime.year, a_datetime.month, a_datetime.day)
    #print 'timetuple:',datetime.datetime.utctimetuple(a_datetime)
    return calendar.timegm(datetime.datetime.utctimetuple(a_datetime))


def main():    
    parser = get_parser()
    (options,args) = parser.parse_args()
    v = options.verbose
    print 'options.min_gap_sec',options.min_gap_sec
    info = AisStreamInfo(station_location = (-70.7165857810977,42.1990684235934),
                         dt_raw_filename='dt.dat',
                         min_gap_sec=options.min_gap_sec,
                         verbose = v)

    print 'forced_time_range:',options.start_time,options.end_time
    if options.start_time is not None:
        #print
        #print type(options.start_time)
        # FIX: is this really the right way to handle setting the range?
        ts = datetime2unixtimestamp(options.start_time)
        if v: print 'setting_start_time:',options.start_time,ts
        info.up.set_start_time(ts)
        #print
        
    for file_num, filename in enumerate(args):
        if v: print 'processing_file:', file_num, filename
        info.add_file(filename)

    if options.end_time is not None:
        #print
        ts = datetime2unixtimestamp(options.end_time)
        if v: print 'setting_end_time:',options.end_time,datetime.datetime.utcfromtimestamp(ts)
        info.up.set_end_time(ts)
        #print

    if True:
        assert info.up.min_sec is not None
        assert info.up.max_sec is not None

        start_str = datetime.datetime.utcfromtimestamp(info.up.min_sec).strftime('%Y-%m-%dT%H:%M')
        end_str   = datetime.datetime.utcfromtimestamp(info.up.max_sec).strftime('%Y-%m-%dT%H:%M')
        print 'time_range:', info.up.min_sec, info.up.max_sec, '(UNIX UTC seconds)  ->  ' , start_str, ' to ',end_str

        dt_sec = info.up.max_sec - info.up.min_sec
        print 'time_length:', dt_sec,'(s) or ', dt_sec / 60.,'(m) or',dt_sec / 3600.,'(h) or ', dt_sec / 3600. / 24., '(d)'
        tot_gap_sec, tot_gap_neg_sec = info.up.total_gap(options.min_gap_sec)
        print 'total_gap_time: (dt=%d)' % options.min_gap_sec, tot_gap_sec, '(s) or ', '%.2f' % (tot_gap_sec / day_sec), '(d)'
        print 'total_gap_neg_time: (dt=%d)' % options.min_gap_sec, tot_gap_neg_sec, '(s) or ', '%.2f' % (tot_gap_neg_sec / day_sec), '(d)'

        #print (dt_sec - tot_gap_sec), dt_sec
        print 'uptime: %.2f (days) => %.2f%%' % (
            ( (dt_sec - tot_gap_sec) / day_sec ),
            ( 100* (dt_sec - tot_gap_sec) / float(dt_sec)  ),
            )

        if options.gap_file is not None:
            o = file(options.gap_file + '-gap.dat','w')
            o.write('# gap_len_sec count_of_gaps gap_len_as_decimal_days gap_len_as_decimal_hours gap_len_as_decimal_minutes\n')
            o.write('# pwd="%s"\n' % (os.getcwd(),))
            if len(args)>0:
                o.write('# first_file=%s\n' % (args[0],))
                o.write('#  last_file=%s\n' % (args[-1],))
            keys = info.up.gap_counts_raw.keys()
            keys.sort()
            for gap_len_sec in keys:
                count = info.up.gap_counts_raw[gap_len_sec]
                o.write('%d %d %.2f %.2f %.2f\n' % (gap_len_sec,count, gap_len_sec/day_sec, gap_len_sec/3600., gap_len_sec/60.))
            o.close()


        if options.up_time_file is None:
            if len(args) == 0:
                options.up_time_file = 'somedata.uptime'
            else:
                options.up_time_file = args[0]+'.uptime'
        o = file(options.up_time_file,'w')

        uptime = info.up.up_time()
        for entry in uptime:
            jday = str(entry[0])[4:].lstrip('0').rjust(3)
            o.write('%s %6.2f\n' % (jday,entry[1]) )

            
    if False:
        print 'count_no_gps:',info.pos_stats.count_no_gps
        print 'count_bad_pos:',info.pos_stats.count_bad_pos
        print 'count_bad_bad_num_bits:',info.pos_stats.count_bad_num_bits
    
        o = file('dist_hist.dat','w')
        for bin in info.pos_stats.dist_hist.bins:
            o.write('%d\n' % bin)

if __name__ == '__main__':
    main()
