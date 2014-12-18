#!/usr/bin/env python
# Consider this template file public domain.  The __license__ is just an example.
# Replace values as needed
__author__    = 'Kurt Schwehr'
__version__   = '$Revision: 4799 $'.split()[1]
__revision__  = __version__ # For pylint
__date__ = '$Date: 2006-09-25 11:09:02 -0400 (Mon, 25 Sep 2006) $'.split()[1]
__copyright__ = '2008'
__license__   = 'Apache 2.0'

__doc__ ='''
Handle creating message 8 encoders

@requires: U{Python<http://python.org/>} >= 2.5
@requires: U{epydoc<http://epydoc.sourceforge.net/>} >= 3.0.1
@requires: U{lxml<http://codespeak.net/lxml/>}

@since: 2008-Apr-01
'''

import sys
import os
import exceptions # For KeyboardInterupt pychecker complaint

import sys, os
from decimal import Decimal
from lxml import etree 

