"""Performance benchmarks for NMEA sentence checksum calculation and verification."""

from nmea import checksum

SAMPLE_NMEA_STRING = "!AIVDM,1,1,,B,35MsUdPOh8JwI:0HUwquiIFH21>i,0*09"
SAMPLE_PAYLOAD_STRING = "AIVDM,1,1,,B,35MsUdPOh8JwI:0HUwquiIFH21>i,0"


def test_benchmark_nmea_checksum_str(benchmark):
    """Benchmark checksumStr calculation for NMEA strings."""
    cs = benchmark(checksum.checksumStr, SAMPLE_PAYLOAD_STRING)
    assert cs == "09"


def test_benchmark_nmea_is_checksum_valid(benchmark):
    """Benchmark isChecksumValid verification for standard NMEA sentences."""
    is_valid = benchmark(checksum.isChecksumValid, SAMPLE_NMEA_STRING)
    assert is_valid is True


def test_benchmark_nmea_corrupted_checksum_validation(benchmark):
    """Benchmark isChecksumValid verification for corrupted NMEA sentences."""
    corrupted_str = "!AIVDM,11,1,,B,35MsUdPOh8JwI:0HUwquiIFH21>i,0*09"
    is_valid = benchmark(checksum.isChecksumValid, corrupted_str)
    assert is_valid is False
