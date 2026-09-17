"""Unit tests for NMEA RMC sentence parsers."""

import pytest

from nmea import rmc


def test_rmc_match_and_lonlat() -> None:
    sentence = "$GPRMC,173011.82,V,4222.8770,N,07103.0096,W,0.00,0.0,151008,14.9,W,N*27"
    match = rmc.compile_obj.search(sentence)
    assert match is not None
    assert match.group("msg_type") == "RMC"
    assert match.group("hour") == "17"
    assert match.group("minute") == "30"

    lon, lat = rmc.lonlat(match)
    assert abs(lon - (-71.05016)) < 1e-4
    assert abs(lat - 42.3812833) < 1e-4


def test_rmc_lonlat_south_east() -> None:
    sentence = (
        "$GPRMC,123519.00,A,4807.0380,S,01131.0000,E,022.4,084.4,230394,003.1,W*6A"
    )
    match = rmc.compile_obj.search(sentence)
    assert match is not None

    lon, lat = rmc.lonlat(match)
    assert abs(lon - 11.516666) < 1e-4
    assert abs(lat - (-48.1173)) < 1e-4


def test_rmc_lonlat_zero() -> None:
    sentence = (
        "$GPRMC,123519.00,A,0000.0000,N,00000.0000,E,022.4,084.4,230394,003.1,W*6A"
    )
    match = rmc.compile_obj.search(sentence)
    assert match is not None

    lon, lat = rmc.lonlat(match)
    assert lon == 0.0
    assert lat == 0.0


def test_rmc_match_all_groups() -> None:
    sentence = "$GPRMC,123519.00,A,4807.038,N,01131.000,E,022.4,084.4,230394,003.1,W*6A"
    match = rmc.compile_obj.search(sentence)
    assert match is not None
    assert match.group("prefix") == "GP"
    assert match.group("msg_type") == "RMC"
    assert match.group("hour") == "12"
    assert match.group("minute") == "35"
    assert match.group("second") == "19.00"
    assert match.group("status") == "A"
    assert match.group("latitude") == "4807.038"
    assert match.group("lat_deg") == "48"
    assert match.group("lat_min") == "07.038"
    assert match.group("north_south") == "N"
    assert match.group("longitude") == "01131.000"
    assert match.group("lon_deg") == "011"
    assert match.group("lon_min") == "31.000"
    assert match.group("east_west") == "E"
    assert match.group("speed_knots") == "022.4"
    assert match.group("course_degrees") == "084.4"
    assert match.group("day") == "23"
    assert match.group("month") == "03"
    assert match.group("year") == "94"
    assert match.group("magnetic_variation_degrees") == "003.1"
    assert match.group("mag_var_east_west") == "W"
    assert match.group("checksum") == "*6A"


def test_rmc_lonlat_zero_padding_edge_case() -> None:
    # A constructed match where lon/lat have leading zeroes that will be stripped to empty strings
    # Simulate the empty string condition in lonlat logic:
    # lon_deg = 0 if len(lon_deg) == 0 else int(lon_deg)
    sentence = "$GPRMC,123519.00,A,0000.000,N,00000.000,E,022.4,084.4,230394,003.1,W*6A"
    match = rmc.compile_obj.search(sentence)
    assert match is not None
    lon, lat = rmc.lonlat(match)
    assert lon == 0.0
    assert lat == 0.0

    # Ensure it works when strings are all zeros
    assert match.group("lon_deg").lstrip("0") == ""
    assert match.group("lat_deg").lstrip("0") == ""
