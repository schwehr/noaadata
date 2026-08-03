"""Comprehensive pytest unit tests for aisutils.nmea_cnc module."""

import pytest
from aisutils.nmea_cnc import msg_1_to_cnc, test
from nmea.checksum import checksumStr


def test_msg_1_to_cnc_valid_unknown_heading() -> None:
    """Test converting AIS message 1 with unknown heading (511 -> 0)."""
    sample = (
        "!AIVDM,1,1,,B,15Mwq1WP01rB2crBh5G:6?v200Rj,0*59,s28057,d-095,"
        "T49.46179499,x91028,rRDSULI1,1224516422"
    )
    result = msg_1_to_cnc(sample)
    assert result is not None
    assert result.startswith("$C&C,")
    assert "*" in result

    payload, checksum = result.split("*")
    assert checksumStr(payload) == checksum

    fields = payload.split(",")
    assert fields[0] == "$C&C"
    assert fields[1] == "366999814"  # UserID / MMSI
    assert fields[2] == "15:27:02.0"  # Formatted UTC time from timestamp
    assert float(fields[3]) == pytest.approx(-79.94475166666666)
    assert float(fields[4]) == pytest.approx(32.770286666666664)
    assert fields[5] == "0"  # Heading 511 mapped to 0
    assert fields[6:] == ["0.0", "0.0", "0.0", "0.0"]


def test_msg_1_to_cnc_valid_heading() -> None:
    """Test converting AIS message 1 with a known heading value."""
    sample = (
        "!AIVDM,1,1,,A,15M6ad0000G?j>FK@9Ds2mV22<1f,0*51,x261293,"
        "b003669707,1224516421\n"
    )
    result = msg_1_to_cnc(sample)
    assert result is not None
    assert result.startswith("$C&C,")
    payload, checksum = result.split("*")
    assert checksumStr(payload) == checksum
    fields = payload.split(",")
    assert fields[0] == "$C&C"
    assert fields[1] == "366062000"  # UserID / MMSI
    assert fields[2] == "15:27:01.0"  # Formatted UTC time
    assert float(fields[3]) == pytest.approx(-122.38088833333333)
    assert float(fields[4]) == pytest.approx(47.626805)
    assert fields[5] == "179"  # Preserved TrueHeading 179
    assert fields[6:] == ["0.0", "0.0", "0.0", "0.0"]


def test_msg_1_to_cnc_whitespace_handling() -> None:
    """Test msg_1_to_cnc handles leading/trailing whitespace correctly."""
    sample = (
        "  \n !AIVDM,1,1,,B,15Mwq1WP01rB2crBh5G:6?v200Rj,0*59,s28057,d-095,"
        "T49.46179499,x91028,rRDSULI1,1224516422 \t \n"
    )
    result = msg_1_to_cnc(sample)
    assert result is not None
    assert result.startswith("$C&C,366999814,")


def test_msg_1_to_cnc_invalid_nmea() -> None:
    """Test msg_1_to_cnc returns None for invalid or unparseable NMEA string."""
    assert msg_1_to_cnc("INVALID NMEA STRING") is None
    assert msg_1_to_cnc("") is None
    assert (
        msg_1_to_cnc(
            "$GPGGA,123519,4807.038,N,01131.000,E,1,08,0.9,545.4,M,46.9,M,,*47"
        )
        is None
    )


def test_nmea_cnc_legacy_test_function(capsys: pytest.CaptureFixture[str]) -> None:
    """Test executing the legacy test helper function in nmea_cnc module."""
    test()
    captured = capsys.readouterr()
    assert "LINE:" in captured.out
    assert "cnc:" in captured.out
    assert "$C&C,366999814" in captured.out
