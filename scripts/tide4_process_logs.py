#!/usr/bin/env python
__author__    = 'Kurt Schwehr'
__version__   = '$Revision: 12383 $'.split()[1]
__revision__  = __version__ # For pylint
__date__ = '$Date: 2009-08-03 09:41:06 -0400 (Mon, 03 Aug 2009) $'.split()[1]
__copyright__ = '2009'
__license__   = 'GPL v3'
__contact__   = 'kurt@ccom.unh.edu'

__doc__ ='''
Try to process the tide data for summer hydro 2009.  Don't trust this code!

@requires: U{Python<http://python.org/>} >= 2.4
@requires: U{epydoc<http://epydoc.sourceforge.net/>} >= 3.0.1

@undocumented: __doc__
@since: 2009-Jun-09
@status: under development
@organization: U{CCOM<http://ccom.unh.edu/>} 

@todo: verify this whole deal
@todo: check the time zones
@todo: get gyre to ntp rather than windows time service
@see: internal ccom wiki on tide4 at Star Island
'''

import re
import sys
import glob
import datetime
import calendar # To get unix utc seconds

# Fix make date and time separate so the column numbers can be auto generated
output_names=['seconds', 'datetime', 'station', 'voltage', 'pressure', 'waterlevel','temp_aand', 'temp_seabird', 'cond_sm_seabird', 'date_aand', 'date_seabird']
output_format = ' '.join(['{'+name+'}' for name in output_names])+'\n'

#header = '\n'.join(['# %d: %s' % (i+1,name) for i,name in enumerate(output_names)])
header='''# 1: seconds
# 2: date
# 3: time
# 4: station
# 5: voltage
# 6: pressure
# 7: waterlevel
# 8: temp_aand
# 9: temp_seabird
# 10: cond_sm_seabird
# 11: date_aand
# 12: date_aand
# 13: date_seabird
# 14: date_seabird'''


print output_format
print header


test_str='''Date/Time:  9.06.09 15:04:08
00 Battery Voltage        10.2  Volt 
01 Reference              76    77   
02 Water level             2.46 m    
03 Water temperature       7.84 Deg.C
04 Pressure               11.74 kPa  
# 12.5633, 3.60414, 09 Jun 2009, 15:10:47'''


aanderraa_date_regex_str = r'''Date/Time:\s+(?P<datetime>\d{1,2}.\d{1,2}.\d{1,2}\s+\d{1,2}:\d{1,2}:\d{1,2})'''
aanderraa_date_strptime = '%y.%m.%d %H:%M:%S' # !@#$!!!! this won't work directly either.  damn this is lame
#aanderraa_date_strptime = '%d.%m.%y %H:%M:%S' # This tide station is really lame for not using 4 digit years
aanderraa_battery_regex_str = r'''(?P<entry_num>\d\d)\s+Battery\s+Voltage\s+(?P<voltage>\d+(\.\d*)?)\s+(?P<units>Volt)'''
aanderraa_reference_regex_str = r'''(?P<entry_num>\d\d)\s+Reference\s+(?P<r1>\d+)\s+(?P<r2>\d+)'''
aanderraa_waterlevel_regex_str = r'''(?P<entry_num>\d\d)\s+Water\s+level\s+(?P<water_level>\d*(\.\d*))\s+(?P<units>[a-z]+)'''
aanderraa_watertemp_regex_str = r'''(?P<entry_num>\d\d)\s+Water\s+temperature\s+(?P<water_temp>\d*(\.\d*))\s+(?P<units>[.A-Za-z]+)'''
aanderraa_waterpressure_regex_str = r'''(?P<entry_num>\d\d)\s+Pressure\s+(?P<water_pressure>\d*(\.\d*))\s+(?P<units>[.A-Za-z]+)'''
seabird_ct_date_strptime = '%d %b %Y, %H:%M:%S'
seabird_ct_regex_str = r'''\#\s+
(?P<temp_c>\d+(\.\d*)?),\s+
(?P<conducitivity_sm>\d+(\.\d*)?),\s+
(?P<datetime>\d{1,2}\s+\w+\s+\d{2,4},\s+ \d{1,2}:\d{1,2}:\d{1,2})'''

regex_dict = {
    'aand_date':re.compile(aanderraa_date_regex_str, re.VERBOSE),
    'aand_bat':re.compile(aanderraa_battery_regex_str, re.VERBOSE),
    'aand_ref':re.compile(aanderraa_reference_regex_str, re.VERBOSE),
    'aand_lvl':re.compile(aanderraa_waterlevel_regex_str, re.VERBOSE),
    'aand_tmp':re.compile(aanderraa_watertemp_regex_str, re.VERBOSE),
    'aand_prs':re.compile(aanderraa_waterpressure_regex_str, re.VERBOSE),
    'seabird_ct':re.compile(seabird_ct_regex_str, re.VERBOSE),
}
'''
regular expressions to match against the tide station reports
'''

if __name__=='__main__':
    from optparse import OptionParser
    parser = OptionParser(usage="%prog [options]",
                          version="%prog "+__version__+' ('+__date__+')')
    (options, args) = parser.parse_args()
    v = options.verbose

    misses = 0


    #year = 2009
    #julian_day = 160

    o = file('tide4-%d-d%03d.dat' % (year,julian_day), 'w')
    o.write('# Do not trust this data until you have verified it yourself.  Watch for timezone issue.\n')
    o.write('# Waterlevel is from the Aanderaa and is not corrected for salinity.\n')
    o.write('# Tide 4 data for Julian day %d on year %d\n\n' % (year,julian_day))
    o.write(header)
    o.write('\n')

    for filename in glob.glob('*.C03'):
        matches = []

        for line in file(filename):
            for key in regex_dict:
                match = regex_dict[key].search(line)
                if match is not None:
                    break
            if match is None:
                if len(line) > 4:
                    print 'No_match_for_line: "%s"' % (line.strip(),)
                misses += 1
                continue
            match = match.groupdict()
            matches.append((key,match))

        # FIX: remove
        if len(matches)<5:
            continue
            
        # filename is JJJSSSSS where J is julian day number and S is seconds since midnight
        print filename, filename[3:].lstrip('0')
        julianday = int(filename[:3].lstrip('0'))
        daysec_str = filename[3:].lstrip('0').split('.')[0]
        if daysec_str == '':
            daysec = 0
        else:
            daysec = int(daysec_str)

        hour = daysec / 3600
        print 'hour:',daysec,'->',hour

        basedate = datetime.datetime.strptime('2009 %d %d:0:0' % (julianday,hour), '%Y %j %H:%M:%S')
        
        # first time found in the file for the waterlevel system
        startdate = None
        for i in range(len(matches)):
            if matches[i][0] == 'aand_date':
                #print matches[i][1]['datestr']
                #print aanderraa_date_strptime
                startdate = datetime.datetime.strptime(matches[i][1]['datetime'],aanderraa_date_strptime)
                break

        if startdate == None:
            o.write ('# File has no aanderaa timestamps: %s\n' % filename)
            continue # This file is empty

        print 'daysec:',daysec
        print 'hour:',hour
        print 'filename:',filename
        print 'basedate:',basedate
        print 'startdate:',startdate
        dt = basedate - startdate
        print 'delta time:',dt, basedate,startdate

        #print
        #print
        #print

        cur_match = {}
        for i in range(len(matches)):
            if matches[i][0] == 'aand_date':
                curdate = datetime.datetime.strptime(matches[i][1]['datetime'],aanderraa_date_strptime) 
                #print curdate,'->', curdate+dt
                actual_curdate = curdate+dt
                cur_match={'datetime':actual_curdate}
                cur_match['aand_date'] = matches[i][1]
                continue

            if matches[i][0] in ('aand_bat','aand_ref','aand_lvl','aand_tmp','aand_prs','seabird_ct'):
                cur_match[matches[i][0]] = matches[i][1]

            if len(cur_match)==8:
                #print 'found_complete:', actual_curdate
                m = cur_match
                t = m['datetime'] # FIX: what time zone is this timestamp in?
                o.write(output_format.format(
                        seconds=calendar.timegm((t.year,t.month,t.day,t.hour,t.minute,t.second)),
                        datetime = t,
                        station = m['aand_ref']['r1'],
                        voltage = m['aand_bat']['voltage'],
                        pressure = m['aand_prs']['water_pressure'],
                        waterlevel = m['aand_lvl']['water_level'],
                        temp_aand = m['aand_tmp']['water_temp'],
                        temp_seabird = m['seabird_ct']['temp_c'],
                        cond_sm_seabird = m['seabird_ct']['conducitivity_sm'],
                        date_aand = datetime.datetime.strptime(m['aand_date']['datetime'],aanderraa_date_strptime),
                        date_seabird = datetime.datetime.strptime(m['seabird_ct']['datetime'],seabird_ct_date_strptime),
                        ))
                cur_match={}

        #print misses
        #print matches
