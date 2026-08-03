"""Unit tests for decoding AIS messages 1-24."""

from ais import ais_msg_1, ais_msg_4
from aisutils import binary


def test_decode_msg_1_position_report() -> None:
    # NMEA string payload for AIS Message 1
    payload = "15Mt9B001;rgAFhGKLaRK1v2040@"
    bv = binary.ais6tobitvec(payload)

    msg = ais_msg_1.decode(bv)
    assert msg["MessageID"] == 1
    assert "UserID" in msg
    assert "longitude" in msg
    assert "latitude" in msg
    assert "SOG" in msg
    assert "COG" in msg


def test_decode_msg_4_basestation_report() -> None:
    # Full 168-bit AIS Message 4 payload (28 6-bit chars)
    payload = "403Ot1i00018?w?W1A4r3@@@@@@@"
    bv = binary.ais6tobitvec(payload)

    msg = ais_msg_4.decode(bv)
    assert msg["MessageID"] == 4
    assert "UserID" in msg
    assert "Time_year" in msg
    assert "Time_month" in msg
    assert "Time_day" in msg
