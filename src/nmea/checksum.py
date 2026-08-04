#!/usr/bin/env python
"""Utilities for working with NMEA strings."""

import functools
import operator
import re

nmeaChecksumRE = re.compile(r"[\!\?][^\*]+\*[0-9A-Fa-f]{2}")


def checksumStr(data: str) -> str:
    """
    Take a NMEA 0183 string and compute the checksum.
    Args:
        data: NMEA message.  Leading ?/! and training checksum are optional
    @type data: str
    Returns:
        hexadecimal value
        str

    Checksum is calculated by xor'ing everything between ? or ! and the *

    >>> checksumStr("!AIVDM,1,1,,B,35MsUdPOh8JwI:0HUwquiIFH21>i,0*09")
    '09'
    >>> checksumStr("AIVDM,1,1,,B,35MsUdPOh8JwI:0HUwquiIFH21>i,0")
    '09'
    """

    if data and data[0] in ("!", "?"):
        data = data[1:]
    if len(data) >= 3 and data[-3] == "*":
        data = data[:-3]

    chk = functools.reduce(operator.xor, data.encode("latin-1"), 0)
    return f"{chk:02X}"


def isChecksumValid(nmeaStr: str, allowTailData: bool = True) -> bool:
    """Return True if the string checks out with the checksum

    Args:
        nmeaStr: NMEA sentence. Leading $ or ! is optional.
        allowTailData: Permit handling of Coast Guard format with data after the checksum.
    Returns:
        True if the checksum matches

    >>> isChecksumValid("!AIVDM,1,1,,B,35MsUdPOh8JwI:0HUwquiIFH21>i,0*09")
    True

    Corrupted:

    >>> isChecksumValid("!AIVDM,11,1,,B,35MsUdPOh8JwI:0HUwquiIFH21>i,0*09")
    False
    """

    if allowTailData:
        match = nmeaChecksumRE.search(nmeaStr)
        if not match:
            return False
        nmeaStr = nmeaStr[: match.end()]

    if nmeaStr[-3] != "*":
        return False
    checksum = nmeaStr[-2:]
    return checksum.upper() == checksumStr(nmeaStr).upper()
