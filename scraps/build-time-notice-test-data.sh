#!/bin/bash

# Kurt Schwehr
# $Id: build-time-notice-test-data.sh 8869 2008-03-05 15:01:04Z schwehr $

# requires GNU date

# 9260m = 5 nautical miles
radius=9260
mmsi=338040883
date --utc +'%Y%m%d-%H%M %Z'
mon=`date --utc +'%-m'`
day=`date --utc +'%-d'`
hour=`date --utc +'%-H'`
min=`date --utc +'%-M'`
echo $mon-$day $hour:$min
echo

ab2_lon=-70.566316
ab2_lat=42.340320

ab3_lon=-70.454336
ab3_lat=42.333248


echo " *** AB 2 - No Whale ***"
echo 

cmd="../ais/timed_circular_notice.py  --encode \
--UserID=$mmsi \
--mon=$mon --day=$day --hour=$hour --min=$min \
--longitude=$ab2_lon \
--latitude=$ab2_lat \
--timetoexpire=0 \
--radius=$radius \
--areatype=0 \
"

echo $cmd
echo 

$cmd --type=nmea > tmp.ais

echo -n "USCG NMEA: "
$cmd --type=nmea

echo -n "NMEA payload: "
$cmd --type=nmeapayload

echo -n "binary: "
$cmd --type=binary

echo
echo "Decode what was just created:"
../ais/timed_circular_notice.py --decode "`cat tmp.ais`"

#rm tmp.ais
echo
echo " ----------------------"
echo " --- Wait 3 minutes ---"
echo " ----------------------"
sleep 180
echo

date --utc +'%Y%m%d-%H%M %Z'
mon=`date --utc +'%-m'`
day=`date --utc +'%-d'`
hour=`date --utc +'%-H'`
min=`date --utc +'%-M'`
echo $mon-$day $hour:$min


echo
echo

echo " *** AB 2 - No Whale  - 3 minutes later - update that still nothing heard *** "
echo 

cmd="../ais/timed_circular_notice.py  --encode \
--UserID=$mmsi \
--mon=$mon --day=$day --hour=$hour --min=$min \
--longitude=$ab2_lon \
--latitude=$ab2_lat \
--timetoexpire=0 \
--radius=$radius \
--areatype=0 \
"
echo $cmd
echo 


$cmd --type=nmea > tmp.ais

echo -n "USCG NMEA: "
$cmd --type=nmea

echo -n "NMEA payload: "
$cmd --type=nmeapayload

echo -n "binary: "
$cmd --type=binary

echo
echo "Decode what was just created:"
../ais/timed_circular_notice.py --decode "`cat tmp.ais`"


echo
echo

echo " *** AB 3 - Whale - expires in 24 hours aka 1440 minutes *** "
echo 

cmd="../ais/timed_circular_notice.py  --encode \
--UserID=$mmsi \
--mon=$mon --day=$day --hour=$hour --min=$min \
--longitude=$ab3_lon \
--latitude=$ab3_lat \
--timetoexpire=1440 \
--radius=$radius \
--areatype=0 \
"
echo $cmd
echo 


$cmd --type=nmea > tmp.ais

echo -n "USCG NMEA: "
$cmd --type=nmea

echo -n "NMEA payload: "
$cmd --type=nmeapayload

echo -n "binary: "
$cmd --type=binary

echo
echo "Decode what was just created:"
../ais/timed_circular_notice.py --decode "`cat tmp.ais`"

