"""Unit tests for NMEA RMC, ZDA, and ZNT sentence parsers."""

from nmea import rmc, zda, znt


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


def test_zda_decode_and_epoch() -> None:
    sentence = "$ZQZDA,110003.00,27,03,2006,-5,00*47"
    decoded = zda.zdaDecode(sentence)
    assert decoded["year"] == 2006
    assert decoded["mon"] == 3
    assert decoded["day"] == 27

    epoch_sec = zda.zdaEpochSeconds(sentence)
    assert epoch_sec > 0


def test_znt_decode() -> None:
    sentence = "$PNTZNT,1270567048.57,127.0.0.1,17.151.16.21,4,1270565749.41,0.000080,-20,0.117325,0.046249*14"
    znt_obj = znt.Znt(sentence)
    assert znt_obj.params["stratum"] == 4
    assert znt_obj.params["talker"] == "NT"
