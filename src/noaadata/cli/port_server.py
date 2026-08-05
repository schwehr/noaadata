#!/usr/bin/env python
__version__ = ["$Revision:", "13407", "$"][1]
__date__ = [
    "$Date:",
    "2010-04-07",
    "10:36:00",
    "-0400",
    "(Wed,",
    "07",
    "Apr",
    "2010)",
    "$",
][1]
__author__ = "Kurt Schwehr"
__doc__ = (
    """
Connect to a socket and provide a service where multiple clients can
connect.  The program optionally logs the data stream to a file.
Migrated from ais-py in August 2007.

@author: """
    + __author__
    + """
@version: """
    + __version__
    + """
@copyright: 2006
@since: 2006-May-04
@var __date__: Date of last svn commit
@undocumented: __version__ __author__ __doc__ myparser

 TODO(schwehr):log rotation!!  Optionally compress the logs when done.  They compress well.
 TODO(schwehr):add udp in and udp out
 TODO(schwehr):line oriented mode so that
 TODO(schwehr):allow the feed in and the exports to be on different interfaces
 TODO(schwehr):rewrite this as a SocketServer?
 TODO(schwehr):optionally read data from a serial port
 TODO(schwehr):multicast out
 TODO(schwehr):timestamps in line mode
 TODO(schwehr):multiple socket inputs and multiple serial port inputs
 TODO(schwehr):use select for blocking IO
"""
)

import _thread
import builtins as exceptions  # For KeyboardInterupt pychecker complaint
import datetime
import os
import socket
import subprocess
import sys
import time
import traceback

import nmea.znt  # NTP tracking

######################################################################

BOMBASTIC = 4
VERBOSE = 3
TRACE = 2
TERSE = 1
ALWAYS = 0
NEVER = 0


def add_verbosity_options(parser):
    """
    Added the verbosity options to a parser
    """
    parser.add_option(
        "-v",
        "--verbose",
        action="count",
        dest="verbosity",
        default=0,
        help="how much information to give.  Specify multiple times to increase verbosity",
    )
    parser.add_option(
        "--verbosity",
        dest="verbosity",
        type="int",
        help="Specify verbosity.  Should be in the range of "
        + str(ALWAYS)
        + "..."
        + str(BOMBASTIC)
        + " (None...Bombastic)",
    )
    parser.add_option(
        "--noisy",
        dest="verbosity",
        action="store_const",
        const=2 * BOMBASTIC,
        help="Go for the max verbosity [" + str(2 * BOMBASTIC) + "]",
    )


######################################################################


def date_str():
    """
    String representing the day so that it sorts correctly
    Returns:
        yyyy-mm-dd
        str
    """
    t = time.gmtime()
    d = "%04d-%02d-%02d" % t[:3]
    return d


######################################################################
class PassThroughServer:
    """Receive data from a socket and write the data to all clients that
    are connected.  Starts two threads and returns to the caller.
    """

    def __init__(self, options):
        self.clients = []
        self.options = options
        if options.log_file:
            self.curLogFile = self.getLogFileName()
            self.log = open(self.curLogFile, "a")
            self.logfile_add_start()
        else:
            self.log = None
        self.count = 0
        self.running = True

        # NTP monitoring
        verbose = options.verbosity > 0

        self.znt = nmea.znt.ZntLogger(
            self.log,  # Make sure to change this with the log file rotation
            enabled=options.znt_enable,
            max_sec=options.znt_max_sec,
            max_cnt=options.znt_max_cnt,
            always=options.znt_always,
            station=self.options.station_id,
            verbose=verbose,
        )

    def stop(self):
        if self.log:
            self.log.write(
                "# Closing log file at {} UTC,{}\n".format(
                    datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M"), time.time()
                )
            )
            self.log.close()
            self.log = None
            self.running = False

    def start(self):
        print("starting threads")
        _thread.start_new_thread(self.passdata, (self,))
        _thread.start_new_thread(self.connection_handler, (self,))

    def getLogFileName(self):
        """Return the log file name.  Appends date if rotation is happenin

        FIX: update when the program can rotate at arbitrary times.
        """
        if self.options.rotateLog:
            return "{}-{}{}".format(
                self.options.log_file,
                datetime.datetime.utcnow().strftime("%Y-%m-%d"),
                self.options.log_file_extension,
            )
        return self.options.log_file

    def logfile_add_start(self):
        if not self.log:
            return
        self.log.write(
            "# Opening log file at {} UTC,{}\n".format(
                datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%d %H:%M"),
                time.time(),
            )
        )
        try:
            self.log.write("# Logging host: {} {} {}\n".format(*os.uname()[:3]))
        except:
            print("os.uname not supported")
        try:
            self.log.write(f"# platform: {sys.platform} \n")
            for line in sys.version.splitlines():
                self.log.write(f"# python: {line} \n")
        except:
            print("Python really should have platform and version!")
        self.log.write("# NTP status:\n")

        try:
            output = subprocess.check_output(["ntpq", "-p", "-n"], text=True)  # nosec B603
            for line in output.splitlines():
                self.log.write(f"#    ntp: {line.rstrip()}\n")
        except Exception as e:
            self.log.write(f"#    ntp: ntpq command failed: {e}\n")

    def passdata(self, unused=None):
        while self.running:
            try:
                self.passdata_actual(unused)
            except Exception as e:
                sys.stderr.write("    Exception:" + str(type(Exception)) + "\n")
                sys.stderr.write("    Exception args:" + str(e) + "\n")
                traceback.print_exc(file=sys.stderr)

    def passdata_actual(self, unused=None):
        """Do not use this.  Call start() instead.

        @bug: how can I get rid of unused?
        """
        print("Starting passthrough server")

        uscg_flag = self.options.uscg
        data_cache = ""
        recv_time = None
        v = self.options.verbosity
        station_id = self.options.station_id

        # remote is where our data comes from
        remote = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        remote.connect((self.options.inHost, self.options.inPort))

        while 1:
            time.sleep(0.001)  # FIX: Replace with select
            # Go slower for debugging
            # if self.options.verbosity>BOMBASTIC: time.sleep(.2)
            # else time.sleep(.01)  # Is this needed to reschedule?

            # Use this for code that executes every N reads
            self.count += 1
            if self.count % 1000 == 1:
                print("# TIME =", time.gmtime())
                print()
                print("#  HOUR,MIN: ", time.gmtime()[3:5])
                print()

            if self.log and self.options.rotateLog:
                new_log_file = self.getLogFileName()
                if self.curLogFile != new_log_file:
                    if self.options.verbosity >= TERSE:
                        print("ROTATING LOG: ", self.curLogFile, new_log_file)
                    now = time.time()
                    self.log.write(
                        "# Closing log file at {} UTC,{}\n".format(
                            datetime.datetime.now(datetime.UTC).strftime(
                                "%Y-%m-%d %H:%M"
                            ),
                            time.time(),
                        )
                    )
                    self.log.close()
                    self.curLogFile = new_log_file
                    self.log = open(self.curLogFile, "a")
                    self.logfile_add_start()
                    self.znt.out_file = (
                        self.log
                    )  # Make the znt handler know about the new log file.

                    # FIX: change the log file in znt
            self.znt.update()

            m = remote.recv(1000)
            now = time.time()
            if len(m) > 0:
                if uscg_flag:
                    if recv_time is None:
                        recv_time = now

                    # Make sure that we log each line with one timestamp that matches
                    # as close as possible
                    # m is bytes, data_cache might be string, need to handle this
                    if isinstance(data_cache, str):
                        data_cache = data_cache.encode("latin-1")

                    data_cache += m
                    if len(data_cache) > 100000:
                        print("WARNING... not seeing line endings.  NOT forwarding")
                        if self.log:
                            self.log.write(data_cache.decode("latin-1"))
                            self.log.write(f"{station_id},{now}\n")
                        recv_time = None
                        data_cache = b""
                        continue

                    if b"\n" not in m:
                        continue

                    lines = data_cache.split(b"\n")
                    for line_b in lines[:-1]:
                        line_str = line_b.decode("latin-1").rstrip()
                        line_str += f",{station_id},{recv_time}\n"

                        if self.log:
                            self.log.write(line_str)
                        if v > TERSE:
                            print(line_str, end=" ")

                        for c in self.clients:
                            try:
                                c.send(line_str.encode("latin-1"))
                            except OSError:
                                print("Client Disconnect")
                                self.clients.remove(c)

                    recv_time = now
                    data_cache = lines[-1]  # Save the last partial line (bytes)

                else:
                    # Log straight through
                    if self.log:
                        self.log.write(
                            m.decode("latin-1")
                        )  # Takes a few before it flushes
                    if v > TERSE:
                        print(m, end=" ")
                    for c in self.clients:
                        try:
                            c.send(m)
                        except OSError:
                            print("Client Disconnect")
                            self.clients.remove(c)

            elif v >= VERBOSE:
                print("no data")

    def connection_handler(self, unused=None):
        """Do not use this.  Call start() instead.  This listens for
        connections and adds the new socket to the clients list.

        @bug: how can I get rid of unused?
        """
        print("starting incoming connection receiver")

        serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serversocket.bind((self.options.outHost, self.options.outPort))
        serversocket.listen(5)

        while self.running:
            (clientsocket, address) = serversocket.accept()
            print("connect from", clientsocket, address)
            self.clients.append(clientsocket)


######################################################################
def main():
    from optparse import OptionParser

    # FIX: is importing __init__ safe?
    parser = OptionParser(
        usage="%prog [options]", version="%prog " + __version__ + " (" + __date__ + ")"
    )

    parser.add_option(
        "-l",
        "--log-file",
        dest="log_file",
        type="string",
        default=None,
        help="Write the stream through a log file [default: %default]",
    )

    parser.add_option(
        "-e",
        "--log-extension",
        dest="log_file_extension",
        type="string",
        default="",
        help="File extension to put on the end of the filename.  "
        'Suggest ".ais" for AIS NMEA or ".gps" for GPS NMEA [default: "%default"]',
    )

    parser.add_option(
        "-i",
        "--in-port",
        dest="inPort",
        type="int",
        default=31414,
        help="Where the data comes from [default: %default]",
    )
    parser.add_option(
        "-I",
        "--in-host",
        dest="inHost",
        type="string",
        default="localhost",
        help="What host to read data from [default: %default]",
    )

    parser.add_option(
        "-o",
        "--out-port",
        dest="outPort",
        type="int",
        default=31401,
        help="Where the data will be available to others [default: %default]",
    )
    parser.add_option(
        "-O",
        "--out-host",
        dest="outHost",
        type="string",
        default="localhost",
        help="What machine the source port is on [default: %default]",
    )
    parser.add_option(
        "--out-gethostname",
        dest="outHostname",
        action="store_true",
        default=False,
        help="Use the default hostname [" + socket.gethostname() + "]",
    )

    parser.add_option(
        "-r",
        "--rotate",
        dest="rotateLog",
        default=False,
        action="store_true",
        help="turn on one a day log rotation." + "  Appends the date to the log",
    )

    parser.add_option(
        "-s",
        "--station-id",
        dest="station_id",
        type="string",
        default=None,
        help="If uscg format is selected, you can specify a station id to"
        + ' put as ",r" before the timestamp  [default: %default]',
    )
    parser.add_option(
        "-u",
        "--uscg",
        dest="uscg",
        default=False,
        action="store_true",
        help="Add the uscg style station and timestamp [default %default]",
    )

    nmea.znt.znt_logger_opts(parser)

    add_verbosity_options(parser)

    (options, args) = parser.parse_args()

    v = options.verbosity

    if options.outHostname:
        options.outHost = socket.gethostname()

    if v >= VERBOSE:
        print(options)
        if len(args) > 0:
            print("UNUSED args:", args)

    pts = PassThroughServer(options)
    pts.start()

    del options  # remove global to force self.options
    i = 0
    running = True
    try:
        while running:
            i += 1
            time.sleep(30)
            if v >= TRACE:
                print("ping", i)
    except exceptions.KeyboardInterrupt:
        running = False
        pts.stop()
    time.sleep(2)  # FIX: Should loop until pts is finished


######################################################################

if __name__ == "__main__":
    main()
