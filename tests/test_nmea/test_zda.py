import calendar

import pytest

from nmea.zda import ggaDecode, zdaDecode, zdaDict2TIMESTAMP, zdaEpochSeconds


def test_zda_decode_valid():
    # Example from docstring
    sentence = "$ZQZDA,110003.00,27,03,2006,-5,00*47"
    result = zdaDecode(sentence)
    expected = {
        "timekeeper": "ZQ",
        "localzonehour": -5,
        "localzonemin": 0,
        "hour": 11,
        "min": 0,
        "hsec": 0,
        "sec": 3,
        "mon": 3,
        "year": 2006,
        "day": 27,
        "decimalsec": 3.0,
    }
    assert result == expected


def test_zda_decode_invalid_length():
    with pytest.raises(AssertionError):
        zdaDecode("$ZQZDA,110")


def test_zda_decode_invalid_start():
    with pytest.raises(AssertionError):
        zdaDecode("?ZQZDA,110003.00,27,03,2006,-5,00*47")


def test_zda_decode_invalid_type():
    with pytest.raises(AssertionError):
        zdaDecode("$ZQRMC,110003.00,27,03,2006,-5,00*47")


def test_zda_epoch_seconds():
    sentence = "$ZQZDA,110003.00,27,03,2006,-5,00*47"
    result = zdaEpochSeconds(sentence)
    # Expected: calendar.timegm((2006, 3, 27, 11, 0, 3.0)) -> 1143457203
    expected = calendar.timegm((2006, 3, 27, 11, 0, 3.0))
    assert result == expected


def test_gga_decode_valid():
    # Example from docstring
    sentence = "$GPGGA,152009.00,3652.48059177,N,07620.02018248,W,1,11,0.8,3.669,M,-34.579,M,,*57"
    result = ggaDecode(sentence)
    assert result["hour"] == "15"
    assert result["min"] == "20"
    assert result["sec"] == "09"
    assert result["hsec"] == "00"
    assert result["lat"] > 36.0
    assert result["lon"] < -76.0
    assert result["qual"] == 1
    assert result["sats"] == 11
    assert result["horz_dilution"] == 0.8
    assert result["alt"] == 3.669
    assert result["alt_units"] == "M"
    assert result["geoidal_sep"] == -34.579
    assert result["geoidal_sep_units"] == "M"
    assert result["age"] is None


def test_gga_decode_south_east():
    # Custom sentence to test S/E lat/lon and age
    sentence = "$GPGGA,152009.00,3652.48059177,S,07620.02018248,E,1,11,0.8,3.669,M,-34.579,M,1.5,*57"
    result = ggaDecode(sentence)
    assert result["lat"] < -36.0
    assert result["lon"] > 76.0
    assert result["age"] == 1.5


def test_gga_decode_validate_true():
    # Validate=True requires len >= 71 and <= 78
    sentence = (
        "$GPGGA,152009.00,3652.4800,N,07620.0200,W,1,11,0.8,3.669,M,-34.50,M,,*57"
    )
    assert 71 <= len(sentence) <= 78
    result = ggaDecode(sentence, validate=True)
    assert result["qual"] == 1


def test_gga_decode_validate_length_fail():
    sentence = "$GPGGA,152009.00,3652.48059177,N,07620.02018248,W,1,11,0.8,3.669,M,-34.579,M,,*57"
    with pytest.raises(AssertionError):
        ggaDecode(sentence, validate=True)


def test_zda_dict2timestamp():
    zda_dict = {
        "hour": 11,
        "min": 0,
        "hsec": 0,
        "sec": 3,
        "mon": 3,
        "year": 2006,
        "day": 27,
    }
    result = zdaDict2TIMESTAMP(zda_dict)
    assert result == "2006-03-27 11:00:03"
