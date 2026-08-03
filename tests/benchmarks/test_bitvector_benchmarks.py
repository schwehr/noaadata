"""Performance benchmarks for BitVector slice extraction, concatenation, padding, and joining."""

from aisutils import binary
from aisutils.BitVector import BitVector


def test_benchmark_bitvector_slice_extraction(benchmark):
    """Benchmark BitVector slice extraction performance."""
    bv = BitVector(bitstring="1010" * 25)  # 100 bits
    res = benchmark(lambda: bv[10:90])
    assert len(res) == 80


def test_benchmark_bitvector_concatenation(benchmark):
    """Benchmark BitVector concatenation performance."""
    bv1 = BitVector(bitstring="1100" * 15)  # 60 bits
    bv2 = BitVector(bitstring="0011" * 15)  # 60 bits
    res = benchmark(lambda: bv1 + bv2)
    assert len(res) == 120


def test_benchmark_bitvector_padding(benchmark):
    """Benchmark setBitVectorSize padding performance."""
    bv = BitVector(intVal=42)
    res = benchmark(binary.setBitVectorSize, bv, 32)
    assert len(res) == 32


def test_benchmark_bitvector_join(benchmark):
    """Benchmark joining multiple BitVectors into one."""
    bv_list = [BitVector(bitstring="1101") for _ in range(20)]
    res = benchmark(binary.joinBV, bv_list)
    assert len(res) == 80
