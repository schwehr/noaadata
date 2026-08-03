"""Structural Protocols for AIS message decoding and handling."""

from typing import Any, Protocol, runtime_checkable

from BitVector import BitVector


@runtime_checkable
class AISMessageHandler(Protocol):
    """Protocol defining the interface for AIS binary message decoders/encoders."""

    def decode(self, bv: BitVector, validate: bool = True) -> dict[str, Any]:
        """Decode a BitVector payload into a dictionary of field values."""
        ...

    def encode(self, params: dict[str, Any], validate: bool = True) -> BitVector:
        """Encode a dictionary of field values into a BitVector payload."""
        ...
