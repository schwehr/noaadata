__author__    = 'Kurt Schwehr'
__version__   = '$Revision: 4799 $'.split()[1]
__revision__  = __version__ # For pylint
__date__ = '$Date: 2006-09-25 11:09:02 -0400 (Mon, 25 Sep 2006) $'.split()[1]
__copyright__ = '2008'
__license__   = 'GPL v3'
__contact__   = 'kurt at ccom.unh.edu'
__doc__ ='''
Tools to support writing python server programs.  Pulled from serial-logger.

@undocumented: __doc__
@since: 2008-Oct-16
@status: under development
@organization: U{CCOM<http://ccom.unh.edu/>}
'''

import datetime
import os
import time
import sys

SERIAL_SPEEDS = [
        #0, 50, 75, 110,
        #134, 150, 200,
        300
        ,600
        ,1200, 1800, 2400, 4800, 9600, 19200
        ,38400, 57600, 115200, 230400
            ]

def create_daemon():
    """nohup like function to detach from the terminal

    if options.daemonMode:
        create_daemon()
        if options.pidFile != None:
            open(options.pidFile, 'w').write(str(os.getpid())+'\n')
    """

    try:
        pid = os.fork()
    except OSError, except_params:
        raise Exception, "%s [%d]" % (except_params.strerror, except_params.errno)

    if (pid == 0):
        # The first child.
        os.setsid()

        try:
            pid = os.fork()	# Fork a second child.
        except OSError, except_params:
            raise Exception, "%s [%d]" % (except_params.strerror, except_params.errno)

        if (pid != 0):
            os._exit(0)	# Exit parent (the first child) of the second child.

    else:
        os._exit(0)	# Exit parent of the first child.

    import resource		# Resource usage information.
    maxfd = resource.getrlimit(resource.RLIMIT_NOFILE)[1]
    if (maxfd == resource.RLIM_INFINITY):
        maxfd = 1024

    # Iterate through and close all file descriptors.
    if True:
        for fd in range(0, maxfd):
            try:
                os.close(fd)
            except OSError:	# ERROR, fd wasn't open to begin with (ignored)
                pass

    # Send all output to /dev/null - FIX: send it to a log file
    os.open('/dev/null', os.O_RDWR)
    os.dup2(0, 1)
    os.dup2(0, 2)

    return

# Did I want to subclass file?
class LogFileWithRotate():
    def __init__(self,prefix='log-', station='runknown', uscg_format=True,verbose=False):
        self.v = verbose
        self.prefix=prefix
        self.log_filename=None
        self.log_file=None
        self.station=station
        self.uscg_format=uscg_format
        self.open()

    def open(self):
        '''Open a log file.  Close old one if it exists'''
        if self.log_file is not None:
            if self.v: print 'closing logfile'
            self.write_tail()
            self.log_file.close()
        now = self.current_date = datetime.datetime.utcnow()
        self.log_filename = self.prefix+now.strftime('%Y-%m-%d')
        if self.v: print 'opening log file: %s' % self.log_filename
        self.log_file = file(self.log_filename,'a')
        self.write_header()

    def write_header(self):
        self.write('# START LOGGING',rotate=False)

    def write_tail(self):
        self.write('# STOP LOGGING',rotate=False)

    def needs_rotate(self):
        'Check if the log needs to be rotated'
        old = self.current_date
        now = datetime.datetime.utcnow()
        return old.strftime('%j') != now.strftime('%j')

    def rotate(self,force=False):
        if not force and not self.needs_rotate():
            return
        if self.v: print 'rotate log file'
        self.open()

    def write(self,data,verbose=False,rotate=True):
        if rotate:
            self.rotate()
        log_str=''

        if self.uscg_format:
            log_str = data
            if data[-1] in ('\n','\r'): log_str = data[:-1]
            log_str += ',%s,%s\n' % ( self.station, time.time() )
        else:
            log_str=data
            if data!='\n': log_str+='\n'

        if verbose:
            print log_str,

        self.log_file.write(log_str)

    def __del__(self):
        print 'shutting down'
        self.write_tail()
        self.log_file.close()
