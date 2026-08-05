"""Unit tests for the NMEA module in aisutils."""

import pytest

from aisutils.nmea import bcfDecode, checksumStr

def test_bcfDecode_valid():
    """Test decoding a valid BCF message."""
    msg = "$AIBCF,12345,7,4731.0,N,05249.0,W,1,2087,2088,2087,2088,1,1,3,0,AI*51"
    result = bcfDecode(msg)

    assert result is not False
    assert result == {
        'posAccuracy': '1',
        'nmeaPrefix': 'AI',
        'TxChanB': '2088',
        'mmsi': '12345',
        'RepeatIndicator': '0',
        'lon': -5249.0,
        'PowerB': '1',
        'posSrc': '7',
        'nmeaCmd': 'BCF',
        'PowerA': '1',
        'BaseStationTalkerID': 'AI',
        'RxChanB': '2088',
        'lat': 4731.0,
        'RxChanA': '2087',
        'TxChanA': '2087',
        'VDLretries': '3'
    }

def test_bcfDecode_invalid_checksum():
    """Test that an invalid checksum results in False when validate=True."""
    # The valid checksum is 51, so we use 52 to make it invalid
    msg = "$AIBCF,12345,7,4731.0,N,05249.0,W,1,2087,2088,2087,2088,1,1,3,0,AI*52"
    result = bcfDecode(msg, validate=True)
    assert result is False

def test_bcfDecode_invalid_length():
    """Test that a truncated message results in False when validate=True."""
    # Removed a few fields from the end, then calculated new checksum
    base_msg = "$AIBCF,12345,7,4731.0,N,05249.0,W,1,2087,2088,2087"
    chk = checksumStr(base_msg)
    msg = f"{base_msg}*{chk}"

    result = bcfDecode(msg, validate=True)
    assert result is False

def test_bcfDecode_empty_lat_lon():
    """Test decoding a BCF message with empty latitude and longitude."""
    base_msg = "$AIBCF,12345,7,,N,,W,1,2087,2088,2087,2088,1,1,3,0,AI"
    chk = checksumStr(base_msg)
    msg = f"{base_msg}*{chk}"

    result = bcfDecode(msg)
    assert result is not False
    assert result['lat'] == ""
    assert result['lon'] == ""

def test_bcfDecode_south_west():
    """Test decoding a BCF message with South and East coordinates (testing both)."""
    # Changed N to S and W to E to test different branches
    # E should make lon positive
    base_msg = "$AIBCF,12345,7,4731.0,S,05249.0,E,1,2087,2088,2087,2088,1,1,3,0,AI"
    chk = checksumStr(base_msg)
    msg = f"{base_msg}*{chk}"

    result = bcfDecode(msg)
    assert result is not False
    assert result['lat'] == -4731.0
    assert result['lon'] == 5249.0
