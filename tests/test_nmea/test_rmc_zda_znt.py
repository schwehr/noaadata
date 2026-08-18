"""Unit tests for NMEA RMC, ZDA, and ZNT sentence parsers."""

import pytest

from nmea import rmc, zda, znt
from nmea.nmea_error import NmeaChecksumError


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


def test_zda_decode_and_epoch() -> None:
    sentence = "$ZQZDA,110003.00,27,03,2006,-5,00*47"
    decoded = zda.zdaDecode(sentence)
    assert decoded["year"] == 2006
    assert decoded["mon"] == 3
    assert decoded["day"] == 27

    epoch_sec = zda.zdaEpochSeconds(sentence)
    assert epoch_sec > 0


def test_znt_decode_valid() -> None:
    sentence = "$PNTZNT,1270567048.57,127.0.0.1,17.151.16.21,4,1270565749.41,0.000080,-20,0.117325,0.046249*14"
    # Using znt.Znt.__new__ to avoid side effects of __init__ which connects to NTP if nmea_str is None
    znt_obj = znt.Znt.__new__(znt.Znt)
    match = znt_obj.decode_znt(sentence)
    assert match["stratum"] == 4
    assert match["talker"] == "NT"
    assert match["timestamp"] == 1270567048.57
    assert match["host"] == "127.0.0.1"
    assert match["ref_clock"] == "17.151.16.21"
    assert match["last_update"] == 1270565749.41
    assert match["offset"] == 0.000080
    assert match["precision"] == -20.0
    assert match["root_delay"] == 0.117325
    assert match["root_dispersion"] == 0.046249

    # Test Znt properties via instantiation
    znt_obj_init = znt.Znt(sentence)
    assert znt_obj_init.params["stratum"] == 4
    assert znt_obj_init.params["talker"] == "NT"


def test_znt_decode_invalid_regex() -> None:
    sentence = "$PNTZNT,invalid,sentence*00"
    znt_obj = znt.Znt.__new__(znt.Znt)
    with pytest.raises(znt.NmeaNotZnt):
        znt_obj.decode_znt(sentence)


def test_znt_decode_invalid_checksum() -> None:
    # Sentence with an intentionally wrong checksum (expected is 14)
    sentence = "$PNTZNT,1270567048.57,127.0.0.1,17.151.16.21,4,1270565749.41,0.000080,-20,0.117325,0.046249*15"
    znt_obj = znt.Znt.__new__(znt.Znt)
    with pytest.raises(NmeaChecksumError) as exc_info:
        znt_obj.decode_znt(sentence)
    assert "checksums mismatch" in str(exc_info.value)
