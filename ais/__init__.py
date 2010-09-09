__version__   = '$Revision: 4799 $'.split()[1]
__docformat__ = 'epytext en'
__author__ = 'Kurt Schwehr <kurt@ccom.unh.edu>'
'''The primary author of ais-py'''
__url__ = 'http://vislab-ccom.unh.edu/~schwehr/src/noaadata/'
'''The ais-py homepage'''

__doc__='''
Python module for Automatic Indentification System (AIS).  This is
the 3rd iteration of creating an AIS codec package in python.  This
version is more a compiler so that it could be altered to emit
something other than python if need be.  The focus this time is on
building a simple distributable batch of code that only requires the
python lxml package when it builds the python.  After that, the only
requirement is the BitVector package by Avi Kak.  BitVector is included
with permission for your convenience, but it is best if you install
BitVector yourself from the original distribution.

@see: NMEA strings at U{http://gpsd.berlios.de/NMEA.txt}
@see: Wikipedia at U{http://en.wikipedia.org/wiki/Automatic_Identification_System}

@author: Kurt Schwehr U{email<mailto:kurt@ccom.unh.edu>} U{homepage<http://schwehr.org>}
@requires: U{Python<http://python.org/>} >= 2.4
@requires: U{lxml<http://codespeak.net/lxml/>} >= 1.1.2
@requires: U{libxml2<http://xmlsoft.org/>} for xmllint
@requires: U{BitVector<http://cobweb.ecn.purdue.edu/~kak/dist/>} >= 1.2
@requires: U{epydoc<http://epydoc.sourceforge.net>} >= 3.0alpha3
@version: '''+__version__+'''

@license: GPL version 2
@copyright: (C) 2006-2007 Kurt Schwehr/UNH

@undocumented: __doc__
@undocumented: __version__ __author__ __url__
@todo: the msgName variable should be generated from the XML
'''

msgNames = {
    1:'Position, Class A' # FIX: explain difference in 1..3
    ,2:'Position, Class A'
    ,3:'Position, Class A'
    ,4:'Base station report'
    ,5:'Ship and Cargo'
    ,6:'Addressed binary message'
    ,7:'ACK for addressed binary message'
    ,8:'Binary broadcast message (BBM)'
    ,9:'SAR Position'
    ,10:'UTC query'
    ,11:'UTC and date response (same format as 4)'
    ,12:'ASRM'
    ,13:'ASRM Ack'
    ,14:'SRBM'
    ,15:'Interrogation'
    ,16:'Assigned mode command'
    ,17:'GNSS broadcast'
    ,18:'Position, Class B'
    ,19:'Position and ship, Class B'
    ,20:'Data link management'
    ,21:'Aids to navigation report'
    ,22:'Channel Management'
    ,23:'Group Assignment Command'
    ,24:'Static data report'
    ,25:'Single slit binary message - addressed or broadcast'
    ,26:'Multi slot binary message with comm state'
    }
'''
Messages in the main AIS name space
'''

# FIX: is this really the right way to do things?  Definitely helps with tab completion and less user code

import ais_msg_1_handcoded
import ais_msg_2_handcoded
import ais_msg_3_handcoded
import ais_msg_4_handcoded
import ais_msg_5
import ais_msg_6
import ais_msg_7_handcoded
import ais_msg_8
import ais_msg_9
import ais_msg_10
import ais_msg_11
import ais_msg_12
#import ais_msg_13
import ais_msg_14
import ais_msg_15
#import ais_msg_16
#import ais_msg_17
import ais_msg_18
import ais_msg_19
import ais_msg_20
import ais_msg_21
import ais_msg_22
#import ais_msg_23
import ais_msg_24_handcoded
#import ais_msg_24
#import ais_msg_25
#import ais_msg_26

import binary

msgModByNumber={
     1: ais_msg_1_handcoded
     ,2: ais_msg_2_handcoded
     ,3: ais_msg_3_handcoded
     ,4: ais_msg_4_handcoded
     ,5: ais_msg_5
     ,6: ais_msg_6
     ,7: ais_msg_7_handcoded
     ,8: ais_msg_8
     ,9: ais_msg_9
     ,10: ais_msg_10
#     ,11: ais_msg_11
     ,12: ais_msg_12
#     ,13: ais_msg_13
     ,14: ais_msg_14
     ,15: ais_msg_15
#     ,16: ais_msg_16
#     ,17: ais_msg_17
     ,18: ais_msg_18
     ,19: ais_msg_19
     ,20: ais_msg_20
     ,21: ais_msg_21
     ,22: ais_msg_22
#     ,23: ais_msg_23
     ,24: ais_msg_24_handcoded
#     ,24: ais_msg_24
#     ,25: ais_msg_25
#     ,26: ais_msg_26

    }
'''
Allows easier decoding of messages without having to write as much code
'''

msgModByFirstChar={
       '1': ais_msg_1_handcoded
    ,  '2': ais_msg_2_handcoded
    ,  '3': ais_msg_3_handcoded
    ,  '4': ais_msg_4_handcoded
    ,  '5': ais_msg_5
    ,  '6': ais_msg_6
    ,  '7': ais_msg_7_handcoded
    ,  '8': ais_msg_8
    ,  '9': ais_msg_9
    ,  ':': ais_msg_10
#    ,  ';': ais_msg_11
    ,  '<': ais_msg_12
#    ,  '=': ais_msg_13
    ,  '>': ais_msg_14
    ,  '?': ais_msg_15
#    ,  '@': ais_msg_16
#    ,  'A': ais_msg_17
    ,  'B': ais_msg_18
    ,  'C': ais_msg_19
    ,  'D': ais_msg_20
    ,  'E': ais_msg_21
    ,  'F': ais_msg_22
#    ,  'G': ais_msg_23
    ,  'H': ais_msg_24_handcoded
#    ,  'H': ais_msg_24
#    ,  'I': ais_msg_25
#    ,  'J': ais_msg_26
}
