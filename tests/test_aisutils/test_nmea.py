"""Unit tests for aisutils.nmea module."""

import pytest

from aisutils.nmea import bbmDecode
from nmea.checksum import checksumStr


def test_bbm_decode_valid() -> None:
    """Test happy path parsing of a valid BBM message."""
    msg = "!xxBBM,1,1,0,3,8,Fs[Ifs?:=2h:ec]dc3?HKI0f3?eFHa4[MGAMO6I2vqG0g,4*32"
    result = bbmDecode(msg)

    assert isinstance(result, dict)
    assert result == {
        "numFillBits": "4",
        "nmeaPrefix": "xx",
        "msgId": "8",
        "aisChan": "3",
        "data": "Fs[Ifs?:=2h:ec]dc3?HKI0f3?eFHa4[MGAMO6I2vqG0g",
        "seqId": "0",
        "nmeaCmd": "BBM",
        "sentNum": "1",
        "totSent": "1"
    }


def test_bbm_decode_validate_false() -> None:
    """Test decoding with invalid checksum when validate is False."""
    msg = "!xxBBM,1,1,0,3,8,Fs[Ifs?:=2h:ec]dc3?HKI0f3?eFHa4[MGAMO6I2vqG0g,4*99"
    result = bbmDecode(msg, validate=False)

    assert isinstance(result, dict)
    assert result["numFillBits"] == "4"
    assert result["nmeaCmd"] == "BBM"


def test_bbm_decode_invalid_checksum(capsys: pytest.CaptureFixture[str]) -> None:
    """Test decoding with invalid checksum when validate is True."""
    msg = "!xxBBM,1,1,0,3,8,Fs[Ifs?:=2h:ec]dc3?HKI0f3?eFHa4[MGAMO6I2vqG0g,4*99"
    result = bbmDecode(msg, validate=True)

    assert result is False
    captured = capsys.readouterr()
    assert "FIX: this should be an exception in bbmDecode.  Bad checksum" in captured.out


def test_bbm_decode_wrong_number_of_fields(capsys: pytest.CaptureFixture[str]) -> None:
    """Test decoding with fewer than 8 fields."""
    msg_base = "!xxBBM,1,1,0,3,8,data"
    checksum = checksumStr(msg_base)
    msg = f"{msg_base}*{checksum}"

    result = bbmDecode(msg, validate=True)

    assert result is False
    captured = capsys.readouterr()
    assert "FIX: this should be an exception in bbmDecode.  wrong number of fields" in captured.out
    assert msg in captured.out
