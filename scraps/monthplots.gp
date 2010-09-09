#!/usr/bin/env gnuplot

set terminal pdf
set key left

set xtics nomirror rotate by -45
set style data linespoints
set datafile missing "-"

set output 'month-summaries-2-lines.pdf'
plot 'month-summaries-2.dat' using 2:xtic(1) t 2, \
'' u 3 t 3,\
'' u 4 t 4,\
'' u 5 t 5,\
'' u 6 t 6

# Bar graph...
set output 'month-summaries-2-bars.pdf'

set style data histogram
set style histogram cluster gap 1
set style fill solid border -1
set boxwidth 0.9

replot

set output 'month-summaries-2-stacked.pdf'

# Stacked ...
set style data histogram
set style histogram rowstacked
set style fill solid border -1
set boxwidth 0.75

replot

