"""Structural Protocols for NMEA sentence decoding and validation."""

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class NMEASentenceHandler(Protocol):
    """Protocol defining the interface for NMEA-0183 sentence parsers and encoders."""

    def decode(self, sentence: str) -> dict[str, Any]:
        """Decode an NMEA-0183 sentence into structured data."""
        ...

    def checksum(self, sentence: str) -> str:
        """Calculate or format the NMEA-0183 checksum for a sentence."""
        ...
