#!/usr/bin/env python

# Parses format from Tom Bolmer on the R/V Revelle
# Hackish conversion code by Kurt Schwehr.  05-May-2011.  Consider this public domain code

# Reduce VDO to 1 every 60 VDO messages

import sys

vdo_count = 0

for filename in sys.argv[1:]:
    for line in open(filename):
        line.strip()
        fields = line.split()

        nmea = fields[1]
        if '!AIVDO' not in nmea and '!AIVDM' not in nmea:
            # ignore AIALR and anything else not AIS that comes through
            continue

        if '!AIVDO' in nmea:
            vdo_count += 1
            if vdo_count % 60 != 1:  # Only want 1 msg / minute
                continue

        # Might consider injecting a 'A' channel hear for code that expects a channel

        station = 'rREVELLE'  # should we be introducing a new code "s" for ship?
        ts = fields[0]

        print '%s,%s,%s' % (nmea,station,ts)
    
