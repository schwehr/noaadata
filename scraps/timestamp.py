#!/usr/bin/env python
import sys

for line in sys.stdin:
    ts = line.split(',')[-1].strip()
    print ts


