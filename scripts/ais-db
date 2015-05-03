#!/usr/bin/env python
"""Command line AIS database utilities.

TODO(schwehr): Move the create strings here to aisutils.database or similiar.
TODO(schwehr): What indices need to get created?
"""

import logging
import os
import sys


import aisutils.database


def main():
    from optparse import OptionParser
    parser = OptionParser(usage='%prog [options]', version='%prog ')

    parser.add_option(
        '-v', '--verbose',
        dest='verbose',
        default=False,
        action='store_true',
        help='Make program output more verbose info as it runs')

    parser.add_option(
        '-t', '--database-type',
        dest='dbType',
        default=aisutils.database.dbTypes[0],
        choices=aisutils.database.dbTypes,
        help='Which database type to use [default: %%default]'
        ' on of (%s)' % ', '.join(aisutils.database.dbTypes))

    aisutils.database.stdCmdlineOptions(parser, 'all')

    parser.add_option(
        '-c', '--create-database',
        dest='createDB',
        default=False,
        action='store_true',
        help='Create the database.  Sqlite does not need this.')

    parser.add_option(
        '--add-postgis',
        dest='addPostgis',
        default=False,
        action='store_true',
        help='Add Postgis capabilities to the database.  Not for Sqlite.')

    # DB table creations
    parser.add_option(
        '-C',
        '--create-tables',
        dest='createTables',
        default=False,
        action='store_true',
        help='Create the tables in the database')

    parser.add_option(
        '--drop-tables',
        dest='dropTables',
        default=False,
        action='store_true',
        help='Remove the tables in the database.  DANGER - destroys data')

    parser.add_option(
        '-i', '--include-msg',
        action='append',
        dest='includeMsgs',
        type='int',
        default=None,
        help='Make a list of messages to put in the db [default: %default]')

    parser.add_option(
        '-e','--exclude-msg',
        action='append',
        dest='excludeMsgs',
        type='int',
        default=None,
        help='Make a list of messages to put in the db [default: %default]')

    parser.add_option(
        '--create-track-lines',
        action='store_true',
        dest='createTrackLinesTable',
        default=False,
        help='Add a track lines table for postgis')

    parser.add_option(
        '--drop-track-lines',
        action='store_true',
        dest='dropTrackLinesTable',
        default=False,
        help='Remove the track lines table for postgis')

    parser.add_option(
        '--create-last-position',
        action='store_true',
        dest='createLastPositionTable',
        default=False,
        help='Add a last position table for postgis')

    parser.add_option(
        '--drop-last-position',
        action='store_true',
        dest='dropLastPositionTable',
        default=False,
        help='Remove the last position table for postgis')

    (options,args) = parser.parse_args()
    verbose = options.verbose

    if options.createDB and options.dbType != 'sqlite':
        if verbose:
            logging.info('Creating database')
        r = os.system('createdb -U postgres '+options.databaseName)
        if r:
            logging.error('Unable to create the database.  Exit code: %d', r)
            return False
        r = os.system('createlang plpgsql ' + options.databaseName)
        if r:
            logging.error('Unable to add language plpgsql.  Exit code: %d', r)
            return False

    cx = aisutils.database.connect(options)

    if options.addPostgis :
        if options.dbType == 'sqlite':
            sys.stderr.write('WARNING: postgis not available for sqlite.  Ignoring request\n')
        else:
            # TODO(schwehr): This no longer works.
            r = os.system('psql -f /sw/share/doc/postgis83/contrib/postgis-1.5/postgis.sql -d '+options.databaseName)
            r = os.system('psql -f /sw/share/doc/postgis83/contrib/postgis-1.5/spatial_ref_sys.sql -d '+options.databaseName)

    if options.createTables:
        if verbose:
            logging.info('Creating tables.')
        aisutils.database.createTables(
            cx,
            dbType=options.dbType,
            includeList=options.includeMsgs,
            excludeList=options.excludeMsgs,
            verbose=verbose)

    if options.dropTables:
        if verbose:
            logging.info('Dropping tables.')
        aisutils.database.dropTables(
            cx,
            includeList=options.includeMsgs,
            excludeList=options.excludeMsgs,
            verbose=verbose)

    if options.createTrackLinesTable:
        sqlCreate = (
            'CREATE TABLE track_lines ('
            'ogc_fid SERIAL PRIMARY KEY, '
            'userid INTEGER, name CHARACTER VARYING(20), '
            'update_timestamp TIMESTAMP WITH TIME ZONE DEFAULT now());'
        )
        sqlCreate += (
            " SELECT AddGeometryColumn('track_lines', 'track',"
            " 4326, 'LINESTRING', 2);"
        )
        if verbose:
            logging.info('Creating track_lines table: %s', sqlCreate)

        cu = cx.cursor()
        cu.execute(sqlCreate)
        cx.commit()

    if options.createLastPositionTable:
        # Course over ground (cog) is a decimal in the position table.
        sqlCreate = (
            'CREATE TABLE last_position '
            '(key SERIAL PRIMARY KEY, userid INTEGER, '
            'name CHARACTER VARYING(20), cog INTEGER, sog REAL, '
            'cg_timestamp TIMESTAMP WITH TIME ZONE DEFAULT now(), '
            'cg_r VARCHAR(15), navigationstatus VARCHAR(30), '
            'shipandcargo VARCHAR(30) );'
        )
        sqlCreate += (
            " SELECT AddGeometryColumn('last_position', 'position',"
            " 4326, 'POINT', 2);"
        )
        if verbose:
            logging.info('Creating last position table: %s', sqlCreate)
        cu = cx.cursor()
        cu.execute(sqlCreate)
        cx.commit()

    if options.dropTrackLinesTable:
        if verbose:
            logging.info('Dropping track_lines table.')
        cu = cx.cursor()
        cu.execute('DROP TABLE track_lines;')
        cx.commit()

    if options.dropLastPositionTable:
        if verbose:
            logging.info('Dropping last_position table.')
        cu = cx.cursor()
        cu.execute('DROP TABLE last_position;')
        cx.commit()

    if verbose:
        sys.stderr.write('Done.\n')

    return True

if __name__=='__main__':
    if not main():
        sys.exit(-1)
