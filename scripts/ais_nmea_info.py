#!/usr/bin/env python

__author__    = 'Kurt Schwehr'
__version__   = '$Revision: 12308 $'.split()[1]
__revision__  = __version__ # For pylint
__date__ = '$Date: 2009-07-22 17:22:17 -0400 (Wed, 22 Jul 2009) $'.split()[1]
__copyright__ = '2008'
__license__   = 'GPL v3'
__contact__   = 'kurt at ccom.unh.edu'

__doc__='''

Summarize the AIS message traffic at the NMEA level without decoding the contents.

@requires: U{epydoc<http://epydoc.sourceforge.net/>} > 3.0
@since: 2009-July-27
@var __date__: Date of last svn commit
@undocumented: __version__ __author__ __doc__ parser
@status: Works, but not complete
'''

from aisutils.uscg import uscg_ais_nmea_regex
import ais.binary
import ais

def nmea_summary(filename):
    msgs = dict([(val,0) for val in ais.binary.encode])

    station_counts = {}
    channel_counts = {'A':0, 'B':0}
    for line in file(filename):
        match = uscg_ais_nmea_regex.search(line)
        if match is None:
            continue
        match = match.groupdict()
        msg = match

        if msg['senNum']=='1':
            first_char = msg['body'][0]
            msgs[first_char] += 1

        if match['chan'] is not None:
            channel_counts[match['chan']] += 1

        if match['station'] is not None:
            station = match['station']
            if station in station_counts:
                station_counts[station] += 1
            else:
                station_counts[station] = 1

    return {'msgs':msgs, 'stations':station_counts, 'channels':channel_counts}


def main():
    from optparse import OptionParser

    parser = OptionParser(usage="%prog [options] file1.ais [file2.ais ...]",version="%prog "+__version__)
    (options,args) = parser.parse_args()

    for filename in args:
        results = nmea_summary(filename)
        print '%s:' % (filename, )

        msgs = results['msgs']

        for msg in ais.binary.encode:
            if msgs[msg] > 0:
                msg_num = ais.binary.encode.index(msg)
                try:
                    msg_name = ais.msgNames[msg_num]
                except KeyError:
                    msg_name = 'Unknown (%d)' % msg_num
                print msg,str(msgs[msg]).ljust(9),msg_name

        print '\nstations and counts:'
        #for station,count in results['stations'].iteritems():
        #    print '  ',station.ljust(15),count

        stations = results['stations'].keys()
        stations.sort()
        for station in stations:
            print '  ',station.ljust(15),results['stations'][station]

        print
        print 'channel_a:',results['channels']['A']
        print 'channel_b:',results['channels']['B']

if __name__=='__main__':
    main()
