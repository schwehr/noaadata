#!/usr/bin/env python
# -*- coding: utf-8 -*-

'Created Fall 2009 by Chaoyi Yin for Kurt Schwehr'

import os,sys,time
import logging
from logging.handlers import BaseRotatingHandler
import socket
import thread
import Queue

class MidnightRotatingFileHandler(BaseRotatingHandler):
    """
    Handler for logging to a file, rotating the log file every midnight.
    """
    def __init__(self, filename, delay=0, symlink=True, prologue=None, epilogue=None, rollover=None):
        self.prefix = filename + "-"
        self.suffix = "%Y-%m-%d"
        self.prologue = prologue
        self.epilogue = epilogue
        self.rollover = rollover
        self.symlink = symlink
        self.rolloverAt = self.computeRollover(int(time.time()))

        if symlink:
            self._symlinkPointToToday(filename)
            
        BaseRotatingHandler.__init__(self, filename, 'a', None, delay)
        # print "Will rollover at %d, %d seconds from now" % (self.rolloverAt, self.rolloverAt - currentTime)
        if self.prologue:
            self.stream.write(self.prologue % self._getParameter())


    def _symlinkPointToToday(self, filename):
        timeTuple = time.gmtime(time.time())        
        dfn = self.prefix + time.strftime(self.suffix, timeTuple)
        try:
            os.remove(filename)
        except OSError, detail:
            if detail.errno != 2:
                raise        
        os.symlink(dfn, filename)
        
    
    def computeRollover(self, currentTime):
        """
        Work out the rollover time based on the specified time.
        """
        t = time.gmtime(currentTime)
        currentHour = t[3]
        currentMinute = t[4]
        currentSecond = t[5]
        _MIDNIGHT = 24 * 60 * 60  # number of seconds in a day
        r = _MIDNIGHT - ((currentHour * 60 + currentMinute) * 60 + currentSecond)
        self.interval = _MIDNIGHT
        return currentTime + r

    def shouldRollover(self, record):
        """
        Determine if rollover should occur.

        record is not used, as we are just comparing times, but it is needed so
        the method signatures are the same
        """
        t = int(time.time())
        if t >= self.rolloverAt:
            return 1
        #print "No need to rollover: %d, %d" % (t, self.rolloverAt)
        return 0

    def doRollover(self):
        """
        do a rollover; in this case, a date/time stamp is appended to the filename
        when the rollover happens.  However, you want the file to be named for the
        start of the interval, not the current time.  If there is a backup count,
        then we have to get a list of matching filenames, sort them and remove
        theos one with the oldest suffix.
        """
        if self.stream:
            if self.epilogue:
                self.stream.write(self.epilogue % self._getParameter())
            
            # rollover
            if self.rollover:
                self.stream.write(self.rollover % self._getParameter())

            self.stream.close()
            
        self._doRollover()
        
        self.mode = 'w'            
        self.stream = self._open()
        currentTime = int(time.time())
        newRolloverAt = self.computeRollover(currentTime)
        while newRolloverAt <= currentTime:
            newRolloverAt = newRolloverAt + self.interval
        self.rolloverAt = newRolloverAt
        if self.prologue:
            self.stream.write(self.prologue % self._getParameter())


    def _doRollover(self):
        if self.symlink:
            self._symlinkPointToToday(self.baseFilename)
        else:
            # get the time that this sequence started at and make it a TimeTuple
            t = self.rolloverAt - self.interval
            timeTuple = time.gmtime(t)
            
            dfn = self.prefix + time.strftime(self.suffix, timeTuple)
            if os.path.exists(dfn):
                os.remove(dfn)
                os.rename(self.baseFilename, dfn)        
            #print "%s -> %s" % (self.baseFilename, dfn)        

    def _getParameter(self):
        d = {}
        d["created"] = time.time()
        return d


class PassThroughServerHandler(logging.Handler):
    '''Receive data from a socket and write the data to all clients that
    are connected.  Starts two threads and returns to the caller.

    Ripped out of port_server, but without the log file support
    '''
    def __init__(self,options):
        logging.Handler.__init__(self)
	self.clients=[]
	self.options = options
        self.q = Queue.Queue()
	self.count=0
        self.v = options.verbose
        self.start()

    def emit(self, record):
        msg = self.format(record)
        self.put("%s\n" % msg)

    def start(self):
	print 'starting threads'
	thread.start_new_thread(self.passdata,(self,))
	thread.start_new_thread(self.connection_handler,(self,))
	return

    def put(self,nmea_str):
        self.q.put(nmea_str)

    def passdata(self,unused=None):
	'''Do not use this.  Call start() instead.

	@bug: how can I get rid of unused?
	'''
	print 'starting passthrough server'

	while 1:
	    time.sleep(.001) # Replace with select
            m = self.q.get()
            if len(m) == 0:
                sys.stderr.write('No data in queue get\n')
                continue
            for c in self.clients:
                try:
                    if self.v:
                        sys.stderr.write('sending message %s' % m)
                        if m[-1] != '\n':
                            sys.stderr.write('\n')
                    c.send(m)
                except socket.error:
                    sys.stderr.write('Client Disconnect\n')
                    self.clients.remove(c)
	
    def connection_handler(self,unused=None):
	'''Do not use this.  Call start() instead.  This listens for
	connections and adds the new socket to the clients list.

	@bug: how can I get rid of unused?
	'''
	sys.stderr.write('starting incoming connection receiver\n')
	sys.stderr.write('  listening for connections at %s:%s\n' % (self.options.outHost, self.options.outPort))

        
	serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	serversocket.bind((self.options.outHost, self.options.outPort))
	serversocket.listen(5)

	while 1:
	    (clientsocket, address) = serversocket.accept()
	    sys.stderr.write('connect from %s\n' % (address,))
	    self.clients.append(clientsocket)    
