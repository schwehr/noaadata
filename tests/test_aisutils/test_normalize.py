"""Comprehensive pytest unit tests for aisutils.normalize module."""

import pytest

from aisutils.normalize import Normalize
from aisutils.uscg import UscgNmea


def test_normalize_init_defaults() -> None:
    """Test Normalize initialization with default arguments."""
    norm = Normalize()
    assert norm.mostRecentTime == 0
    assert norm.ttl == 30
    assert norm.stations == {}
    assert norm.v is False
    assert norm.empty() is True


def test_normalize_init_custom() -> None:
    """Test Normalize initialization with custom arguments."""
    norm = Normalize(maxsize=10, ttl=60, verbose=True)
    assert norm.mostRecentTime == 0
    assert norm.ttl == 60
    assert norm.stations == {}
    assert norm.v is True
    assert norm.maxsize == 10


def test_normalize_cull() -> None:
    """Test cull method (currently a pass placeholder)."""
    norm = Normalize()
    # Ensure calling cull does not raise any exceptions
    norm.cull()


def test_normalize_single_sentence_message() -> None:
    """Test put with a single-sentence AIS message."""
    norm = Normalize()
    msg = "!AIVDM,1,1,,B,15Cjtd0Oj;Jp7ilG7=UkKBoB0<06,0*63,s1234,d-119,T12.34567123,r003669958,S4321,1085889680"
    norm.put(msg)

    assert norm.mostRecentTime == 1085889680.0
    assert norm.qsize() == 1
    result = norm.get()
    assert result == msg
    assert norm.empty() is True


def test_normalize_most_recent_time_tracking() -> None:
    """Test that mostRecentTime keeps track of the maximum timestamp seen."""
    norm = Normalize()
    msg1 = "!AIVDM,1,1,,B,15Cjtd0Oj;Jp7ilG7=UkKBoB0<06,0*63,r003669958,1000"
    msg2 = "!AIVDM,1,1,,B,15Cjtd0Oj;Jp7ilG7=UkKBoB0<06,0*63,r003669958,500"
    msg3 = "!AIVDM,1,1,,B,15Cjtd0Oj;Jp7ilG7=UkKBoB0<06,0*63,r003669958,2000"

    norm.put(msg1)
    assert norm.mostRecentTime == 1000.0

    norm.put(msg2)
    assert norm.mostRecentTime == 1000.0  # Should not decrease

    norm.put(msg3)
    assert norm.mostRecentTime == 2000.0  # Should update to larger timestamp


def test_normalize_multi_sentence_success() -> None:
    """Test successful reassembly of a 2-sentence AIS message."""
    norm = Normalize()
    part1 = "!AIVDM,2,1,1,A,55?P6P021b61@80:00000000000,0*1C,r003669958,1085889680"
    part2 = "!AIVDM,2,2,1,A,000000000000000000000000000,0*1D,r003669958,1085889681"

    norm.put(part1)
    # Part 1 alone should not yield a completed message in the queue
    assert norm.empty() is True
    assert "r003669958" in norm.stations
    assert len(norm.stations["r003669958"]) == 1

    norm.put(part2)
    # Part 2 completes the message
    assert norm.qsize() == 1
    assembled_str = norm.get()
    assert norm.empty() is True

    # Parse assembled string to verify correctness
    assembled_msg = UscgNmea(assembled_str)
    assert assembled_msg.totalSentences == 1
    assert assembled_msg.sentenceNum == 1
    assert assembled_msg.sequentialMsgId == 1
    assert assembled_msg.aisChannel == "A"
    assert (
        assembled_msg.contents
        == "55?P6P021b61@80:00000000000000000000000000000000000000"
    )
    assert assembled_msg.station == "r003669958"
    assert assembled_msg.cg_sec == 1085889680.0  # Retains first timestamp


def test_normalize_dangling_fragment(capsys: pytest.CaptureFixture[str]) -> None:
    """Test receiving the final sentence without receiving the preceding sentences."""
    norm = Normalize()
    # Sentence 2 of 2, but station r003669958 has no stored part 1
    part2 = "!AIVDM,2,2,1,A,000000000000000000000000000,0*1D,r003669958,1085889681"

    norm.put(part2)
    assert norm.empty() is True

    captured = capsys.readouterr()
    assert "dropping dangling fragment" in captured.err


def test_normalize_partial_message_discarded(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Test discarding a multi-sentence message when intermediate parts are missing."""
    norm = Normalize(verbose=True)
    # Part 1 of 3
    part1 = "!AIVDM,3,1,2,B,55?P6P0,0*1C,r003669958,1085889680"
    # Skip part 2 and send part 3 of 3
    part3 = "!AIVDM,3,3,2,B,0000000,0*1D,r003669958,1085889682"

    norm.put(part1)
    assert norm.empty() is True

    norm.put(part3)
    assert norm.empty() is True

    captured = capsys.readouterr()
    assert "partial message.  Discarding" in captured.err


def test_normalize_partial_message_discarded_quiet(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Test discarding a partial message when verbose is False."""
    norm = Normalize(verbose=False)
    part1 = "!AIVDM,3,1,2,B,55?P6P0,0*1C,r003669958,1085889680"
    part3 = "!AIVDM,3,3,2,B,0000000,0*1D,r003669958,1085889682"

    norm.put(part1)
    norm.put(part3)
    assert norm.empty() is True

    captured = capsys.readouterr()
    assert captured.err == ""


def test_normalize_mismatched_seq_id() -> None:
    """Test that fragments with different sequentialMsgId are not combined."""
    norm = Normalize()
    # Part 1 with seqId 1
    part1 = "!AIVDM,2,1,1,A,55?P6P021b61@80:00000000000,0*1C,r003669958,1085889680"
    # Part 2 with seqId 2 (mismatched)
    part2 = "!AIVDM,2,2,2,A,000000000000000000000000000,0*1D,r003669958,1085889681"

    norm.put(part1)
    norm.put(part2)
    # Should fail to reassemble because seqId mismatch
    assert norm.empty() is True


def test_normalize_mismatched_channel() -> None:
    """Test that fragments with different channels are not combined."""
    norm = Normalize()
    # Part 1 on channel A
    part1 = "!AIVDM,2,1,1,A,55?P6P021b61@80:00000000000,0*1C,r003669958,1085889680"
    # Part 2 on channel B (mismatched)
    part2 = "!AIVDM,2,2,1,B,000000000000000000000000000,0*1D,r003669958,1085889681"

    norm.put(part1)
    norm.put(part2)
    assert norm.empty() is True


def test_normalize_multiple_stations_interleaved() -> None:
    """Test handling interleaved fragments from different stations."""
    norm = Normalize()
    st1_p1 = "!AIVDM,2,1,1,A,STATION1_PART1,0*00,r001,1000"
    st2_p1 = "!AIVDM,2,1,1,A,STATION2_PART1,0*00,r002,1001"
    st1_p2 = "!AIVDM,2,2,1,A,STATION1_PART2,0*00,r001,1002"
    st2_p2 = "!AIVDM,2,2,1,A,STATION2_PART2,0*00,r002,1003"

    norm.put(st1_p1)
    norm.put(st2_p1)
    assert norm.empty() is True

    norm.put(st1_p2)
    assert norm.qsize() == 1
    msg1 = UscgNmea(norm.get())
    assert msg1.station == "r001"
    assert msg1.contents == "STATION1_PART1STATION1_PART2"

    norm.put(st2_p2)
    assert norm.qsize() == 1
    msg2 = UscgNmea(norm.get())
    assert msg2.station == "r002"
    assert msg2.contents == "STATION2_PART1STATION2_PART2"


def test_normalize_intermediate_fillbits_assertion() -> None:
    """Test assertion error when intermediate part has non-zero fillbits."""
    norm = Normalize()
    # Intermediate part (sentence 1 of 2) with non-zero fillbits (e.g., 2)
    part1 = "!AIVDM,2,1,1,A,55?P6P021b61@80:00000000000,2*1C,r003669958,1085889680"
    part2 = "!AIVDM,2,2,1,A,000000000000000000000000000,0*1D,r003669958,1085889681"

    norm.put(part1)
    with pytest.raises(AssertionError):
        norm.put(part2)
