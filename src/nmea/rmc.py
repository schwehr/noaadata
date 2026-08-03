#!/usr/bin/env python
__author__ = "Kurt Schwehr"
__version__ = ["$Revision:", "4799", "$"][1]
__revision__ = __version__  # For pylint
__date__ = [
    "$Date:",
    "2006-09-25",
    "11:09:02",
    "-0400",
    "(Mon,",
    "25",
    "Sep",
    "2006)",
    "$",
][1]
__copyright__ = "2008"
__license__ = "Apache 2.0"

"""RMC - GPS Position.

TODO(schwehr): What is 'N' for the mode?
  Sent by SR162G.   N must be for no lock.
"""

import re

rawstr = r"""^[$!](?P<prefix>[A-Z][A-Z])(?P<msg_type>RMC),
(?P<hour>\d\d)(?P<minute>\d\d)(?P<second>\d\d\.\d\d),
(?P<status>[A-Z]),
(?P<latitude>(?P<lat_deg>\d\d)(?P<lat_min>\d\d*.\d*)),
(?P<north_south>[NS]),
(?P<longitude>(?P<lon_deg>\d\d\d)(?P<lon_min>\d\d.\d*)),
(?P<east_west>[EW]),
(?P<speed_knots>\d*.\d*),
(?P<course_degrees>\d*.\d*),
(?P<day>\d\d)(?P<month>\d\d)(?P<year>\d\d),
(?P<magnetic_variation_degrees>\d*.\d*),
(?P<mag_var_east_west>[EW])
(,(?P<mode>[ADEN]))?
(?P<checksum>[*][0-9A-F][0-9A-F])"""
matchstr = "$GPRMC,173011.82,V,4222.8770,N,07103.0096,W,0.00,0.0,151008,14.9,W,N*27"

compile_obj = re.compile(rawstr, re.VERBOSE)
compile_obj = re.compile(rawstr, re.VERBOSE)


def lonlat(match):
    lon_deg = match.group("lon_deg").lstrip("0")
    lon_deg = 0 if len(lon_deg) == 0 else int(lon_deg)

    lon_min = match.group("lon_min").lstrip("0")
    lon_min = 0 if len(lon_min) == 0 else float(lon_min)

    lon = lon_deg + lon_min / 60.0

    if match.group("east_west") == "W":
        lon = -lon

    lat_deg = match.group("lat_deg").lstrip("0")
    lat_deg = 0 if len(lat_deg) == 0 else int(lat_deg)

    lat_min = match.group("lat_min").lstrip("0")
    lat_min = 0 if len(lat_min) == 0 else float(lat_min)

    lat = lat_deg + lat_min / 60.0

    if match.group("north_south") == "S":
        lat = -lat

    return lon, lat


if __name__ == "__main__":
    matchstr = "$GPRMC,173011.82,V,4222.8770,N,07103.0096,W,0.00,0.0,151008,14.9,W,N*27"
    match_obj = compile_obj.search(matchstr)
    print(lonlat(match_obj))
