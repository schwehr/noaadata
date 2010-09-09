#!/usr/bin/env python
__author__ = 'Kurt Schwehr'
__version__ = '$Revision: 2275 $'.split()[1]
__revision__  = __version__ # For pylint
__date__ = '$Date: 2006-07-10 16:22:35 -0400 (Mon, 10 Jul 2006) $'.split()[1]
__copyright__ = '2008'
__license__   = 'GPL v3'
__contact__   = 'kurt at ccom.unh.edu'

__doc__='''
Feed AIS data to who ever connects at a moderated rate.

@var __date__: Date of last svn commit
@undocumented: __doc__ myparser
@status: under development
@since: 05-May-2009

@requires: U{Python<http://python.org/>} >= 2.5
'''

import sys

import time
import datetime

import socket
import thread
import select

import traceback
import exceptions


class DataServer:
    def __init__(self,options):
        self.options = options

    def run(self):
        datastream = file(self.options.datafile)

        inHost = self.options.inHost
        inPort = self.options.inPort
        timeout = self.options.timeout
        running = False

        serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        serversocket.bind((inHost, inPort))
        serversocket.listen(5)

        while True:
            

            (clientsocket, address) = serversocket.accept()
            sys.stderr.write('connect from '+str(clientsocket)+' '+str(address)+'\n')
            running = True
            while running:
                readersready, outputready, exceptready = select.select([],[clientsocket,],[],0)
                for sock in outputready:
                    data= datastream.readline()
                    print data.strip()
                    try:
                        sock.send(data)
                    except:
                        running = False
                time.sleep(self.options.delay)

def main():
    from optparse import OptionParser

    # FIX: is importing __init__ safe?
    parser = OptionParser(usage="%prog [options]",
                          version="%prog "+__version__ + " ("+__date__+")")

    parser.add_option('-i', '--in-port', dest='inPort', type='int', default=31414
                      , help='Where the data comes from [default: %default]')
    parser.add_option('-I', '--in-host', dest='inHost', type='string', default='localhost'
                      , help='What host to read data from [default: %default]')
    parser.add_option('--in-gethostname', dest='inHostname', action='store_true', default=False
                      , help='Where the data comes from [default: %default]')
    parser.add_option('-t', '--timeout', dest='timeout', type='float', default='3', 
                      help='Number of seconds to timeout after if no data [default: %default]')
    parser.add_option('-d', '--delay', dest='delay', type='float', default='.5', 
                      help='Number of seconds delay between sends [default: %default]')

    parser.add_option('-f', '--file', dest='datafile', default='uscg-logs-2009-05-06', 
                      help='data file to send [default: %default]')



    parser.add_option('-v', '--verbose', dest='verbose', default=False, action='store_true'
                      , help='Make the test output verbose')
    (options, args) = parser.parse_args()

    ds = DataServer(options)
    ds.run()



######################################################################
if __name__ == '__main__':
    main()
