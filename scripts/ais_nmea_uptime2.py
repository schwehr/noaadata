#!/usr/bin/env python

__author__    = 'Kurt Schwehr'
__version__   = '$Revision: 4799 $'.split()[1]
__revision__  = __version__ # For pylint
__date__ = '$Date: 2006-09-25 11:09:02 -0400 (Mon, 25 Sep 2006) $'.split()[1]
__copyright__ = '2009'
__license__   = 'GPL v3'
__contact__   = 'kurt at ccom.unh.edu'
__doc__ ='''
A second try at defining uptime.  Think about making a histogram of time gaps.  Being that this is the uscg, we have to do this just by station.

@requires: U{Python<http://python.org/>} >= 2.5
@requires: U{epydoc<http://epydoc.sourceforge.net/>} >= 3.0.1

@undocumented: __doc__
@since: 2010-Mar-23
@status: under development
@organization: U{CCOM<http://ccom.unh.edu/>} 
'''

class Uptime:
    def __init__(self):
        self.gap_counts={}
    def add_file(self,filename):
        old_sec = None

        for line in file(filename):
            sec = int(line.split(',')[-1])
            if old_sec == None:
                old_sec = sec
                continue
            
            dt = sec - old_sec
            if dt < 2:
                old_sec = sec
                continue
            
            if dt not in self.gap_counts:
                self.gap_counts[dt] = 1
            else:
                self.gap_counts[dt] += 1
            #print old_sec, sec, dt, self.gap_counts[dt]
            old_sec = sec
    def total_gap(self,min_gap=5*60):
        tot = 0
        for key in self.gap_counts:
            if key < min_gap:
                continue
            tot += key + self.gap_counts[key]
        return tot
            
import sys
import datetime

if __name__ == '__main__':
    up = Uptime()
    up.add_file(sys.argv[1])
    #print up.gap_counts
    #for key in up.gap_counts:
    #    print key, up.gap_counts[key]
    date = datetime.datetime.strptime(sys.argv[1].split('.')[0], '%Y%m%d'

                                      )
    julian_day = int(date.strftime('%j').lstrip('0'))
    print julian_day, up.total_gap(), sys.argv[1]

print 'FIX: handle the between day gaps!!!'
