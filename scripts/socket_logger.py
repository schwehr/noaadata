#!/usr/bin/env python
__version__ = '$Revision: 7470 $'.split()[1]
__date__ = '$Date: 2007-11-06 10:31:44 -0500 (Tue, 06 Nov 2007) $'.split()[1]
__author__ = 'Kurt Schwehr'

__doc__="""
FIX: write a description

@requires: U{epydoc<http://epydoc.sourceforge.net/>} > 3.0alpha3

@author: """+__author__+"""
@version: """ + __version__ +"""
@var __date__: Date of last svn commit
@undocumented: __version__ __author__ __doc__ parser
@status: under development
@license: GPL v2
@since: 2007-Mar-05
@organization: U{CCOM<http://ccom.unh.edu/>}

@todo: give this a optparse interface
@todo: make it flexible.

"""

import socket,select
import sys
import time

o = file('norfolk-log.ais','a')
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('10.1.1.29', 5505))
s.send("$xxBSQ,ACA,*03\x0D\x0A")
buf=''
while True:
    readersready,outputready,exceptready = select.select([s],[],[],.1)
    for sock in readersready:
        data = sock.recv(100)
        buf += data
        newline=buf.find('\n')
        if -1!=newline:
            fields = buf.split('\n')
            msg=fields[0].strip()+','+str(time.time())
            print msg
            o.write(msg+'\n')
            if len(fields)>1:
                buf=''+buf[newline+1:]
            else:
                buf=''

