"""Unit tests for binary AIS bitvector conversions and bit manipulations."""

from aisutils import binary
from BitVector import BitVector


def test_ais6tobitvec() -> None:
    payload = "15Mt9B001;rgAFhGKLaRK1v2040@"
    bv = binary.ais6tobitvec(payload)
    assert len(bv) == len(payload) * 6
    assert int(bv[:6]) == 1  # AIS Message 1


def test_set_bit_vector_size() -> None:
    bv = BitVector.from_int(5)
    padded = binary.setBitVectorSize(bv, 8)
    assert len(padded) == 8
    assert int(padded) == 5


def test_bv_from_signed_int() -> None:
    bv_pos = binary.bvFromSignedInt(5, 8)
    assert len(bv_pos) == 8
    assert bv_pos[0] == 0

    bv_neg = binary.bvFromSignedInt(-5, 8)
    assert len(bv_neg) == 8
    assert bv_neg[0] == 1
