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

from aisutils import binary, sqlhelp, uscg
from BitVector import BitVector

TrueBV = BitVector.from_bitstring("1")
FalseBV = BitVector.from_bitstring("0")


fieldList = (
    "MessageID",
    "RepeatIndicator",
    "UserID",
    "Altitude",
    "SOG",
    "PositionAccuracy",
    "Position_longitude",
    "Position_latitude",
    "COG",
    "TimeStamp",
    "Reserved",
    "DTE",
    "Spare",
    "assigned_mode",
    "RAIM",
    "comm_state",
    "state_syncstate",
    "state_slottimeout",
    "state_slotoffset",
)

fieldListPostgres = (
    "MessageID",
    "RepeatIndicator",
    "UserID",
    "Altitude",
    "SOG",
    "PositionAccuracy",
    "Position",  # PostGIS data type
    "COG",
    "TimeStamp",
    "Reserved",
    "DTE",
    "Spare",
    "assigned_mode",
    "RAIM",
    "comm_state",
    "state_syncstate",
    "state_slottimeout",
    "state_slotoffset",
)

toPgFields = {
    "Position_longitude": "Position",
    "Position_latitude": "Position",
}
"""
Go to the Postgis field names from the straight field name
"""

fromPgFields = {
    "Position": (
        "Position_longitude",
        "Position_latitude",
    ),
}
"""
Go from the Postgis field names to the straight field name
"""

pgTypes = {
    "Position": "POINT",
}
"""
Lookup table for each postgis field name to get its type.
"""


def encode(params, validate=False):
    """Create a SARposition binary message payload to pack into an AIS Msg SARposition.

    Fields in params:
      - MessageID(uint): AIS message number.  Must be 9 (field automatically set to "9")
      - RepeatIndicator(uint): Indicated how many times a message has been repeated
      - UserID(uint): Unique ship identification number (MMSI)
      - Altitude(uint): Altitude (GNSS)
      - SOG(uint): Speed over ground
      - PositionAccuracy(uint): Accuracy of positioning fixes
      - Position_longitude(decimal): Location of the vessel  East West location
      - Position_latitude(decimal): Location of the vessel  North South location
      - COG(udecimal): Course over ground
      - TimeStamp(uint): UTC second when the report was generated
      - Reserved(uint): Reserved for regional applications.  Should be set to zero. (field automatically set to "0")
      - DTE(bool): Dtta terminal ready
      - Spare(uint): Not used.  Should be set to zero. (field automatically set to "0")
      - assigned_mode(uint): autonomous or assigned mode
      - RAIM(bool): Receiver autonomous integrity monitoring flag
      - comm_state(uint): SOTDMA or ITDMA
      - state_syncstate(uint): Communications State - SOTDMA  Synchronization state
      - state_slottimeout(uint): Communications State - SOTDMA  Frames remaining until a new slot is selected
      - state_slotoffset(uint): Communications State - SOTDMA  In what slot will the next transmission occur. BROKEN
    Args:
        params: Dictionary of field names/values.  Throws a ValueError exception if required is missing
        validate: Set to true to cause checking to occur.  Runs slower.  FIX: not implemented.
    Returns:
        BitVector
        encoded binary message (for binary messages, this needs to be wrapped in a msg 8
    @note: The returned bits may not be 6 bit aligned.  It is up to you to pad out the bits.
    """

    bvList = []
    bvList.append(binary.setBitVectorSize(BitVector.from_int(9), 6))
    if "RepeatIndicator" in params:
        bvList.append(
            binary.setBitVectorSize(BitVector.from_int(params["RepeatIndicator"]), 2)
        )
    else:
        bvList.append(binary.setBitVectorSize(BitVector.from_int(0), 2))
    bvList.append(binary.setBitVectorSize(BitVector.from_int(params["UserID"]), 30))
    if "Altitude" in params:
        bvList.append(binary.setBitVectorSize(BitVector.from_int(params["Altitude"]), 12))
    else:
        bvList.append(binary.setBitVectorSize(BitVector.from_int(4095), 12))
    if "SOG" in params:
        bvList.append(binary.setBitVectorSize(BitVector.from_int(params["SOG"]), 10))
    else:
        bvList.append(binary.setBitVectorSize(BitVector.from_int(1023), 10))
    bvList.append(
        binary.setBitVectorSize(BitVector.from_int(params["PositionAccuracy"]), 1)
    )
    if "Position_longitude" in params:
        bvList.append(
            binary.bvFromSignedInt(
                int(Decimal(params["Position_longitude"]) * Decimal("600000")), 28
            )
        )
    else:
        bvList.append(binary.bvFromSignedInt(108600000, 28))
    if "Position_latitude" in params:
        bvList.append(
            binary.bvFromSignedInt(
                int(Decimal(params["Position_latitude"]) * Decimal("600000")), 27
            )
        )
    else:
        bvList.append(binary.bvFromSignedInt(54600000, 27))
    if "COG" in params:
        bvList.append(
            binary.setBitVectorSize(
                BitVector.from_int(int(Decimal(params["COG"]) * Decimal("10"))), 12
            )
        )
    else:
        bvList.append(binary.setBitVectorSize(BitVector.from_int(3600), 12))
    if "TimeStamp" in params:
        bvList.append(binary.setBitVectorSize(BitVector.from_int(params["TimeStamp"]), 6))
    else:
        bvList.append(binary.setBitVectorSize(BitVector.from_int(60), 6))
    bvList.append(binary.setBitVectorSize(BitVector.from_int(0), 8))
    if params["DTE"]:
        bvList.append(TrueBV)
    else:
        bvList.append(FalseBV)
    bvList.append(binary.setBitVectorSize(BitVector.from_int(0), 3))
    bvList.append(binary.setBitVectorSize(BitVector.from_int(params["assigned_mode"]), 1))
    if params["RAIM"]:
        bvList.append(TrueBV)
    else:
        bvList.append(FalseBV)
    bvList.append(binary.setBitVectorSize(BitVector.from_int(params["comm_state"]), 1))
    bvList.append(
        binary.setBitVectorSize(BitVector.from_int(params["state_syncstate"]), 2)
    )
    bvList.append(
        binary.setBitVectorSize(BitVector.from_int(params["state_slottimeout"]), 3)
    )
    bvList.append(
        binary.setBitVectorSize(BitVector.from_int(params["state_slotoffset"]), 14)
    )

    return binary.joinBV(bvList)


def decode(bv, validate=False):
    """Unpack a SARposition message.

    Fields in params:
      - MessageID(uint): AIS message number.  Must be 9 (field automatically set to "9")
      - RepeatIndicator(uint): Indicated how many times a message has been repeated
      - UserID(uint): Unique ship identification number (MMSI)
      - Altitude(uint): Altitude (GNSS)
      - SOG(uint): Speed over ground
      - PositionAccuracy(uint): Accuracy of positioning fixes
      - Position_longitude(decimal): Location of the vessel  East West location
      - Position_latitude(decimal): Location of the vessel  North South location
      - COG(udecimal): Course over ground
      - TimeStamp(uint): UTC second when the report was generated
      - Reserved(uint): Reserved for regional applications.  Should be set to zero. (field automatically set to "0")
      - DTE(bool): Dtta terminal ready
      - Spare(uint): Not used.  Should be set to zero. (field automatically set to "0")
      - assigned_mode(uint): autonomous or assigned mode
      - RAIM(bool): Receiver autonomous integrity monitoring flag
      - comm_state(uint): SOTDMA or ITDMA
      - state_syncstate(uint): Communications State - SOTDMA  Synchronization state
      - state_slottimeout(uint): Communications State - SOTDMA  Frames remaining until a new slot is selected
      - state_slotoffset(uint): Communications State - SOTDMA  In what slot will the next transmission occur. BROKEN
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
    r["MessageID"] = 9
    r["RepeatIndicator"] = int(bv[6:8])
    r["UserID"] = int(bv[8:38])
    r["Altitude"] = int(bv[38:50])
    r["SOG"] = int(bv[50:60])
    r["PositionAccuracy"] = int(bv[60:61])
    r["Position_longitude"] = Decimal(binary.signedIntFromBV(bv[61:89])) / Decimal(
        "600000"
    )
    r["Position_latitude"] = Decimal(binary.signedIntFromBV(bv[89:116])) / Decimal(
        "600000"
    )
    r["COG"] = Decimal(int(bv[116:128])) / Decimal("10")
    r["TimeStamp"] = int(bv[128:134])
    r["Reserved"] = 0
    r["DTE"] = bool(int(bv[142:143]))
    r["Spare"] = 0
    r["assigned_mode"] = int(bv[146:147])
    r["RAIM"] = bool(int(bv[147:148]))
    r["comm_state"] = int(bv[148:149])
    r["state_syncstate"] = int(bv[149:151])
    r["state_slottimeout"] = int(bv[151:154])
    r["state_slotoffset"] = int(bv[154:168])
    return r


def decodeMessageID(bv, validate=False):
    return 9


def decodeRepeatIndicator(bv, validate=False):
    return int(bv[6:8])


def decodeUserID(bv, validate=False):
    return int(bv[8:38])


def decodeAltitude(bv, validate=False):
    return int(bv[38:50])


def decodeSOG(bv, validate=False):
    return int(bv[50:60])


def decodePositionAccuracy(bv, validate=False):
    return int(bv[60:61])


def decodePosition_longitude(bv, validate=False):
    return Decimal(binary.signedIntFromBV(bv[61:89])) / Decimal("600000")


def decodePosition_latitude(bv, validate=False):
    return Decimal(binary.signedIntFromBV(bv[89:116])) / Decimal("600000")


def decodeCOG(bv, validate=False):
    return Decimal(int(bv[116:128])) / Decimal("10")


def decodeTimeStamp(bv, validate=False):
    return int(bv[128:134])


def decodeReserved(bv, validate=False):
    return 0


def decodeDTE(bv, validate=False):
    return bool(int(bv[142:143]))


def decodeSpare(bv, validate=False):
    return 0


def decodeassigned_mode(bv, validate=False):
    return int(bv[146:147])


def decodeRAIM(bv, validate=False):
    return bool(int(bv[147:148]))


def decodecomm_state(bv, validate=False):
    return int(bv[148:149])


def decodestate_syncstate(bv, validate=False):
    return int(bv[149:151])


def decodestate_slottimeout(bv, validate=False):
    return int(bv[151:154])


def decodestate_slotoffset(bv, validate=False):
    return int(bv[154:168])


def printHtml(params, out=sys.stdout):
    out.write("<h3>SARposition</h3>\n")
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
    out.write("<td>Altitude</td>\n")
    out.write("<td>uint</td>\n")
    if "Altitude" in params:
        out.write("    <td>" + str(params["Altitude"]) + "</td>\n")
        if str(params["Altitude"]) in AltitudeDecodeLut:
            out.write("<td>" + AltitudeDecodeLut[str(params["Altitude"])] + "</td>")
        else:
            out.write("<td><i>Missing LUT entry</i></td>")
    out.write("<td>meters</td>\n")
    out.write("</tr>\n")
    out.write("\n")
    out.write("<tr>\n")
    out.write("<td>SOG</td>\n")
    out.write("<td>uint</td>\n")
    if "SOG" in params:
        out.write("    <td>" + str(params["SOG"]) + "</td>\n")
        if str(params["SOG"]) in SOGDecodeLut:
            out.write("<td>" + SOGDecodeLut[str(params["SOG"])] + "</td>")
        else:
            out.write("<td><i>Missing LUT entry</i></td>")
    out.write("<td>knots</td>\n")
    out.write("</tr>\n")
    out.write("\n")
    out.write("<tr>\n")
    out.write("<td>PositionAccuracy</td>\n")
    out.write("<td>uint</td>\n")
    if "PositionAccuracy" in params:
        out.write("    <td>" + str(params["PositionAccuracy"]) + "</td>\n")
        if str(params["PositionAccuracy"]) in PositionAccuracyDecodeLut:
            out.write(
                "<td>"
                + PositionAccuracyDecodeLut[str(params["PositionAccuracy"])]
                + "</td>"
            )
        else:
            out.write("<td><i>Missing LUT entry</i></td>")
    out.write("</tr>\n")
    out.write("\n")
    out.write("<tr>\n")
    out.write("<td>Position_longitude</td>\n")
    out.write("<td>decimal</td>\n")
    if "Position_longitude" in params:
        out.write("    <td>" + str(params["Position_longitude"]) + "</td>\n")
        out.write("    <td>" + str(params["Position_longitude"]) + "</td>\n")
    out.write("<td>degrees</td>\n")
    out.write("</tr>\n")
    out.write("\n")
    out.write("<tr>\n")
    out.write("<td>Position_latitude</td>\n")
    out.write("<td>decimal</td>\n")
    if "Position_latitude" in params:
        out.write("    <td>" + str(params["Position_latitude"]) + "</td>\n")
        out.write("    <td>" + str(params["Position_latitude"]) + "</td>\n")
    out.write("<td>degrees</td>\n")
    out.write("</tr>\n")
    out.write("\n")
    out.write("<tr>\n")
    out.write("<td>COG</td>\n")
    out.write("<td>udecimal</td>\n")
    if "COG" in params:
        out.write("    <td>" + str(params["COG"]) + "</td>\n")
        out.write("    <td>" + str(params["COG"]) + "</td>\n")
    out.write("<td>degrees</td>\n")
    out.write("</tr>\n")
    out.write("\n")
    out.write("<tr>\n")
    out.write("<td>TimeStamp</td>\n")
    out.write("<td>uint</td>\n")
    if "TimeStamp" in params:
        out.write("    <td>" + str(params["TimeStamp"]) + "</td>\n")
        if str(params["TimeStamp"]) in TimeStampDecodeLut:
            out.write("<td>" + TimeStampDecodeLut[str(params["TimeStamp"])] + "</td>")
        else:
            out.write("<td><i>Missing LUT entry</i></td>")
    out.write("<td>seconds</td>\n")
    out.write("</tr>\n")
    out.write("\n")
    out.write("<tr>\n")
    out.write("<td>Reserved</td>\n")
    out.write("<td>uint</td>\n")
    if "Reserved" in params:
        out.write("    <td>" + str(params["Reserved"]) + "</td>\n")
        out.write("    <td>" + str(params["Reserved"]) + "</td>\n")
    out.write("</tr>\n")
    out.write("\n")
    out.write("<tr>\n")
    out.write("<td>DTE</td>\n")
    out.write("<td>bool</td>\n")
    if "DTE" in params:
        out.write("    <td>" + str(params["DTE"]) + "</td>\n")
        out.write("    <td>" + str(params["DTE"]) + "</td>\n")
    out.write("</tr>\n")
    out.write("\n")
    out.write("<tr>\n")
    out.write("<td>Spare</td>\n")
    out.write("<td>uint</td>\n")
    if "Spare" in params:
        out.write("    <td>" + str(params["Spare"]) + "</td>\n")
        out.write("    <td>" + str(params["Spare"]) + "</td>\n")
    out.write("</tr>\n")
    out.write("\n")
    out.write("<tr>\n")
    out.write("<td>assigned_mode</td>\n")
    out.write("<td>uint</td>\n")
    if "assigned_mode" in params:
        out.write("    <td>" + str(params["assigned_mode"]) + "</td>\n")
        if str(params["assigned_mode"]) in assigned_modeDecodeLut:
            out.write(
                "<td>" + assigned_modeDecodeLut[str(params["assigned_mode"])] + "</td>"
            )
        else:
            out.write("<td><i>Missing LUT entry</i></td>")
    out.write("</tr>\n")
    out.write("\n")
    out.write("<tr>\n")
    out.write("<td>RAIM</td>\n")
    out.write("<td>bool</td>\n")
    if "RAIM" in params:
        out.write("    <td>" + str(params["RAIM"]) + "</td>\n")
        if str(params["RAIM"]) in RAIMDecodeLut:
            out.write("<td>" + RAIMDecodeLut[str(params["RAIM"])] + "</td>")
        else:
            out.write("<td><i>Missing LUT entry</i></td>")
    out.write("</tr>\n")
    out.write("\n")
    out.write("<tr>\n")
    out.write("<td>comm_state</td>\n")
    out.write("<td>uint</td>\n")
    if "comm_state" in params:
        out.write("    <td>" + str(params["comm_state"]) + "</td>\n")
        if str(params["comm_state"]) in comm_stateDecodeLut:
            out.write("<td>" + comm_stateDecodeLut[str(params["comm_state"])] + "</td>")
        else:
            out.write("<td><i>Missing LUT entry</i></td>")
    out.write("</tr>\n")
    out.write("\n")
    out.write("<tr>\n")
    out.write("<td>state_syncstate</td>\n")
    out.write("<td>uint</td>\n")
    if "state_syncstate" in params:
        out.write("    <td>" + str(params["state_syncstate"]) + "</td>\n")
        if str(params["state_syncstate"]) in state_syncstateDecodeLut:
            out.write(
                "<td>"
                + state_syncstateDecodeLut[str(params["state_syncstate"])]
                + "</td>"
            )
        else:
            out.write("<td><i>Missing LUT entry</i></td>")
    out.write("</tr>\n")
    out.write("\n")
    out.write("<tr>\n")
    out.write("<td>state_slottimeout</td>\n")
    out.write("<td>uint</td>\n")
    if "state_slottimeout" in params:
        out.write("    <td>" + str(params["state_slottimeout"]) + "</td>\n")
        if str(params["state_slottimeout"]) in state_slottimeoutDecodeLut:
            out.write(
                "<td>"
                + state_slottimeoutDecodeLut[str(params["state_slottimeout"])]
                + "</td>"
            )
        else:
            out.write("<td><i>Missing LUT entry</i></td>")
    out.write("<td>frames</td>\n")
    out.write("</tr>\n")
    out.write("\n")
    out.write("<tr>\n")
    out.write("<td>state_slotoffset</td>\n")
    out.write("<td>uint</td>\n")
    if "state_slotoffset" in params:
        out.write("    <td>" + str(params["state_slotoffset"]) + "</td>\n")
        out.write("    <td>" + str(params["state_slotoffset"]) + "</td>\n")
    out.write("</tr>\n")
    out.write("</table>\n")


def printKml(params, out=sys.stdout):
    """KML (Keyhole Markup Language) for Google Earth, but without the header/footer"""
    out.write("    <Placemark>\n")
    out.write("        <name>" + str(params["UserID"]) + "</name>\n")
    out.write("        <description>\n")
    import io

    buf = io.StringIO()
    printHtml(params, buf)
    import cgi

    out.write(cgi.escape(buf.getvalue()))
    out.write("        </description>\n")
    out.write("        <styleUrl>#m_ylw-pushpin_copy0</styleUrl>\n")
    out.write("        <Point>\n")
    out.write("            <coordinates>")
    out.write(str(params["Position_longitude"]))
    out.write(",")
    out.write(str(params["Position_latitude"]))
    out.write(",0</coordinates>\n")
    out.write("        </Point>\n")
    out.write("    </Placemark>\n")


def printFields(
    params, out=sys.stdout, format="std", fieldList=None, dbType="postgres"
):
    """Print a SARposition message to stdout.

    Fields in params:
      - MessageID(uint): AIS message number.  Must be 9 (field automatically set to "9")
      - RepeatIndicator(uint): Indicated how many times a message has been repeated
      - UserID(uint): Unique ship identification number (MMSI)
      - Altitude(uint): Altitude (GNSS)
      - SOG(uint): Speed over ground
      - PositionAccuracy(uint): Accuracy of positioning fixes
      - Position_longitude(decimal): Location of the vessel  East West location
      - Position_latitude(decimal): Location of the vessel  North South location
      - COG(udecimal): Course over ground
      - TimeStamp(uint): UTC second when the report was generated
      - Reserved(uint): Reserved for regional applications.  Should be set to zero. (field automatically set to "0")
      - DTE(bool): Dtta terminal ready
      - Spare(uint): Not used.  Should be set to zero. (field automatically set to "0")
      - assigned_mode(uint): autonomous or assigned mode
      - RAIM(bool): Receiver autonomous integrity monitoring flag
      - comm_state(uint): SOTDMA or ITDMA
      - state_syncstate(uint): Communications State - SOTDMA  Synchronization state
      - state_slottimeout(uint): Communications State - SOTDMA  Frames remaining until a new slot is selected
      - state_slotoffset(uint): Communications State - SOTDMA  In what slot will the next transmission occur. BROKEN
    Args:
        params: Dictionary of field names/values.
        out: File like object to write to.
    Returns:
        stdout
        text to out
    """

    if format == "std":
        out.write("SARposition:\n")
        if "MessageID" in params:
            out.write("    MessageID:           " + str(params["MessageID"]) + "\n")
        if "RepeatIndicator" in params:
            out.write(
                "    RepeatIndicator:     " + str(params["RepeatIndicator"]) + "\n"
            )
        if "UserID" in params:
            out.write("    UserID:              " + str(params["UserID"]) + "\n")
        if "Altitude" in params:
            out.write("    Altitude:            " + str(params["Altitude"]) + "\n")
        if "SOG" in params:
            out.write("    SOG:                 " + str(params["SOG"]) + "\n")
        if "PositionAccuracy" in params:
            out.write(
                "    PositionAccuracy:    " + str(params["PositionAccuracy"]) + "\n"
            )
        if "Position_longitude" in params:
            out.write(
                "    Position_longitude:  " + str(params["Position_longitude"]) + "\n"
            )
        if "Position_latitude" in params:
            out.write(
                "    Position_latitude:   " + str(params["Position_latitude"]) + "\n"
            )
        if "COG" in params:
            out.write("    COG:                 " + str(params["COG"]) + "\n")
        if "TimeStamp" in params:
            out.write("    TimeStamp:           " + str(params["TimeStamp"]) + "\n")
        if "Reserved" in params:
            out.write("    Reserved:            " + str(params["Reserved"]) + "\n")
        if "DTE" in params:
            out.write("    DTE:                 " + str(params["DTE"]) + "\n")
        if "Spare" in params:
            out.write("    Spare:               " + str(params["Spare"]) + "\n")
        if "assigned_mode" in params:
            out.write("    assigned_mode:       " + str(params["assigned_mode"]) + "\n")
        if "RAIM" in params:
            out.write("    RAIM:                " + str(params["RAIM"]) + "\n")
        if "comm_state" in params:
            out.write("    comm_state:          " + str(params["comm_state"]) + "\n")
        if "state_syncstate" in params:
            out.write(
                "    state_syncstate:     " + str(params["state_syncstate"]) + "\n"
            )
        if "state_slottimeout" in params:
            out.write(
                "    state_slottimeout:   " + str(params["state_slottimeout"]) + "\n"
            )
        if "state_slotoffset" in params:
            out.write(
                "    state_slotoffset:    " + str(params["state_slotoffset"]) + "\n"
            )
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
    elif format == "kml":
        printKml(params, out)
    elif format == "kml-full":
        out.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        out.write('<kml xmlns="http://earth.google.com/kml/2.1">\n')
        out.write("<Document>\n")
        out.write("    <name>SARposition</name>\n")
        printKml(params, out)
        out.write("</Document>\n")
        out.write("</kml>\n")
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

AltitudeEncodeLut = {
    "4095 or higher": "4095",
}  # AltitudeEncodeLut

AltitudeDecodeLut = {
    "4095": "4095 or higher",
}  # AltitudeEncodeLut

SOGEncodeLut = {
    "1022 knots or higher": "1022",
}  # SOGEncodeLut

SOGDecodeLut = {
    "1022": "1022 knots or higher",
}  # SOGEncodeLut

PositionAccuracyEncodeLut = {
    "low (greater than 10 m)": "0",
    "high (less than 10 m)": "1",
}  # PositionAccuracyEncodeLut

PositionAccuracyDecodeLut = {
    "0": "low (greater than 10 m)",
    "1": "high (less than 10 m)",
}  # PositionAccuracyEncodeLut

TimeStampEncodeLut = {
    "not available/default": "60",
    "manual input": "61",
    "dead reckoning": "62",
    "inoperative": "63",
}  # TimeStampEncodeLut

TimeStampDecodeLut = {
    "60": "not available/default",
    "61": "manual input",
    "62": "dead reckoning",
    "63": "inoperative",
}  # TimeStampEncodeLut

assigned_modeEncodeLut = {
    "autonomous and continuous mode": "0",
    "assigned mode": "1",
}  # assigned_modeEncodeLut

assigned_modeDecodeLut = {
    "0": "autonomous and continuous mode",
    "1": "assigned mode",
}  # assigned_modeEncodeLut

RAIMEncodeLut = {
    "not in use": "False",
    "in use": "True",
}  # RAIMEncodeLut

RAIMDecodeLut = {
    "False": "not in use",
    "True": "in use",
}  # RAIMEncodeLut

comm_stateEncodeLut = {
    "SOTDMA": "0",
    "ITDMA": "1",
}  # comm_stateEncodeLut

comm_stateDecodeLut = {
    "0": "SOTDMA",
    "1": "ITDMA",
}  # comm_stateEncodeLut

state_syncstateEncodeLut = {
    "UTC direct": "0",
    "UTC indirect": "1",
    "synchronized to a base station": "2",
    "synchronized to another station": "3",
}  # state_syncstateEncodeLut

state_syncstateDecodeLut = {
    "0": "UTC direct",
    "1": "UTC indirect",
    "2": "synchronized to a base station",
    "3": "synchronized to another station",
}  # state_syncstateEncodeLut

state_slottimeoutEncodeLut = {
    "Last frame in this slot": "0",
    "1 frames left": "1",
    "2 frames left": "2",
    "3 frames left": "3",
    "4 frames left": "4",
    "5 frames left": "5",
    "6 frames left": "6",
    "7 frames left": "7",
}  # state_slottimeoutEncodeLut

state_slottimeoutDecodeLut = {
    "0": "Last frame in this slot",
    "1": "1 frames left",
    "2": "2 frames left",
    "3": "3 frames left",
    "4": "4 frames left",
    "5": "5 frames left",
    "6": "6 frames left",
    "7": "7 frames left",
}  # state_slottimeoutEncodeLut

######################################################################
# SQL SUPPORT
######################################################################

dbTableName = "SARposition"
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
    c = sqlhelp.create("SARposition", dbType=dbType)
    c.addPrimaryKey()
    if "MessageID" in fields:
        c.addInt("MessageID")
    if "RepeatIndicator" in fields:
        c.addInt("RepeatIndicator")
    if "UserID" in fields:
        c.addInt("UserID")
    if "Altitude" in fields:
        c.addInt("Altitude")
    if "SOG" in fields:
        c.addInt("SOG")
    if "PositionAccuracy" in fields:
        c.addInt("PositionAccuracy")
    if dbType != "postgres" and "Position_longitude" in fields:
        c.addDecimal("Position_longitude", 8, 5)
    if dbType != "postgres" and "Position_latitude" in fields:
        c.addDecimal("Position_latitude", 8, 5)
    if "COG" in fields:
        c.addDecimal("COG", 4, 1)
    if "TimeStamp" in fields:
        c.addInt("TimeStamp")
    if "Reserved" in fields:
        c.addInt("Reserved")
    if "DTE" in fields:
        c.addBool("DTE")
    if "Spare" in fields:
        c.addInt("Spare")
    if "assigned_mode" in fields:
        c.addInt("assigned_mode")
    if "RAIM" in fields:
        c.addBool("RAIM")
    if "comm_state" in fields:
        c.addInt("comm_state")
    if "state_syncstate" in fields:
        c.addInt("state_syncstate")
    if "state_slottimeout" in fields:
        c.addInt("state_slottimeout")
    if "state_slotoffset" in fields:
        c.addInt("state_slotoffset")

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

    if dbType == "postgres":
        # --- EPSG 4326 : WGS 84
        # INSERT INTO "spatial_ref_sys" ("srid","auth_name","auth_srid","srtext","proj4text") VALUES (4326,'EPSG',4326,'GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],TOWGS84[0,0,0,0,0,0,0],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.01745329251994328,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4326"]]','+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs ');
        c.addPostGIS("Position", "POINT", 2, SRID=4326)

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

    i = sqlhelp.insert("SARposition", dbType=dbType)

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
MessageID & 6 & AIS message number.  Must be 9 \\\\ \\hline
RepeatIndicator & 2 & Indicated how many times a message has been repeated \\\\ \\hline
UserID & 30 & Unique ship identification number (MMSI) \\\\ \\hline
Altitude & 12 & Altitude (GNSS) \\\\ \\hline
SOG & 10 & Speed over ground \\\\ \\hline
PositionAccuracy & 1 & Accuracy of positioning fixes \\\\ \\hline
Position\\_longitude & 28 & Location of the vessel  East West location \\\\ \\hline
Position\\_latitude & 27 & Location of the vessel  North South location \\\\ \\hline
COG & 12 & Course over ground \\\\ \\hline
TimeStamp & 6 & UTC second when the report was generated \\\\ \\hline
Reserved & 8 & Reserved for regional applications.  Should be set to zero. \\\\ \\hline
DTE & 1 & Dtta terminal ready \\\\ \\hline
Spare & 3 & Not used.  Should be set to zero. \\\\ \\hline
assigned\\_mode & 1 & autonomous or assigned mode \\\\ \\hline
RAIM & 1 & Receiver autonomous integrity monitoring flag \\\\ \\hline
comm\\_state & 1 & SOTDMA or ITDMA \\\\ \\hline
state\\_syncstate & 2 & Communications State - SOTDMA  Synchronization state \\\\ \\hline
state\\_slottimeout & 3 & Communications State - SOTDMA  Frames remaining until a new slot is selected \\\\ \\hline
state\\_slotoffset & 14 & Communications State - SOTDMA  In what slot will the next transmission occur. BROKEN\\\\ \\hline \\hline
Total bits & 168 & Appears to take 1 slot \\\\ \\hline
\\end{tabular}
\\caption{AIS message number 9: Search and rescue position report.  Changed in 1371-4}
\\label{tab:SARposition}
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
        + """AIS message number.  Must be 9
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
Altitude"""
        + delim
        + "12"
        + delim
        + """Altitude (GNSS)
SOG"""
        + delim
        + "10"
        + delim
        + """Speed over ground
PositionAccuracy"""
        + delim
        + "1"
        + delim
        + """Accuracy of positioning fixes
Position_longitude"""
        + delim
        + "28"
        + delim
        + """Location of the vessel  East West location
Position_latitude"""
        + delim
        + "27"
        + delim
        + """Location of the vessel  North South location
COG"""
        + delim
        + "12"
        + delim
        + """Course over ground
TimeStamp"""
        + delim
        + "6"
        + delim
        + """UTC second when the report was generated
Reserved"""
        + delim
        + "8"
        + delim
        + """Reserved for regional applications.  Should be set to zero.
DTE"""
        + delim
        + "1"
        + delim
        + """Dtta terminal ready
Spare"""
        + delim
        + "3"
        + delim
        + """Not used.  Should be set to zero.
assigned_mode"""
        + delim
        + "1"
        + delim
        + """autonomous or assigned mode
RAIM"""
        + delim
        + "1"
        + delim
        + """Receiver autonomous integrity monitoring flag
comm_state"""
        + delim
        + "1"
        + delim
        + """SOTDMA or ITDMA
state_syncstate"""
        + delim
        + "2"
        + delim
        + """Communications State - SOTDMA  Synchronization state
state_slottimeout"""
        + delim
        + "3"
        + delim
        + """Communications State - SOTDMA  Frames remaining until a new slot is selected
state_slotoffset"""
        + delim
        + "14"
        + delim
        + """Communications State - SOTDMA  In what slot will the next transmission occur. BROKEN
Total bits"""
        + delim
        + """168"""
        + delim
        + """Appears to take 1 slot"""
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
    params["MessageID"] = 9
    params["RepeatIndicator"] = 1
    params["UserID"] = 1193046
    params["Altitude"] = 1001
    params["SOG"] = 342
    params["PositionAccuracy"] = 1
    params["Position_longitude"] = Decimal("-122.16328055555556")
    params["Position_latitude"] = Decimal("37.424458333333334")
    params["COG"] = Decimal("34.5")
    params["TimeStamp"] = 35
    params["Reserved"] = 0
    params["DTE"] = False
    params["Spare"] = 0
    params["assigned_mode"] = 1
    params["RAIM"] = False
    params["comm_state"] = 1
    params["state_syncstate"] = 2
    params["state_slottimeout"] = 0
    params["state_slotoffset"] = 1221

    return params


class TestSARposition(unittest.TestCase):
    """Use testvalue tag text from each type to build test case the SARposition message"""

    def testEncodeDecode(self):
        params = testParams()
        bits = encode(params)
        r = decode(bits)

        # Check that each parameter came through ok.
        assert r["MessageID"] == params["MessageID"]
        assert r["RepeatIndicator"] == params["RepeatIndicator"]
        assert r["UserID"] == params["UserID"]
        assert r["Altitude"] == params["Altitude"]
        assert r["SOG"] == params["SOG"]
        assert r["PositionAccuracy"] == params["PositionAccuracy"]
        self.assertAlmostEqual(r["Position_longitude"], params["Position_longitude"], 5)
        self.assertAlmostEqual(r["Position_latitude"], params["Position_latitude"], 5)
        self.assertAlmostEqual(r["COG"], params["COG"], 1)
        assert r["TimeStamp"] == params["TimeStamp"]
        assert r["Reserved"] == params["Reserved"]
        assert r["DTE"] == params["DTE"]
        assert r["Spare"] == params["Spare"]
        assert r["assigned_mode"] == params["assigned_mode"]
        assert r["RAIM"] == params["RAIM"]
        assert r["comm_state"] == params["comm_state"]
        assert r["state_syncstate"] == params["state_syncstate"]
        assert r["state_slottimeout"] == params["state_slottimeout"]
        assert r["state_slotoffset"] == params["state_slotoffset"]


def addMsgOptions(parser):
    parser.add_option(
        "-d",
        "--decode",
        dest="doDecode",
        default=False,
        action="store_true",
        help='decode a "SARposition" AIS message',
    )
    parser.add_option(
        "-e",
        "--encode",
        dest="doEncode",
        default=False,
        action="store_true",
        help='encode a "SARposition" AIS message',
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
        "--Altitude-field",
        dest="AltitudeField",
        default=4095,
        metavar="uint",
        type="int",
        help="Field parameter value [default: %default]",
    )
    parser.add_option(
        "--SOG-field",
        dest="SOGField",
        default=1023,
        metavar="uint",
        type="int",
        help="Field parameter value [default: %default]",
    )
    parser.add_option(
        "--PositionAccuracy-field",
        dest="PositionAccuracyField",
        metavar="uint",
        type="int",
        help="Field parameter value [default: %default]",
    )
    parser.add_option(
        "--Position_longitude-field",
        dest="Position_longitudeField",
        default=Decimal("181"),
        metavar="decimal",
        type="string",
        help="Field parameter value [default: %default]",
    )
    parser.add_option(
        "--Position_latitude-field",
        dest="Position_latitudeField",
        default=Decimal("91"),
        metavar="decimal",
        type="string",
        help="Field parameter value [default: %default]",
    )
    parser.add_option(
        "--COG-field",
        dest="COGField",
        default=Decimal("360"),
        metavar="udecimal",
        type="string",
        help="Field parameter value [default: %default]",
    )
    parser.add_option(
        "--TimeStamp-field",
        dest="TimeStampField",
        default=60,
        metavar="uint",
        type="int",
        help="Field parameter value [default: %default]",
    )
    parser.add_option(
        "--DTE-field",
        dest="DTEField",
        metavar="bool",
        type="int",
        help="Field parameter value [default: %default]",
    )
    parser.add_option(
        "--assigned_mode-field",
        dest="assigned_modeField",
        metavar="uint",
        type="int",
        help="Field parameter value [default: %default]",
    )
    parser.add_option(
        "--RAIM-field",
        dest="RAIMField",
        metavar="bool",
        type="int",
        help="Field parameter value [default: %default]",
    )
    parser.add_option(
        "--comm_state-field",
        dest="comm_stateField",
        metavar="uint",
        type="int",
        help="Field parameter value [default: %default]",
    )
    parser.add_option(
        "--state_syncstate-field",
        dest="state_syncstateField",
        metavar="uint",
        type="int",
        help="Field parameter value [default: %default]",
    )
    parser.add_option(
        "--state_slottimeout-field",
        dest="state_slottimeoutField",
        metavar="uint",
        type="int",
        help="Field parameter value [default: %default]",
    )
    parser.add_option(
        "--state_slotoffset-field",
        dest="state_slotoffsetField",
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

    outputChoices = ("std", "html", "csv", "sql", "kml", "kml-full")
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
        if options.AltitudeField is None:
            parser.error("missing value for AltitudeField")
        if options.SOGField is None:
            parser.error("missing value for SOGField")
        if options.PositionAccuracyField is None:
            parser.error("missing value for PositionAccuracyField")
        if options.Position_longitudeField is None:
            parser.error("missing value for Position_longitudeField")
        if options.Position_latitudeField is None:
            parser.error("missing value for Position_latitudeField")
        if options.COGField is None:
            parser.error("missing value for COGField")
        if options.TimeStampField is None:
            parser.error("missing value for TimeStampField")
        if options.DTEField is None:
            parser.error("missing value for DTEField")
        if options.assigned_modeField is None:
            parser.error("missing value for assigned_modeField")
        if options.RAIMField is None:
            parser.error("missing value for RAIMField")
        if options.comm_stateField is None:
            parser.error("missing value for comm_stateField")
        if options.state_syncstateField is None:
            parser.error("missing value for state_syncstateField")
        if options.state_slottimeoutField is None:
            parser.error("missing value for state_slottimeoutField")
        if options.state_slotoffsetField is None:
            parser.error("missing value for state_slotoffsetField")
    msgDict = {
        "MessageID": "9",
        "RepeatIndicator": options.RepeatIndicatorField,
        "UserID": options.UserIDField,
        "Altitude": options.AltitudeField,
        "SOG": options.SOGField,
        "PositionAccuracy": options.PositionAccuracyField,
        "Position_longitude": options.Position_longitudeField,
        "Position_latitude": options.Position_latitudeField,
        "COG": options.COGField,
        "TimeStamp": options.TimeStampField,
        "Reserved": "0",
        "DTE": options.DTEField,
        "Spare": "0",
        "assigned_mode": options.assigned_modeField,
        "RAIM": options.RAIMField,
        "comm_state": options.comm_stateField,
        "state_syncstate": options.state_syncstateField,
        "state_slottimeout": options.state_slottimeoutField,
        "state_slotoffset": options.state_slotoffsetField,
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
                        bv = BitVector.from_bitstring(msg)
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
