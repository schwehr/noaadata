"""Unit tests for NMEA checksum validation and sentence decoding."""

import pytest

from nmea.checksum import checksumStr, isChecksumValid
from nmea.gga import ggaDecode, zdaDecode, zdaDict2TIMESTAMP


@pytest.mark.parametrize(
    ("nmea_str", "expected_checksum"),
    [
        ("!AIVDM,1,1,,B,35MsUdPOh8JwI:0HUwquiIFH21>i,0*09", "09"),
        ("AIVDM,1,1,,B,35MsUdPOh8JwI:0HUwquiIFH21>i,0", "09"),
    ],
)
def test_checksum_str(nmea_str: str, expected_checksum: str) -> None:
    assert checksumStr(nmea_str) == expected_checksum


def test_is_checksum_valid_true() -> None:
    valid_sentence = "!AIVDM,1,1,,B,35MsUdPOh8JwI:0HUwquiIFH21>i,0*09"
    assert isChecksumValid(valid_sentence) is True


def test_is_checksum_valid_false() -> None:
    corrupted_sentence = "!AIVDM,11,1,,B,35MsUdPOh8JwI:0HUwquiIFH21>i,0*09"
    assert isChecksumValid(corrupted_sentence) is False


def test_gga_decode() -> None:
    sentence = "$GPGGA,152009.00,3652.48059177,N,07620.02018248,W,1,11,0.8,3.669,M,-34.579,M,,*57"
    result = ggaDecode(sentence)
    assert result["hour"] == "15"
    assert result["min"] == "20"
    assert result["sec"] == "09"
    assert result["qual"] == 1
    assert result["sats"] == 11
    assert abs(result["horz_dilution"] - 0.8) < 1e-5
    assert abs(result["alt"] - 3.669) < 1e-5


def test_zda_decode_and_timestamp() -> None:
    sentence = "$ZQZDA,110003.00,27,03,2006,-5,00*47"
    decoded = zdaDecode(sentence)
    assert decoded["year"] == 2006
    assert decoded["mon"] == 3
    assert decoded["day"] == 27
    assert decoded["hour"] == 11
    assert decoded["min"] == 0
    assert decoded["sec"] == 3

    timestamp = zdaDict2TIMESTAMP(decoded)
    assert timestamp == "2006-03-27 11:00:03"
