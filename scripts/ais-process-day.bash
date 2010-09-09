#!/bin/bash

# Process one day of USCG AIS data.

# Get a list of mmsi and name pairs

#today=`date +%Y%m%d-%H%M`

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
echo Processing day $day ...

rm -rf $day

# -v
./ais_uscg_splitstations.py -s $day -S $filename

ls -1 $day > $day/.stations
mv $day/.stations $day/stations

########################################
# Split out some of the message types.  
########################################

# Should ok to group nmea strings by message now that each station is separate.

#if false; then
if true; then
    for file in $day/*/log.ais; do
	echo $file
	grep -A 1 ',[AB],5' $file | grep -v '\-\-' | egrep 'VD[MO]' > $file.5
	egrep ',[AB],[123]' $file | egrep 'VD[MO]' > $file.123
	#./ais_positions.py $file.123 > $file.123.positions
	./ais_names.py $file.5 | sort -un > $file.5.names
    done
    sort -un $day/*/log.ais.5.names > $day/ships-seen
else
    echo "Skipping ship names by station"
fi

# Make a list of all ships for the day

egrep ',[AB],[123]' $filename | egrep 'VD[MO]' > $day/log.ais.123

# Use -m 100 to avoid ships at anchor from cluttering the world
echo Getting ship positions ...
./ais_positions.py $day/log.ais.123 -m 50 > $day/positions
