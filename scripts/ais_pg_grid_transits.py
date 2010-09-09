#!/usr/bin/env python

__version__ = '$Revision: 12605 $'.split()[1]
__date__ = '$Date: 2009-09-21 08:25:58 -0400 (Mon, 21 Sep 2009) $'.split()[1]
__author__ = 'Kurt Schwehr'

__doc__="""

Create a grid from ais transit lines.  Improved from
ais_pg_grid.py to allow arbitrary gridding of any set of transits

@requires: U{epydoc<http://epydoc.sourceforge.net/>} > 3.0alpha3
@requires: U{psycopg2<http://initd.org/projects/psycopg2>}
@requires: U{postgreSQL<http://www.postgresql.org/>} => 8.2
@requires: U{postgis<http://postgis.org>} => 8.2
@requires: U{pyproj<>}
@requires: grid.py

@author: """+__author__+"""
@version: """ + __version__ +"""
@var __date__: Date of last svn commit
@undocumented: __version__ __author__ __doc__ parser
@status: under development
@license: GPL v3
@since: 2010-Mar-11

"""

import math
import sys
import os

import aisutils.grid as grid
import psycopg2 as psycopg
from pyproj import Proj
from optparse import OptionParser

def get_parser():
    parser = OptionParser(usage="%prog [options] [transit_num] [transit_num] ...",version="%prog "+__version__)
    parser.add_option('-b','--basename',default='tmp', help='Base file name for output')

    parser.add_option('-x','--x-min', default=-70.7, type='float', help='Geographic lon range (-180..180) [default: %default]')
    parser.add_option('-X','--x-max', default=-69.9, type='float', help='Geographic lon range (-180..180) [default: %default]')
    parser.add_option('-y', '--y-min', default=42.0, type='float', help='Geographic lat range (-90..90) [default: %default]')
    parser.add_option('-Y', '--y-max', default=42.9, type='float', help='Geographic lat range (-90..90) [default: %default]')

    parser.add_option('-s', '--step', default=1852, type='float', help='cell size in meters [default: %default (1 nautical mile)]')

    parser.add_option('-d', '--database-name',default='ais', help='Name of database within the postgres server [default: %default]')
    parser.add_option('-D', '--database-host',default='localhost', help='Database hostname [default: %default]')
    parser.add_option('-u', '--database-user',default=os.getlogin(), help='Database user [default: %default]')

    parser.add_option('-v', '--verbose', default=False, action='store_true', help='Make the test output verbose')

    parser.add_option('-t', '--tracks-file', default=None, help='File containing space separated track id numbers [default: use args]')
    
    return parser

def lon_to_utm_zone(lon):
    return int(( lon + 180 ) / 6) + 1


def main():
    parser = get_parser()
    (options,args) = parser.parse_args()
    verbose = options.verbose
    options_dict = vars(options)


    #print options

    assert options.x_min < options.x_max
    assert options.y_min < options.y_max

    zone = lon_to_utm_zone(options.x_min)
    assert (zone == lon_to_utm_zone(options.x_max) )

    params={'proj':'utm','zone':int(zone)}
    proj = Proj(params)

    ll = proj(options.x_min,options.y_min)
    ur = proj(options.x_max,options.y_max)
    
    g = grid.Grid(ll[0],ll[1], ur[0],ur[1], stepSize=options.step)# , verbose=options.verbose)
    basename=options.basename
    g.writeLayoutGnuplot(basename+'-grd.dat')

    # Make sure they are all numbers
    #[int(track) for track in args]
    #tracks = ','.join(args)
    tracks = args

    connectStr = "dbname='{database_name}' user='{database_user}' host='{database_host}'".format(**options_dict)
    if verbose:
        print 'CONNECT:',connectStr
    cx = psycopg.connect(connectStr)
    cu = cx.cursor()

    print 'FIX: lookup EPSG for UTM zone here rather than hardcoding'
    
    if options.tracks_file is not None:
        for line in file(options.tracks_file):
            #more_tracks = [int(t) for t in line.split()]
            for item in line.split():
                tracks.append(int(item))

    #cu.execute('SELECT AsText(Transform(track,32619)) FROM tpath WHERE id IN ('+tracks+');')
    #for track_count,track_wkt in enumerate(cu.fetchall()):
    for track_count, track_id in enumerate(tracks):
        if track_count % 200==0:
            print 'track_count:',track_count
        
        cu.execute('SELECT AsText(Transform(track,32619)) FROM tpath WHERE id=%d;' %(int(track_id),) )
        track_wkt=cu.fetchone()[0]
        trackseq = grid.wktLine2list(track_wkt);
        if len(trackseq)<2:
            print 'TOO SHORT: ',track_count, len(trackseq)
            sys.exit('crap')
        g.addMultiSegLine(trackseq)

    print 'track_count:',track_count

    g.writeCellsGnuplot(basename+'-cells.dat')
    g.writeArcAsciiGrid(basename+'-grd.asc')
    
######################################################################
if __name__=='__main__':
    main()
