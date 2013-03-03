#!/usr/bin/env python
__copyright__ = '2006-2013'
__doc__= ''' 
Distutils setup script for the Automatic Identification System tools.

@var __date__: Date of last svn commit
@undocumented: __doc__
@since: Fall 2006
@status: under development

@requires: U{Python<http://python.org/>} >= 2.7
@requires: U{psycopg2<http://http://initd.org/projects/psycopg2/>} >= 2.0.6
@todo: Get all the requires in here
@todo: Allow ezsetup/setuptools support
@todo: Does this need to set the interpreter for all scripts on setup?
@todo: Could use feedback on my coding template
@see: doc/template.py for coding template
'''

import ast
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
            return ast.literal_eval(line.split('=')[1].strip())

import glob
SCRIPTS=glob.glob('scripts/*')
'List of files that are executable and that need to be installed in the bin folder/path'

if __name__=='__main__':

    setup(name='noaadata-py',
          version=Version(),
          author='Kurt Schwehr',
          author_email='schwehr@gmail.comx',
          url='https://github.com/schwehr/noaadata',
          description='Encode/decode NOAA co-ops marine data and marine AIS',
          long_description='''Library for handling marine Automatic Identification System (AIS)
messages and NOAA marine data messages from http://opendap.co-ops.nos.noaa.gov/axis/. 
Has extensions to handle the USCG N-AIS receive fields.  The SOAP code is a bit rusty and now
uses pydap.

For AIS ship traffic, noaadata provides bridges to sqlite3 and
postgresql/postgis databases.  Is able to generate Google Earth KML
files for AIS.

Part of the UNH/NOAA Chart of the Future project.

Still in development.  Some rough edges.
          ''',
          license='BSD',
          keywords='axis, soap, marine, NOAA, AIS, N-AIS, binary messages, NMEA',
          platforms='All platforms',
          classifiers=[
            'Topic :: System :: Networking',
            'Development Status :: 4 - Beta',
            'Environment :: Console',
            'Intended Audience :: Science/Research',
            'License :: OSI Approved :: GNU General Public License (GPL)',
            'Topic :: Communications',
            'Topic :: Database',
            'Topic :: Scientific/Engineering :: Information Analysis',
            'Topic :: Scientific/Engineering :: Interface Engine/Protocol Translator',
            'Topic :: Scientific/Engineering :: Visualization',
            'Topic :: Software Development :: Code Generators',
            'Topic :: Scientific/Engineering :: GIS',
            ],
          packages=['noaadata','ais','aisutils','nmea'],
          scripts=SCRIPTS,
          )

