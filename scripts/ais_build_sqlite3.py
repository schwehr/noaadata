#!/usr/bin/env python

# License: Apache 2.0

"""Create or add to a database.

First attempt.  This could be made better/faster.
Assumes that all ais messages have been "normalized" - messages are one line
only.

Only works with sqlite3.  Uses the internal python sqlite db interface.
"""

import datetime
from decimal import Decimal
import StringIO
import sqlite3
import sys
import time

from aisutils import BitVector
from aisutils import binary

import ais.ais_msg_1
import ais.ais_msg_2
import ais.ais_msg_3
import ais.ais_msg_4
import ais.ais_msg_5
import ais.ais_msg_18
import ais.ais_msg_19


def createTables(cx, verbose=False):
    """Create tables in a SQLite databases.

    Args:
      cx: database connection
    """
    cu = cx.cursor()

    if verbose:
        print str(ais.ais_msg_1.sqlCreate(dbType='sqlite'))
    try:
        cu.execute(str(ais.ais_msg_1.sqlCreate(dbType='sqlite')))
    except:
        print 'Warning: position table already exists'

    # Skip 2 and 3 since they are also position messages

    if verbose: print str(ais.ais_msg_4.sqlCreate(dbType='sqlite'))
    cu.execute(str(ais.ais_msg_4.sqlCreate(dbType='sqlite')))

    if verbose: print str(ais.ais_msg_5.sqlCreate(dbType='sqlite'))
    cu.execute(str(ais.ais_msg_5.sqlCreate(dbType='sqlite')))

    cu.execute(str(ais.ais_msg_18.sqlCreate(dbType='sqlite')))
    cu.execute(str(ais.ais_msg_19.sqlCreate(dbType='sqlite')))

    cx.commit()

def loadData(cx,datafile,verbose=False
             , uscg=True):
    '''
    Try to read data from an open file object.  Not yet well tested.

    @param cx: database connection
    @param verbose: pring out more if true
    @param uscg: Process uscg tail information to get timestamp and receive station
    @rtype: None
    @return: Nothing

    @note: can not handle multiline AIS messages.  They must be normalized first.
    '''
    cu = cx.cursor()
    lineNum = 0

    #counts = {1:0,2:0,3:0,4:0,5:0}
    counts = {}
    countsTotal = {} # Includes ignored messages

    for i in range(64):
        counts[i]=0
        countsTotal[i]=0

    for line in datafile:
        lineNum += 1
        if lineNum%1000==0:
            print lineNum
            cx.commit()

        if line[3:6] not in ('VDM|VDO'):
            continue  # Not an AIS VHF message.
        try:
            msgNum = int(binary.ais6tobitvec(line.split(',')[5][0]))
        except:
            print 'line would not decode',line
            continue

        countsTotal[msgNum]+=1

        if verbose: print 'msgNum:',msgNum

        payload = bv = binary.ais6tobitvec(line.split(',')[5])

        # TODO(schwehr): Take padding into account.x
        if msgNum in (1,2,3):
            if len(bv) < 168:
                print 'ERROR: skipping bad position message, line:',lineNum
                print '  ',line,
                print '   Got length',len(bv), 'expected', 168
                continue
        elif msgNum == 5:
            if len(bv) < 424:
                print 'ERROR: skipping bad shipdata message, line:',lineNum
                print '  ',line,
                print '   Got length',len(bv), 'expected', 424
                continue

        fields=line.split(',')

        cg_timestamp = None
        cg_station   = None
        if uscg:
            try:
                cg_sec = int(float(fields[-1])) # US Coast Guard time stamp.
                print 'cg_sec:',cg_sec,type(cg_sec)
                cg_timestamp = datetime.datetime.utcfromtimestamp(float(cg_sec))
            except:
            #print len(fields),fields
            for i in range(len(fields)-1,5,-1):
                if 0<len(fields[i]) and 'r' == fields[i][0]:
                    cg_station = fields[i]
                    break # Found it so ditch the for loop

        ins = None

        try:
            if   msgNum==1: ins = ais.ais_msg_1.sqlInsert(ais.ais_msg_1.decode(bv),dbType='sqlite')
            elif msgNum==2: ins = ais.ais_msg_2.sqlInsert(ais.ais_msg_2.decode(bv),dbType='sqlite')
            elif msgNum==3: ins = ais.ais_msg_3.sqlInsert(ais.ais_msg_3.decode(bv),dbType='sqlite')
            elif msgNum==4: ins = ais.ais_msg_4.sqlInsert(ais.ais_msg_4.decode(bv),dbType='sqlite')
            elif msgNum==5: ins = ais.ais_msg_5.sqlInsert(ais.ais_msg_5.decode(bv),dbType='sqlite')

            elif msgNum==18: ins = ais.ais_msg_18.sqlInsert(ais.ais_msg_18.decode(bv),dbType='sqlite')
            elif msgNum==19: ins = ais.ais_msg_19.sqlInsert(ais.ais_msg_19.decode(bv),dbType='sqlite')
            else:
                if verbose:
                    print 'Warning... not handling type',msgNum,'line:',lineNum
                continue
        except:
            print 'ERROR:  some decode error?','line:',lineNum
            print '  ',line
            continue

        counts[msgNum] += 1

        if uscg:
            # FIX: make cg_timestamp work
            if None != cg_timestamp: ins.add('cg_timestamp',cg_timestamp)
            if None != cg_station:   ins.add('cg_r',        cg_station)
        if verbose: print str(ins)

        # FIX: redo this correctly???
        #try:
        print str(ins)
        cu.execute(str(ins))
    print '\nMessages found:'
    for key in countsTotal:
        if countsTotal[key]>0:
            print str(key)+':',countsTotal[key]

    print '\nMessages processed:'
    for key in counts:
        if counts[key]>0:
            print str(key)+':',counts[key]
    cx.commit()


############################################################
if __name__=='__main__':
    from optparse import OptionParser
    parser = OptionParser(usage="%prog [options] file1.ais [file2.ais ...]",
                          version='%prog ')

    parser.add_option('-d','--database-file',dest='databaseFilename',default='ais.db3'
                      ,help='Name of the sqlite3 database file to write [default: %default]')
    parser.add_option('-C','--with-create',dest='createTables',default=False, action='store_true'
                      ,help='Create the tables in the database')

    parser.add_option('--without-uscg',dest='uscgTail',default=True,action='store_false'
                      ,help='Do not look for timestamp and receive station at the end of each line [default: with-uscg]')

    parser.add_option('-v','--verbose',dest='verbose',default=False,action='store_true'
                      ,help='Make program output more verbose info as it runs')

    (options,args) = parser.parse_args()
    cx = sqlite3.connect(options.databaseFilename)

    print 'FIX: cg_sec and cg_timestamp are currently broken'

    if options.createTables:
        createTables(cx,verbose=options.verbose)

    if len(args)==0:
        print 'processing from stdin'

        loadData(cx,sys.stdin,verbose=options.verbose,uscg=options.uscgTail)
    else:
        for filename in args:
            print 'processing file:',filename
            loadData(cx,file(filename,'r'),verbose=options.verbose,uscg=options.uscgTail)
