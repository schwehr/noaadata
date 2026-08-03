"""Unit tests for BitVector manipulation and operations."""

from aisutils.BitVector import BitVector


def test_bitvector_init_bitstring() -> None:
    bv = BitVector(bitstring="110001")
    assert len(bv) == 6
    assert str(bv) == "110001"
    assert bv[0] == 1
    assert bv[1] == 1
    assert bv[2] == 0


def test_bitvector_init_intval() -> None:
    bv = BitVector(intVal=45, size=16)
    assert len(bv) == 16
    assert bv.intValue() == 45


def test_bitvector_bitwise_operations() -> None:
    bv1 = BitVector(bitstring="1100")
    bv2 = BitVector(bitstring="1010")

    assert str(bv1 | bv2) == "1110"
    assert str(bv1 & bv2) == "1000"
    assert str(bv1 ^ bv2) == "0110"
    assert str(~bv1) == "0011"


def test_bitvector_slicing() -> None:
    bv = BitVector(bitstring="11001100")
    slice_bv = bv[2:6]
    assert str(slice_bv) == "0011"


def test_bitvector_count_bits() -> None:
    bv = BitVector(bitstring="101101")
    assert bv.count_bits() == 4
