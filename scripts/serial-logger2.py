#!/usr/bin/env python
__author__    = 'Kurt Schwehr'
__version__   = '$Revision: 8524 $'.split()[1]
__revision__  = __version__
__date__      = '$Date: 2008-02-05 11:03:16 -0500 (Tue, 05 Feb 2008) $'.split()[1]
__copyright__ = '2007-2009'
__license__   = 'GPL v3'
__doc__ = '''
Simple serial port logger.  Log times added to the stream are in UTC
seconds since the Epoch (UTC).

Modified by Chaoyi Yin Fall 2009.

@requires: U{epydoc<http://epydoc.sourceforge.net/>} > 3.0alpha3
@requires: U{pyserial<http://pyserial.sourceforge.net/>}
@status: under development
@since: 2007-Feb-17
@undocumented: __doc__ parser defaultPort defaultPorts speeds
@todo: Add a line for STOP LOGGING when a log file is closed
@todo: Add lines at start of logging for computer name, user name, and ???
@todo: Follow up on suggestions from A. Maitland Bottom
@todo: Optional WWW and UDP transmitting
@todo: Clean way to shut down
'''

import os,socket,serial
import logging
from lockfile import LockFailed
from logger_handlers import MidnightRotatingFileHandler, PassThroughServerHandler

class SerialLoggerFormatter:
    def __init__(self, uscgFormat=True, mark=True, stationId=None):
        self.uscgFormat = uscgFormat
        self.mark = mark
        self.stationId = stationId

    def format(self, record):
        record.message = record.getMessage()
        line = record.message.strip()
        if len(line) == 0:
            if self.mark:
                s = '# MARK: '+str(record.created)
            else:
                s = ''
        else:
            if self.uscgFormat:
                s = record.message
                if self.stationId:
                    s += ',r' + self.stationId
                s += ','+str(record.created)
            else:
                s = '# ' + str(record.created) + '\n'
                s += record.message
        return s

def run(options):
    ser = serial.Serial(options.port, options.baud, timeout=options.timeout)

    logger = logging.getLogger("root")
    logger.setLevel(logging.INFO)
    formatter = SerialLoggerFormatter(uscgFormat=options.uscgFormat,
                                      mark=options.mark,
                                      stationId=options.stationId)
    
    prologue = '# START LOGGING UTC seconds since the epoch: %(created)f\n'
    prologue+='# SPEED:       ' + str(options.baud)+'\n'
    prologue+='# PORT:        ' + str(options.port)+'\n'
    prologue+='# TIMEOUT:     ' + str(options.timeout)+'\n'
    prologue+='# STATIONID:   ' + str(options.stationId)+'\n'
    prologue+='# DAEMON MODE: ' + str(options.daemonMode)+'\n'
    # getlogin is not happy as a daemon
    #prologue+='# USER:        ' + str(os.getlogin())+'\n'
    epilogue = '# STOP LOGGING UTC seconds since the epoch: %(created)f\n'
    rollover = "# Log roll over\n"
    fh = MidnightRotatingFileHandler(options.log_prefix,
                                     epilogue=epilogue,
                                     prologue=prologue,
                                     rollover=rollover)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    if options.tcpOutput:
        ptsh = PassThroughServerHandler(options)
        ptsh.setFormatter(formatter)
        logger.addHandler(ptsh)

    if not options.daemonMode:
        ch = logging.StreamHandler()
        ch.setFormatter(formatter)
        logger.addHandler(ch)
    
    while True:
        # import time
        # time.sleep(5)
        # logger.info("hello")
        line = ser.readline().strip()
        logger.info(line)

def parseOptions():
    from optparse import OptionParser

    parser = OptionParser(usage="%prog [options]",
                          version="%prog "+__version__)

    #################### log 
    parser.add_option('-l', '--log-prefix', dest='log_prefix', type='string', default='log',
                      help='prefix before date of the log file [default: %default]')

    parser.add_option('-v', '--verbose', dest='verbose', default=False, action='store_true',
                      help='Make the test output verbose')

    # not used below
    parser.add_option('-F', '--no-flush', dest='flush', default=True, action='store_false',
                      help='Do not flush after each write')

    #################### log format
    parser.add_option('-m', '--mark-timeouts', dest='mark', default=False, action='store_true',
                      help='Mark the timeouts in the log file')

    parser.add_option('-u', '--uscg-format', dest='uscgFormat', default=False, action='store_true',
                      help='Switch to the USCG N-AIS format with ",station,UTC sec" at the end of each line')

    parser.add_option('-s', '--station-id', dest='stationId', type='string', default=None,
                      help='If uscg format is selected, you can specify a station id to'
                      +' put as ",r" before the timestamp  [default: %default]')

    #################### daemon
    parser.add_option('-d'
                      ,'--daemon'
                      ,dest='daemonMode'
                      ,default=False,action='store_true'
                      ,help='Detach from the terminal and run as a daemon service.'
                      +'  Returns the pid. [default: %default]')

    parser.add_option('--pid-file'
                      ,dest='pidFile'
                      ,default="lock"
                      ,help='Where to write the process id when in daemon mode')


    parser.add_option('-w', '--working-directory',
                      dest='working_directory',
                      type='string',
                      default=os.path.abspath(os.path.curdir),
                      help='daemon working directory [default: %default]')

    #################### pts
    parser.add_option('--enable-tcp-out', dest='tcpOutput', default=False, action='store_true',
                      help='Create a server that clients can connect to and receive data')
    parser.add_option('-o','--out-port', dest="outPort", type='int',default=31500,
                      help='Where the data will be available to others [default: %default]')
    parser.add_option('-O','--out-host',dest='outHost',type='string', default='localhost',
                      help='What machine the source port is on [default: %default]')
    # not used below
    parser.add_option('--out-gethostname',dest='outHostname', action='store_true', default=False,
                      help='Use the default hostname ['+socket.gethostname()+']')
    parser.add_option('-a','--allow',action='append',dest='hosts_allow'
                      ,help='Add hosts to a list that are allowed to connect [default: all]')

    #################### serial

    default_ports = {'Darwin':'/dev/tty.KeySerial1', 'Linux':'/dev/ttyS0'}
    default_port = '/dev/ttyS0'
    if os.uname()[0] in default_ports:
        default_port = default_ports[os.uname()[0]]

    parser.add_option('-p'
                      ,'--port'
                      ,dest='port'
                      ,type='string'
                      ,default=default_port,
                      help='What serial port device to option [default: %default]')

    #speeds=serial.baudEnumToInt.keys()
    #speeds.sort()
    speeds = [
        #0, 50, 75, 110,
        #134, 150, 200, 
        300
        ,600 
        ,1200, 1800, 2400, 4800, 9600, 19200
        ,38400, 57600, 115200, 230400
            ]

    speeds = [str(s) for s in speeds]

    parser.add_option('-b', '--baud', dest='baud',
                      choices=speeds, type='choice', default='38400',
                      help='Port speed [default: %default].  Choices: '+', '.join(speeds))

    parser.add_option('-t', '--timeout', dest='timeout', type='float', default='300',
                      help='Number of seconds to timeout after if no data [default: %default]')

    options, arguments = parser.parse_args()
    options.baud = int(options.baud)

    return options

def main():
    options = parseOptions()

    if options.pidFile:
        from daemon import pidlockfile
        pidfile = pidlockfile.PIDLockFile(options.pidFile)
        try:
            pidfile.acquire(timeout=1.0)
            pidfile.release()
        except LockFailed:
            raise
    else:
        pidfile = None
        
    if options.daemonMode:
        from daemon import DaemonContext
        with DaemonContext(pidfile=pidfile, working_directory=options.working_directory):
            run(options)
    else:
        if pidfile:
            with pidfile:
                run(options)
        else:
            run(options)

if __name__ == '__main__':
    main()

