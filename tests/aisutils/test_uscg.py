"""Unit tests for src/aisutils/uscg.py in tests/aisutils/test_uscg.py."""

import io
import time

import pytest

from BitVector import BitVector
from aisutils.uscg import (
    UscgNmea,
    create_nmea,
    get_contents,
    get_station,
    uscg_ais_nmea_regex,
    write_uscg_nmea_fields,
)


def test_uscg_regex_parse_valid() -> None:
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


def test_uscg_regex_parse_full_fields() -> None:
    sample = "!AIVDM,1,1,3,B,15Cjtd0Oj;Jp7ilG7=UkKBoB0<06,0*63,s1234,d-119,T12.345,S4321,x100,r003669958,1085889680"
    match = uscg_ais_nmea_regex.search(sample)
    assert match is not None
    groupdict = match.groupdict()
    assert groupdict["talker"] == "AI"
    assert groupdict["stringType"] == "VDM"
    assert groupdict["total"] == "1"
    assert groupdict["senNum"] == "1"
    assert groupdict["seqId"] == "3"
    assert groupdict["chan"] == "B"
    assert groupdict["body"] == "15Cjtd0Oj;Jp7ilG7=UkKBoB0<06"
    assert groupdict["fillBits"] == "0"
    assert groupdict["checksum"] == "63"
    assert groupdict["s_rssi"] == "1234"
    assert groupdict["signal_strength"] == "-119"
    assert groupdict["time_of_arrival"] == "12.345"
    assert groupdict["slot"] == "4321"
    assert groupdict["x_station_counter"] == "100"
    assert groupdict["station"] == "r003669958"
    assert groupdict["station_type"] == "r"
    assert groupdict["timeStamp"] == "1085889680"


def test_uscg_regex_parse_invalid() -> None:
    invalid_sample = "INVALID_NMEA_STRING"
    match = uscg_ais_nmea_regex.search(invalid_sample)
    assert match is None


def test_write_uscg_nmea_fields() -> None:
    sample = "!AIVDM,1,1,,B,15Cjtd0Oj;Jp7ilG7=UkKBoB0<06,0*63,s1234,d-119,T12.345,S4321,x100,r003669958,1085889680"
    out = io.StringIO()
    write_uscg_nmea_fields(sample, out=out, indent="\t")
    res = out.getvalue()
    assert "prefix = AI" in res
    assert "stringType = VDM" in res
    assert "total = 1" in res
    assert "senNum = 1" in res
    assert "chan = B" in res
    assert "body = 15Cjtd0Oj;Jp7ilG7=UkKBoB0<06" in res
    assert "checksum = 63" in res
    assert "slot = 4321" in res
    assert "s = 1234" in res
    assert "signal_strength = -119" in res
    assert "time_of_arrival = 12.345" in res
    assert "x = 100" in res
    assert "station = r003669958" in res
    assert "station_type = r" in res
    assert "timeStamp = 1085889680" in res

    # Non-matching string test
    out2 = io.StringIO()
    write_uscg_nmea_fields("INVALID", out=out2)
    assert out2.getvalue() == ""


def test_get_station() -> None:
    nmea_recv = (
        "!AIVDM,1,1,,B,15Cjtd0Oj;Jp7ilG7=UkKBoB0<06,0*63,s1234,r003669958,1085889680"
    )
    assert get_station(nmea_recv) == "r003669958"

    nmea_base = "!AIVDM,1,1,,B,15Cjtd0Oj;Jp7ilG7=UkKBoB0<06,0*63,b12345,1085889680"
    assert get_station(nmea_base) == "b12345"

    nmea_none = "!AIVDM,1,1,,B,15Cjtd0Oj;Jp7ilG7=UkKBoB0<06,0*63,1085889680"
    assert get_station(nmea_none) is None


def test_get_contents() -> None:
    nmea = "!AIVDM,1,1,,B,15Cjtd0Oj;Jp7ilG7=UkKBoB0<06,0*63,s1234,1085889680"
    assert get_contents(nmea) == "15Cjtd0Oj;Jp7ilG7=UkKBoB0<06"


def test_uscg_nmea_class_default() -> None:
    un = UscgNmea()
    assert not hasattr(un, "cg_sec")


def test_uscg_nmea_class_full() -> None:
    sample = "!AIVDM,1,1,2,B,15Cjtd0Oj;Jp7ilG7=UkKBoB0<06,0*63,s1234,d-119,T12.34567,S4321,x99,r003669958,1085889680"
    un = UscgNmea(sample)

    assert un.nmeaType == "AIVDM"
    assert un.totalSentences == 1
    assert un.sentenceNum == 1
    assert un.sequentialMsgId == 2
    assert un.aisChannel == "B"
    assert un.contents == "15Cjtd0Oj;Jp7ilG7=UkKBoB0<06"
    assert un.fillbits == 0
    assert un.checksumStr == "63"
    assert un.msgTypeChar == "1"

    assert un.rssi == 1234
    assert un.signalStrength == -119
    assert un.timeOfArrival == 12.34567
    assert un.slotNumber == 4321
    assert un.x == 99
    assert un.station == "r003669958"
    assert un.stationTypeCode == "r"
    assert un.cg_sec == 1085889680.0
    assert un.timestamp.year == 2004
    assert un.sqlTimestampStr is not None


def test_uscg_nmea_class_partial_and_errors() -> None:
    # Sentence 2 (msgTypeChar should be None), no sequentialMsgId, invalid float time of arrival
    sample = "!AIVDM,2,2,,A,15Cjtd0Oj;Jp7ilG7=UkKBoB0<06,0*63,TBOGUS,1085889680"
    un = UscgNmea(sample)
    assert un.totalSentences == 2
    assert un.sentenceNum == 2
    assert un.sequentialMsgId is None
    assert un.msgTypeChar is None
    assert not hasattr(un, "timeOfArrival")


def test_uscg_nmea_get_bitvector() -> None:
    sample = "!AIVDM,1,1,,B,15Cjtd0Oj;Jp7ilG7=UkKBoB0<06,0*63,1085889680"
    un = UscgNmea(sample)
    bv = un.getBitVector()
    assert isinstance(bv, BitVector)
    assert len(bv) > 0


def test_uscg_nmea_equality() -> None:
    s1 = "!AIVDM,1,1,,B,15Cjtd0Oj;Jp7ilG7=UkKBoB0<06,0*63,s1234,d-119,T12.345,r003669958,S4321,1085889680"
    s1_same = "!AIVDM,1,1,,B,15Cjtd0Oj;Jp7ilG7=UkKBoB0<06,0*63,s1234,d-119,T12.345,r003669958,S4321,1085889680"
    s2_diff_sec = "!AIVDM,1,1,,B,15Cjtd0Oj;Jp7ilG7=UkKBoB0<06,0*63,s1234,d-119,T12.345,r003669958,S4321,1085889681"
    s3_diff_senNum = "!AIVDM,1,2,,B,15Cjtd0Oj;Jp7ilG7=UkKBoB0<06,0*63,s1234,d-119,T12.345,r003669958,S4321,1085889680"

    m1 = UscgNmea(s1)
    m1_same = UscgNmea(s1_same)
    m2 = UscgNmea(s2_diff_sec)
    m3 = UscgNmea(s3_diff_senNum)

    assert m1 == m1
    assert m1 == m1_same
    assert m1 != m2
    assert m1 != m3


def test_uscg_nmea_build_nmea_and_str() -> None:
    sample = "!AIVDM,1,1,2,B,15Cjtd0Oj;Jp7ilG7=UkKBoB0<06,0*63,s1234,d-119,T12.34567123,S4321,x99,r003669958,1085889680.0"
    un = UscgNmea(sample)
    rebuilt = un.buildNmea()
    assert rebuilt == sample
    assert str(un) == sample


def test_uscg_nmea_build_nmea_no_seq_id() -> None:
    sample = "!AIVDM,1,1,,B,15Cjtd0Oj;Jp7ilG7=UkKBoB0<06,0*63,r003669958,1085889680.0"
    un = UscgNmea(sample)
    rebuilt = un.buildNmea()
    assert rebuilt == sample


def test_create_nmea_basic() -> None:
    bv = BitVector.from_bitstring(
        (
            "0010000001010000100110000110000011001100010110"
            "1110111111001100101011000101101101011110011111"
            "0010001100110011000001110100011001000000000000"
            "000000000000111001111000000000"
        )[:168]
    )
    nmea_str = create_nmea(bv, cg_sec=1202235568)
    assert nmea_str.startswith("!AIVDM,1,1,,A,")
    assert "runknown" in nmea_str
    assert nmea_str.endswith("1202235568")


def test_create_nmea_custom_params() -> None:
    bv = BitVector.from_bitstring("001000000101")
    nmea_str = create_nmea(
        bv,
        nmeaType="!AIVDO",
        totalSentences=2,
        sentenceNum=1,
        sequentialMsgId=5,
        aisChannel="B",
        station="bStation1",
        cg_sec=1000000000.0,
    )
    assert nmea_str.startswith("!AIVDO,2,1,5,B,")
    assert "bStation1" in nmea_str
    assert nmea_str.endswith("1000000000.0")


def test_create_nmea_default_time() -> None:
    bv = BitVector.from_bitstring("001000")
    t_before = time.time()
    nmea_str = create_nmea(bv)
    t_after = time.time()
    ts = float(nmea_str.split(",")[-1])
    assert t_before <= ts <= t_after


def test_create_nmea_assertions() -> None:
    large_bv = BitVector(size=170)
    with pytest.raises(AssertionError):
        create_nmea(large_bv)

    valid_bv = BitVector(size=24)
    with pytest.raises(AssertionError):
        create_nmea(valid_bv, totalSentences=6)

    with pytest.raises(AssertionError):
        create_nmea(valid_bv, totalSentences=2, sentenceNum=2)

    with pytest.raises(AssertionError):
        create_nmea(valid_bv, sequentialMsgId=10)
