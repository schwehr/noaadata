#!/usr/bin/env python

__author__    = 'Kurt Schwehr'
__version__   = '$Revision: 4799 $'.split()[1]
__revision__  = __version__ # For pylint
__date__ = '$Date: 2006-09-25 11:09:02 -0400 (Mon, 25 Sep 2006) $'.split()[1]
__copyright__ = '2009'
__license__   = 'GPL v3'
__contact__   = 'kurt at ccom.unh.edu'
__doc__ ='''
Look at a stream of USCG NMEA messages in the old format and give an estimate of uptime.
How many minutes did we receive data from during the time span?

@requires: U{Python<http://python.org/>} >= 2.5
@requires: U{epydoc<http://epydoc.sourceforge.net/>} >= 3.0.1

@undocumented: __doc__
@since: 2009-Jun-09
@status: under development
@organization: U{CCOM<http://ccom.unh.edu/>} 
'''

import sys
import datetime
import traceback

def uptime(filename):
    times = set()
    'minute increments'
    tmin = None
    tmax = None
    for linenum,line in enumerate(file(filename)):
        if '!AIVDM' != line[:6]:
            continue
        try:
            t = int(line.split(',')[-1])
            t = datetime.datetime.utcfromtimestamp(t)
        except Exception, e:
            #sys.stderr.write('    Exception:' + str(type(Exception))+'\n')
            #sys.stderr.write('    Exception args:'+ str(e)+'\n')
            #sys.stderr.write('    LINE: %s\n' % (line,))
            #traceback.print_exc(file=sys.stderr)
            continue

        t = datetime.datetime(t.year, t.month, t.day, t.hour, t.minute)
        
        if tmin is None:
            tmin = t
            tmax = t
        if t < tmin: tmin = t
        if t > tmax: tmax = t
        times.add(t)

        if linenum % 10000 == 0:
            sys.stderr.write('%d: %s\n' % ( linenum, str(t)))

    dt = tmax - tmin

    #print tmin,tmax,len(times)
    #print tmin.strftime('%j')
    #print tmax.strftime('%j')
    minutes = len(times)
    minutes_expected = (dt.days * 3600*24 + dt.seconds) / 60.

    #print minutes / minutes_expected
    julian_day = tmax.strftime('%j')
    return julian_day, minutes / minutes_expected

def main():
    '''
    FIX: document main
    '''
    from optparse import OptionParser
    parser = OptionParser(usage="%prog [options]",
                          version="%prog "+__version__+' ('+__date__+')')

    parser.add_option('-v', '--verbose', dest='verbose', default=False, action='store_true',
                      help='run the tests run in verbose mode')

    (options, args) = parser.parse_args()
    v = options.verbose

    for filename in args:
        day,up = uptime(filename)
        print day,up


if __name__ == '__main__':
    main()
