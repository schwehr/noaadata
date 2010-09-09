#!/usr/bin/env python
__version__ = '$Revision: 2189 $'.split()[1]
__date__ = '$Date: 2006-05-29 15:40:45 -0400 (Mon, 29 May 2006) $'.split()[1]
__author__ = 'Kurt Schwehr'

# Create a proprietary NTP NMEA status message
# By "proprietary", I simply mean that it is not in the NMEA 4.0 spec
# NOTE: I happily violate the 80 character line limit in NMEA.
# Author: Kurt Schwehr
# Since: 2010-Apr-3
# License: LGPL

# returns "#" when ntp not ready... ntplib.ref_id_to_text(response.ref_id, response.stratum)

import time, datetime, ntplib, re

from nmea_error import NmeaError, NmeaChecksumError

class NmeaNotZnt(Exception): pass

def checksum_str(data):
    end = data.rfind('*')
    if -1 == end:
        end = len(data)
    start=1
    sum = 0
    for c in data[start:end]:
        sum = sum ^ ord(c)
    sum_hex = "%x" % sum
    if len(sum_hex) == 1:
        sum_hex = '0' + sum_hex
    checksum = sum_hex.upper()
    return checksum

def make_float(a_dict, key):
    a_dict[key] = float(a_dict[key])
    
znt_regex_str = r'''[$]P?(?P<talker>[A-Z][A-Z])(?P<nmea_type>ZNT),
(?P<timestamp>\d+([.]\d+)?),
(?P<host>\d{1,3}[.]\d{1,3}[.]\d{1,3}[.]\d{1,3}),
(?P<ref_clock>\d{1,3}[.]\d{1,3}[.]\d{1,3}[.]\d{1,3}),
(?P<stratum>\d+?),
(?P<last_update>\d+([.]\d+)?),
(?P<offset>-?\d+([.]\d+)?),
(?P<precision>-?\d+([.]\d+)?),
(?P<root_delay>-?\d+([.]\d+)?),
(?P<root_dispersion>-?\d+([.]\d+)?)
\*(?P<checksum>[0-9A-F][0-9A-F])
'''
'''
P - Optional proprietary tag.  Would be nice if this became a standard message.
'''

znt_regex = re.compile(znt_regex_str,  re.VERBOSE)

def print_response(response):
    print('Version number : %d' % response.version)
    print('Offset : %f' % response.offset)
    print('Stratum : %s (%d)' % (ntplib.stratum_to_text(response.stratum),
        response.stratum))
    print('Precision : %d' % response.precision)
    print('Root delay : %f ' % response.root_delay)
    print('Root dispersion : %f' % response.root_dispersion)
    print('Delay : %f' % response.delay)
    print('Leap indicator : %s (%d)' % (ntplib.leap_to_text(response.leap), response.leap))
    print('Poll : %d' % response.poll)
    print('Mode : %s (%d)' % (ntplib.mode_to_text(response.mode), response.mode))
    print('Python time: %f, %s' % (time.time(), str(datetime.datetime.utcnow())))
    print('Transmit timestamp : ' + time.ctime(response.tx_time))
    print('Reference timestamp : ' + time.ctime(response.ref_time))
    print('Original timestamp : ' + time.ctime(response.orig_time))
    print('Receive timestamp : ' + time.ctime(response.recv_time))
    print('Destination timestamp : ' + time.ctime(response.dest_time))
    print('Reference clock identifier : ' + ntplib.ref_id_to_text(response.ref_id, response.stratum))

class Znt():
    '''NMEA proprietary NTP status report

    $NTZNT,1270379515.39,17.151.16.23,3,1270378814.66,7.41481781006e-05,-20,0.268142700195,0.0267639160156*33
    $PNTZNT,1270567048.57,127.0.0.1,17.151.16.21,4,1270565749.41,0.000080,-20,0.117325,0.046249*14
    
    Fields:
    timestamp - UNIX UTC timestamp
    host - IP address of the host that this report is about
    ref_clock - remote host that this host is syncronized to
    stratum - how far from the time source
    last_update - how long since this host has heard from its ref clock
    offset -
    precision -
    root_delay -
    root_dispersion -
    '''
    
    def __init__(self, nmea_str=None, talker='NT', hostname='127.0.0.1'):
        if nmea_str is not None:
            self.decode_znt(nmea_str)
            return
        self.get_status(talker=talker, hostname=hostname)

    def get_status(self, talker='NT', hostname='127.0.0.1', flag_proprietary=True):
        '''Query a NTP server to get the status of time

        FIX: I do not like that I save a string into self.params
        '''
        params = {}
        client = ntplib.NTPClient()

        timestamp1 = time.time()
        response = client.request(hostname) #, version=4)
        timestamp2 = time.time()
        if flag_proprietary and talker[0] != 'P':
            talker = 'P' + talker
        params['talker'] = talker
        params['timestamp'] = (timestamp1 + timestamp2) /2.
        params['host'] = hostname # Must be IP4 ip address
        params['ref_clock'] = ntplib.ref_id_to_text(response.ref_id, response.stratum)
        params['stratum'] = response.stratum
        params['last_update'] = response.ref_time
        params['offset'] = '%f' % response.offset
        params['precision'] = response.precision
        params['root_delay'] = '%.6f' % response.root_delay
        params['root_dispersion'] = '%.6f' % response.root_dispersion

        #nmea_str = '${talker}ZNT,{timestamp},{host},{ref_clock},{stratum},{last_update},'
        #nmea_str += '{offset},{precision},{root_delay},{root_dispersion}'
        #nmea_str = nmea_str.format(**params)
        fields = []
        for key in ('timestamp','host','ref_clock','stratum','last_update','offset','precision','root_delay','root_dispersion'):
            fields.append(str(params[key]))
        nmea_str = '$' + talker + 'ZNT,' + ','.join(fields)

        checksum = checksum_str(nmea_str)
        nmea_str += '*' + checksum

        self.nmea_str = nmea_str
        self.params = params

        try:
            match = znt_regex.search(nmea_str).groupdict()
        except:
            print 'results are wrong???'
            print_response(response) 

        return nmea_str

    def decode_znt(self,nmea_str):
        try:
            match = znt_regex.search(nmea_str).groupdict()
        except:
            raise NmeaNotZnt()

        if checksum_str(nmea_str) != match['checksum']:
            raise NmeaChecksumError('checksums missmatch.  Got "%s", expected "%s"'
                                    % (match['checksum'],checksum_str(nmea_str)) )

        match['stratum'] = int(match['stratum'])

        for key in ('timestamp','last_update','offset','precision','root_delay','root_dispersion'):
            make_float(match,key)

        self.params = match
        return match

    def pretty(self):
        lines = ['ZNT - NMEA Proprietary NTP status report\n',]
        for field in ('talker','timestamp','host','ref_clock', 'stratum',
                      'last_update','offset','precision','root_delay','root_dispersion'):
            lines.append(field.rjust(18) +':    ' + str(self.params[field]) )
        return '\n'.join(lines)


class ZntLogger():
    def __init__(self, out_file, enabled=True, max_sec=None, max_cnt=None, always=False,
                 station=None, verbose=False):
        '''Log NTP status to a file like stream.
        @param max_sec: The maximum amount of allowable time before a write
        @param max_count: The maximum number of times called before a write
        @param always: Set to true to always write a message
        @param station: if station is included, use the USCG NMEA station and UNIX UTC time stamp format
        '''
        self.out_file = out_file
        self.max_sec = max_sec
        self.max_cnt = max_cnt
        self.always = always
        self.last_write = time.time()
        self.cnt_since_last = 0
        self.station = station
        self.verbose = verbose

        self.enabled = enabled
        
        assert max_sec or max_cnt or always

    def will_write(self):
        if not self.enabled: return False
        if self.always: return True
        if self.max_sec is not None and (self.max_sec + self.last_write < time.time() ):
            return True
        if self.max_cnt is not None and (self.cnt_since_last >= self.max_cnt ):
            return True
        return False

    def state_str(self):
        if not self.enabled: return 'update: NOT ENABLED'
        if not self.will_write():
            s = 'update: NO write...'
            if self.max_cnt is not None: s += '  remaining_cnt: %d'   % (self.max_cnt - self.cnt_since_last)
            if self.max_sec is not None: s += '  remaining_sec: %.1f' % (self.max_sec - (time.time() - self.last_write) )
            return s
        return 'update: WILL write'
    
    def update(self, force = False):
        'force only works if the system is enabled'
        if not self.enabled: return
        
        if not force and not self.will_write():
            self.cnt_since_last += 1
            return
        
        self.cnt_since_last = 0
        self.last_write = time.time()

        znt_str = Znt().nmea_str
        
        if self.station is not None:
            znt_str += ',%s,%.2f' % (self.station, time.time())

        self.out_file.write(znt_str + '\n')

        if self.verbose:
            print znt_str

def znt_logger_opts(parser):
    parser.add_option('--znt-enable', default=False, action='store_true')
    parser.add_option('--znt-max-sec', type='float',default = 5)
    parser.add_option('--znt-max-cnt', type='int', default=10000)
    parser.add_option('--znt-always', default=False, action='store_true')

    return parser


def main():
    from optparse import OptionParser
    parser = OptionParser(usage="%prog", version="%prog 0.1")
    parser.add_option('-H','--hostname',default='127.0.0.1',
                      help='Host IPv4 address [default: %default]')
    parser.add_option('-v', '--verbose', default=False, action='store_true')
    parser.add_option('--one-shot', default=False, action='store_true')
    parser.add_option('--out-file', default='out.znt')
    parser.add_option('--station', default=None)
    parser.add_option('--delay', type='float', default = 0.5)

    znt_logger_opts(parser)
    
    (options, args) = parser.parse_args()
    #if options.verbose: print options

    if options.one_shot:
        znt = Znt(hostname = options.hostname)
        print znt.nmea_str

        znt2 = Znt(znt.nmea_str)
        if options.verbose:
            print
            print znt2.pretty()

    znt_logger = ZntLogger( file(options.out_file,'w'),
                            enabled = True,  # Just force on in the case of the test program
                            max_sec=options.znt_max_sec,
                            max_cnt=options.znt_max_cnt,
                            always=options.znt_always,
                            station=options.station,
                            verbose=options.verbose)
    while True:
        time.sleep(options.delay)
        znt_logger.update()
        

if __name__ == '__main__':
    main()
