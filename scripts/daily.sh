#!/bin/bash

for file in ../u*20[0-9][0-9]-08-??.bz2; do 
#for file in 20[0-9][0-9]-??-??; do 
    basename=`basename $file`
    basename=${basename%%.bz2}
    basename=${basename##uscg-nais-dl1-}
    echo $basename

    tmp=$basename.norm

    bzcat $file | ais_normalize.py > $tmp

    ##ais_nmea_info.py $tmp > $basename.nmea_info

    # Lookback:  125 stations * 1000 messages = 125000
    ##egrep 'AIVDM,1,1,[0-9]?,[AB],5' $tmp  > $basename.5
    egrep 'AIVDM,1,1,[0-9]?,[AB],5' $tmp | ais_nmea_remove_dups.py -v -l 100000 > $basename.5.unique

    #rm $tmp
done