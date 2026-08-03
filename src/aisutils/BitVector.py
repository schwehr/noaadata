"""Wrapper for schwehr/bitvector-modern BitVector providing legacy keyword compatibility."""

from typing import Any

import BitVector as _bv_mod

_ModernBitVector = _bv_mod.BitVector


class BitVector(_ModernBitVector):
    """Modern BitVector extending schwehr/bitvector-modern with legacy constructor compatibility."""

    def __init__(
        self,
        *args: Any,
        intVal: int | None = None,
        bitstring: str | None = None,
        bitlist: Any = None,
        size: int | None = None,
        filename: str | None = None,
        stream: Any = None,
        **kwargs: Any,
    ):
        if intVal is not None:
            if size is not None:
                bv_obj = _ModernBitVector.from_int(intVal, size=size)
            else:
                bv_obj = _ModernBitVector.from_int(intVal)
            super().__init__(size=bv_obj._size)
            self.vector = bv_obj.vector
        elif bitstring is not None:
            bv_obj = _ModernBitVector.from_bitstring(bitstring)
            super().__init__(size=bv_obj._size)
            self.vector = bv_obj.vector
        elif filename is not None or stream is not None:
            if filename is not None:
                bv_obj = _ModernBitVector.from_file_path(filename)
            else:
                bv_obj = _ModernBitVector.from_stream(stream)
            super().__init__(size=bv_obj._size)
            self.vector = bv_obj.vector
        else:
            super().__init__(size=size, bitlist=bitlist)

    def intValue(self) -> int:
        """Legacy alias for int(self)."""
        return int(self)

    def count_bits(self) -> int:
        """Legacy alias for bit_count()."""
        return self.bit_count()

    def set_bit_vector_size(self, new_size: int) -> None:
        """Legacy helper to resize bit vector in place."""
        if new_size > self._size:
            self.pad_from_left(new_size - self._size)
        elif new_size < self._size:
            val = int(self) & ((1 << new_size) - 1)
            bv_obj = _ModernBitVector.from_int(val, size=new_size)
            self._size = bv_obj._size
            self.vector = bv_obj.vector


class BitVectorIterator:
    """Iterator wrapper for BitVector sequence traversal."""

    def __init__(self, bv: BitVector):
        self._bv = bv
        self._idx = 0

    def __iter__(self):
        return self

    def __next__(self) -> int:
        if self._idx < len(self._bv):
            res = int(self._bv[self._idx])
            self._idx += 1
            return res
        raise StopIteration


__all__ = ["BitVector", "BitVectorIterator"]
