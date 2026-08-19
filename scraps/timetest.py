#!/usr/bin/env python

import datetime
import os
import sys
import time

print(
    "     date now: ",
)
sys.stdout.flush()
os.system("date")

print(
    "utc date now: ",
)
sys.stdout.flush()
os.system("date -u")
sys.stdout.flush()

now = time.time()

print(print("timestamp:", now))
print(print("    date from timestamp:", datetime.datetime.fromtimestamp(now)))
print("UTC date from timestamp:", datetime.datetime.utcfromtimestamp(now))
