#!/usr/bin/env python
__author__    = 'Kurt Schwehr'
__version__   = '$Revision: 11839 $'.split()[1]
__revision__  = __version__
__date__      = '$Date: 2009-05-05 17:34:17 -0400 (Tue, 05 May 2009) $'.split()[1]
__copyright__ = '2007, 2008'
__license__   = 'GPL v2'
__doc__ = '''
Daemon tool to detach from the terminal

@requires: U{epydoc<http://epydoc.sourceforge.net/>} > 3.0alpha3
@status: under development
@since: 2008-Feb-04
@undocumented: __doc__
@todo: Clean way to shut down
'''

import os

def stdCmdlineOptions(parser,skip_short=False):
    '''
    Standard command line options
    @param parser: OptionParser parser that will get the additional options
    '''

    if skip_short:
        parser.add_option('--daemon'
                          ,dest='daemon_mode'
                          ,default=False,action='store_true'
                          ,help='Detach from the terminal and run as a daemon service.'
                          +'  Returns the pid. [default: %default]')
    else:
        parser.add_option('-d'
                          ,'--daemon'
                          ,dest='daemon_mode'
                          ,default=False,action='store_true'
                          ,help='Detach from the terminal and run as a daemon service.'
                          +'  Returns the pid. [default: %default]')



    # FIX: have an option to make a default pid file location

    parser.add_option('--pid-file'
                      ,dest='pid_file'
                      ,default=None
                      ,help='Where to write the process id when in daemon mode')


def start(pid_file=None):
    '''
    Jump to daemon mode.  Must set either
    @param options: must have pid_file key
    '''
    create()
    if pid_file != None:
        open(pid_file, 'w').write(str(os.getpid())+'\n')


def create():
    """
    nohup like function to detach from the terminal.  Best to call start(), not this.
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

    return (0)
