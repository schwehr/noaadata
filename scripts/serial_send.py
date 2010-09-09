#!/usr/bin/env python

__version__ = '$Revision: 10544 $'.split()[1]
__date__ = '$Date: 2008-10-14 19:30:01 -0400 (Tue, 14 Oct 2008) $'.split()[1]
__author__ = 'Kurt Schwehr'

DOS_EOL = "\x0D\x0A"
'''
DOS style end-of-line (<cr><lf>) for talking to AIS base stations
'''
EOL=DOS_EOL
EOL='\r\n'

import os, time, serial

if __name__=='__main__':
    from optparse import OptionParser

    parser = OptionParser(usage="%prog [options]",
                            version="%prog "+__version__)

    defaultPorts = {'Darwin':'/dev/tty.KeySerial1', 'Linux':'/dev/ttyS0'}
    defaultPort = '/dev/ttyS0'
    if os.uname()[0] in defaultPorts: defaultPort=defaultPorts[os.uname()[0]]

    parser.add_option('-p','--port',dest='port',type='string', default=defaultPort,
                      help='What serial port device to option [default: %default]')

    #speeds=serial.baudEnumToInt.keys()
    #speeds.sort()
    speeds=[ #0, 50, 75, 110,
            #134, 150, 200, 
            300, 
            600, 
            1200, 
            1800, 
            2400, 
            4800, 
            9600,
            19200, 38400, 57600, 115200, 230400
            ]

    speeds=[str(s) for s in speeds]

    parser.add_option('-b','--baud',dest='baud',
                      choices=speeds, type='choice', default='38400',
                      help='Port speed [default: %default].  Choices: '+', '.join(speeds))

    parser.add_option('-t', '--timeout', dest='timeout', type='float', default='1',
                      help='Number of seconds to timeout after if no data [default: %default]')

    parser.add_option('-n', '--number-listens', dest='num_listens', type='int', default='10',
                      help='Number of loops to listen for responses [default: %default]')

    (options,args) = parser.parse_args()
    #options.timeout=10

    options.baud = int(options.baud)

    if 0==len(args):
        print 'NOTHING TO SEND'

    time.sleep(.1)
    for arg in args:
        print 'sending',arg


        ser = serial.Serial(options.port,options.baud,timeout=options.timeout)
        print 'sending "%s"' % arg.strip()
        ser.write(arg.strip()+EOL)
        print 'sent at',time.time()

        time.sleep(.1)

        for i in range(options.num_listens):
            line = ser.readline().strip()
            #line = ser.read(100).strip()
            print time.time(),'returned: "'+str(line)+'"'
            time.sleep(.1)
