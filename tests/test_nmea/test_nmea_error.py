import pytest

from nmea.nmea_error import NmeaChecksumError, NmeaError


def test_nmea_error_inheritance():
    """Test that NmeaError is an Exception."""
    assert issubclass(NmeaError, Exception)


def test_nmea_checksum_error_inheritance():
    """Test that NmeaChecksumError inherits from NmeaError and Exception."""
    assert issubclass(NmeaChecksumError, NmeaError)
    assert issubclass(NmeaChecksumError, Exception)


def test_raise_nmea_error():
    """Test raising and catching NmeaError."""
    with pytest.raises(NmeaError) as exc_info:
        raise NmeaError("General NMEA error occurred")

    assert str(exc_info.value) == "General NMEA error occurred"


def test_raise_nmea_checksum_error():
    """Test raising and catching NmeaChecksumError."""
    with pytest.raises(NmeaChecksumError) as exc_info:
        raise NmeaChecksumError("Invalid checksum")

    assert str(exc_info.value) == "Invalid checksum"

    # Also make sure it can be caught as NmeaError
    with pytest.raises(NmeaError):
        raise NmeaChecksumError("Invalid checksum")
