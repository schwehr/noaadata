"""Property-based tests for bidirectional 6-bit ASCII encoding/decoding in aisstring.py."""

from hypothesis import given, strategies as st
from aisutils import aisstring

# Strategy for valid 6-bit AIS characters
ais_chars = st.sampled_from(aisstring.characterLUT)

# Strategy for strings of valid AIS characters
ais_strings = st.text(alphabet=aisstring.characterLUT, min_size=1, max_size=50)


@given(s=ais_strings)
def test_aisstring_encode_decode_roundtrip_invariant(s):
    """Property: decode(encode(s)) == s for any string of valid 6-bit AIS characters."""
    bits = aisstring.encode(s)
    decoded = aisstring.decode(bits)
    assert decoded == s


@given(s=ais_strings)
def test_aisstring_encoded_bit_length_invariant(s):
    """Property: len(encode(s)) == 6 * len(s)."""
    bits = aisstring.encode(s)
    assert len(bits) == 6 * len(s)


@given(s=ais_strings, extra_chars=st.integers(min_value=0, max_value=20))
def test_aisstring_encode_bitsize_option_invariant(s, extra_chars):
    """Property: encode(s, bitSize=target_bits) creates a BitVector of length target_bits."""
    target_bits = 6 * (len(s) + extra_chars)
    bits = aisstring.encode(s, bitSize=target_bits)
    assert len(bits) == target_bits


@given(s=ais_strings, target_len=st.integers(min_value=1, max_value=60))
def test_aisstring_pad_unpad_invariant(s, target_len):
    """Property: unpad(pad(s, max(len(s), target_len)), removeBlanks=False) == s."""
    length = max(len(s), target_len)
    padded = aisstring.pad(s, length)
    assert len(padded) == length
    # If s does not end with '@', unpadding removes added '@'
    if not s.endswith("@"):
        unpadded = aisstring.unpad(padded, removeBlanks=False)
        assert unpadded == s


@given(c=ais_chars)
def test_character_lookup_table_consistency_invariant(c):
    """Property: characterLUT, characterDict, and characterBits are mutually consistent."""
    val = aisstring.characterDict[c]
    assert 0 <= val < 64
    assert aisstring.characterLUT[val] == c
    assert int(aisstring.characterBits[c]) == val
