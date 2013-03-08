#!/usr/bin/env python
__author__    = 'Kurt Schwehr'
__version__   = '$Revision: 4799 $'.split()[1]
__revision__  = __version__ # For pylint
__date__ = '$Date: 2006-09-25 11:09:02 -0400 (Mon, 25 Sep 2006) $'.split()[1]
__copyright__ = '2008'
__license__   = 'GPL v3'
__contact__   = 'kurt at ccom.unh.edu'
__deprecated__ = 'what goes here?'

__doc__ ='''
RMC - GPS Position

@undocumented: __doc__
@since: 2009-Jan-06
@status: under development
@organization: U{CCOM<http://ccom.unh.edu/>} 

@todo: FIX!!! turn this something useful
@todo: Document the field names
@todo: What is 'N' for the mode?  Got it from the SR162G? N must be for no lock
'''

import re

rawstr = r'''^[$!](?P<prefix>[A-Z][A-Z])(?P<msg_type>RMC)
,(?P<hour>\d\d)(?P<minute>\d\d)(?P<second>\d\d\.\d\d)
,(?P<status>[A-Z])
,(?P<latitude>(?P<lat_deg>\d\d)(?P<lat_min>\d\d*.\d*))
,(?P<north_south>[NS])
,(?P<longitude>(?P<lon_deg>\d\d\d)(?P<lon_min>\d\d.\d*))
,(?P<east_west>[EW])
,(?P<speed_knots>\d*.\d*)
,(?P<course_degrees>\d*.\d*)
,(?P<day>\d\d)(?P<month>\d\d)(?P<year>\d\d)
,(?P<magnetic_variation_degrees>\d*.\d*)
,(?P<mag_var_east_west>[EW])
(,(?P<mode>[ADEN]))?
(?P<checksum>[*][0-9A-F][0-9A-F])'''
#
#matchstr = '$GPRMC,121437.60,A,4212.0258,N,07040.9543,W,18.08,94.6,011008,15.1,W,A*34,rrvauk-sr162g,1222863277.98'
#
matchstr = '$GPRMC,173011.82,V,4222.8770,N,07103.0096,W,0.00,0.0,151008,14.9,W,N*27'

# FIX: what is the N mode?

compile_obj = re.compile(rawstr,  re.VERBOSE)
match_obj = compile_obj.search(matchstr)

print 'prefix     ', match_obj.group('prefix')
print 'msg_type   ', match_obj.group('msg_type')
print 'hour       ', match_obj.group('hour')
print 'minute     ', match_obj.group('minute')
print 'second     ', match_obj.group('second')
print 'status     ', match_obj.group('status')
print 'latitude   ', match_obj.group('latitude')
print 'lat_deg    ', match_obj.group('lat_deg')
print 'lat_min    ', match_obj.group('lat_min')
print 'north_south', match_obj.group('north_south')
print 'longitude  ', match_obj.group('longitude')
print 'lon_deg    ', match_obj.group('lon_deg')
print 'lon_min    ', match_obj.group('lon_min')
print 'east_west  ', match_obj.group('east_west')
print 'speed_knots', match_obj.group('speed_knots')
print 'course_degrees', match_obj.group('course_degrees')
print 'day        ', match_obj.group('day')
print 'month      ', match_obj.group('month')
print 'year       ', match_obj.group('year')
print 'magnetic_variation_degrees', match_obj.group('magnetic_variation_degrees')
print 'mag_var_east_west', match_obj.group('mag_var_east_west')
print 'mode       ', match_obj.group('mode')
print 'checksum   ', match_obj.group('checksum')

def lonlat(match):

    lon_deg = match_obj.group('lon_deg').lstrip('0')
    if len(lon_deg)==0: lon_deg = 0
    else: lon_deg = int(lon_deg)

    lon_min = match_obj.group('lon_min').lstrip('0')
    if len(lon_min)==0: lon_min = 0
    else: lon_min = float(lon_min)

    lon = lon_deg + lon_min/60.

    if 'W' == match_obj.group('east_west'):
        lon = -lon


    lat_deg = match_obj.group('lat_deg').lstrip('0')
    if len(lat_deg)==0: lat_deg = 0
    else: lat_deg = int(lat_deg)

    lat_min = match_obj.group('lat_min').lstrip('0')
    if len(lat_min)==0: lat_min = 0
    else: lat_min = float(lat_min)

    lat = lat_deg + lat_min/60.

    if 'S' == match_obj.group('north_south'):
        lat = -lat


    return lon,lat


    
print lonlat(match_obj)    
