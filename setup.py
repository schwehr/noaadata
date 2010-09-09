#!/usr/bin/env python
__version__ = '$Revision: 10404 $'.split()[1]
__date__ = '$Date: 2008-09-24 22:45:05 -0400 (Wed, 24 Sep 2008) $'.split()[1]
__author__ = 'Kurt Schwehr'
__copyright__ = '2006-2008'
__version__=file('VERSION').readline().strip()
__license__   = 'GPL v3'
__contact__   = 'kurt at ccom.unh.edu'
__doc__= ''' 
Distutils setup script for the Automatic Identification System tools.

@var __date__: Date of last svn commit
@undocumented: __doc__
@since: Fall 2006
@status: under development
@organization: U{CCOM<http://ccom.unh.edu/>}

@requires: U{Python<http://python.org/>} >= 2.5
@requires: U{epydoc<http://epydoc.sourceforge.net/>} >= 3.0.1
@requires: U{psycopg2<http://http://initd.org/projects/psycopg2/>} >= 2.0.6
@todo: Get all the requires in here
@todo: Allow ezsetup/setuptools support
@todo: Does this need to set the interpreter for all scripts on setup?
@todo: Could use feedback on my coding template
@see: doc/template.py for coding template
'''

from distutils.core import setup

# Setuptools / eggs, etc.
#from setuptools import setup


url='http://vislab-ccom.unh.edu/~schwehr/software/noaadata'
download_url=url+'/downloads/noaadata-py-'+__version__+'.tar.bz2'
print download_url

import glob
SCRIPTS=glob.glob('scripts/*')
'List of files that are executable and that need to be installed in the bin folder/path'

if __name__=='__main__':

    setup(name='noaadata-py',
          version=__version__,
          author=__author__,
          author_email='kurt@ccom.unh.edu',
          maintainer='Kurt Schwehr',
          maintainer_email='kurt@ccom.unh.edu',
          url=url,
          download_url=download_url,
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
          license=__license__,
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

