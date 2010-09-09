#!/bin/bash

# Process one day of USCG AIS data... focused on just that stations that the stellwagen bank cares about

# r003669947 - NOAA/Cape Cod
# r000006099 - Volpe Center
# To be determined - NOAA/Cape Ann

# We also use Fisher Island East (r003669959)

if [ $# != 1 ]; then
    echo "ERROR: must specify 1 argument the N-AIS log file:"
    echo "  $0 filefile"
    echo
    echo "Note: The filename must conform to 'foo-bar-YYYY-MM-DD' for proper date extraction"
    echo
    echo "For example:"
    echo "  $0 uscg-logs-2007-01-01"
    exit $EXIT_FAILURE
fi

filename=$1
day=`echo $filename | cut -d '-' -f 3,4,5`

# First decimation of the data
#egrep '^[$!]AIVDM,2,[12],[0-9]?,[AB],[^*]*[0-9A-F][0-9A-F],[a-zA-Z0-9,]*(r003669947|r000006099|r003669959)' 
egrep '^[$!]AIVDM,2,[12],[0-9]?,[AB],' $filename | egrep 'r003669947|r000006099|r003669959' > 1.tmp

for station in r000006099 r003669947 r003669959; do
    echo Processing station: $station
    rm -f $station-5.tmp $station-5.csv
    grep $station 1.tmp | egrep -A 1 '^[$!]AIVDM,2,1,[0-9]?,[AB],5' > $station-5.tmp
    ./merge5.py $station-5.tmp | sort -nu > $station-5.csv
done

cat r003669947-5.csv r000006099-5.csv r003669959-5.csv | sort -u > vessels-$day.csv

rm -f *.tmp
