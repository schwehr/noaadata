#!/usr/bin/env python
__author__ = 'Kurt Schwehr'
__version__ = '$Revision: 2275 $'.split()[1]
__revision__  = __version__ # For pylint
__date__ = '$Date: 2006-07-10 16:22:35 -0400 (Mon, 10 Jul 2006) $'.split()[1]
__copyright__ = '2008'
__license__   = 'Apache 2.0'

__doc__='''
Connect to N-AIS and pump the data into Postgres/Postgis.  This is a
non-threaded rewrite of ais-port-forward and ais-net-to-postgis.
Which are just cranky.

@since: 05-May-2009
'''

errors_file = file('errors-nais2postgis','w+')

import traceback, exceptions

import sys
import time
import socket
import select
import exceptions # For KeyboardInterupt pychecker complaint
import logging # Python's logger module for tracking progress
import aisutils.daemon
import aisutils.uscg
import aisutils.normalize

import ais.sqlhelp
import aisutils.database

#import ais.ais_msg_1 as msg1
import ais

from ais.ais_msg_1 import NavigationStatusDecodeLut
from ais.ais_msg_5 import shipandcargoDecodeLut

#ais_msgs_supported = ('B','C','H')
ais_msgs_supported = ('1','2','3','4','5','B','H') # ,'C', 'H')
''' Which AIS messages will be handled.  The rest will be dropped. '''

def rebuild_track_line(cu,userid,name,start_time=None,point_limit=50):
    q = 'SELECT AsText(position) FROM position WHERE userid=%s ORDER BY cg_sec DESC LIMIT %s;'

    cu.execute(q,(userid, point_limit))
    linePoints=[]
    for row in cu.fetchall():
        x,y = row[0].split()
        x = x.split('(')[1]
        y = y.split(')')[0]
        if x=='181' and y=='91':
            continue
        linePoints.append(row[0].split('(')[1].split(')')[0])
    if len(linePoints)<2:
        #print 'Not enough points.  Delete if exists'
        cu.execute('DELETE FROM track_lines WHERE userid = %s;',(userid,))
        return
    lineWKT='LINESTRING('+','.join(linePoints)+')'

    cu.execute('DELETE FROM track_lines WHERE userid=%s;', (userid,) )
    q = 'INSERT INTO track_lines (userid,name,track) VALUES (%s,%s,GeomFromText(%s,4326));'
    cu.execute(q, (userid,name,lineWKT) )


def rebuild_b_track_line(cu,userid,name,start_time=None,point_limit=50):

    q = 'SELECT AsText(position) FROM positionb WHERE userid=%s ORDER BY cg_sec DESC LIMIT %s;'

    cu.execute(q,(userid, point_limit))
    linePoints=[]
    for row in cu.fetchall():
        x,y = row[0].split()
        x = x.split('(')[1]
        y = y.split(')')[0]
        if x=='181' and y=='91':
            continue
        linePoints.append(row[0].split('(')[1].split(')')[0])
    if len(linePoints)<2:
        #print 'Not enough points.  Delete if exists'
        cu.execute('DELETE FROM track_lines WHERE userid = %s;',(userid,))
        return
    lineWKT='LINESTRING('+','.join(linePoints)+')'

    cu.execute('DELETE FROM track_lines WHERE userid=%s;', (userid,) )
    q = 'INSERT INTO track_lines (userid,name,track) VALUES (%s,%s,GeomFromText(%s,4326));'
    cu.execute(q, (userid,name,lineWKT) )


    return


def handle_insert_update(cx, uscg_msg, msg_dict, aismsg):
    db_uncommitted_count = 0 # how many commits were done... return this

    msg_type = msg_dict['MessageID']

    userid = int(msg_dict['UserID'])

    cu = cx.cursor()

    if msg_type in (1,2,3):
        x = msg_dict['longitude']
        y = msg_dict['latitude']

        #print 'FIX:',x,y

        if x > 180 or y > 90:
            return # 181, 91 is the invalid gps value

        if options.lon_min is not None and options.lon_min > x: return
        if options.lon_max is not None and options.lon_max < x: return
        if options.lat_min is not None and options.lat_min > y: return
        if options.lat_max is not None and options.lat_max < y: return

        ins = aismsg.sqlInsert(msg_dict, dbType='postgres')
        ins.add('cg_sec',       uscg_msg.cg_sec)
        ins.add('cg_timestamp', uscg_msg.sqlTimestampStr)
        ins.add('cg_r',         uscg_msg.station)

        try:
            cu.execute(str(ins))
            #print 'Added pos'
        except Exception,e:
            errors_file.write('pos SQL INSERT ERROR for line: %s\t\n',str(msg_dict))
            errors_file.write(str(ins))
            errors_file.write('\n')
            errors_file.flush()
            traceback.print_exc(file=errors_file)
            traceback.print_exc()
            sys.stderr.write('\n\nBAD DB INSERT\n\n')
            return False


        db_uncommitted_count += 1

        navigationstatus = msg_dict['NavigationStatus']
        shipandcargo = 'unknown'
        cg_r = uscg_msg.station

        if str(navigationstatus) in NavigationStatusDecodeLut:
            navigationstatus = NavigationStatusDecodeLut[str(navigationstatus)]

        # get key of the old value
        cu.execute('SELECT key FROM last_position WHERE userid=%s;', (userid,))
        row = cu.fetchall()
        if len(row)>0:
            cu.execute('DELETE FROM last_position WHERE userid = %s;', (userid,))
        cu.execute('SELECT name,shipandcargo FROM shipdata WHERE userid=%s LIMIT 1;',(userid,))
        row = cu.fetchall()
        if len(row)>0:
            name = row[0][0].rstrip(' @')
            shipandcargo = int(row[0][1])
            if str(shipandcargo) in shipandcargoDecodeLut:
                shipandcargo = shipandcargoDecodeLut[str(shipandcargo)]
                if len(shipandcargo) > 29:
                    shipandcargo = shipandcargo[:29]
            else:
                shipandcargo = str(shipandcargo)

        else:
            name = str(userid)

        q = 'INSERT INTO last_position (userid,name,cog,sog,position,cg_r,navigationstatus, shipandcargo) VALUES (%s,%s,%s,%s,GeomFromText(\'POINT('+str(msg_dict['longitude'])+' '+str(msg_dict['latitude']) +')\',4326),%s,%s,%s);'

        if msg_dict['COG'] == 511:
            msg_dict['COG'] = 0 # make unknowns point north

        cu.execute(q,(userid,name,msg_dict['COG'],msg_dict['SOG'],cg_r,navigationstatus,shipandcargo))

        # drop the old value
        rebuild_track_line(cu,userid,name)  # This will leave out the current point

        return True # need to commit db

    if msg_type == 4:
        cu.execute('DELETE FROM bsreport WHERE userid = %s;',(userid,))
        db_uncommitted_count += 1

        ins = aismsg.sqlInsert(msg_dict, dbType='postgres')
        ins.add('cg_sec',       uscg_msg.cg_sec)
        ins.add('cg_timestamp', uscg_msg.sqlTimestampStr)
        ins.add('cg_r',         uscg_msg.station)

        cu.execute(str(ins))

        return True # need to commit db

    if msg_type == 5:
        cu.execute('DELETE FROM shipdata WHERE userid = %s;',(userid,))

        ins = aismsg.sqlInsert(msg_dict, dbType='postgres')
        ins.add('cg_sec',       uscg_msg.cg_sec)
        ins.add('cg_timestamp', uscg_msg.sqlTimestampStr)
        ins.add('cg_r',         uscg_msg.station)

        try:
            cu.execute(str(ins))
        except Exception,e:
            #errors_file = file('errors-nais2postgis','w+')
            errors_file.write('SQL INSERT ERROR for line: %s\t\n',str(msg_dict))
            errors_file.write(str(ins))
            errors_file.write('\n')
            errors_file.flush()
            traceback.print_exc(file=errors_file)
            traceback.print_exc()
            sys.stderr.write('\n\nBAD DB INSERT\n\n')
            return False

        return True # need to commit db

    if msg_type == 18:

        x = msg_dict['longitude']
        y = msg_dict['latitude']

        if x > 180 or y > 90:
            return # 181, 91 is the invalid gps value
        #print 'trying class b',x,y

        if options.lon_min is not None and options.lon_min > x: return
        if options.lon_max is not None and options.lon_max < x: return
        if options.lat_min is not None and options.lat_min > y: return
        if options.lat_max is not None and options.lat_max < y: return

        #print 'inserting class b'

        ins = aismsg.sqlInsert(msg_dict, dbType='postgres')
        ins.add('cg_sec',       uscg_msg.cg_sec)
        ins.add('cg_timestamp', uscg_msg.sqlTimestampStr)
        ins.add('cg_r',         uscg_msg.station)

        cu.execute(str(ins))

        #navigationstatus = msg_dict['NavigationStatus']
        shipandcargo = 'unknown'
        cg_r = uscg_msg.station

        cu.execute('SELECT key FROM last_position WHERE userid=%s;', (userid,))
        row = cu.fetchall()
        if len(row)>0:
            cu.execute('DELETE FROM last_position WHERE userid = %s;', (userid,))

        cu.execute('SELECT name FROM b_staticdata WHERE partnum=0 AND userid=%s LIMIT 1;',(userid,))
        row = cu.fetchall()
        if len(row)>0:
            name = row[0][0].rstrip(' @')
        else:
            name = str(userid)

        cu.execute('SELECT shipandcargo FROM b_staticdata WHERE partnum=1 AND userid=%s LIMIT 1;',(userid,))
        row = cu.fetchall()
        if len(row)>0:
            shipandcargo = int(row[0][0])
            if str(shipandcargo) in shipandcargoDecodeLut:
                shipandcargo = shipandcargoDecodeLut[str(shipandcargo)]
                if len(shipandcargo) > 29:
                    shipandcargo = shipandcargo[:29]
            else:
                shipandcargo = str(shipandcargo)

        # FIX: add navigation status
        q = 'INSERT INTO last_position (userid,name,cog,sog,position,cg_r,shipandcargo) VALUES (%s,%s,%s,%s,GeomFromText(\'POINT('+str(msg_dict['longitude'])+' '+str(msg_dict['latitude']) +')\',4326),%s,%s);'

        if msg_dict['COG'] == 511:
            msg_dict['COG'] = 0 # make unknowns point north

        cu.execute(q,(userid,name,msg_dict['COG'],msg_dict['SOG'],cg_r,shipandcargo) )

        rebuild_b_track_line(cu,userid,name)

        return True # need to commit db


    if msg_type == 19: # Class B extended report
        cu.execute ('DELETE FROM b_pos_and_shipdata WHERE userid=%s AND partnum=%s;', (userid,msg_dict['partnum']))

        ins = aismsg.sqlInsert(msg_dict, dbType='postgres')
        ins.add('cg_sec',       uscg_msg.cg_sec)
        ins.add('cg_timestamp', uscg_msg.sqlTimestampStr)
        ins.add('cg_r',         uscg_msg.station)
        print 'msg 19:',str(ins)

        cu.execute(str(ins))

        return True # need to commit db

    if msg_type == 24: # Class B static data report.  Either part A (0) or B (0)
        # remove the old value, but only do it by parts
        cu.execute ('DELETE FROM b_staticdata WHERE userid=%s AND partnum=%s;', (userid,msg_dict['partnum']))

        ins = aismsg.sqlInsert(msg_dict, dbType='postgres')
        ins.add('cg_sec',       uscg_msg.cg_sec)
        ins.add('cg_timestamp', uscg_msg.sqlTimestampStr)
        ins.add('cg_r',         uscg_msg.station)

        cu.execute(str(ins))

        return True

    return False # No db commit needed


class Nais2Postgis:
    def __init__(self,options):
        self.v = options.verbose
        self.options = options
        self.timeout=options.timeout
        self.nais_connected = False
        self.loop_count = 0
        self.nais_src = None
        self.cx = aisutils.database.connect(options, dbType='postgres')
        self.cu = self.cx.cursor()
        self.norm_queue = aisutils.normalize.Normalize() # for multipart messages
        self.bad = file('bad.ais','w')

        # Database commit handling... only commit every so often to
        self.db_last_commit_time = 0
        self.db_uncommitted_count = 0


    def do_one_loop(self):
        '''
        @return: true on success, false if disconnected or other error.
        '''


        connection_attempts = 0
        while not self.nais_connected:
            self.loop_count += 1
            connection_attempts += 1
            if connection_attempts%100 == 1:
                logging.warn('Connecting to NAIS')
                sys.stderr.write('connecting to %s:%d\n' %
                                 (str(self.options.inHost), self.options.inPort))
            try:
                self.nais_src = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.nais_src.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                self.nais_src.connect((self.options.inHost, self.options.inPort))
            except socket.error, inst:
                if self.loop_count%50 == 0:
                    sys.stderr.write('%d : Failed to connect to nais_src ... %s\tWill try again\n' %
                                     (self.loop_count,str(inst)))
                time.sleep(.5)
            else:
                self.nais_connected=True
                logging.warn('Connected to NAIS')
                sys.stderr.write('Connected...\n')
            #time.sleep(.1)


        readersready,outputready,exceptready = select.select([self.nais_src,],[],[],self.timeout)

        if len(readersready) == 0:
            return

        for sock in readersready:
            msgs = sock.recv(10000)
            if len(msgs)==0:
                self.nais_connected=False
                logging.warn('DISCONNECT from NAIS\n')
                sys.stderr.write('DISCONNECT from NAIS\n')
            if self.v:
                sys.stderr.write('recved %d bytes: %s\n' % (len(msgs),msgs.strip()) )

        if not self.nais_connected:
            return False

        #
        # FIX: does not handle partial messages coming through!
        #

        for msg in msgs.split('\n'):
            msg = msg.strip()
            if 'AIVDM'!= msg[1:6]: continue
            try:
                self.norm_queue.put(msg)
            except Exception, e:
                sys.stderr.write('Bad AIVDM message: %s\n' % (msg,))
                sys.stderr.write('   Exception:' + str(type(Exception))+'\n')
                sys.stderr.write('   Exception args:'+ str(e)+'\n')
                traceback.print_exc(file=sys.stderr)
                continue


        while self.norm_queue.qsize() > 0:
            #print 'norm_queue loop',self.norm_queue.qsize()
            msg = self.norm_queue.get()

            try:
                uscg_msg = aisutils.uscg.UscgNmea(msg)
            except Exception, e:
                logging.exception('uscg decode exception %s for msg: %s' % (str(e),msg))
                self.bad.write('uscg decode exception %s for msg: %s' % (str(e),msg ) )
                #self.bad.write(msg+'\n')
                continue

            # FIX: hack for ERMA
#            if uscg_msg.station not in ('r01SPHA1', 'r07CSJU1', 'r07XPON1'):
                # If it's not Portsmouth, NH or Puerto Rico, do not deal with the message
#                continue

            #print 'MSG CHAR',uscg_msg.msgTypeChar,'     ',ais_msgs_supported
            if uscg_msg.msgTypeChar not in ais_msgs_supported:
                #logging.warn('msg not supportd "%s"' % (msg[7],))
                continue
            #else:
                #print 'allowing',uscg_msg.msgTypeChar
                #print '  ',msg

            try:
                aismsg = ais.msgModByFirstChar[uscg_msg.msgTypeChar]
            except Exception, e:
                sys.stderr.write('   Dropping unknown msg type: %s\n\t%s\n' % (uscg_msg.msgTypeChar,str(e),) )
                self.bad.write(msg+'\n')
                continue

            bv = ais.binary.ais6tobitvec(uscg_msg.contents)
            try:
                msg_dict = aismsg.decode(bv)
            except Exception, e:
                sys.stderr.write('   Dropping bad msg and calling continue: %s,%s\n' % (str(e),msg,) )
                self.bad.write(msg+'\n')
                continue


            #print msg_dict
            #print 'uscg_msg:',type(uscg_msg)
            try:
                if handle_insert_update(self.cx, uscg_msg, msg_dict, aismsg):
                    self.db_uncommitted_count += 1

            except Exception, e:
                sys.stderr.write('*** handle_insert_update exception\n')
                sys.stderr.write('   Exception:' + str(type(Exception))+'\n')
                sys.stderr.write('   Exception args:'+ str(e)+'\n')
                traceback.print_exc(file=sys.stderr)
                self.bad.write(msg+'\n')
                self.cx.commit() # reset the transaction

        #print 'Should commit?',self.db_last_commit_time, time.time() - self.db_last_commit_time, self.db_uncommitted_count

        # Check on database commits
        if (self.db_last_commit_time is None) or (time.time() - self.db_last_commit_time > 30. and self.db_uncommitted_count > 0):
            #print 'committing:',self.db_last_commit_time,self.db_uncommitted_count
            self.db_last_commit_time = time.time()
            self.db_uncommitted_count = 0
            try:
                #print 'Committing'
                self.cx.commit()
                #print '  Successful'
            except Exception, e:
                # FIX: What are we likely to see here?
                sys.stderr.write('*** handle_insert_update exception\n')
                sys.stderr.write('   Exception:' + str(type(Exception))+'\n')
                sys.stderr.write('   Exception args:'+ str(e)+'\n')
                traceback.print_exc(file=sys.stderr)
                self.bad.write(msg+'\n')
                time.sleep(.1)
                self.cx.commit() # reset the transaction


######################################################################


if __name__=='__main__':
    from optparse import OptionParser

    # FIX: is importing __init__ safe?
    parser = OptionParser(usage="%prog [options]"
                          ,version="%prog "+__version__ + " ("+__date__+")")

    parser.add_option('-i','--in-port',dest='inPort',type='int', default=31414
                      ,help='Where the data comes from [default: %default]')
    parser.add_option('-I','--in-host',dest='inHost',type='string',default='localhost'
                      ,help='What host to read data from [default: %default]')
    parser.add_option('--in-gethostname',dest='inHostname', action='store_true', default=False
                        ,help='Where the data comes from [default: %default]')

    parser.add_option('-t','--timeout',dest='timeout',type='float', default='5'
                      ,help='Number of seconds to timeout after if no data [default: %default]')

#    parser.add_option('-a','--add-station',action='append',dest='allowStations'
#                      ,default=None
#                      ,help='Specify limited set stations to forward (e.g. r003679900) [default: all]')

#    parser.add_option('-x','--lon-min', dest='lon_min', type='float', default=-71
    parser.add_option('-x','--lon-min', dest='lon_min', type='float', default=None
                      ,help=' [default: %default]')
    parser.add_option('-X','--lon-max', dest='lon_max', type='float', default=None
                      ,help=' [default: %default]')

#    parser.add_option('-y','--lat-min', dest='lat_min', type='float', default=42
    parser.add_option('-y','--lat-min', dest='lat_min', type='float', default=None
                      ,help=' [default: %default]')
    parser.add_option('-Y','--lat-max', dest='lat_max', type='float', default=None
                      ,help=' [default: %default]')


    aisutils.daemon.stdCmdlineOptions(parser, skip_short=True)

    aisutils.database.stdCmdlineOptions(parser, 'postgres')

    parser.add_option('-v','--verbose',dest='verbose',default=False,action='store_true'
                      ,help='Make the test output verbose')

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

    sys.stderr.write('Bounding box: X: %s to %s \t\t Y: %s to %s\n' % (options.lon_min,options.lon_max,options.lat_min,options.lat_max))

    if options.inHostname:
        options.inHost=socket.gethostname()

    if options.daemon_mode:
        aisutils.daemon.start(options.pid_file)

    logging.basicConfig(filename = options.log_file
                        , level  = options.log_level
                        )

    n2p = Nais2Postgis(options)
    loop_count=0
    while True:
        loop_count += 1
        if 0 == loop_count % 1000:
            print 'top level loop',loop_count
        try:
            n2p.do_one_loop()
        except Exception, e:
            sys.stderr.write('*** do_one_loop exception\n')
            sys.stderr.write('   Exception:' + str(type(Exception))+'\n')
            sys.stderr.write('   Exception args:'+ str(e)+'\n')
            traceback.print_exc(file=sys.stderr)
            continue

        time.sleep(0.01)
