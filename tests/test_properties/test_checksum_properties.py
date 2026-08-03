"""Property-based tests for NMEA-0183 XOR checksum calculation invariance in checksum.py."""

import re

from hypothesis import given
from hypothesis import strategies as st

from nmea import checksum

# Printable ASCII characters suitable for NMEA payloads (excluding !, ?, *)
nmea_payload_chars = st.characters(
    min_codepoint=32, max_codepoint=126, exclude_characters=["!", "?", "*"]
)
# NMEA payload strings must have len >= 3 due to checksumStr indexing assumptions
nmea_payload_strings = st.text(alphabet=nmea_payload_chars, min_size=3, max_size=80)


@given(s=nmea_payload_strings)
def test_checksum_format_invariant(s):
    """Property: checksumStr(s) returns a 2-character uppercase hex string [0-9A-F]{2}."""
    cs = checksum.checksumStr(s)
    assert len(cs) == 2
    assert re.match(r"^[0-9A-F]{2}$", cs) is not None


@given(s=nmea_payload_strings, prefix=st.sampled_from(["!", "?"]))
def test_valid_nmea_checksum_invariant(s, prefix):
    """Property: isChecksumValid returns True for properly constructed NMEA strings."""
    cs = checksum.checksumStr(s)
    nmea_str = f"{prefix}{s}*{cs}"
    assert checksum.isChecksumValid(nmea_str) is True


@given(s=nmea_payload_strings, prefix=st.sampled_from(["!", "?"]), data=st.data())
def test_corrupted_payload_detection_invariant(s, prefix, data):
    """Property: mutating any character in the payload causes isChecksumValid to return False."""
    cs = checksum.checksumStr(s)
    mutate_idx = data.draw(st.integers(min_value=0, max_value=len(s) - 1))
    orig_char = s[mutate_idx]
    # Replace orig_char with a different printable ASCII character
    new_char = chr(
        (ord(orig_char) + 1) if ord(orig_char) < 126 else (ord(orig_char) - 1)
    )
    corrupted_s = s[:mutate_idx] + new_char + s[mutate_idx + 1 :]

    # Calculate expected new checksum and verify old checksum fails on corrupted string
    corrupted_nmea_str = f"{prefix}{corrupted_s}*{cs}"
    if checksum.checksumStr(corrupted_s) != cs:
        assert checksum.isChecksumValid(corrupted_nmea_str) is False


@given(s1=nmea_payload_strings, s2=nmea_payload_strings)
def test_checksum_xor_composition_invariant(s1, s2):
    """Property: checksumStr(s1 + s2) == checksumStr(s1) ^ checksumStr(s2)."""
    val1 = int(checksum.checksumStr(s1), 16)
    val2 = int(checksum.checksumStr(s2), 16)
    combined_val = int(checksum.checksumStr(s1 + s2), 16)
    assert combined_val == (val1 ^ val2)


@given(s=nmea_payload_strings)
def test_checksum_prefix_stripping_invariant(s):
    """Property: leading '!' or '?' prefixes are stripped and produce identical checksums."""
    cs_plain = checksum.checksumStr(s)
    cs_excl = checksum.checksumStr("!" + s)
    cs_quest = checksum.checksumStr("?" + s)
    assert cs_excl == cs_plain
    assert cs_quest == cs_plain
