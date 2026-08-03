#!/usr/bin/env python
# License: Apache 2.0
"""
Rebuild cache tables for the current vessel traffic status.

This works on the last_position and track_lines tables.
"""

import datetime
import logging
import sys
import time

import aisutils.database
import aisutils.uscg
import magicdate


def main():
    from optparse import OptionParser

    parser = OptionParser(
        usage="%prog [options]",
        option_class=magicdate.MagicDateOption)

    aisutils.database.stdCmdlineOptions(parser, 'postgres')

    parser.add_option(
        '-l', '--limit-points',
        dest='limitPoints',
        type='int',
        default=10,
        help='Max number of points for a ship track [default: %default]')

    parser.add_option(
        '-n', '--no-limit-points',
        dest='limitPoints',
        action='store_const',
        const=None,
        help='Make points unlimited')

    parser.add_option(
        '-v', '--verbose',
        dest='verbose',
        default=False,
        action='store_true',
        help='Make the test output verbose')

    parser.add_option(
        '-a', '--all',
        dest='updateAll',
        default=False,
        action='store_true',
        help='Update all the cache tables')

    parser.add_option(
        '-T', '--track-lines',
        dest='updateTrackLines',
        default=False,
        action='store_true',
        help='Update the track_lines table')

    parser.add_option(
        '-L', '--last-position',
        dest='updateLastPosition',
        default=False,
        action='store_true',
        help='Update the last_position table')

    parser.add_option(
        '--time-limit-all',
        dest='timeLimitAll',
        type='magicdate',
        help='Limit all caches by one magic date time (e.g. "1 hour ago")'
             '-s and -S override this [default %default]')

    parser.add_option(
        '-s', '--track-start-time',
        dest='track_start',
        type='magicdate',
        default=None,
        help='magicdate - Oldest allowable time for a track line '
             '[default %default]')

    parser.add_option(
        '-S', '--last-position-start-time',
        dest='last_position_start',
        type='magicdate',
        default=None,
        help='magicdate - Oldest allowable time for a last position '
             '[default %default]')

    options, args = parser.parse_args()
    verbose = options.verbose

    if options.timeLimitAll is not None:
        when = datetime.datetime.now() - datetime.timedelta(hours=options.timeLimitAll)
        if options.track_start == None:
            options.track_start = when
        if options.last_position_start == None:
            options.last_position_start = when

    if type(options.last_position_start) is datetime.date:
        d = options.last_position_start
        options.last_position_start = datetime.datetime(d.year, d.month, d.day)

    if verbose:
        logging.info('time constraints %s %s', options.track_start,
                     options.last_position_start)

    if options.updateAll:
        options.updateTrackLines=True
        options.updateLastPosition=True

    # TODO(schwehr): Don't force these.
    options.uscg = True
    options.dbType = 'postgres'

    cx = aisutils.database.connect(options,dbType=options.dbType)

    # To get to UTC from magicdate's local datetime.
    tzoffset = datetime.timedelta(seconds=time.timezone)

    if options.updateTrackLines:
        startTime = options.track_start + tzoffset
        if verbose:
            logging.info('Updating track_lines (%s to %s)',
                         startTime, datetime.datetime.utcnow())

        aisutils.database.rebuild_track_lines(
            cx,
            limitPoints=options.limitPoints,
            startTime=startTime,
            verbose=verbose)

    if options.updateLastPosition:
        startTime = options.last_position_start + tzoffset
        if verbose:
            logging.info('Updating last_position (%s to %s)\n',
                         startTime, datetime.datetime.utcnow())
        aisutils.database.rebuild_last_position(
            cx,
            startTime=startTime,
            verbose=verbose)


if __name__=='__main__':
    main()
