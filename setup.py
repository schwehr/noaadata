#!/usr/bin/env python
# Distutils setup script for the Automatic Identification System tools.

import glob
import sys

try:
    from setuptools import setup
except:
    sys.exit('Requires distribute or setuptools')

from setuptools import find_packages

def Version():
    """Get the package version string."""
    for line in open('noaadata/__init__.py'):
        if line.startswith('__version__'):
            return line.split('=')[1].rstrip().strip(' \'')

setup(name='noaadata-py',
      version=Version(),
      author='Kurt Schwehr',
      author_email='schwehr@gmail.com',
      url='https://github.com/schwehr/noaadata',
      description='Encode/decode NOAA co-ops marine data and marine AIS',
      long_description="""Library for handling marine Automatic
Identification System (AIS) messages and NOAA marine data messages
from http://opendap.co-ops.nos.noaa.gov/axis/.  Has extensions to
handle the USCG N-AIS receive fields.  The SOAP code is a bit rusty
and now uses pydap.

For AIS ship traffic, noaadata provides bridges to sqlite3 and
postgresql/postgis databases.  Is able to generate Google Earth KML
files for AIS.
""",
      license='Apache 2.0',
      keywords='AIS, binary messages, NMEA',
      platforms='All platforms',
      classifiers=[
        'Topic :: System :: Networking',
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: Apache 2.0',
        'Topic :: Communications',
        'Topic :: Database',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Scientific/Engineering :: GIS'],
      packages=['noaadata','ais','aisutils','nmea'],
      scripts=glob.glob('scripts/*'))

