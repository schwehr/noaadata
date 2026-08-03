"""Unit tests for USCG N-AIS NMEA extension regex parsing."""

import pytest
from aisutils.uscg import uscg_ais_nmea_regex


def test_uscg_regex_parse() -> None:
    sample = "!AIVDM,1,1,,B,15Mt9B001;rgAFhGKLaRK1v2040@,0*2A,r003669983,1165795916"
    match = uscg_ais_nmea_regex.search(sample)
    assert match is not None
    groupdict = match.groupdict()
    assert groupdict["talker"] == "AI"
    assert groupdict["stringType"] == "VDM"
    assert groupdict["total"] == "1"
    assert groupdict["senNum"] == "1"
    assert groupdict["chan"] == "B"
    assert groupdict["body"] == "15Mt9B001;rgAFhGKLaRK1v2040@"
    assert groupdict["checksum"] == "2A"
    assert groupdict["station"] == "r003669983"
    assert groupdict["timeStamp"] == "1165795916"
