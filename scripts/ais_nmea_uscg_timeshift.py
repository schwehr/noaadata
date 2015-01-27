#!/usr/bin/env python
"""Calculate the within minute slew of the USCG timestamp compared to
the extended "T" time within the minute.  I hope this comes from the
receiver GPS time and not from AISLogger.  Actually, this just shows
that they all move together.  I thought that this was done by the
receiver, but no, it appears to be done by the java logging code.
"""

import datetime
import sys

import ais.ais_msg_1_handcoded as ais_msg_1
import ais.ais_msg_4_handcoded as ais_msg_4

from aisutils.uscg import uscg_ais_nmea_regex
from aisutils import binary


print '* emacs org-mode table'

print '#+ATTR_HTML: border="1" rules="all" frame="all"'
print '|USCG datetime| cg s | dt cg s | T | dT  | t | S | slot t |',
print 'msg slot num | msg slot t|msg hour| msg min | msg sec | MMSI |'

all_keys = set()
cg_s_prev = None
time_of_arrival_prev = None
for line in file(sys.argv[1]):
    line = line.rstrip()
    if len(line) < 5 or 'AIVDM' not in line:
        continue
    match = uscg_ais_nmea_regex.search(line).groupdict()

    cg_s = float(match['timeStamp'])
    uscg = datetime.datetime.utcfromtimestamp(float(match['timeStamp']))
    if cg_s_prev is not None:
        dt = cg_s - cg_s_prev
        dt = '%5d' % dt
    else:
        dt = 'N/A'.rjust(5)
    cg_s_prev = cg_s

    try:
        time_of_arrival = float(match['time_of_arrival'])
    except:
        time_of_arrival = None

    if time_of_arrival is None:
        dt_time_of_arrival = 'N/A'.rjust(8)
    else:
        if time_of_arrival_prev is not None:
            dt_time_of_arrival = time_of_arrival - time_of_arrival_prev
            dt_time_of_arrival = '%8.4f' % dt_time_of_arrival
        else:
            dt_time_of_arrival = 'N/A'.rjust(8)
        time_of_arrival_prev = time_of_arrival

    try:
        slot_num = int(match['slot'])
        slot_t = slot_num / 2250. * 60
        slot_t = '%5.2f' % slot_t
    except:
        slot_num = 'N/A'
        slot_t = 'N/A'


    print '|',uscg,'|',cg_s,'|',dt,'|',time_of_arrival,'|', dt_time_of_arrival,'|', match['t_recver_hhmmss'], '|',slot_num, '|',slot_t , '|',

    if match['body'][0] in ('1','2','3'):
        bits = binary.ais6tobitvec(match['body'])
        msg = ais_msg_1.decode(bits)
        #print msg.keys()
        #all_keys.update(set(msg.keys()))
        msg_slot = 'N/A'
        if 'slot_number' not in msg:
            msg['slot_number'] = 'N/A'
            msg['slot_time'] = 'N/A'
        else:
            msg['slot_time'] = msg['slot_number'] / 2250. * 60
        if 'commstate_utc_hour' not in msg:
            msg['commstate_utc_hour'] = msg['commstate_utc_min'] = 'N/A'

        print '{slot_number}|{slot_time}|{commstate_utc_hour}|{commstate_utc_min}|{TimeStamp}|{UserID}|'.format(**msg)
    elif match['body'][0] == '4':
        bits = binary.ais6tobitvec(match['body'])
        msg = ais_msg_4.decode(bits)
        all_keys.update(set(msg.keys()))
        #print msg

        msg_slot = 'N/A'
        if 'slot_number' not in msg:
            msg['slot_number'] = 'N/A'
            msg['slot_time'] = 'N/A'
        else:
            msg['slot_time'] = msg['slot_number'] / 2250. * 60

        #print '|',uscg,'|',cg_s,'|',dt,'|',time_of_arrival,'|', dt_time_of_arrival,'|', match['t_recver_hhmmss'], '|',slot_num, '|','%5.2f' % slot_t , '|',
        print '{slot_number}|{slot_time}|{Time_hour}|{Time_min}|{Time_sec}| b{UserID}|'.format(**msg)
    else:
        print '|'*6
        pass



#print all_keys
