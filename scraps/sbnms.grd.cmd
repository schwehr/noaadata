#! /bin/csh -f
#
# Shellscript to create Postscript plot of data in grd file
# Created by macro mbm_grdplot
#
# This shellscript created by following command line:
# mbm_grdplot -Isbnms.grd -R-71/-69.75/41.75/43 -T
#
# Define shell variables used in this script:

#set mon=01
#set monName=Jan
set mon=$1
set monName=$2

echo "Processing ** $mon - $monName **"

set PDF_FILE         = 2006${mon}-transits.pdf
set PNG_FILE         = 2006${mon}-transits.png
set PS_FILE         = 2006${mon}-transits.ps
#set PS_FILE         = sbnms.grd.ps
set CPT_FILE        = sbnms.grd.cpt
set MAP_PROJECTION  = m
#set MAP_SCALE       = 4.4486
set MAP_SCALE       = 2.5
##set MAP_REGION      = -71/-69.75/41.75/43
# SBNMS regions...
##set MAP_REGION      = -71/-69.75/42/42:52

# Great South Channel (GSC)
set MAP_REGION      = -70.25/-68.00/40.75/42.5

set X_OFFSET        = 1.4697
set Y_OFFSET        = 2
#
# Save existing GMT defaults
echo Saving GMT defaults...
gmtdefaults -L > gmtdefaults$$
#
# Set new GMT defaults
echo Setting new GMT defaults...
gmtset MEASURE_UNIT inch
gmtset PAPER_MEDIA archA+
gmtset ANOT_FONT Helvetica
gmtset LABEL_FONT Helvetica
gmtset HEADER_FONT Helvetica
gmtset ANOT_FONT_SIZE 8
gmtset LABEL_FONT_SIZE 8
gmtset HEADER_FONT_SIZE 10
gmtset FRAME_WIDTH 0.075
gmtset TICK_LENGTH 0.075
gmtset PAGE_ORIENTATION LANDSCAPE
gmtset COLOR_BACKGROUND 0/0/0
gmtset COLOR_FOREGROUND 255/255/255
gmtset COLOR_NAN 255/255/255
gmtset PLOT_DEGREE_FORMAT ddd:mm
#
# Make color pallette table file
echo Making color pallette table file...
echo   -300  37  57 175   -270  40 127 251 > $CPT_FILE
echo   -270  40 127 251   -240  50 190 255 >> $CPT_FILE
echo   -240  50 190 255   -210 106 235 255 >> $CPT_FILE
echo   -210 106 235 255   -180 138 236 174 >> $CPT_FILE
echo   -180 138 236 174   -150 205 255 162 >> $CPT_FILE
echo   -150 205 255 162   -120 240 236 121 >> $CPT_FILE
echo   -120 240 236 121    -90 255 189  87 >> $CPT_FILE
echo    -90 255 189  87    -60 255 161  68 >> $CPT_FILE
echo    -60 255 161  68    -30 255 186 133 >> $CPT_FILE
echo    -30 255 186 133      0 255 255 255 >> $CPT_FILE
#
# Define data files to be plotted:
#set DATA_FILE        = sbnms.grd
#set DATA_FILE        = gom-bathy-coastalrelief-3sec.grd

# Coastal relief model 3sec from http://www.ngdc.noaa.gov/mgg/coastal/coastal.html
set DATA_FILE        = gsc-coastrel-71-67-40-43.grd

set INTENSITY_FILE   = 
#
# Make color image
echo Running grdimage...
grdimage $DATA_FILE -J$MAP_PROJECTION$MAP_SCALE \
	-R$MAP_REGION -C$CPT_FILE \
	-P -X$X_OFFSET -Y$Y_OFFSET -K -V >! $PS_FILE


# grdimage $DATA_FILE -J$MAP_PROJECTION$MAP_SCALE \
# 	-R$MAP_REGION -C$CPT_FILE \
# 	-P -X$X_OFFSET -Y$Y_OFFSET -K -V >! $PS_FILE

#
# Make coastline data plot
echo Running pscoast...
pscoast \
	-J$MAP_PROJECTION$MAP_SCALE \
	-R$MAP_REGION \
	-Df \
	-G200 \
	-W1p \
	-P -K -O -V >> $PS_FILE

psxy \
	-Wthicker,red \
	gsc.dat \
	-J$MAP_PROJECTION$MAP_SCALE \
	-R$MAP_REGION \
	-K -O -V >> $PS_FILE

psxy \
	-Wthick,red \
	gsc.tss.dat \
	-J$MAP_PROJECTION$MAP_SCALE \
	-R$MAP_REGION \
	-K -O -V >> $PS_FILE

#        -W3
psxy \
	-Wthicker,red \
	stellwagen.dat \
	-J$MAP_PROJECTION$MAP_SCALE \
	-R$MAP_REGION \
	-K -O -V >> $PS_FILE

psxy \
	-Wthin,red \
	stellwagen-5nm.dat \
	-J$MAP_PROJECTION$MAP_SCALE \
	-R$MAP_REGION \
	-K -O -V >> $PS_FILE

#	stellwagen-5nm.dat stellwagen.dat \
#01.xymt.transits.psxy.multiseg
#200602-transits.transits.psxy.multiseg

psxy \
	2006${mon}-transits.transits.psxy.multiseg -M \
	-J$MAP_PROJECTION$MAP_SCALE \
	-R$MAP_REGION \
	-K -O -V >> $PS_FILE


#	sbnms-buoys-maru.dat -Sa \

psxy \
	maru-xy.dat -Sd \
	stellwagen-5nm.dat stellwagen.dat \
	-J$MAP_PROJECTION$MAP_SCALE \
	-R$MAP_REGION \
	-K -O -V >> $PS_FILE

psxy \
 	-Wthickest,black \
 	sbnms-buoys-ab.xys -Sc \
 	stellwagen-5nm.dat stellwagen.dat \
 	-J$MAP_PROJECTION$MAP_SCALE \
 	-R$MAP_REGION \
 	-K -O -V >> $PS_FILE

echo Running pstext...
pstext \
    -D0/.1 \
	sbnms-buoys-ab.xyt \
	stellwagen-5nm.dat stellwagen.dat \
	-J$MAP_PROJECTION$MAP_SCALE \
	-R$MAP_REGION \
	-K -O -V >> $PS_FILE



#
# Make color scale
echo Running psscale...
psscale -C$CPT_FILE \
	-D2.7803/-0.5000/5.5607/0.1500h \
	-B":meters:" \
	-P -K -O -V >> $PS_FILE
#
# Make basemap
echo Running psbasemap...
psbasemap -J$MAP_PROJECTION$MAP_SCALE \
	-R$MAP_REGION \
	-B15m/15m:."SBNMS AIS Transits ${monName}-2006": \
	-P -O -V >> $PS_FILE

#	-B30m/30m:."SBNMS AIS Tracks": \


#
# Delete surplus files
echo Deleting surplus files...
/bin/rm -f $CPT_FILE
#
# Reset GMT default fonts
echo Resetting GMT fonts...
/bin/mv gmtdefaults$$ .gmtdefaults
#
# Run ghostview
echo Producing pdf and png products
ps2pdf ${PS_FILE}
convert ${PS_FILE} ${PNG_FILE}
rm ${PS_FILE}
open ${PDF_FILE}



#
# All done!
echo All done!
