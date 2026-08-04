"""Unit tests for binary AIS bitvector conversions and bit manipulations."""

from BitVector import BitVector

from aisutils import binary


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


def test_float_bitvector_conversions() -> None:
    val = 12.345
    bv = binary.float2bitvec(val)
    assert len(bv) == 32
    recovered = binary.bitvec2float(bv)
    assert abs(recovered - val) < 1e-5


def test_bit_count_and_parity() -> None:
    bv = BitVector.from_bitstring("101101")
    assert binary.bit_count(bv) == 4
    assert binary.parity(bv) == 0

    bv_odd = BitVector.from_bitstring("10101")
    assert binary.bit_count(bv_odd) == 3
    assert binary.parity(bv_odd) == 1
