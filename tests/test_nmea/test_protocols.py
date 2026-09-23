"""Unit tests for NMEA structural protocols."""

from typing import Any

import pytest

from nmea.protocols import NMEASentenceHandler


class ConformingNMEADecoder:
    """A dummy class that implements the NMEASentenceHandler protocol."""

    def decode(self, sentence: str) -> dict[str, Any]:
        if not sentence.startswith("$") and not sentence.startswith("!"):
            raise ValueError("Invalid NMEA sentence format")
        return {"talker": sentence[1:3], "sentence_id": sentence[3:6], "raw": sentence}

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


def process_nmea_sentence(
    handler: NMEASentenceHandler, sentence: str
) -> dict[str, Any]:
    """Helper function to test protocol-based decoding behavior."""
    return handler.decode(sentence)


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


def test_nmea_sentence_handler_decode_execution() -> None:
    """Test calling the decode method on a conforming NMEASentenceHandler instance."""
    decoder: NMEASentenceHandler = ConformingNMEADecoder()
    sentence = "$GPRMC,123519,A,4807.038,N,01131.000,E,022.4,084.4,230394,003.1,W*6A"

    result = decoder.decode(sentence)

    assert isinstance(result, dict)
    assert result["talker"] == "GP"
    assert result["sentence_id"] == "RMC"
    assert result["raw"] == sentence


def test_nmea_sentence_handler_decode_via_protocol_helper() -> None:
    """Test calling decode via a function accepting NMEASentenceHandler protocol type."""
    decoder = ConformingNMEADecoder()
    sentence = "$GPGGA,123519,4807.038,N,01131.000,E,1,08,0.9,545.4,M,46.9,M,,*47"

    result = process_nmea_sentence(decoder, sentence)

    assert result == {"talker": "GP", "sentence_id": "GGA", "raw": sentence}


def test_nmea_sentence_handler_decode_error_handling() -> None:
    """Test that decode propagates exceptions for invalid inputs when implemented."""
    decoder = ConformingNMEADecoder()
    invalid_sentence = "INVALID_SENTENCE"

    with pytest.raises(ValueError, match="Invalid NMEA sentence format"):
        decoder.decode(invalid_sentence)
