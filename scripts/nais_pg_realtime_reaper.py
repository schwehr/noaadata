#!/usr/bin/env python
__author__ = 'Kurt Schwehr'
__version__ = '$Revision: 2275 $'.split()[1]
__revision__  = __version__ # For pylint
__date__ = '$Date: 2006-07-10 16:22:35 -0400 (Mon, 10 Jul 2006) $'.split()[1]
__copyright__ = '2009'
__license__   = 'GPL v3'
__contact__   = 'kurt at ccom.unh.edu'

__doc__='''

@var __date__: Date of last svn commit
@undocumented: __doc__ myparser
@status: under development
@since: 2009-May-10

@requires: U{Python<http://python.org/>} >= 2.5
'''
import traceback
import sys
import exceptions # For KeyboardInterupt pychecker complaint
import logging # Python's logger module for tracking progress

import time
import datetime

import magicdate
import pytz

import aisutils.daemon
import aisutils.database

def mark_utc(dt):
    '''Take a datetime object in UTC without timezone set and return one with utc marked'''
    # print 'pytz utc:',pytz.utc,type(pytz.utc)
    return datetime.datetime(dt.year,dt.month,dt.day, dt.hour, dt.minute, dt.second, tzinfo=pytz.utc)


class Clean:
    def __init__(self,options):
        self.options = options
        self.track_start = options.track_start
        self.last_position_start = options.track_start
        self.cx = aisutils.database.connect(options, dbType='postgres')
        self.cu = self.cx.cursor()
        self.verbose = options.verbose

    def do_once(self):
        cx = self.cx
        cu = self.cu
        v = self.verbose

        tzoffset = datetime.timedelta(seconds=time.timezone) # Always work in utc.  Magicdate is local


        if self.track_start is not None:
            track_start = mark_utc(magicdate.magicdate(self.track_start)+tzoffset )
            if v:
                cu.execute('SELECT COUNT(*) FROM track_lines WHERE update_timestamp < %s;', (track_start,))
                print 'Deleting from track_lines:',cu.fetchone()[0]

            cu.execute('DELETE FROM track_lines WHERE update_timestamp < %s;', (track_start,))

            # if the points are too old to be in a track_line, then delete them
            if v:
                cu.execute('SELECT COUNT(*) FROM position WHERE cg_timestamp < %s;', (track_start,))
                print 'Deleting from position:',cu.fetchone()[0]

            cu.execute('DELETE FROM position WHERE cg_timestamp < %s;', (track_start,))



        if self.last_position_start is not None:
            last_position_start = mark_utc(magicdate.magicdate(self.last_position_start)+tzoffset )
            
            if v:
                cu.execute('SELECT COUNT(*) FROM last_position WHERE cg_timestamp < %s;', (track_start,))
                print 'Deleting from last_position:',cu.fetchone()[0]

            cu.execute('DELETE FROM last_position WHERE cg_timestamp < %s;', (last_position_start,))

        if self.last_position_start is not None or self.track_start is not None:
            cx.commit()


######################################################################

def main():
    from optparse import OptionParser

    # FIX: is importing __init__ safe?
    parser = OptionParser(usage="%prog [options]"
                          ,version="%prog "+__version__ + " ("+__date__+")")

    aisutils.daemon.stdCmdlineOptions(parser, skip_short=True)

    aisutils.database.stdCmdlineOptions(parser, 'postgres')

    parser.add_option('-s', '--track-start-time', dest='track_start', type='str',
                      default=None,
                      help='magicdate - Oldest allowable time for a track line [default %default]')

    parser.add_option('-S', '--last-position-start-time', dest='last_position_start', type='str',
                      default=None,
                      help='magicdate - Oldest allowable time for a last position [default %default]')

    parser.add_option('--loop',dest='loop',default=False,action='store_true',
                      help='Make run loop with clean-time delay')

    parser.add_option('--loop-delay', dest='loop_delay', type='float',
                      default=60,
                      help='Time in seconds between database cleanup of the track lines [default %default]')

    parser.add_option('-v','--verbose',dest='verbose',default=False,action='store_true',
                      help='Make the test output verbose')

    default_log = sys.argv[0].split('/')[-1]+'.log'

    parser.add_option('-l', '--log-file', dest='log_file', type='string', default=default_log,
                      help='Tracing and logging file for status [default: %default]')

    parser.add_option('-L','--log-level',dest='log_level',type='int', default='0'
                      ,help='Log level for tracing.  Defaults to all [default: %default]')

    (options,args) = parser.parse_args()
    v = options.verbose
    if v:
        sys.stderr.write('starting logging to %s at %d\n' % 
                         (options.log_file, options.log_level) )

    if options.daemon_mode:
        aisutils.daemon.start(options.pid_file)

    logging.basicConfig(filename = options.log_file
                        , level  = options.log_level
                        )


    clean = Clean(options)
    clean.do_once()

        
######################################################################
if __name__=='__main__':
    main()
