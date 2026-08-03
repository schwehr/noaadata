"""Performance benchmarks for BitVector slice extraction, concatenation, padding, and joining."""

from BitVector import BitVector

from aisutils import binary


def test_benchmark_bitvector_slice_extraction(benchmark):
    """Benchmark BitVector slice extraction performance."""
    bv = BitVector.from_bitstring("1010" * 25)  # 100 bits
    res = benchmark(lambda: bv[10:90])
    assert len(res) == 80


def test_benchmark_bitvector_concatenation(benchmark):
    """Benchmark BitVector concatenation performance."""
    bv1 = BitVector.from_bitstring("1100" * 15)  # 60 bits
    bv2 = BitVector.from_bitstring("0011" * 15)  # 60 bits
    res = benchmark(lambda: bv1 + bv2)
    assert len(res) == 120


def test_benchmark_bitvector_padding(benchmark):
    """Benchmark setBitVectorSize padding performance."""
    bv = BitVector.from_int(42)
    res = benchmark(binary.setBitVectorSize, bv, 32)
    assert len(res) == 32


def test_benchmark_bitvector_join(benchmark):
    """Benchmark joining multiple BitVectors into one."""
    bv_list = [BitVector.from_bitstring("1101") for _ in range(20)]
    res = benchmark(binary.joinBV, bv_list)
    assert len(res) == 80
