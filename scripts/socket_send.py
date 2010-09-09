#!/usr/bin/env python

__version__ = '$Revision: 7470 $'.split()[1]
__date__ = '$Date: 2007-11-06 10:31:44 -0500 (Tue, 06 Nov 2007) $'.split()[1]
__author__ = 'Kurt Schwehr'

__doc__='''
Send a message to a socket.  Used to control an AIS base station over ethernet.

@requires: U{lxml<http://codespeak.net/lxml/>} - For libxml2 ElementTree interface.  Not actually required for the template, but this is just a demo or requirements.
@requires: U{Python<http://python.org/>} >= 2.4
@requires: U{epydoc<http://epydoc.sourceforge.net/>} >= 3.0alpha3
@requires: BitVector

@author: U{'''+__author__+'''<http://schwehr.org/>}
@version: ''' + __version__ +'''
@copyright: 2006
@var __date__: Date of last svn commit
@undocumented: __version__ __author__ __doc__ parser
@since: 2007-Mar-05
@status: under development
@organization: U{CCOM<http://ccom.unh.edu/>}
@license: GPL v2
'''

import socket,select
import sys
import time


DOS_EOL = "\x0D\x0A"
'''
DOS style end-of-line (<cr><lf>) for talking to AIS base stations
'''
EOL=DOS_EOL


if __name__=='__main__':
    from optparse import OptionParser

    # FIX: is importing __init__ safe?
    parser = OptionParser(usage="%prog [options]",
                          version="%prog "+__version__ + " ("+__date__+")")

    parser.add_option('-p','--port',dest='port',type='int', default=5505
                      ,help='What TCP/IP port number [default: %default]')
    parser.add_option('-H','--host',dest='host',type='string',default='10.1.1.29'
                      ,help='Target host to send the data [default: %default]')

    parser.add_option('-d','--dos-eol',dest='eolDos',action='store_true'
                      ,help='Use dos style (<cr><lf>) newline [default]')
    parser.add_option('-u','--unix-eol',dest='eolDos',action='store_false',default=True
                      ,help='Use unix style (<lf>) newlines instead of DOS.')
    parser.add_option('-v','--verbose',dest='verbose',default=False,action='store_true',
                      help='run the tests run in verbose mode')

    parser.add_option('-r','--receive',dest='receive',default=True,action='store_true'
                      ,help='Receive on the port after transmitting [default: %default]')
    parser.add_option('-t','--time',dest='time',type='float',default=2
                      ,help='How many seconds to listen after each send [default: %default sec]')
    parser.add_option('-T','--uscg-timestamps',dest='uscgFormat',default=False,action='store_true',
                      help='Use USCG N-AIS format with ",UTCsec" at the end of each line')
    
#    parser.add_option('p','--query-prefix',default='xx'
#                      ,help=' [default: %default]')
#    
#    parser.add_option('-q','--query',default=None
#                      ,help='send a query (known choices: ACA, B[default: None]
#                      )

    (options,args) = parser.parse_args()
    verbose = options.verbose

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    if verbose: print 'connecting to',options.host+':'+str(options.port)
    s.connect((options.host, options.port))
    #s.send("$xxBSQ,ACA,*03\x0D\x0A")
    #s.send('$xxBSQ,CBM,*0C'+DOS_EOL)
    #s.send('$xxCAB,0,0,,*40'+EOL)
    #s.send("$xxBSQ,ACA,*03\x0D\x0A")

    buf=''
    for arg in args:
        if options.verbose: 
            print 'Using DOS EOL style:',options.eolDos
            print 'sending:',arg,['(unix newline)','(dos newline)'][int(options.eolDos)]

        if options.eolDos: arg+=DOS_EOL
        else: arg+='\n'
        s.send(arg)

        start = time.time()
        #print start
        while options.receive and ( time.time()-start < options.time ):
            #print time.time()-start
            readersready,outputready,exceptready = select.select([s],[],[],1)
            for sock in readersready:
                data = sock.recv(100)
                buf += data
                newline=buf.find('\n')
                if -1!=newline:
                    fields = buf.split('\n')
                    if options.uscgFormat: 
                        print fields[0].strip()+','+str(time.time())
                    else:
                        print fields[0].strip()
                    if len(fields)>1:
                        buf=''+buf[newline+1:]
                    else:
                        buf=''
    if len(buf)>0: print buf

    #s.send('$xxCAB,0,0,,*40'+EOL)
    #s.send('$xxCAB,1,1,1,1*40'+EOL)
    
