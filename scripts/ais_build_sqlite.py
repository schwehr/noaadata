#!/usr/bin/env python

__author__    = 'Kurt Schwehr'
__version__   = '$Revision: 12565 $'.split()[1]
__revision__  = __version__ # For pylint
__date__ = '$Date: 2009-09-08 21:37:44 -0400 (Tue, 08 Sep 2009) $'.split()[1]
__copyright__ = '2008'
__license__   = 'GPL v3'
__contact__   = 'kurt at ccom.unh.edu'

__doc__='''

Create or add to a database.  First attempt.  This could be made better/faster.
Assumes that all ais messages have been "normalized" - messages are one line only.

Only deals with sqlite right now.

CREATE INDEX pos_userid_idx ON position(userid);
CREATE INDEX pos_pkt_id_idx ON position(pkt_id);
CREATE INDEX pos_cg_sec_idx ON position(cg_sec);
CREATE INDEX pos_cg_timestamp_idx ON position(cg_timestamp);
CREATE INDEX pos_cg_r_idx ON position(cg_r);
CREATE INDEX pos_dup_idx ON position(dup_flag);

CREATE INDEX bsrep_userid_idx ON bsreport(userid);
CREATE INDEX bsrep_pkt_id_idx ON bsreport(pkt_id);
CREATE INDEX bsrep_cg_sec_idx ON bsreport(cg_sec);
CREATE INDEX bsrep_cg_timestamp_idx ON bsreport(cg_timestamp);
CREATE INDEX bsrep_cg_r_idx ON bsreport(cg_r);
CREATE INDEX bsrep_dup_idx ON bsreport(dup_flag);

VACUUM;

@requires: U{epydoc<http://epydoc.sourceforge.net/>} > 3.0
@requires: U{BitVector<http://cheeseshop.python.org/pypi/BitVector>}

@var __date__: Date of last svn commit
@undocumented: __version__ __author__ __doc__ parser
@status: Works, but not complete
'''

import sys
import traceback
import datetime
import exceptions

from decimal import Decimal
from BitVector import BitVector
import StringIO

import ais.binary    as binary
#import ais.aisstring as aisstring

#import ais

#import aisutils.database

import ais.ais_msg_1_handcoded
import ais.ais_msg_2_handcoded
import ais.ais_msg_3_handcoded
import ais.ais_msg_4_handcoded
import ais.ais_msg_5
import ais.ais_msg_18
import ais.ais_msg_19
#import ais.ais_msg_8
#import ais.ais_msg_21

import nmea.checksum # for isChecksumValid

import pysqlite2.dbapi2 as sqlite
import pysqlite2.dbapi2


class TrackDuplicates:
    '''handle a feed and assign packet identifiers for duplicates
    Get this out into aisutils.

    Does not distinguish duplicates coming from the same receiver (should that ever happen)
    '''
    
    def __init__(self, lookback_length=None, lookback_time_sec=5*60):
        self.lookback_length = lookback_length
        self.lookback_time_sec = lookback_time_sec

        self.queue = []  # dicts of (time_sec,pkt_id,payload)

        self.next_new_id = 1 # skip zero: useful to not have a zero... bool(0) is False

        self.newest_time_sec = 0  # Unix UTC sec


    def check_packet(self, time_sec, payload):
        'payload is the text in the 5th position of any message... the encoded message'

        found = False
        for pkt in reversed(self.queue): # Search backwards since dups are likely close to the front, no?
            if payload == pkt['payload']:
                found = True
                break

        if found:
            return pkt['pkt_id'],True  # Skipping cleaning to save time

        # ! found... add packet to queue
        self.queue.append(dict(time_sec=time_sec, pkt_id = self.next_new_id, payload=payload))
        pkt_id = self.next_new_id
        self.next_new_id += 1
        if self.newest_time_sec < time_sec:
            self.newest_time_sec = time_sec
        

        # clean up queue wrt to length
        if self.lookback_length:
            while len(self.queue) > self.lookback_length:
                self.queue.pop(0) # drop oldest

        #
        # drop messages that are too old
        #
        span = 10 # Don't look too far back for speed.  Probably could work with just 1 or 2
        threshold_time = self.newest_time_sec - self.lookback_time_sec

        drop_list = []

        if self.lookback_time_sec and len(self.queue) > span:
            if len(self.queue) > span: span = len(self.queue)
            for i in range(span):
                if self.queue[i]['time_sec'] < threshold_time:
                    drop_list.append(i)

        for key in reversed(drop_list): # go backwards so we don't mess up the order
            self.queue.pop(key)

        return pkt_id,False


#def create_tables(cx, payload_table=False, verbose=False):
def create_tables(cx, verbose=False):
    '''
    param cx: database connection
    '''
    cu = cx.cursor()

#    if payload_table:
#        cu.execute(aisutils.database.payload_table_sql)

    if verbose: print str(ais.ais_msg_1_handcoded.sqlCreate(dbType='sqlite'))
    try:
        cu.execute(str(ais.ais_msg_1_handcoded.sqlCreate(dbType='sqlite')))
    except:
        print 'Warning: position table already exists'

    # Skip 2 and 3 since they are also position messages
    
    if verbose: print str(ais.ais_msg_4_handcoded.sqlCreate(dbType='sqlite'))
    cu.execute(str(ais.ais_msg_4_handcoded.sqlCreate(dbType='sqlite')))

    if verbose: print str(ais.ais_msg_5.sqlCreate(dbType='sqlite'))
    cu.execute(str(ais.ais_msg_5.sqlCreate(dbType='sqlite')))

    cu.execute(str(ais.ais_msg_18.sqlCreate(dbType='sqlite')))
    cu.execute(str(ais.ais_msg_19.sqlCreate(dbType='sqlite')))

    # For tracking packets and duplicate content.  Each unique payload gets an ID number
    # FIX: make these added to the sqlhelper object before executing
    cu.execute('ALTER TABLE position  ADD pkt_id INTEGER;') 
    cu.execute('ALTER TABLE position  ADD dup_flag BOOLEAN;') 

    cu.execute('ALTER TABLE bsreport  ADD pkt_id INTEGER;') 
    cu.execute('ALTER TABLE bsreport  ADD dup_flag BOOLEAN;') 
    #cu.execute('ALTER TABLE positionb ADD (pkt_id INTEGER, dup BOOLEAN);') 

    cu.execute('ALTER TABLE position ADD est_sec INTEGER;') # Best estimated time
    cu.execute('ALTER TABLE position ADD est_sec_type INTEGER;') # Where did the est_sec come from?

    cu.execute('ALTER TABLE bsreport ADD est_sec INTEGER;') # Best estimated time

    cx.commit()


def get_max_key(cx):
    '''
    return the maximum key from the database across tables
    '''
    max_key = None
    cu = cx.cursor()
    for table in ('position','bsreport','shipdata','positionb','b_pos_and_shipdata'):
        cu.execute('SELECT max(key) FROM %s;' % (table,))
        key = cu.fetchone()
        if key[0] is None:
            continue

        if max_key is None:
            max_key = int(key[0])
            continue

        if max_key < int(key[0]):
            max_key = int(key[0])
        
    return max_key


def load_data(cx, datafile=sys.stdin, verbose=False, uscg=True):
#	     uscg=True, payload_table=False):
    '''
    Try to read data from an open file object.  Not yet well tested.

    @param cx: database connection
    @param verbose: pring out more if true
    @param uscg: Process uscg tail information to get timestamp and receive station
    @rtype: None
    @return: Nothing

    @note: can not handle multiline AIS messages.  They must be normalized first.
    '''
#    @param payload_table: Create a table that contains the nmea payload text (useful for distinguisig unique messages)

    v = verbose # Hmm... "v"... the irony

    cu = cx.cursor()
    lineNum = 0

    next_key = 0
    max_key = get_max_key(cx)
    if max_key is not None:
        next_key = max_key + 1
    print 'keys_starting_at:',next_key

    message_set = (1,2,3,4,5,18,19)
    counts = {}
    for msg_num in message_set:
        counts[msg_num] = 0

    counts['checksum_failed'] = 0

    track_dups = TrackDuplicates(lookback_length=1000)

    for line in datafile:
	lineNum += 1
	if lineNum%1000==0:
	    print lineNum
	    cx.commit()
            
	if len(line)<15 or line[3:6] not in ('VDM|VDO'): continue # Not an AIS VHF message

        #print 'FIX: validate checksum'
        if not nmea.checksum.isChecksumValid(line):
            print >> sys.stderr, 'WARNING: invalid checksum:\n\t',line,
            print >> sys.stderr, '   ',nmea.checksum.checksumStr(line)
            counts['checksum_failed'] += 1

	fields=line.split(',') # FIX: use this split throughout below...

	try:
	    msg_num = int(binary.ais6tobitvec(fields[5][0]))
	except:
	    print 'line would not decode',line
	    continue
	if verbose: print 'msg_num:',msg_num
	if msg_num not in message_set: 
	    if verbose: 
                print 'skipping',line
                print '  not in msg set:',str(message_set)
	    continue

        try:
            bv = binary.ais6tobitvec(fields[5])
        except:
            print >> sys.stderr, 'ERROR: Unable to decode bits in line:\n\t',line
            traceback.print_exc(file=sys.stderr)
            continue

        # FIX: need to take padding into account ... right before the *
	if msg_num in (1,2,3,4,18):
	    if len(bv) != 168:
		print 'ERROR: skipping bad one slot message, line:',lineNum
		print '  ',line,
		print '   Got length',len(bv), 'expected', 168
		continue
	elif msg_num == 5:
            # 426 has 2 pad bits
	    if len(bv) not in (424,426):
		print 'ERROR: skipping bad shipdata message, line:',lineNum
		print '  ',line,
		print '   Got length',len(bv), 'expected', 424
		continue
	    
	ins = None

	try:
	    if   msg_num== 1: ins = ais.ais_msg_1_handcoded.sqlInsert(ais.ais_msg_1_handcoded.decode(bv),dbType='sqlite')
	    elif msg_num== 2: ins = ais.ais_msg_2_handcoded.sqlInsert(ais.ais_msg_2_handcoded.decode(bv),dbType='sqlite')
	    elif msg_num== 3: ins = ais.ais_msg_3_handcoded.sqlInsert(ais.ais_msg_3_handcoded.decode(bv),dbType='sqlite')
	    elif msg_num== 4: ins = ais.ais_msg_4_handcoded.sqlInsert(ais.ais_msg_4_handcoded.decode(bv),dbType='sqlite')
	    elif msg_num== 5: ins = ais.ais_msg_5.sqlInsert(ais.ais_msg_5.decode(bv),dbType='sqlite')
            elif msg_num==18: ins = ais.ais_msg_18.sqlInsert(ais.ais_msg_18.decode(bv),dbType='sqlite') # Class B position
            elif msg_num==19: ins = ais.ais_msg_19.sqlInsert(ais.ais_msg_19.decode(bv),dbType='sqlite') # Class B position
            else:
		print 'Warning... not handling type',msg_num,'line:',lineNum
		continue
	except:
	    print 'ERROR:  some decode error?','line:',lineNum
	    print '  ',line
	    continue

	counts[msg_num] += 1

	if uscg:
            from aisutils.uscg import uscg_ais_nmea_regex
            match = uscg_ais_nmea_regex.search(line).groupdict()
            
            try:
                cg_sec = int(float(match['timeStamp']))
                ins.add('cg_sec', cg_sec)
                #ins.add('cg_sec', int(float(match['timeStamp'])) )
                ins.add('cg_timestamp', str(datetime.datetime.utcfromtimestamp(float(match['timeStamp']))) )
                ins.add('cg_r', match['station'] )
            except:
                print >> sys.stderr, match
                print >> sys.stderr, 'bad uscg sections',line,
                continue

            # Optional fields that are not always there

            if match['time_of_arrival'] is not None:
                try:
                    ins.add('cg_t_arrival',  float(match['time_of_arrival']))
                except:
                    print >> sys.stderr, 'WARNING: corrupted time of arrival (T) in line.  T ignored\n\t',line
                    pass # Not critical if corrupted
                

            if match['slot'] is not None:
                ins.add('cg_s_slotnum',  int(match['slot']) )

        if msg_num in (1,2,3,4):
            pkt_id,dup_flag = track_dups.check_packet(cg_sec,fields[5]) # Pass in the NMEA payload string of data
            if v:
                print 'dup_check:',pkt_id,dup_flag,fields[5]
            ins.add('pkt_id',pkt_id)
            ins.add('dup_flag',dup_flag)


        ins.add('key',next_key)
        next_key += 1

	if verbose: 
            print str(ins)
	try:
            cu.execute(str(ins))
        except pysqlite2.dbapi2.OperationalError, params:
	#except OperationalError,  params:
            if -1 != params.message.find('no such table'):
                print 'ERROR:',params.message
                sys.exit('You probably need to run with --with-create')
            print 'params',params
            print type(params)
	    print 'ERROR: sql error?','line:',lineNum
	    print '  ', str(ins)
	    print '  ',line

            if False:
                # Give some debugging flexibility
                from IPython.Shell import IPShellEmbed
                ipshell = IPShellEmbed(argv=[])
                ipshell() 
                sys.exit('Gave up')

#        if payload_table and msg_num in (1,2,3):
#            payload = fields[5]
#            key = cu.execute('SELECT key from')

    print counts
    cx.commit()
	

############################################################
if __name__=='__main__':
    from optparse import OptionParser
    parser = OptionParser(usage="%prog [options] file1.ais [file2.ais ...]",version="%prog "+__version__)

    parser.add_option('-d','--database-file',dest='databaseFilename',default='ais.db3',
                      help='Name of the python file to write [default: %default]')
    parser.add_option('-C','--with-create',dest='create_tables',default=False, action='store_true',
                      help='Do not create the tables in the database')

    parser.add_option('--without-uscg',dest='uscgTail',default=True,action='store_false',
                      help='Do not look for timestamp and receive station at the end of each line [default: with-uscg]')

#    parser.add_option('-p','--payload-table', dest='payload_table', default=False, action='store_true',
#                      help='Add an additional table that stores the NMEA payload text')

    parser.add_option('-v','--verbose',dest='verbose',default=False,action='store_true',
                      help='Make program output more verbose info as it runs')

    (options,args) = parser.parse_args()
    cx = sqlite.connect(options.databaseFilename)

    if options.create_tables:
        create_tables(cx, verbose=options.verbose)
#        create_tables(cx, options.payload_table, verbose=options.verbose)

   
    
    if len(args)==0:
        args = (sys.stdin,)
        print 'processing from stdin'

    for filename in args:
        print 'processing file:',filename
        load_data(
            cx, 
            file(filename,'r'), 
            verbose=options.verbose,
            uscg=options.uscgTail, 
            )
#            payload_table=options.payload_table
