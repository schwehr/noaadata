#!/bin/bash

# What ships passed through the Stellwagen bank on this day?

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


#egrep 'r000006099|r003669947|r003669959' $1 | egrep 'AIVDM,1,1,[0-9]?,[AB],[1-3]' > 123.ais

echo "Building names"
for receiver in r000006099 r003669947 r003669959 ; do
    echo $receiver
    grep $receiver $1 | egrep -A 1 'AIVDM,2,1,[0-9]?,[AB],5' | grep -v '\-\-' > $receiver.5.notmerged
    PYTHONPATH=.. ./ais_names.py -o $receiver.names.raw $receiver.5.notmerged
    sort -n -u $receiver.names.raw > $receiver.names
done
cat *.names | sort -n -u > names

PYTHONPATH=.. ./ais_position_in_polygon.py 123.ais -v  > inside.ais

./ais_positions.py -o inside.tracks < inside.ais 

# Get all the ships by mmsi
ship_mmsi=`awk '{print $2}' inside.tracks | sort -u -n`

echo "# ship names and first location" > ship_starts.dat
for ship in $ship_mmsi; do
    echo ship $ship
    loc=`grep " $ship " inside.tracks | head -1 | awk '{print $3,$4}'`
    name=`grep $ship names | awk '{print $2}'`
    echo $loc $name
    echo $loc $name >> ship_starts.dat
done

gnuplot <<EOF
  set terminal gif
  set output 'tracks.gif'
  set title "$1 UTC"
  # set yrange [40.9:42.8]
  # set xrange [-70.75:-68.4]
  # plot 'gsc.dat' with l, 'stellwagen.dat' with l, "inside.tracks" using 3:4
  #plot 'stellwagen.dat' with lp, 'inside.tracks' using 3:4
  plot 'stellwagen.dat' with l, 'inside.tracks' using 3:4
EOF

