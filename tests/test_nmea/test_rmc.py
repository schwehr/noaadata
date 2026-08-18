"""Unit tests for NMEA RMC sentence parser."""

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


def test_rmc_south_east() -> None:
    # Sentence with South and East (adding .00 for seconds to match \d\d\.\d\d regex)
    sentence = "$GPRMC,123519.00,A,4807.038,S,01131.000,E,022.4,084.4,230394,003.1,W*6A"
    match = rmc.compile_obj.search(sentence)
    assert match is not None

    lon, lat = rmc.lonlat(match)
    assert abs(lon - (11 + 31.0 / 60)) < 1e-4
    assert abs(lat - -(48 + 7.038 / 60)) < 1e-4


def test_rmc_zero_values() -> None:
    # Sentence with zero degrees and minutes
    sentence = "$GPRMC,123519.00,A,0000.000,N,00000.000,E,022.4,084.4,230394,003.1,W*6A"
    match = rmc.compile_obj.search(sentence)
    assert match is not None

    lon, lat = rmc.lonlat(match)
    assert lon == 0.0
    assert lat == 0.0


def test_rmc_zero_degrees() -> None:
    # Sentence with zero degrees but non-zero minutes
    sentence = "$GPRMC,123519.00,A,0010.500,N,00015.000,E,022.4,084.4,230394,003.1,W*6A"
    match = rmc.compile_obj.search(sentence)
    assert match is not None

    lon, lat = rmc.lonlat(match)
    assert abs(lon - (0 + 15.0 / 60.0)) < 1e-4
    assert abs(lat - (0 + 10.5 / 60.0)) < 1e-4


def test_rmc_zero_minutes() -> None:
    # Sentence with zero minutes but non-zero degrees
    sentence = "$GPRMC,123519.00,A,4500.000,N,12000.000,E,022.4,084.4,230394,003.1,W*6A"
    match = rmc.compile_obj.search(sentence)
    assert match is not None

    lon, lat = rmc.lonlat(match)
    assert abs(lon - 120.0) < 1e-4
    assert abs(lat - 45.0) < 1e-4


def test_rmc_no_match() -> None:
    # Invalid sentence format
    sentence = "$GPFOO,123519.00,A,4807.038,S,01131.000,E,022.4,084.4,230394,003.1,W*6A"
    match = rmc.compile_obj.search(sentence)
    assert match is None
