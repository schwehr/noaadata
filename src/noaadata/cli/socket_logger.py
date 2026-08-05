#!/usr/bin/env python
__version__ = ["$Revision:", "7470", "$"][1]
__date__ = [
    "$Date:",
    "2007-11-06",
    "10:31:44",
    "-0500",
    "(Tue,",
    "06",
    "Nov",
    "2007)",
    "$",
][1]
__author__ = "Kurt Schwehr"

__doc__ = """
FIX: write a description

@status: under development
@license: Apache 2.0
@since: 2007-Mar-05

 TODO(schwehr):give this a optparse interface
 TODO(schwehr):make it flexible.
"""

import select
import socket
import time


def main():
    o = open("norfolk-log.ais", "a")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("10.1.1.29", 5505))
    s.send(b"$xxBSQ,ACA,*03\x0d\x0a")
    buf = b""
    while True:
        readersready, _outputready, _exceptready = select.select([s], [], [], 0.1)
        for sock in readersready:
            data = sock.recv(100)
            buf += data
            newline = buf.find(b"\n")
            if newline != -1:
                fields = buf.split(b"\n")
                msg = fields[0].decode("latin-1").strip() + "," + str(time.time())
                print(msg)
                o.write(msg + "\n")
                buf = b"" + buf[newline + 1 :] if len(fields) > 1 else b""


if __name__ == "__main__":
    main()
