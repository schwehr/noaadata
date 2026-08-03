"""Unit tests for AIS 6-bit ASCII string encoding, decoding, and padding removal."""

import pytest
from aisutils import aisstring


@pytest.mark.parametrize(
    "text",
    [
        "A",
        "TEST",
        "HELLO WORLD",
        "1234567890",
        "SHIP-NAME",
    ],
)
def test_encode_decode_roundtrip(text: str) -> None:
    encoded = aisstring.encode(text)
    decoded = aisstring.decode(encoded)
    assert decoded == text


def test_encode_fixed_bitsize() -> None:
    text = "SHIP"
    encoded = aisstring.encode(text, bitSize=60)
    assert len(encoded) == 60
    decoded = aisstring.decode(encoded)
    assert decoded == "SHIP@@@@@@"


@pytest.mark.parametrize(
    "padded_str, expected_unpadded",
    [
        ("@", ""),
        ("A@", "A"),
        ("ABCDEF1234@@@@@", "ABCDEF1234"),
        ("A@B", "A@B"),
        (" ", ""),
        ("MY SHIP NAME    ", "MY SHIP NAME"),
        ("MY SHIP NAME    @@@@", "MY SHIP NAME"),
    ],
)
def test_unpad(padded_str: str, expected_unpadded: str) -> None:
    assert aisstring.unpad(padded_str) == expected_unpadded
