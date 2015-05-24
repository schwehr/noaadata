#!/usr/bin/env python
# License: Apache 2.0
"""Connect to the NOAA SOAP server and rebroadcast the results.

@author: U{'''+__author__+'''<http://schwehr.org/>}
@version: ''' + __version__ +'''
@copyright: (C) 2006 Kurt Schwehr

@bug: FIX: NOT WRITTEN YET.  Doh!
"""
import sys #, os, shutil
import time
import socket
import thread
import select


class TideDataServer:

    def __init__(self,options):
        self.running = True
        self.options = options


if __name__=='__main__':
    from optparse import OptionParser

    # FIX: is importing __init__ safe?
    parser = OptionParser(usage="%prog [options]",
                            version="%prog "+__version__+'  ('+__date__+')')

    parser.add_option('-i','--in-port',dest='inPort',type='int', default=31401,
			help='Where the data comes from [default: %default]')
    parser.add_option('-I','--in-host',dest='inHost',type='string',default='localhost',
			help='What host to read data from [default: %default]')
    parser.add_option('--in-gethostname',dest='inHostname', action='store_true', default=False,
			help='Where the data comes from ['+socket.gethostname()+']')


    parser.add_option('-o','--out-port', dest="outPort", type='int',default=31500,
			help='Where the data will be available to others [default: %default]')
    parser.add_option('-O','--out-host',dest='outHost',type='string', default='localhost',
			help='What machine the source port is on [default: %default]')
    parser.add_option('--out-gethostname',dest='outHostname', action='store_true', default=False,
			help='Use the default hostname ['+socket.gethostname()+']')
    parser.add_option('-v','--verbose',dest='verbose',default=False,action='store_true',
		      help='Make the test output verbose')
