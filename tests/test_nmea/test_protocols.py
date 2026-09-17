"""Unit tests for NMEA structural protocols."""

from typing import Any

from nmea.protocols import NMEASentenceHandler


class ConformingNMEADecoder:
    """A dummy class that implements the NMEASentenceHandler protocol."""

    def decode(self, sentence: str) -> dict[str, Any]:
        return {"talker": "GP", "sentence_id": "RMC"}

    def checksum(self, sentence: str) -> str:
        return "00"


class NonConformingNMEADecoderMissingChecksum:
    """A dummy class missing the checksum method."""

    def decode(self, sentence: str) -> dict[str, Any]:
        return {"talker": "GP"}


class NonConformingNMEADecoderMissingDecode:
    """A dummy class missing the decode method."""

    def checksum(self, sentence: str) -> str:
        return "00"


def test_nmea_sentence_handler_conforming() -> None:
    """Test that a compliant class is recognized by the protocol."""
    decoder = ConformingNMEADecoder()
    assert isinstance(decoder, NMEASentenceHandler)


def test_nmea_sentence_handler_non_conforming() -> None:
    """Test that non-compliant classes are rejected by the protocol."""
    missing_checksum = NonConformingNMEADecoderMissingChecksum()
    assert not isinstance(missing_checksum, NMEASentenceHandler)

    missing_decode = NonConformingNMEADecoderMissingDecode()
    assert not isinstance(missing_decode, NMEASentenceHandler)
