"""Performance benchmarks for Class A AIS position report decoding (Messages 1, 2, and 3)."""

from ais import ais_msg_1, ais_msg_2, ais_msg_3
from aisutils import binary

# Standard 168-bit payloads for AIS Messages 1, 2, and 3
MSG_1_PAYLOAD = "15Mt9B001;rgAFhGKLaRK1v2040@"
MSG_2_PAYLOAD = "25Mt9B001;rgAFhGKLaRK1v2040@"
MSG_3_PAYLOAD = "35Mt9B001;rgAFhGKLaRK1v2040@"

BV_MSG_1 = binary.ais6tobitvec(MSG_1_PAYLOAD)
BV_MSG_2 = binary.ais6tobitvec(MSG_2_PAYLOAD)
BV_MSG_3 = binary.ais6tobitvec(MSG_3_PAYLOAD)


def test_benchmark_ais_msg_1_decode(benchmark):
    """Benchmark AIS Class A Message 1 position report decoding."""
    msg = benchmark(ais_msg_1.decode, BV_MSG_1)
    assert msg["MessageID"] == 1
    assert "UserID" in msg


def test_benchmark_ais_msg_2_decode(benchmark):
    """Benchmark AIS Class A Message 2 position report decoding."""
    msg = benchmark(ais_msg_2.decode, BV_MSG_2)
    assert msg["MessageID"] == 2
    assert "UserID" in msg


def test_benchmark_ais_msg_3_decode(benchmark):
    """Benchmark AIS Class A Message 3 position report decoding."""
    msg = benchmark(ais_msg_3.decode, BV_MSG_3)
    assert msg["MessageID"] == 3
    assert "UserID" in msg


def test_benchmark_ais_nmea_payload_to_bitvector(benchmark):
    """Benchmark converting 6-bit AIS NMEA ASCII payload into a BitVector."""
    bv = benchmark(binary.ais6tobitvec, MSG_1_PAYLOAD)
    assert len(bv) == 168
