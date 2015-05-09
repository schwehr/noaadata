#!/usr/bin/env python
"""Filter AIS data to remove duplicates.

 TODO(schwehr):Be able to look out across a couple seconds for messages that are dup receives
"""

import sys


def getMsg(nmeaMsg):
    ''' Return everything in the base nmea message'''

    return nmeaMsg[:nmeaMsg.find(',',nmeaMsg.find('*'))]


def filterInTimestamp(lineList):
    '''
    Decimate lines to only return unique reports
     TODO(schwehr):have it prefer reports with s, d, and T fields

     TODO(schwehr):preserve order within each second and support multi line messages
    '''
    if 1==len(lineList):
        # NOP
        print lineList[0],
        return

    msgDict={} # Key by unique messages
    for line in lineList:
        msg = getMsg(line)
        if msg not in msgDict:
            msgDict[msg]=[line]
        else:
            msgDict[msg].append(line)

    for key in msgDict:
        msgs=msgDict[key]
        if len(msgs)==1:
            print msgs[0],
            continue

        lens = [len(line) for line in msgs]
        lens.sort()
        maxLen = lens[-1]

        for line in msgs:
            if len(line)==maxLen:
                print line,
                break


tsOld = None

linesInTS=[] # Collection of all lines in the time

for line in sys.stdin:
    ts = line.split(',')[-1].strip()
    if ts!=tsOld:
        if None!=tsOld:
            filterInTimestamp(linesInTS)

        linesInTS=[]
        tsOld=ts
        #print 'starting timestamp',tsOld

    fields=line.split(',')
    if fields[1]=='1' and fields[2]=='1':
        # Can only handle single line messages
        linesInTS.append(line)
    else:
        print line,

if None!=tsOld:
    filterInTimestamp(linesInTS)
