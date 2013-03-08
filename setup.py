#!/usr/bin/env python
__copyright__ = '2006-2013'
__doc__= ''' 
Distutils setup script for the Automatic Identification System tools.

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
            return ast.literal_eval(line.split('=')[1].strip())

# TODO: build the python code from the xml definitions
setup(name='noaadata-py',
      version=Version(),
      author='Kurt Schwehr',
      author_email='schwehr@gmail.comx',
      url='https://github.com/schwehr/noaadata',
      description='Encode/decode NOAA co-ops marine data and marine AIS',
      long_description=open('README').read(),
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
      packages=['noaadata'],
      scripts=glob.glob('scripts/*'),
      install_requires=['BitVector'],
      setup_requires=['lxml'],
      )
