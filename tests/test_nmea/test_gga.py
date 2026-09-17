import calendar

import pytest

from nmea.gga import (
    ggaDecode,
    zdaDecode,
    zdaDict2TIMESTAMP,
    zdaEpochSeconds,
)


def test_zda_decode_valid():
    """Test zdaDecode with a valid ZDA NMEA string."""
    sentence = "$ZQZDA,110003.00,27,03,2006,-5,00*47"
    decoded = zdaDecode(sentence)
    assert decoded["timekeeper"] == "ZQ"
    assert decoded["hour"] == 11
    assert decoded["min"] == 0
    assert decoded["sec"] == 3
    assert decoded["hsec"] == 0
    assert decoded["day"] == 27
    assert decoded["mon"] == 3
    assert decoded["year"] == 2006
    assert decoded["localzonehour"] == -5
    assert decoded["localzonemin"] == 0


def test_zda_decode_invalid():
    """Test zdaDecode with invalid ZDA strings."""
    # Too short
    with pytest.raises(AssertionError):
        zdaDecode("$ZQZDA,110003")

    # Incorrect starting character
    with pytest.raises(AssertionError):
        zdaDecode("ZQZDA,110003.00,27,03,2006,-5,00*47")

    # Incorrect sentence type
    with pytest.raises(AssertionError):
        zdaDecode("$ZQGGA,110003.00,27,03,2006,-5,00*47")

    # Missing dot in time
    with pytest.raises(AssertionError):
        zdaDecode("$ZQZDA,110003000,27,03,2006,-5,00*47")


def test_zda_epoch_seconds():
    """Test zdaEpochSeconds."""
    sentence = "$ZQZDA,110003.00,27,03,2006,-5,00*47"
    epoch = zdaEpochSeconds(sentence)
    # The time is 2006-03-27 11:00:03 UTC
    expected_epoch = calendar.timegm((2006, 3, 27, 11, 0, 3))
    assert epoch == expected_epoch


def test_zda_dict2timestamp():
    """Test zdaDict2TIMESTAMP."""
    zda_dict = {
        "hour": 11,
        "min": 0,
        "hsec": 0,
        "sec": 3,
        "mon": 3,
        "year": 2006,
        "day": 27,
        "timekeeper": "ZQ",
        "localzonehour": -5,
        "localzonemin": 0,
    }
    timestamp = zdaDict2TIMESTAMP(zda_dict)
    assert timestamp == "2006-03-27 11:00:03"


def test_gga_decode_valid():
    """Test ggaDecode with a valid GGA NMEA string."""
    sentence = "$GPGGA,152009.00,3652.48059177,N,07620.02018248,W,1,11,0.8,3.669,M,-34.579,M,,*57"
    result = ggaDecode(sentence)

    assert result["hour"] == "15"
    assert result["min"] == "20"
    assert result["sec"] == "09"
    assert result["hsec"] == "00"
    assert result["qual"] == 1
    assert result["sats"] == 11
    assert abs(result["horz_dilution"] - 0.8) < 1e-5
    assert abs(result["alt"] - 3.669) < 1e-5
    assert result["alt_units"] == "M"
    assert abs(result["geoidal_sep"] - (-34.579)) < 1e-5
    assert result["geoidal_sep_units"] == "M"
    assert result["age"] is None  # Since it's empty in this case

    # Test Lat / Lon calculations
    # Latitude: 36 deg 52.48059177 min N = 36 + 52.48059177/60 = 36.8746765
    assert abs(result["lat"] - 36.8746765295) < 1e-5
    # Longitude: 076 deg 20.02018248 min W = -(76 + 20.02018248/60) = -76.3336697
    assert abs(result["lon"] - (-76.333669708)) < 1e-5


def test_gga_decode_south_east():
    """Test ggaDecode with Southern Hemisphere and Eastern Hemisphere coordinates."""
    # Dummy values modified for S and E
    sentence = "$GPGGA,152009.00,3652.48059177,S,07620.02018248,E,1,11,0.8,3.669,M,-34.579,M,,*57"
    result = ggaDecode(sentence)

    # Latitude should be negative for South
    assert result["lat"] < 0
    assert abs(result["lat"] - (-36.8746765295)) < 1e-5

    # Longitude should be positive for East
    assert result["lon"] > 0
    assert abs(result["lon"] - 76.333669708) < 1e-5


def test_gga_decode_age():
    """Test ggaDecode where differential GPS data age is provided."""
    # Added '1.5' for age field
    sentence = "$GPGGA,152009.00,3652.48059177,N,07620.02018248,W,1,11,0.8,3.669,M,-34.579,M,1.5,0000*57"
    result = ggaDecode(sentence)
    assert result["age"] == 1.5
    assert result["diff_ref_station"] == "0000*57"


def test_gga_decode_validate():
    """Test ggaDecode with validation enabled."""
    valid_sentence = "$GPGGA,152009.00,3652.48059177,N,07620.02018248,W,1,11,0.8,3.669,M,-34.579,M,,*57"
    # Should not raise exception
    ggaDecode(valid_sentence, validate=True)

    # Invalid length (too short)
    with pytest.raises(AssertionError):
        ggaDecode("$GPGGA,152009", validate=True)

    # Invalid length (too long)
    too_long = "$GPGGA,152009.00,3652.48059177,N,07620.02018248,W,1,11,0.8,3.669,M,-34.579,M,1.5,00000*575757"
    with pytest.raises(AssertionError):
        ggaDecode(too_long, validate=True)

    # Incorrect starting character
    with pytest.raises(AssertionError):
        ggaDecode(
            "GPGGA,152009.00,3652.48059177,N,07620.02018248,W,1,11,0.8,3.669,M,-34.579,M,,*57",
            validate=True,
        )

    # Incorrect sentence type
    with pytest.raises(AssertionError):
        ggaDecode(
            "$GPZDA,152009.00,3652.48059177,N,07620.02018248,W,1,11,0.8,3.669,M,-34.579,M,,*57",
            validate=True,
        )
