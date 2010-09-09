#!/usr/bin/env python
__author__    = 'Kurt Schwehr'
__version__ = '$Revision: 9672 $'.split()[1]
__date__ = '$Date: 2008-06-20 01:49:30 -0400 (Fri, 20 Jun 2008) $'.split()[1]
__author__ = 'Kurt Schwehr'
__copyright__ = '2007'
__license__   = 'GPL v3'
__contact__   = 'kurt at ccom.unh.edu'

__doc__ = '''

Return positions of vessels, but require a minimum distance moved before emitting the next point.

@requires: U{epydoc<http://epydoc.sourceforge.net/>} > 3.0alpha3
@requires: U{pyproj<http://http://python.org/pypi/pyproj/>}

@var __date__: Date of last svn commit
@undocumented: __doc__ parser
@status: under development
@license: GPL
'''

import sys
#import os

# Can decode messages 1,2,3 will any of the three codecs
import ais.binary    as binary
import ais.ais_msg_1 as ais_msg_1
#import ais.aisstring as aisstring

from pyproj import Proj
import math

def dist (lon1, lat1, lon2, lat2):
    'calculate 2D distance.  Should be good enough for points that are close together'
    dx = (lon1-lon2)
    dy = (lat1-lat2)
    return math.sqrt(dx*dx + dy*dy)

def getPosition(logfile, outfile, minDist=None):
    '''
    Pull the positions from the log file
    @param logfile: file like object
    @param outfile: file like object destination
    @param minDist: how far apart points must be apart to be considered unique
    '''
    # FIX: use the right utm zone.  14 is the central US so it will kind of work
    params = {'proj':'utm', 'zone':14} #int(options.zone)}
    proj = None
    if minDist != None:
        proj = Proj(params)

    positions = {} # Last recoded ship position

    for line in logfile: 
        fields = line.split(',')
        # FIX: use regex instead
        if '!AIVDM' != fields[0]:
            continue
        if '1' != fields[1] and '1' != fields[2]: # Must be the start of a sequence
            continue
        if fields[5][0] not in ('1','2','3'):
            continue

        bv = binary.ais6tobitvec(fields[5][:39]) # Hacked for speed

        timestamp = fields[-1].strip()
        mmsi = str(ais_msg_1.decodeUserID(bv))
        lon = ais_msg_1.decodelongitude(bv)
        lat = ais_msg_1.decodelatitude(bv)

        d = None
        if mmsi not in positions:
            positions[mmsi] = (lon, lat)
        elif minDist != None:
            lonOld, latOld = positions[mmsi]
            oldUTM = proj(lonOld, latOld)
            newUTM = proj(lon, lat)
            d = dist(oldUTM[0], oldUTM[1], newUTM[0], newUTM[1])
            if str(d)=='nan':
                continue #pass  # FIX: Print but do not save nan values???
            elif d < minDist:
                continue
            else:
                positions[mmsi] = (lon, lat)

        lon = str(lon)
        lat = str(lat)

        if len(mmsi) < 9:
            mmsi += ' '*(9-len(mmsi))

        fLen = 12 # field length ... how much space

        if len(lon)>fLen:
            lon = lon[:fLen]
        if len(lon)<fLen:
            lon += ' '*(fLen-len(lon))

        if len(lat)>fLen:
            lat = lat[:fLen]
        if len(lat)<fLen:
            lat += ' '*(fLen-len(lat))

        outfile.write(timestamp+' '+str(mmsi)+' '+lon+' '+lat+'\n')

def main():
    from optparse import OptionParser
    parser = OptionParser(usage="%prog [options] logfile1 [logfile2 logfile3 ...] ", version="%prog "+__version__)
    parser.add_option('-o', '--output', dest='outputFileName', default=None,
                      help='Name of the python file to write [default: stdout]')
    parser.add_option('-m', '--min-dist', dest='minDist', default=None, type='float',
                      help='minimum distance to move before output a new position in meters [default: None]')

    # FIX: add option that a max time between positions to pass if the ship is not moving

    (options, args) = parser.parse_args()
    
    outfile = sys.stdout

    if None != options.outputFileName:
        print 'outfilename=', options.outputFileName
        outfile = file(options.outputFileName, 'w')

    if 0 == len(args):
        getPosition(sys.stdin, outfile, options.minDist)
    else: 
        for filename in args:
            getPosition(file(filename), outfile, options.minDist)

if __name__ == '__main__':
    main()
