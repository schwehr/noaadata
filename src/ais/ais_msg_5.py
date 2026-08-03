#!/usr/bin/env python

"""Functions to serialize/deserialize binary messages.

Need to then wrap these functions with the outer AIS packet and then
convert the whole binary blob to a NMEA string.  Those functions are
not currently provided in this file.

serialize: python to ais binary
deserialize: ais binary to python

The generated code uses translators.py, binary.py, and aisstring.py
which should be packaged with the resulting files.

TODO(schwehr): Put in a description of the message here with fields and types.
"""

import sys
import unittest
from decimal import Decimal

from aisutils import aisstring, binary, sqlhelp, uscg
from aisutils.BitVector import BitVector

fieldList = (
    "MessageID",
    "RepeatIndicator",
    "UserID",
    "AISversion",
    "IMOnumber",
    "callsign",
    "name",
    "shipandcargo",
    "dimA",
    "dimB",
    "dimC",
    "dimD",
    "fixtype",
    "ETAmonth",
    "ETAday",
    "ETAhour",
    "ETAminute",
    "draught",
    "destination",
    "dte",
    "Spare",
)

fieldListPostgres = (
    "MessageID",
    "RepeatIndicator",
    "UserID",
    "AISversion",
    "IMOnumber",
    "callsign",
    "name",
    "shipandcargo",
    "dimA",
    "dimB",
    "dimC",
    "dimD",
    "fixtype",
    "ETAmonth",
    "ETAday",
    "ETAhour",
    "ETAminute",
    "draught",
    "destination",
    "dte",
    "Spare",
)

toPgFields = {}
"""
Go to the Postgis field names from the straight field name
"""

fromPgFields = {}
"""
Go from the Postgis field names to the straight field name
"""

pgTypes = {}
"""
Lookup table for each postgis field name to get its type.
"""


def encode(params, validate=False):
    """Create a shipdata binary message payload to pack into an AIS Msg shipdata.

    Fields in params:
      - MessageID(uint): AIS message number.  Must be 5 (field automatically set to "5")
      - RepeatIndicator(uint): Indicated how many times a message has been repeated
      - UserID(uint): Unique ship identification number (MMSI)
      - AISversion(uint): Compliant with what edition.  0 is the first edition.
      - IMOnumber(uint): vessel identification number (different than mmsi)
      - callsign(aisstr6): Ship radio call sign
      - name(aisstr6): Vessel name
      - shipandcargo(uint): what
      - dimA(uint): Distance from bow to reference position
      - dimB(uint): Distance from reference position to stern
      - dimC(uint): Distance from port side to reference position
      - dimD(uint): Distance from reference position to starboard side
      - fixtype(uint): Method used for positioning
      - ETAmonth(uint): Estimated time of arrival - month
      - ETAday(uint): Estimated time of arrival - day
      - ETAhour(uint): Estimated time of arrival - hour
      - ETAminute(uint): Estimated time of arrival - minutes
      - draught(udecimal): Maximum present static draught
      - destination(aisstr6): Where is the vessel going
      - dte(uint): Data terminal ready
      - Spare(uint): Reserved for definition by a regional authority. (field automatically set to "0")
    Args:
        params: Dictionary of field names/values.  Throws a ValueError exception if required is missing
        validate: Set to true to cause checking to occur.  Runs slower.  FIX: not implemented.
    Returns:
        BitVector
        encoded binary message (for binary messages, this needs to be wrapped in a msg 8
    @note: The returned bits may not be 6 bit aligned.  It is up to you to pad out the bits.
    """

    bvList = []
    bvList.append(binary.setBitVectorSize(BitVector(intVal=5), 6))
    if "RepeatIndicator" in params:
        bvList.append(
            binary.setBitVectorSize(BitVector(intVal=params["RepeatIndicator"]), 2)
        )
    else:
        bvList.append(binary.setBitVectorSize(BitVector(intVal=0), 2))
    bvList.append(binary.setBitVectorSize(BitVector(intVal=params["UserID"]), 30))
    if "AISversion" in params:
        bvList.append(
            binary.setBitVectorSize(BitVector(intVal=params["AISversion"]), 2)
        )
    else:
        bvList.append(binary.setBitVectorSize(BitVector(intVal=0), 2))
    if "IMOnumber" in params:
        bvList.append(
            binary.setBitVectorSize(BitVector(intVal=params["IMOnumber"]), 30)
        )
    else:
        bvList.append(binary.setBitVectorSize(BitVector(intVal=0), 30))
    if "callsign" in params:
        bvList.append(aisstring.encode(params["callsign"], 42))
    else:
        bvList.append(aisstring.encode("@@@@@@@", 42))
    if "name" in params:
        bvList.append(aisstring.encode(params["name"], 120))
    else:
        bvList.append(aisstring.encode("@@@@@@@@@@@@@@@@@@@@", 120))
    if "shipandcargo" in params:
        bvList.append(
            binary.setBitVectorSize(BitVector(intVal=params["shipandcargo"]), 8)
        )
    else:
        bvList.append(binary.setBitVectorSize(BitVector(intVal=0), 8))
    if "dimA" in params:
        bvList.append(binary.setBitVectorSize(BitVector(intVal=params["dimA"]), 9))
    else:
        bvList.append(binary.setBitVectorSize(BitVector(intVal=0), 9))
    if "dimB" in params:
        bvList.append(binary.setBitVectorSize(BitVector(intVal=params["dimB"]), 9))
    else:
        bvList.append(binary.setBitVectorSize(BitVector(intVal=0), 9))
    if "dimC" in params:
        bvList.append(binary.setBitVectorSize(BitVector(intVal=params["dimC"]), 6))
    else:
        bvList.append(binary.setBitVectorSize(BitVector(intVal=0), 6))
    if "dimD" in params:
        bvList.append(binary.setBitVectorSize(BitVector(intVal=params["dimD"]), 6))
    else:
        bvList.append(binary.setBitVectorSize(BitVector(intVal=0), 6))
    if "fixtype" in params:
        bvList.append(binary.setBitVectorSize(BitVector(intVal=params["fixtype"]), 4))
    else:
        bvList.append(binary.setBitVectorSize(BitVector(intVal=0), 4))
    if "ETAmonth" in params:
        bvList.append(binary.setBitVectorSize(BitVector(intVal=params["ETAmonth"]), 4))
    else:
        bvList.append(binary.setBitVectorSize(BitVector(intVal=0), 4))
    if "ETAday" in params:
        bvList.append(binary.setBitVectorSize(BitVector(intVal=params["ETAday"]), 5))
    else:
        bvList.append(binary.setBitVectorSize(BitVector(intVal=0), 5))
    if "ETAhour" in params:
        bvList.append(binary.setBitVectorSize(BitVector(intVal=params["ETAhour"]), 5))
    else:
        bvList.append(binary.setBitVectorSize(BitVector(intVal=24), 5))
    if "ETAminute" in params:
        bvList.append(binary.setBitVectorSize(BitVector(intVal=params["ETAminute"]), 6))
    else:
        bvList.append(binary.setBitVectorSize(BitVector(intVal=60), 6))
    if "draught" in params:
        bvList.append(
            binary.setBitVectorSize(
                BitVector(intVal=int(Decimal(params["draught"]) * Decimal("10"))), 8
            )
        )
    else:
        bvList.append(binary.setBitVectorSize(BitVector(intVal=0), 8))
    if "destination" in params:
        bvList.append(aisstring.encode(params["destination"], 120))
    else:
        bvList.append(aisstring.encode("@@@@@@@@@@@@@@@@@@@@", 120))
    bvList.append(binary.setBitVectorSize(BitVector(intVal=params["dte"]), 1))
    bvList.append(binary.setBitVectorSize(BitVector(intVal=0), 1))

    return binary.joinBV(bvList)


def decode(bv, validate=False):
    """Unpack a shipdata message.

    Fields in params:
      - MessageID(uint): AIS message number.  Must be 5 (field automatically set to "5")
      - RepeatIndicator(uint): Indicated how many times a message has been repeated
      - UserID(uint): Unique ship identification number (MMSI)
      - AISversion(uint): Compliant with what edition.  0 is the first edition.
      - IMOnumber(uint): vessel identification number (different than mmsi)
      - callsign(aisstr6): Ship radio call sign
      - name(aisstr6): Vessel name
      - shipandcargo(uint): what
      - dimA(uint): Distance from bow to reference position
      - dimB(uint): Distance from reference position to stern
      - dimC(uint): Distance from port side to reference position
      - dimD(uint): Distance from reference position to starboard side
      - fixtype(uint): Method used for positioning
      - ETAmonth(uint): Estimated time of arrival - month
      - ETAday(uint): Estimated time of arrival - day
      - ETAhour(uint): Estimated time of arrival - hour
      - ETAminute(uint): Estimated time of arrival - minutes
      - draught(udecimal): Maximum present static draught
      - destination(aisstr6): Where is the vessel going
      - dte(uint): Data terminal ready
      - Spare(uint): Reserved for definition by a regional authority. (field automatically set to "0")
    @type bv: BitVector
    Args:
        bv: Bits defining a message
        validate: Set to true to cause checking to occur.  Runs slower.  FIX: not implemented.
    Returns:
        dict
        params
    """

    # Would be nice to check the bit count here..
    # if validate:
    #    assert (len(bv)==FIX: SOME NUMBER)
    r = {}
    r["MessageID"] = 5
    r["RepeatIndicator"] = int(bv[6:8])
    r["UserID"] = int(bv[8:38])
    r["AISversion"] = int(bv[38:40])
    r["IMOnumber"] = int(bv[40:70])
    r["callsign"] = aisstring.decode(bv[70:112])
    r["name"] = aisstring.decode(bv[112:232])
    r["shipandcargo"] = int(bv[232:240])
    r["dimA"] = int(bv[240:249])
    r["dimB"] = int(bv[249:258])
    r["dimC"] = int(bv[258:264])
    r["dimD"] = int(bv[264:270])
    r["fixtype"] = int(bv[270:274])
    r["ETAmonth"] = int(bv[274:278])
    r["ETAday"] = int(bv[278:283])
    r["ETAhour"] = int(bv[283:288])
    r["ETAminute"] = int(bv[288:294])
    r["draught"] = Decimal(int(bv[294:302])) / Decimal("10")
    r["destination"] = aisstring.decode(bv[302:422])
    r["dte"] = int(bv[422:423])
    r["Spare"] = 0
    return r


def decodeMessageID(bv, validate=False):
    return 5


def decodeRepeatIndicator(bv, validate=False):
    return int(bv[6:8])


def decodeUserID(bv, validate=False):
    return int(bv[8:38])


def decodeAISversion(bv, validate=False):
    return int(bv[38:40])


def decodeIMOnumber(bv, validate=False):
    return int(bv[40:70])


def decodecallsign(bv, validate=False):
    return aisstring.decode(bv[70:112])


def decodename(bv, validate=False):
    return aisstring.decode(bv[112:232])


def decodeshipandcargo(bv, validate=False):
    return int(bv[232:240])


def decodedimA(bv, validate=False):
    return int(bv[240:249])


def decodedimB(bv, validate=False):
    return int(bv[249:258])


def decodedimC(bv, validate=False):
    return int(bv[258:264])


def decodedimD(bv, validate=False):
    return int(bv[264:270])


def decodefixtype(bv, validate=False):
    return int(bv[270:274])


def decodeETAmonth(bv, validate=False):
    return int(bv[274:278])


def decodeETAday(bv, validate=False):
    return int(bv[278:283])


def decodeETAhour(bv, validate=False):
    return int(bv[283:288])


def decodeETAminute(bv, validate=False):
    return int(bv[288:294])


def decodedraught(bv, validate=False):
    return Decimal(int(bv[294:302])) / Decimal("10")


def decodedestination(bv, validate=False):
    return aisstring.decode(bv[302:422])


def decodedte(bv, validate=False):
    return int(bv[422:423])


def decodeSpare(bv, validate=False):
    return 0


def printHtml(params, out=sys.stdout):
    out.write("<h3>shipdata</h3>\n")
    out.write('<table border="1">\n')
    out.write('<tr bgcolor="orange">\n')
    out.write('<th align="left">Field Name</th>\n')
    out.write('<th align="left">Type</th>\n')
    out.write('<th align="left">Value</th>\n')
    out.write('<th align="left">Value in Lookup Table</th>\n')
    out.write('<th align="left">Units</th>\n')
    out.write("</tr>\n")
    out.write("\n")
    out.write("<tr>\n")
    out.write("<td>MessageID</td>\n")
    out.write("<td>uint</td>\n")
    if "MessageID" in params:
        out.write("    <td>" + str(params["MessageID"]) + "</td>\n")
        out.write("    <td>" + str(params["MessageID"]) + "</td>\n")
    out.write("</tr>\n")
    out.write("\n")
    out.write("<tr>\n")
    out.write("<td>RepeatIndicator</td>\n")
    out.write("<td>uint</td>\n")
    if "RepeatIndicator" in params:
        out.write("    <td>" + str(params["RepeatIndicator"]) + "</td>\n")
        if str(params["RepeatIndicator"]) in RepeatIndicatorDecodeLut:
            out.write(
                "<td>"
                + RepeatIndicatorDecodeLut[str(params["RepeatIndicator"])]
                + "</td>"
            )
        else:
            out.write("<td><i>Missing LUT entry</i></td>")
    out.write("</tr>\n")
    out.write("\n")
    out.write("<tr>\n")
    out.write("<td>UserID</td>\n")
    out.write("<td>uint</td>\n")
    if "UserID" in params:
        out.write("    <td>" + str(params["UserID"]) + "</td>\n")
        out.write("    <td>" + str(params["UserID"]) + "</td>\n")
    out.write("</tr>\n")
    out.write("\n")
    out.write("<tr>\n")
    out.write("<td>AISversion</td>\n")
    out.write("<td>uint</td>\n")
    if "AISversion" in params:
        out.write("    <td>" + str(params["AISversion"]) + "</td>\n")
        out.write("    <td>" + str(params["AISversion"]) + "</td>\n")
    out.write("</tr>\n")
    out.write("\n")
    out.write("<tr>\n")
    out.write("<td>IMOnumber</td>\n")
    out.write("<td>uint</td>\n")
    if "IMOnumber" in params:
        out.write("    <td>" + str(params["IMOnumber"]) + "</td>\n")
        out.write("    <td>" + str(params["IMOnumber"]) + "</td>\n")
    out.write("</tr>\n")
    out.write("\n")
    out.write("<tr>\n")
    out.write("<td>callsign</td>\n")
    out.write("<td>aisstr6</td>\n")
    if "callsign" in params:
        out.write("    <td>" + str(params["callsign"]) + "</td>\n")
        out.write("    <td>" + str(params["callsign"]) + "</td>\n")
    out.write("</tr>\n")
    out.write("\n")
    out.write("<tr>\n")
    out.write("<td>name</td>\n")
    out.write("<td>aisstr6</td>\n")
    if "name" in params:
        out.write("    <td>" + str(params["name"]) + "</td>\n")
        out.write("    <td>" + str(params["name"]) + "</td>\n")
    out.write("</tr>\n")
    out.write("\n")
    out.write("<tr>\n")
    out.write("<td>shipandcargo</td>\n")
    out.write("<td>uint</td>\n")
    if "shipandcargo" in params:
        out.write("    <td>" + str(params["shipandcargo"]) + "</td>\n")
        if str(params["shipandcargo"]) in shipandcargoDecodeLut:
            out.write(
                "<td>" + shipandcargoDecodeLut[str(params["shipandcargo"])] + "</td>"
            )
        else:
            out.write("<td><i>Missing LUT entry</i></td>")
    out.write("</tr>\n")
    out.write("\n")
    out.write("<tr>\n")
    out.write("<td>dimA</td>\n")
    out.write("<td>uint</td>\n")
    if "dimA" in params:
        out.write("    <td>" + str(params["dimA"]) + "</td>\n")
        out.write("    <td>" + str(params["dimA"]) + "</td>\n")
    out.write("<td>m</td>\n")
    out.write("</tr>\n")
    out.write("\n")
    out.write("<tr>\n")
    out.write("<td>dimB</td>\n")
    out.write("<td>uint</td>\n")
    if "dimB" in params:
        out.write("    <td>" + str(params["dimB"]) + "</td>\n")
        out.write("    <td>" + str(params["dimB"]) + "</td>\n")
    out.write("<td>m</td>\n")
    out.write("</tr>\n")
    out.write("\n")
    out.write("<tr>\n")
    out.write("<td>dimC</td>\n")
    out.write("<td>uint</td>\n")
    if "dimC" in params:
        out.write("    <td>" + str(params["dimC"]) + "</td>\n")
        if str(params["dimC"]) in dimCDecodeLut:
            out.write("<td>" + dimCDecodeLut[str(params["dimC"])] + "</td>")
        else:
            out.write("<td><i>Missing LUT entry</i></td>")
    out.write("<td>m</td>\n")
    out.write("</tr>\n")
    out.write("\n")
    out.write("<tr>\n")
    out.write("<td>dimD</td>\n")
    out.write("<td>uint</td>\n")
    if "dimD" in params:
        out.write("    <td>" + str(params["dimD"]) + "</td>\n")
        if str(params["dimD"]) in dimDDecodeLut:
            out.write("<td>" + dimDDecodeLut[str(params["dimD"])] + "</td>")
        else:
            out.write("<td><i>Missing LUT entry</i></td>")
    out.write("<td>m</td>\n")
    out.write("</tr>\n")
    out.write("\n")
    out.write("<tr>\n")
    out.write("<td>fixtype</td>\n")
    out.write("<td>uint</td>\n")
    if "fixtype" in params:
        out.write("    <td>" + str(params["fixtype"]) + "</td>\n")
        if str(params["fixtype"]) in fixtypeDecodeLut:
            out.write("<td>" + fixtypeDecodeLut[str(params["fixtype"])] + "</td>")
        else:
            out.write("<td><i>Missing LUT entry</i></td>")
    out.write("</tr>\n")
    out.write("\n")
    out.write("<tr>\n")
    out.write("<td>ETAmonth</td>\n")
    out.write("<td>uint</td>\n")
    if "ETAmonth" in params:
        out.write("    <td>" + str(params["ETAmonth"]) + "</td>\n")
        out.write("    <td>" + str(params["ETAmonth"]) + "</td>\n")
    out.write("</tr>\n")
    out.write("\n")
    out.write("<tr>\n")
    out.write("<td>ETAday</td>\n")
    out.write("<td>uint</td>\n")
    if "ETAday" in params:
        out.write("    <td>" + str(params["ETAday"]) + "</td>\n")
        out.write("    <td>" + str(params["ETAday"]) + "</td>\n")
    out.write("</tr>\n")
    out.write("\n")
    out.write("<tr>\n")
    out.write("<td>ETAhour</td>\n")
    out.write("<td>uint</td>\n")
    if "ETAhour" in params:
        out.write("    <td>" + str(params["ETAhour"]) + "</td>\n")
        out.write("    <td>" + str(params["ETAhour"]) + "</td>\n")
    out.write("</tr>\n")
    out.write("\n")
    out.write("<tr>\n")
    out.write("<td>ETAminute</td>\n")
    out.write("<td>uint</td>\n")
    if "ETAminute" in params:
        out.write("    <td>" + str(params["ETAminute"]) + "</td>\n")
        out.write("    <td>" + str(params["ETAminute"]) + "</td>\n")
    out.write("</tr>\n")
    out.write("\n")
    out.write("<tr>\n")
    out.write("<td>draught</td>\n")
    out.write("<td>udecimal</td>\n")
    if "draught" in params:
        out.write("    <td>" + str(params["draught"]) + "</td>\n")
        if str(params["draught"]) in draughtDecodeLut:
            out.write("<td>" + draughtDecodeLut[str(params["draught"])] + "</td>")
        else:
            out.write("<td><i>Missing LUT entry</i></td>")
    out.write("<td>m</td>\n")
    out.write("</tr>\n")
    out.write("\n")
    out.write("<tr>\n")
    out.write("<td>destination</td>\n")
    out.write("<td>aisstr6</td>\n")
    if "destination" in params:
        out.write("    <td>" + str(params["destination"]) + "</td>\n")
        out.write("    <td>" + str(params["destination"]) + "</td>\n")
    out.write("</tr>\n")
    out.write("\n")
    out.write("<tr>\n")
    out.write("<td>dte</td>\n")
    out.write("<td>uint</td>\n")
    if "dte" in params:
        out.write("    <td>" + str(params["dte"]) + "</td>\n")
        if str(params["dte"]) in dteDecodeLut:
            out.write("<td>" + dteDecodeLut[str(params["dte"])] + "</td>")
        else:
            out.write("<td><i>Missing LUT entry</i></td>")
    out.write("</tr>\n")
    out.write("\n")
    out.write("<tr>\n")
    out.write("<td>Spare</td>\n")
    out.write("<td>uint</td>\n")
    if "Spare" in params:
        out.write("    <td>" + str(params["Spare"]) + "</td>\n")
        out.write("    <td>" + str(params["Spare"]) + "</td>\n")
    out.write("</tr>\n")
    out.write("</table>\n")


def printFields(
    params, out=sys.stdout, format="std", fieldList=None, dbType="postgres"
):
    """Print a shipdata message to stdout.

    Fields in params:
      - MessageID(uint): AIS message number.  Must be 5 (field automatically set to "5")
      - RepeatIndicator(uint): Indicated how many times a message has been repeated
      - UserID(uint): Unique ship identification number (MMSI)
      - AISversion(uint): Compliant with what edition.  0 is the first edition.
      - IMOnumber(uint): vessel identification number (different than mmsi)
      - callsign(aisstr6): Ship radio call sign
      - name(aisstr6): Vessel name
      - shipandcargo(uint): what
      - dimA(uint): Distance from bow to reference position
      - dimB(uint): Distance from reference position to stern
      - dimC(uint): Distance from port side to reference position
      - dimD(uint): Distance from reference position to starboard side
      - fixtype(uint): Method used for positioning
      - ETAmonth(uint): Estimated time of arrival - month
      - ETAday(uint): Estimated time of arrival - day
      - ETAhour(uint): Estimated time of arrival - hour
      - ETAminute(uint): Estimated time of arrival - minutes
      - draught(udecimal): Maximum present static draught
      - destination(aisstr6): Where is the vessel going
      - dte(uint): Data terminal ready
      - Spare(uint): Reserved for definition by a regional authority. (field automatically set to "0")
    Args:
        params: Dictionary of field names/values.
        out: File like object to write to.
    Returns:
        stdout
        text to out
    """

    if format == "std":
        out.write("shipdata:\n")
        if "MessageID" in params:
            out.write("    MessageID:        " + str(params["MessageID"]) + "\n")
        if "RepeatIndicator" in params:
            out.write("    RepeatIndicator:  " + str(params["RepeatIndicator"]) + "\n")
        if "UserID" in params:
            out.write("    UserID:           " + str(params["UserID"]) + "\n")
        if "AISversion" in params:
            out.write("    AISversion:       " + str(params["AISversion"]) + "\n")
        if "IMOnumber" in params:
            out.write("    IMOnumber:        " + str(params["IMOnumber"]) + "\n")
        if "callsign" in params:
            out.write("    callsign:         " + str(params["callsign"]) + "\n")
        if "name" in params:
            out.write("    name:             " + str(params["name"]) + "\n")
        if "shipandcargo" in params:
            out.write("    shipandcargo:     " + str(params["shipandcargo"]) + "\n")
        if "dimA" in params:
            out.write("    dimA:             " + str(params["dimA"]) + "\n")
        if "dimB" in params:
            out.write("    dimB:             " + str(params["dimB"]) + "\n")
        if "dimC" in params:
            out.write("    dimC:             " + str(params["dimC"]) + "\n")
        if "dimD" in params:
            out.write("    dimD:             " + str(params["dimD"]) + "\n")
        if "fixtype" in params:
            out.write("    fixtype:          " + str(params["fixtype"]) + "\n")
        if "ETAmonth" in params:
            out.write("    ETAmonth:         " + str(params["ETAmonth"]) + "\n")
        if "ETAday" in params:
            out.write("    ETAday:           " + str(params["ETAday"]) + "\n")
        if "ETAhour" in params:
            out.write("    ETAhour:          " + str(params["ETAhour"]) + "\n")
        if "ETAminute" in params:
            out.write("    ETAminute:        " + str(params["ETAminute"]) + "\n")
        if "draught" in params:
            out.write("    draught:          " + str(params["draught"]) + "\n")
        if "destination" in params:
            out.write("    destination:      " + str(params["destination"]) + "\n")
        if "dte" in params:
            out.write("    dte:              " + str(params["dte"]) + "\n")
        if "Spare" in params:
            out.write("    Spare:            " + str(params["Spare"]) + "\n")
        elif format == "csv":
            if options.fieldList is None:
                options.fieldList = fieldList
            needComma = False
            for field in fieldList:
                if needComma:
                    out.write(",")
                needComma = True
                if field in params:
                    out.write(str(params[field]))
                # else: leave it empty
            out.write("\n")
    elif format == "html":
        printHtml(params, out)
    elif format == "sql":
        sqlInsertStr(params, out, dbType=dbType)
    else:
        print("ERROR: unknown format:", format)
        raise AssertionError()


RepeatIndicatorEncodeLut = {
    "default": "0",
    "do not repeat any more": "3",
}  # RepeatIndicatorEncodeLut

RepeatIndicatorDecodeLut = {
    "0": "default",
    "3": "do not repeat any more",
}  # RepeatIndicatorEncodeLut

shipandcargoEncodeLut = {
    "Wing in ground (WIG), all ships of this type": "20",
    "Wing in ground (WIG), Hazardous category A": "21",
    "Wing in ground (WIG), Hazardous category B": "22",
    "Wing in ground (WIG), Hazardous category C": "23",
    "Wing in ground (WIG), Hazardous category D": "24",
    "Wing in ground (WIG), Reserved for future use": "25",
    "Wing in ground (WIG), Reserved for future use": "26",
    "Wing in ground (WIG), Reserved for future use": "27",
    "Wing in ground (WIG), Reserved for future use": "28",
    "Wing in ground (WIG), No additional information": "29",
    "fishing": "30",
    "towing": "31",
    "towing length exceeds 200m or breadth exceeds 25m": "32",
    "dredging or underwater ops": "33",
    "diving ops": "34",
    "military ops": "35",
    "sailing": "36",
    "pleasure craft": "37",
    "reserved": "38",
    "reserved": "39",
    "High speed craft (HSC), all ships of this type": "40",
    "High speed craft (HSC), Hazardous category A": "41",
    "High speed craft (HSC), Hazardous category B": "42",
    "High speed craft (HSC), Hazardous category C": "43",
    "High speed craft (HSC), Hazardous category D": "44",
    "High speed craft (HSC), Reserved for future use": "45",
    "High speed craft (HSC), Reserved for future use": "46",
    "High speed craft (HSC), Reserved for future use": "47",
    "High speed craft (HSC), Reserved for future use": "48",
    "High speed craft (HSC), No additional information": "49",
    "pilot vessel": "50",
    "search and rescue vessel": "51",
    "tug": "52",
    "port tender": "53",
    "anti-polution equipment": "54",
    "law enforcement": "55",
    "spare - local vessel": "56",
    "spare - local vessel": "57",
    "medical transport": "58",
    "ship according to RR Resolution No. 18": "59",
    "passenger, all ships of this type": "60",
    "passenger, Hazardous category A": "61",
    "passenger, Hazardous category B": "62",
    "passenger, Hazardous category C": "63",
    "passenger, Hazardous category D": "64",
    "passenger, Reserved for future use": "65",
    "passenger, Reserved for future use": "66",
    "passenger, Reserved for future use": "67",
    "passenger, Reserved for future use": "68",
    "passenger, No additional information": "69",
    "cargo, all ships of this type": "70",
    "cargo, Hazardous category A": "71",
    "cargo, Hazardous category B": "72",
    "cargo, Hazardous category C": "73",
    "cargo, Hazardous category D": "74",
    "cargo, Reserved for future use": "75",
    "cargo, Reserved for future use": "76",
    "cargo, Reserved for future use": "77",
    "cargo, Reserved for future use": "78",
    "cargo, No additional information": "79",
    "tanker, all ships of this type": "80",
    "tanker, Hazardous category A": "81",
    "tanker, Hazardous category B": "82",
    "tanker, Hazardous category C": "83",
    "tanker, Hazardous category D": "84",
    "tanker, Reserved for future use": "85",
    "tanker, Reserved for future use": "86",
    "tanker, Reserved for future use": "87",
    "tanker, Reserved for future use": "88",
    "tanker, No additional information": "89",
    "other type, all ships of this type": "90",
    "other type, Hazardous category A": "91",
    "other type, Hazardous category B": "92",
    "other type, Hazardous category C": "93",
    "other type, Hazardous category D": "94",
    "other type, Reserved for future use": "95",
    "other type, Reserved for future use": "96",
    "other type, Reserved for future use": "97",
    "other type, Reserved for future use": "98",
    "other type, No additional information": "99",
}  # shipandcargoEncodeLut

shipandcargoDecodeLut = {
    "20": "Wing in ground (WIG), all ships of this type",
    "21": "Wing in ground (WIG), Hazardous category A",
    "22": "Wing in ground (WIG), Hazardous category B",
    "23": "Wing in ground (WIG), Hazardous category C",
    "24": "Wing in ground (WIG), Hazardous category D",
    "25": "Wing in ground (WIG), Reserved for future use",
    "26": "Wing in ground (WIG), Reserved for future use",
    "27": "Wing in ground (WIG), Reserved for future use",
    "28": "Wing in ground (WIG), Reserved for future use",
    "29": "Wing in ground (WIG), No additional information",
    "30": "fishing",
    "31": "towing",
    "32": "towing length exceeds 200m or breadth exceeds 25m",
    "33": "dredging or underwater ops",
    "34": "diving ops",
    "35": "military ops",
    "36": "sailing",
    "37": "pleasure craft",
    "38": "reserved",
    "39": "reserved",
    "40": "High speed craft (HSC), all ships of this type",
    "41": "High speed craft (HSC), Hazardous category A",
    "42": "High speed craft (HSC), Hazardous category B",
    "43": "High speed craft (HSC), Hazardous category C",
    "44": "High speed craft (HSC), Hazardous category D",
    "45": "High speed craft (HSC), Reserved for future use",
    "46": "High speed craft (HSC), Reserved for future use",
    "47": "High speed craft (HSC), Reserved for future use",
    "48": "High speed craft (HSC), Reserved for future use",
    "49": "High speed craft (HSC), No additional information",
    "50": "pilot vessel",
    "51": "search and rescue vessel",
    "52": "tug",
    "53": "port tender",
    "54": "anti-polution equipment",
    "55": "law enforcement",
    "56": "spare - local vessel",
    "57": "spare - local vessel",
    "58": "medical transport",
    "59": "ship according to RR Resolution No. 18",
    "60": "passenger, all ships of this type",
    "61": "passenger, Hazardous category A",
    "62": "passenger, Hazardous category B",
    "63": "passenger, Hazardous category C",
    "64": "passenger, Hazardous category D",
    "65": "passenger, Reserved for future use",
    "66": "passenger, Reserved for future use",
    "67": "passenger, Reserved for future use",
    "68": "passenger, Reserved for future use",
    "69": "passenger, No additional information",
    "70": "cargo, all ships of this type",
    "71": "cargo, Hazardous category A",
    "72": "cargo, Hazardous category B",
    "73": "cargo, Hazardous category C",
    "74": "cargo, Hazardous category D",
    "75": "cargo, Reserved for future use",
    "76": "cargo, Reserved for future use",
    "77": "cargo, Reserved for future use",
    "78": "cargo, Reserved for future use",
    "79": "cargo, No additional information",
    "80": "tanker, all ships of this type",
    "81": "tanker, Hazardous category A",
    "82": "tanker, Hazardous category B",
    "83": "tanker, Hazardous category C",
    "84": "tanker, Hazardous category D",
    "85": "tanker, Reserved for future use",
    "86": "tanker, Reserved for future use",
    "87": "tanker, Reserved for future use",
    "88": "tanker, Reserved for future use",
    "89": "tanker, No additional information",
    "90": "other type, all ships of this type",
    "91": "other type, Hazardous category A",
    "92": "other type, Hazardous category B",
    "93": "other type, Hazardous category C",
    "94": "other type, Hazardous category D",
    "95": "other type, Reserved for future use",
    "96": "other type, Reserved for future use",
    "97": "other type, Reserved for future use",
    "98": "other type, Reserved for future use",
    "99": "other type, No additional information",
}  # shipandcargoEncodeLut

dimCEncodeLut = {
    "63 m or greater": "63",
}  # dimCEncodeLut

dimCDecodeLut = {
    "63": "63 m or greater",
}  # dimCEncodeLut

dimDEncodeLut = {
    "63 m or greater": "63",
}  # dimDEncodeLut

dimDDecodeLut = {
    "63": "63 m or greater",
}  # dimDEncodeLut

fixtypeEncodeLut = {
    "undefined": "0",
    "GPS": "1",
    "GLONASS": "2",
    "combined GPS/GLONASS": "3",
    "Loran-C": "4",
    "Chayka": "5",
    "integrated navigation system": "6",
    "surveyed": "7",
}  # fixtypeEncodeLut

fixtypeDecodeLut = {
    "0": "undefined",
    "1": "GPS",
    "2": "GLONASS",
    "3": "combined GPS/GLONASS",
    "4": "Loran-C",
    "5": "Chayka",
    "6": "integrated navigation system",
    "7": "surveyed",
}  # fixtypeEncodeLut

draughtEncodeLut = {
    "25.5 m or greater": "25.5",
}  # draughtEncodeLut

draughtDecodeLut = {
    "25.5": "25.5 m or greater",
}  # draughtEncodeLut

dteEncodeLut = {
    "available": "0",
    "not available": "1",
}  # dteEncodeLut

dteDecodeLut = {
    "0": "available",
    "1": "not available",
}  # dteEncodeLut

######################################################################
# SQL SUPPORT
######################################################################

dbTableName = "shipdata"
"Database table name"


def sqlCreateStr(
    outfile=sys.stdout,
    fields=None,
    extraFields=None,
    addCoastGuardFields=True,
    dbType="postgres",
):
    """
    Return the SQL CREATE command for this message type
    Args:
        outfile: file like object to print to.
        fields: which fields to put in the create.  Defaults to all.
        extraFields: A sequence of tuples containing (name,sql type) for additional fields
        addCoastGuardFields: Add the extra fields that come after the NMEA check some from the USCG N-AIS format
        dbType: Which flavor of database we are using so that the create is tailored ('sqlite' or 'postgres')
    @type addCoastGuardFields: bool
    Returns:
        sql create string
        str

    @see: sqlCreate
    """
    # FIX: should this sqlCreate be the same as in LaTeX (createFuncName) rather than hard coded?
    outfile.write(
        str(sqlCreate(fields, extraFields, addCoastGuardFields, dbType=dbType))
    )


def sqlCreate(
    fields=None, extraFields=None, addCoastGuardFields=True, dbType="postgres"
):
    """Return the sqlhelp object to create the table.

    Args:
        fields: which fields to put in the create.  Defaults to all.
        extraFields: A sequence of tuples containing (name,sql type) for additional fields
        addCoastGuardFields: Add the extra fields that come after the NMEA check some from the USCG N-AIS format
    @type addCoastGuardFields: bool
        dbType: Which flavor of database we are using so that the create is tailored ('sqlite' or 'postgres')
    Returns:
        An object that can be used to generate a return
        sqlhelp.create
    """
    if fields is None:
        fields = fieldList
    c = sqlhelp.create("shipdata", dbType=dbType)
    c.addPrimaryKey()
    if "MessageID" in fields:
        c.addInt("MessageID")
    if "RepeatIndicator" in fields:
        c.addInt("RepeatIndicator")
    if "UserID" in fields:
        c.addInt("UserID")
    if "AISversion" in fields:
        c.addInt("AISversion")
    if "IMOnumber" in fields:
        c.addInt("IMOnumber")
    if "callsign" in fields:
        c.addVarChar("callsign", 7)
    if "name" in fields:
        c.addVarChar("name", 20)
    if "shipandcargo" in fields:
        c.addInt("shipandcargo")
    if "dimA" in fields:
        c.addInt("dimA")
    if "dimB" in fields:
        c.addInt("dimB")
    if "dimC" in fields:
        c.addInt("dimC")
    if "dimD" in fields:
        c.addInt("dimD")
    if "fixtype" in fields:
        c.addInt("fixtype")
    if "ETAmonth" in fields:
        c.addInt("ETAmonth")
    if "ETAday" in fields:
        c.addInt("ETAday")
    if "ETAhour" in fields:
        c.addInt("ETAhour")
    if "ETAminute" in fields:
        c.addInt("ETAminute")
    if "draught" in fields:
        c.addDecimal("draught", 3, 1)
    if "destination" in fields:
        c.addVarChar("destination", 20)
    if "dte" in fields:
        c.addInt("dte")
    if "Spare" in fields:
        c.addInt("Spare")

    if addCoastGuardFields:
        # c.addInt('cg_s_rssi')  # Relative signal strength indicator
        # c.addInt('cg_d_strength')  # dBm receive strength
        # c.addVarChar('cg_x',10)  # Idonno
        c.addInt("cg_t_arrival")  # Receive timestamp from the AIS equipment 'T'
        c.addInt("cg_s_slotnum")  # Slot received in
        c.addVarChar(
            "cg_r", 15
        )  # Receiver station ID  -  should usually be an MMSI, but sometimes is a string
        c.addInt("cg_sec")  # UTC seconds since the epoch

        c.addTimestamp(
            "cg_timestamp"
        )  # UTC decoded cg_sec - not actually in the data stream

    return c


def sqlInsertStr(params, outfile=sys.stdout, extraParams=None, dbType="postgres"):
    """
    Return the SQL INSERT command for this message type
    Args:
        params: dictionary of values keyed by field name
        outfile: file like object to print to.
        extraParams: A sequence of tuples containing (name,sql type) for additional fields
    Returns:
        sql create string
        str

    @see: sqlCreate
    """
    outfile.write(str(sqlInsert(params, extraParams, dbType=dbType)))


def sqlInsert(params, extraParams=None, dbType="postgres"):
    """
    Give the SQL INSERT statement
    Args:
        params: dict keyed by field name of values
        extraParams: any extra fields that you have created beyond the normal ais message fields
    Returns:
        sqlhelp.insert
        insert class instance
     TODO(schwehr):allow optional type checking of params?
    @warning: this will take invalid keys happily and do what???
    """

    i = sqlhelp.insert("shipdata", dbType=dbType)

    if dbType == "postgres":
        finished = []
        for key in params:
            if key in finished:
                continue

            if key not in toPgFields and key not in fromPgFields:
                if type(params[key]) == Decimal:
                    i.add(key, float(params[key]))
                else:
                    i.add(key, params[key])
            elif key in fromPgFields:
                val = params[key]
                # Had better be a WKT type like POINT(-88.1 30.321)
                i.addPostGIS(key, val)
                finished.append(key)
            else:
                # Need to construct the type.
                pgName = toPgFields[key]
                # valStr='GeomFromText(\''+pgTypes[pgName]+'('
                valStr = pgTypes[pgName] + "("
                vals = []
                for nonPgKey in fromPgFields[pgName]:
                    vals.append(str(params[nonPgKey]))
                    finished.append(nonPgKey)
                valStr += " ".join(vals) + ")"
                i.addPostGIS(pgName, valStr)
    else:
        for key in params:
            if type(params[key]) == Decimal:
                i.add(key, float(params[key]))
            else:
                i.add(key, params[key])

    if extraParams is not None:
        for key in extraParams:
            i.add(key, extraParams[key])

    return i


######################################################################
# LATEX SUPPORT
######################################################################


def latexDefinitionTable(outfile=sys.stdout):
    """
    Return the LaTeX definition table for this message type
    Args:
        outfile: file like object to print to.
    @type outfile: file obj
    Returns:
        LaTeX table string via the outfile
        str

    """
    o = outfile

    o.write("""
\\begin{table}%[htb]
\\centering
\\begin{tabular}{|l|c|l|}
\\hline
Parameter & Number of bits & Description
\\\\  \\hline\\hline
MessageID & 6 & AIS message number.  Must be 5 \\\\ \\hline
RepeatIndicator & 2 & Indicated how many times a message has been repeated \\\\ \\hline
UserID & 30 & Unique ship identification number (MMSI) \\\\ \\hline
AISversion & 2 & Compliant with what edition.  0 is the first edition. \\\\ \\hline
IMOnumber & 30 & vessel identification number (different than mmsi) \\\\ \\hline
callsign & 42 & Ship radio call sign \\\\ \\hline
name & 120 & Vessel name \\\\ \\hline
shipandcargo & 8 & Type of ship and cargo type \\\\ \\hline
dimA & 9 & Distance from bow to reference position \\\\ \\hline
dimB & 9 & Distance from reference position to stern \\\\ \\hline
dimC & 6 & Distance from port side to reference position \\\\ \\hline
dimD & 6 & Distance from reference position to starboard side \\\\ \\hline
fixtype & 4 & Method used for positioning \\\\ \\hline
ETAmonth & 4 & Estimated time of arrival - month \\\\ \\hline
ETAday & 5 & Estimated time of arrival - day \\\\ \\hline
ETAhour & 5 & Estimated time of arrival - hour \\\\ \\hline
ETAminute & 6 & Estimated time of arrival - minutes \\\\ \\hline
draught & 8 & Maximum present static draught \\\\ \\hline
destination & 120 & Where is the vessel going \\\\ \\hline
dte & 1 & Data terminal ready \\\\ \\hline
Spare & 1 & Reserved for definition by a regional authority.\\\\ \\hline \\hline
Total bits & 424 & Appears to take 2 slots \\\\ \\hline
\\end{tabular}
\\caption{AIS message number 5: Class A vessel data report}
\\label{tab:shipdata}
\\end{table}
""")


######################################################################
# Text Definition
######################################################################


def textDefinitionTable(outfile=sys.stdout, delim="    "):
    """Return the text definition table for this message type

    Args:
        outfile: file like object to print to.
    @type outfile: file obj
    Returns:
        text table string via the outfile
        str

    """
    o = outfile
    o.write(
        "Parameter"
        + delim
        + "Number of bits"
        + delim
        + """Description
MessageID"""
        + delim
        + "6"
        + delim
        + """AIS message number.  Must be 5
RepeatIndicator"""
        + delim
        + "2"
        + delim
        + """Indicated how many times a message has been repeated
UserID"""
        + delim
        + "30"
        + delim
        + """Unique ship identification number (MMSI)
AISversion"""
        + delim
        + "2"
        + delim
        + """Compliant with what edition.  0 is the first edition.
IMOnumber"""
        + delim
        + "30"
        + delim
        + """vessel identification number (different than mmsi)
callsign"""
        + delim
        + "42"
        + delim
        + """Ship radio call sign
name"""
        + delim
        + "120"
        + delim
        + """Vessel name
shipandcargo"""
        + delim
        + "8"
        + delim
        + """Type of ship and cargo type
dimA"""
        + delim
        + "9"
        + delim
        + """Distance from bow to reference position
dimB"""
        + delim
        + "9"
        + delim
        + """Distance from reference position to stern
dimC"""
        + delim
        + "6"
        + delim
        + """Distance from port side to reference position
dimD"""
        + delim
        + "6"
        + delim
        + """Distance from reference position to starboard side
fixtype"""
        + delim
        + "4"
        + delim
        + """Method used for positioning
ETAmonth"""
        + delim
        + "4"
        + delim
        + """Estimated time of arrival - month
ETAday"""
        + delim
        + "5"
        + delim
        + """Estimated time of arrival - day
ETAhour"""
        + delim
        + "5"
        + delim
        + """Estimated time of arrival - hour
ETAminute"""
        + delim
        + "6"
        + delim
        + """Estimated time of arrival - minutes
draught"""
        + delim
        + "8"
        + delim
        + """Maximum present static draught
destination"""
        + delim
        + "120"
        + delim
        + """Where is the vessel going
dte"""
        + delim
        + "1"
        + delim
        + """Data terminal ready
Spare"""
        + delim
        + "1"
        + delim
        + """Reserved for definition by a regional authority.
Total bits"""
        + delim
        + """424"""
        + delim
        + """Appears to take 2 slots"""
    )


######################################################################
# UNIT TESTING
######################################################################
def testParams():
    """Return a params file base on the testvalue tags.
    Returns:
        dict
        params based on testvalue tags
    """
    params = {}
    params["MessageID"] = 5
    params["RepeatIndicator"] = 1
    params["UserID"] = 1193046
    params["AISversion"] = 0
    params["IMOnumber"] = 3210
    params["callsign"] = "PIRATE1"
    params["name"] = "BLACK PEARL@@@@@@@@@"
    params["shipandcargo"] = 55
    params["dimA"] = 10
    params["dimB"] = 11
    params["dimC"] = 12
    params["dimD"] = 13
    params["fixtype"] = 1
    params["ETAmonth"] = 2
    params["ETAday"] = 28
    params["ETAhour"] = 9
    params["ETAminute"] = 54
    params["draught"] = Decimal("21.1")
    params["destination"] = "NOWHERE@@@@@@@@@@@@@"
    params["dte"] = 0
    params["Spare"] = 0

    return params


class Testshipdata(unittest.TestCase):
    """Use testvalue tag text from each type to build test case the shipdata message"""

    def testEncodeDecode(self):
        params = testParams()
        bits = encode(params)
        r = decode(bits)

        # Check that each parameter came through ok.
        assert r["MessageID"] == params["MessageID"]
        assert r["RepeatIndicator"] == params["RepeatIndicator"]
        assert r["UserID"] == params["UserID"]
        assert r["AISversion"] == params["AISversion"]
        assert r["IMOnumber"] == params["IMOnumber"]
        assert r["callsign"] == params["callsign"]
        assert r["name"] == params["name"]
        assert r["shipandcargo"] == params["shipandcargo"]
        assert r["dimA"] == params["dimA"]
        assert r["dimB"] == params["dimB"]
        assert r["dimC"] == params["dimC"]
        assert r["dimD"] == params["dimD"]
        assert r["fixtype"] == params["fixtype"]
        assert r["ETAmonth"] == params["ETAmonth"]
        assert r["ETAday"] == params["ETAday"]
        assert r["ETAhour"] == params["ETAhour"]
        assert r["ETAminute"] == params["ETAminute"]
        self.assertAlmostEqual(r["draught"], params["draught"], 1)
        assert r["destination"] == params["destination"]
        assert r["dte"] == params["dte"]
        assert r["Spare"] == params["Spare"]


def addMsgOptions(parser):
    parser.add_option(
        "-d",
        "--decode",
        dest="doDecode",
        default=False,
        action="store_true",
        help='decode a "shipdata" AIS message',
    )
    parser.add_option(
        "-e",
        "--encode",
        dest="doEncode",
        default=False,
        action="store_true",
        help='encode a "shipdata" AIS message',
    )
    parser.add_option(
        "--RepeatIndicator-field",
        dest="RepeatIndicatorField",
        default=0,
        metavar="uint",
        type="int",
        help="Field parameter value [default: %default]",
    )
    parser.add_option(
        "--UserID-field",
        dest="UserIDField",
        metavar="uint",
        type="int",
        help="Field parameter value [default: %default]",
    )
    parser.add_option(
        "--AISversion-field",
        dest="AISversionField",
        default=0,
        metavar="uint",
        type="int",
        help="Field parameter value [default: %default]",
    )
    parser.add_option(
        "--IMOnumber-field",
        dest="IMOnumberField",
        default=0,
        metavar="uint",
        type="int",
        help="Field parameter value [default: %default]",
    )
    parser.add_option(
        "--callsign-field",
        dest="callsignField",
        default="@@@@@@@",
        metavar="aisstr6",
        type="string",
        help="Field parameter value [default: %default]",
    )
    parser.add_option(
        "--name-field",
        dest="nameField",
        default="@@@@@@@@@@@@@@@@@@@@",
        metavar="aisstr6",
        type="string",
        help="Field parameter value [default: %default]",
    )
    parser.add_option(
        "--shipandcargo-field",
        dest="shipandcargoField",
        default=0,
        metavar="uint",
        type="int",
        help="Field parameter value [default: %default]",
    )
    parser.add_option(
        "--dimA-field",
        dest="dimAField",
        default=0,
        metavar="uint",
        type="int",
        help="Field parameter value [default: %default]",
    )
    parser.add_option(
        "--dimB-field",
        dest="dimBField",
        default=0,
        metavar="uint",
        type="int",
        help="Field parameter value [default: %default]",
    )
    parser.add_option(
        "--dimC-field",
        dest="dimCField",
        default=0,
        metavar="uint",
        type="int",
        help="Field parameter value [default: %default]",
    )
    parser.add_option(
        "--dimD-field",
        dest="dimDField",
        default=0,
        metavar="uint",
        type="int",
        help="Field parameter value [default: %default]",
    )
    parser.add_option(
        "--fixtype-field",
        dest="fixtypeField",
        default=0,
        metavar="uint",
        type="int",
        help="Field parameter value [default: %default]",
    )
    parser.add_option(
        "--ETAmonth-field",
        dest="ETAmonthField",
        default=0,
        metavar="uint",
        type="int",
        help="Field parameter value [default: %default]",
    )
    parser.add_option(
        "--ETAday-field",
        dest="ETAdayField",
        default=0,
        metavar="uint",
        type="int",
        help="Field parameter value [default: %default]",
    )
    parser.add_option(
        "--ETAhour-field",
        dest="ETAhourField",
        default=24,
        metavar="uint",
        type="int",
        help="Field parameter value [default: %default]",
    )
    parser.add_option(
        "--ETAminute-field",
        dest="ETAminuteField",
        default=60,
        metavar="uint",
        type="int",
        help="Field parameter value [default: %default]",
    )
    parser.add_option(
        "--draught-field",
        dest="draughtField",
        default=Decimal("0"),
        metavar="udecimal",
        type="string",
        help="Field parameter value [default: %default]",
    )
    parser.add_option(
        "--destination-field",
        dest="destinationField",
        default="@@@@@@@@@@@@@@@@@@@@",
        metavar="aisstr6",
        type="string",
        help="Field parameter value [default: %default]",
    )
    parser.add_option(
        "--dte-field",
        dest="dteField",
        metavar="uint",
        type="int",
        help="Field parameter value [default: %default]",
    )


def main():
    from optparse import OptionParser

    parser = OptionParser(usage="%prog [options]")

    parser.add_option(
        "--unit-test",
        dest="unittest",
        default=False,
        action="store_true",
        help="run the unit tests",
    )
    parser.add_option(
        "-v",
        "--verbose",
        dest="verbose",
        default=False,
        action="store_true",
        help="Make the test output verbose",
    )

    # FIX: remove nmea from binary messages.  No way to build the whole packet?
    # FIX: or build the surrounding msg 8 for a broadcast?
    typeChoices = (
        "binary",
        "nmeapayload",
        "nmea",
    )  # FIX: what about a USCG type message?
    parser.add_option(
        "-t",
        "--type",
        choices=typeChoices,
        type="choice",
        dest="ioType",
        default="nmeapayload",
        help="What kind of string to write for encoding ("
        + ", ".join(typeChoices)
        + ") [default: %default]",
    )

    outputChoices = ("std", "html", "csv", "sql")
    parser.add_option(
        "-T",
        "--output-type",
        choices=outputChoices,
        type="choice",
        dest="outputType",
        default="std",
        help="What kind of string to output (" + ", ".join(outputChoices) + ") "
        "[default: %default]",
    )

    parser.add_option(
        "-o",
        "--output",
        dest="outputFileName",
        default=None,
        help="Name of the python file to write [default: stdout]",
    )

    parser.add_option(
        "-f",
        "--fields",
        dest="fieldList",
        default=None,
        action="append",
        choices=fieldList,
        help="Which fields to include in the output.  Currently only for csv "
        "output [default: all]",
    )

    parser.add_option(
        "-p",
        "--print-csv-field-list",
        dest="printCsvfieldList",
        default=False,
        action="store_true",
        help="Print the field name for csv",
    )

    parser.add_option(
        "-c",
        "--sql-create",
        dest="sqlCreate",
        default=False,
        action="store_true",
        help="Print out an sql create command for the table.",
    )

    parser.add_option(
        "--latex-table",
        dest="latexDefinitionTable",
        default=False,
        action="store_true",
        help="Print a LaTeX table of the type",
    )

    parser.add_option(
        "--text-table",
        dest="textDefinitionTable",
        default=False,
        action="store_true",
        help="Print delimited table of the type (for Word table importing)",
    )

    parser.add_option(
        "--delimt-text-table",
        dest="delimTextDefinitionTable",
        default="    ",
        help="Delimiter for text table [default: '%default'] "
        "(for Word table importing)",
    )

    dbChoices = ("sqlite", "postgres")
    parser.add_option(
        "-D",
        "--db-type",
        dest="dbType",
        default="postgres",
        choices=dbChoices,
        type="choice",
        help="What kind of database (" + ", ".join(dbChoices) + ") [default: %default]",
    )

    addMsgOptions(parser)

    options, args = parser.parse_args()

    if options.unittest:
        sys.argv = [sys.argv[0]]
        if options.verbose:
            sys.argv.append("-v")
        unittest.main()

    outfile = sys.stdout
    if options.outputFileName is not None:
        outfile = file(options.outputFileName, "w")

    if options.doEncode:
        # Make sure all non required options are specified.
        if options.RepeatIndicatorField is None:
            parser.error("missing value for RepeatIndicatorField")
        if options.UserIDField is None:
            parser.error("missing value for UserIDField")
        if options.AISversionField is None:
            parser.error("missing value for AISversionField")
        if options.IMOnumberField is None:
            parser.error("missing value for IMOnumberField")
        if options.callsignField is None:
            parser.error("missing value for callsignField")
        if options.nameField is None:
            parser.error("missing value for nameField")
        if options.shipandcargoField is None:
            parser.error("missing value for shipandcargoField")
        if options.dimAField is None:
            parser.error("missing value for dimAField")
        if options.dimBField is None:
            parser.error("missing value for dimBField")
        if options.dimCField is None:
            parser.error("missing value for dimCField")
        if options.dimDField is None:
            parser.error("missing value for dimDField")
        if options.fixtypeField is None:
            parser.error("missing value for fixtypeField")
        if options.ETAmonthField is None:
            parser.error("missing value for ETAmonthField")
        if options.ETAdayField is None:
            parser.error("missing value for ETAdayField")
        if options.ETAhourField is None:
            parser.error("missing value for ETAhourField")
        if options.ETAminuteField is None:
            parser.error("missing value for ETAminuteField")
        if options.draughtField is None:
            parser.error("missing value for draughtField")
        if options.destinationField is None:
            parser.error("missing value for destinationField")
        if options.dteField is None:
            parser.error("missing value for dteField")
    msgDict = {
        "MessageID": "5",
        "RepeatIndicator": options.RepeatIndicatorField,
        "UserID": options.UserIDField,
        "AISversion": options.AISversionField,
        "IMOnumber": options.IMOnumberField,
        "callsign": options.callsignField,
        "name": options.nameField,
        "shipandcargo": options.shipandcargoField,
        "dimA": options.dimAField,
        "dimB": options.dimBField,
        "dimC": options.dimCField,
        "dimD": options.dimDField,
        "fixtype": options.fixtypeField,
        "ETAmonth": options.ETAmonthField,
        "ETAday": options.ETAdayField,
        "ETAhour": options.ETAhourField,
        "ETAminute": options.ETAminuteField,
        "draught": options.draughtField,
        "destination": options.destinationField,
        "dte": options.dteField,
        "Spare": "0",
    }

    bits = encode(msgDict)
    if options.ioType == "binary":
        print(str(bits))
    elif options.ioType == "nmeapayload":
        # FIX: figure out if this might be necessary at compile time
        bitLen = len(bits)
        if bitLen % 6 != 0:
            bits = bits + BitVector(size=(6 - (bitLen % 6)))  # Pad out to multiple of 6
        print(binary.bitvectoais6(bits)[0])

    # FIX: Do not emit this option for the binary message payloads.  Does not make sense.
    elif options.ioType == "nmea":
        nmea = uscg.create_nmea(bits)
        print(nmea)
    else:
        sys.exit("ERROR: unknown ioType.  Help!")

        if options.sqlCreate:
            sqlCreateStr(outfile, options.fieldList, dbType=options.dbType)

        if options.latexDefinitionTable:
            latexDefinitionTable(outfile)

        # For conversion to word tables
        if options.textDefinitionTable:
            textDefinitionTable(outfile, options.delimTextDefinitionTable)

        if options.printCsvfieldList:
            # Make a csv separated list of fields that will be displayed for csv
            if options.fieldList is None:
                options.fieldList = fieldList
            import io

            buf = io.StringIO()
            for field in options.fieldList:
                buf.write(field + ",")
            result = buf.getvalue()
            if result[-1] == ",":
                print(result[:-1])
            else:
                print(result)

        if options.doDecode:
            if len(args) == 0:
                args = sys.stdin
            for msg in args:
                bv = None

                if msg[0] in ("$", "!") and msg[3:6] in ("VDM", "VDO"):
                    # Found nmea
                    # FIX: do checksum
                    bv = binary.ais6tobitvec(msg.split(",")[5])
                else:  # either binary or nmeapayload... expect mostly nmeapayloads
                    # assumes that an all 0 and 1 string can not be a nmeapayload
                    binaryMsg = True
                    for c in msg:
                        if c not in ("0", "1"):
                            binaryMsg = False
                            break
                    if binaryMsg:
                        bv = BitVector(bitstring=msg)
                    else:  # nmeapayload
                        bv = binary.ais6tobitvec(msg)

                printFields(
                    decode(bv),
                    out=outfile,
                    format=options.outputType,
                    fieldList=options.fieldList,
                    dbType=options.dbType,
                )


############################################################
if __name__ == "__main__":
    main()
