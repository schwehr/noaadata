#!/usr/bin/env python
"""List all of the AIS stations within a set of log files.

@license: Apache 2.0
"""

import os
import sys


def getStation(line, withR=False):
    fields=line.split(',')
    if '!AIVDM' != fields[0]:
        return None

    foundChecksum=False
    for i,f in enumerate(fields):
        if i<5: continue
        # must come after the checksum field
        if len(f)<1: continue
        if not foundChecksum:
            if -1==f.find('*'): continue  # FIX: Is this sufficient to make sure this is a checksum?
            #if '0'==f[0]: continue
            foundChecksum=True
            continue
        if len(f)<2: continue
        if f[0] not in  ('r','b'): continue
        if withR: return f
        return f[1:]
    return None


if __name__=='__main__':

        from optparse import OptionParser
        parser = OptionParser(usage="%prog [options] file1.ais [file2 ...]", version="%prog ")

        parser.add_option('-c','--count-for-station',dest='count_each_station',default=False,action='store_true',
                          help='Count the number of lines for each station')
        parser.add_option('-r','--without-r',dest='withR',default=True,action='store_false',
                          help='Do not keep the r in the station name')
        parser.add_option('-v','--verbose',dest='verbose',default=False,action='store_true',
                          help='Make the test output verbose')

        parser.add_option('--progress',dest='progress',default=False,action='store_true',
                          help='Print out the line count every n lines')

        (options,args) = parser.parse_args()
        verbose = options.verbose

        progress_interval = 1000000

        if options.count_each_station:
            stations = {}
            for filename in args:
                for linenum,line in enumerate(open(filename)):
                    if options.progress:
                        if linenum % progress_interval == 0:
                            sys.stderr.write('linenum: %d\n' % linenum)
                    station = getStation(line,options.withR)
                    if station:
                        if station not in stations:
                            stations[station]=1
                        else:
                            stations[station]+=1
            for station in stations:
                print station, stations[station]

        else:
            stations = set()
            for filename in args:
                if options.verbose: print 'Processing file:',filename
                for linenum,line in enumerate(open(filename)):
                    if options.progress:
                        if linenum % progress_interval == 0:
                            sys.stderr.write('linenum: %d\n' % linenum)
                    station = getStation(line,options.withR)
                    if None==station:
                        if verbose: print 'WARNING: no station for line',line
                        continue

                    if verbose and station not in stations:
                        print 'New station:',station

                    stations.add(station)

            for item in stations:
                print item
