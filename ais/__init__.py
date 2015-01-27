"""Python module for Automatic Indentification System (AIS).

This is the 3rd iteration of creating an AIS codec package in python.
This version is more a compiler so that it could be altered to emit
something other than python if need be.  The focus this time is on
building a simple distributable batch of code that only requires the
python lxml package when it builds the python.  After that, the only
requirement is the BitVector package by Avi Kak.  BitVector is
included with permission for your convenience, but it is best if you
install BitVector yourself from the original distribution.

See Also:
  http://gpsd.berlios.de/NMEA.txt
  http://en.wikipedia.org/wiki/Automatic_Identification_System

License: Apache 2.0
"""

# FIX: is this really the right way to do things?
# Definitely helps with tab completion and less user code

import ais.ais_msg_1_handcoded
import ais.ais_msg_2_handcoded
import ais.ais_msg_3_handcoded
import ais.ais_msg_4_handcoded
import ais.ais_msg_5
import ais.ais_msg_6
import ais.ais_msg_7_handcoded
import ais.ais_msg_8
import ais.ais_msg_9
import ais.ais_msg_10
import ais.ais_msg_11
import ais.ais_msg_12
# import ais.ais_msg_13
import ais.ais_msg_14
import ais.ais_msg_15
# import ais.ais_msg_16
# import ais.ais_msg_17
import ais.ais_msg_18
import ais.ais_msg_19
import ais.ais_msg_20
import ais.ais_msg_21
import ais.ais_msg_22
# import ais.ais_msg_23
import ais.ais_msg_24_handcoded
# import ais.ais_msg_24
# import ais.ais_msg_25
# import ais.ais_msg_26
# import ais.ais_msg_27

msgNames = {
    1: 'Position, Class A',  # FIX: Explain difference between 1..3.
    2: 'Position, Class A',
    3: 'Position, Class A',
    4: 'Base station report',
    5: 'Ship and Cargo',
    6: 'Addressed binary message',
    7: 'ACK for addressed binary message',
    8: 'Binary broadcast message (BBM)',
    9: 'SAR Position',
    10: 'UTC query',
    11: 'UTC and date response (same format as 4)',
    12: 'ASRM',
    13: 'ASRM Ack',
    14: 'SRBM',
    15: 'Interrogation',
    16: 'Assigned mode command',
    17: 'GNSS broadcast',
    18: 'Position, Class B',
    19: 'Position and ship, Class B',
    20: 'Data link management',
    21: 'Aids to navigation report',
    22: 'Channel Management',
    23: 'Group Assignment Command',
    24: 'Static data report',
    25: 'Single slit binary message - addressed or broadcast',
    26: 'Multi slot binary message with comm state'
    }
"""Messages in the main AIS name space."""

msgModByNumber = {
    1: ais.ais_msg_1_handcoded,
    2: ais.ais_msg_2_handcoded,
    3: ais.ais_msg_3_handcoded,
    4: ais.ais_msg_4_handcoded,
    5: ais.ais_msg_5,
    6: ais.ais_msg_6,
    7: ais.ais_msg_7_handcoded,
    8: ais.ais_msg_8,
    9: ais.ais_msg_9,
    10: ais.ais_msg_10,
    # 11: ais.ais_msg_11,
    12: ais.ais_msg_12,
    # 13: ais.ais_msg_13,
    14: ais.ais_msg_14,
    15: ais.ais_msg_15,
    # 16: ais.ais_msg_16,
    # 17: ais.ais_msg_17,
    18: ais.ais_msg_18,
    19: ais.ais_msg_19,
    20: ais.ais_msg_20,
    21: ais.ais_msg_21,
    22: ais.ais_msg_22,
    # 23: ais.ais_msg_23,
    24: ais.ais_msg_24_handcoded,
    # 24: ais.ais_msg_24,
    # 25: ais.ais_msg_25,
    # 26: ais.ais_msg_26,
    # 27: ais.ais_msg_27,
    }
"""Allow easier decoding of messages without having to write as much code."""

msgModByFirstChar = {
    '1': ais.ais_msg_1_handcoded,
    '2': ais.ais_msg_2_handcoded,
    '3': ais.ais_msg_3_handcoded,
    '4': ais.ais_msg_4_handcoded,
    '5': ais.ais_msg_5,
    '6': ais.ais_msg_6,
    '7': ais.ais_msg_7_handcoded,
    '8': ais.ais_msg_8,
    '9': ais.ais_msg_9,
    ':': ais.ais_msg_10,
    #';': ais.ais_msg_11,
    '<': ais.ais_msg_12,
    # '=': ais.ais_msg_13,
    '>': ais.ais_msg_14,
    '?': ais.ais_msg_15,
    # '@': ais.ais_msg_16
    # 'A': ais.ais_msg_17,
    'B': ais.ais_msg_18,
    'C': ais.ais_msg_19,
    'D': ais.ais_msg_20,
    'E': ais.ais_msg_21,
    'F': ais.ais_msg_22,
    # 'G': ais.ais_msg_23,
    'H': ais.ais_msg_24_handcoded,
    # 'H': ais.ais_msg_24,
    # 'I': ais.ais_msg_25,
    # 'J': ais.ais_msg_26,
    # 'K': ais.ais_msg_26,
}
