#!/usr/bin/env python

__author__    = 'Kurt Schwehr'
__version__   = '$Revision: 12308 $'.split()[1]
__revision__  = __version__ # For pylint
__date__ = '$Date: 2009-07-22 17:22:17 -0400 (Wed, 22 Jul 2009) $'.split()[1]
__copyright__ = '2010'
__license__   = 'GPL v3'
__contact__   = 'kurt at ccom.unh.edu'

# since 2010-04-14
# Find if we have missing files in per day logs

import magicdate, sys, os, datetime

def date_generator(start_date, end_date):
    cur_date = start_date
    dt = datetime.timedelta(days=1)
    while cur_date < end_date:
        yield cur_date
        cur_date += dt


def main():
    from optparse import OptionParser
    parser = OptionParser(option_class=magicdate.MagicDateOption,
                          usage='%prog [options]',
                          version='%prog '+__version__)
    parser.add_option('-s', '--start-date', type='magicdate', default=None, help='Force a start time (magicdate)')
    parser.add_option('-e', '--end-date',   type='magicdate', default=magicdate.magicdate('today'), help='Force an end  time (magicdate) [default: %default]')
    parser.add_option('-l', '--log-format', default='%Y%m%d.log', help='datetime strftime format string to create the log file names to search for [default: %default]')
    (options,args) = parser.parse_args()

    assert options.start_date is not None
    for d in date_generator(options.start_date, options.end_date):
        #print d.strftime(options.log_format)
        filename = d.strftime(options.log_format)
        try:
            s = os.stat(filename)
        except OSError:
            print 'missing',filename
        

        


if __name__ == '__main__':
    main()
