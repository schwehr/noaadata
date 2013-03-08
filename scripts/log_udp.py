#!/usr/bin/env python

import socket
import time
from noaadata.aisutils import server

host='0.0.0.0' # All interfaces
port=4000
buffer = 10000

sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
sock.bind((host,port))

log = server.LogFileWithRotate('log-ccom-wx-','rnhccom',True,True)

while 1:
    data,addr = sock.recvfrom(buffer)
    
    if not data:
        log.write("NO DATA")
	break
    else:
        timestamp = time.time()
    log_str = '%s,%s' % (data.strip(),addr[0])
    #print log_str
    log.write(log_str,verbose=True)
