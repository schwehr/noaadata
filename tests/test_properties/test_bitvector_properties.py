"""Property-based tests for BitVector slicing, padding, and binary unpacking invariants."""

from BitVector import BitVector
from hypothesis import given
from hypothesis import strategies as st

from aisutils import binary


# Custom strategy to generate random BitVectors (min_size >= 1 for legacy BitVector compatibility)
@st.composite
def bitvectors(draw, min_size=1, max_size=100):
    size = draw(st.integers(min_value=min_size, max_value=max_size))
    bit_list = draw(st.lists(st.sampled_from([0, 1]), min_size=size, max_size=size))
    return BitVector(bitlist=bit_list)


@given(bv=bitvectors(min_size=2, max_size=100), data=st.data())
def test_bitvector_slicing_concatenation_invariant(bv, data):
    """Property: bv[:k] + bv[k:] == bv for any split point 1 <= k < len(bv)."""
    k = data.draw(st.integers(min_value=1, max_value=len(bv) - 1))
    left = bv[:k]
    right = bv[k:]
    assert len(left) == k
    assert len(right) == len(bv) - k
    reconstructed = left + right
    assert len(reconstructed) == len(bv)
    assert str(reconstructed) == str(bv)


@given(bv1=bitvectors(min_size=1, max_size=50), bv2=bitvectors(min_size=1, max_size=50))
def test_bitvector_addition_length_invariant(bv1, bv2):
    """Property: len(bv1 + bv2) == len(bv1) + len(bv2)."""
    combined = bv1 + bv2
    assert len(combined) == len(bv1) + len(bv2)


@given(
    bv=bitvectors(min_size=1, max_size=50),
    target_size=st.integers(min_value=1, max_value=64),
)
def test_set_bitvector_size_padding_invariant(bv, target_size):
    """Property: setBitVectorSize pads with left zeros to at least target_size."""
    padded = binary.setBitVectorSize(bv, target_size)
    expected_len = max(len(bv), target_size)
    assert len(padded) == expected_len
    # Verify rightmost bits match original bv
    assert str(padded[len(padded) - len(bv) :]) == str(bv)


@given(
    bit_size=st.integers(min_value=2, max_value=32),
    data=st.data(),
)
def test_signed_int_bitvector_roundtrip_invariant(bit_size, data):
    """Property: signedIntFromBV(bvFromSignedInt(val, bit_size)) == val."""
    min_val = -(1 << (bit_size - 1))
    max_val = (1 << (bit_size - 1)) - 1
    val = data.draw(st.integers(min_value=min_val, max_value=max_val))

    bv = binary.bvFromSignedInt(val, bit_size)
    assert len(bv) == bit_size
    decoded_val = binary.signedIntFromBV(bv)
    assert decoded_val == val


@given(
    num_chars=st.integers(min_value=1, max_value=20),
    data=st.data(),
)
def test_ais6_bitvector_roundtrip_invariant(num_chars, data):
    """Property: 6-bit aligned BitVector roundtrips through bitvectoais6 and ais6tobitvec."""
    bit_len = num_chars * 6
    bit_list = data.draw(
        st.lists(st.sampled_from([0, 1]), min_size=bit_len, max_size=bit_len)
    )
    bv_orig = BitVector(bitlist=bit_list)

    str6, pad_count = binary.bitvectoais6(bv_orig)
    assert pad_count == 0
    assert len(str6) == num_chars

    bv_decoded = binary.ais6tobitvec(str6)
    assert len(bv_decoded) == bit_len
    assert str(bv_decoded) == str(bv_orig)


@given(bv_list=st.lists(bitvectors(min_size=1, max_size=20), min_size=1, max_size=5))
def test_join_bv_invariant(bv_list):
    """Property: joinBV([bv1, bv2, ...]) == bv1 + bv2 + ..."""
    joined = binary.joinBV(bv_list)
    expected_length = sum(len(bv) for bv in bv_list)
    assert len(joined) == expected_length
    expected_str = "".join(str(bv) for bv in bv_list)
    assert str(joined) == expected_str
