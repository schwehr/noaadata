#!/usr/bin/env python
import sys

timeshift=27593333

for filename in sys.argv[1:]:
    for line in file(filename):
        fields = line.split(',')
        ts = int(fields[-1].split('.')[0])
        ts += timeshift
        newFields = fields[:-1]
        newFields.append(str(ts))
        print ','.join(newFields)

