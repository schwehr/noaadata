#!/bin/bash

# Update the web page with the latest water level AIS nmea strings.

#    '8638610':'Sewells Point',
#    '8639348':'Money Point',
#    '8638863':'CBBT', 
#    '8632200':'Kiptopeke Beach',
#    '8637689':'Yorktown USCG Training Center'

# Need to have the noaadata package in your python package or installed.

. ~/.bashrc

#echo $0
#pwd
#type -a python

#rm -f 8*.ais
DATE=/sw/bin/gdate # Use gnu date - fink coreutils-default
DUMPWL=`pwd`/scripts/dump_wl.py
date=`$DATE --utc +%Y%m%d-%H%M`
#for station in 8638610 ; do
for station in 8638610 8639348 8638863 8632200 8637689; do
    echo $station
    echo "./make_waterlevel_ais.py -s $station -o $station.ais "
    ./make_waterlevel_ais.py -s $station -o $station.ais 
    str=`cat $station.ais`
    echo "(cd ais && $DUMPWL -T html -o ../$station.html \"$str\")"
    (cd ais && $DUMPWL -T html -o ../$station.html "$str")
    (cd ais && $DUMPWL -o ../$station.txt "$str")
done
echo "# $date utc" > current.ais
cat 8*.ais >> current.ais

# Accumulate past messages
cat current.ais >> log.ais

if [ -z "$SKIP_WEB" ]; then
    echo "Uploading data"
    scp *.ais vislab-ccom.unh.edu:www/ais/waterlevel/live/
    scp [0-9]*.txt vislab-ccom.unh.edu:www/ais/waterlevel/live/txt/
    scp [0-9]*.html vislab-ccom.unh.edu:www/ais/waterlevel/live/html/
fi
echo done.

