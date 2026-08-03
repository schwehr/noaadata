#!/usr/bin/env python

__version__ = "3.3.1"
__author__ = "Avinash Kak (kak@purdue.edu)"
__date__ = "2014-February-4"
__url__ = "https://engineering.purdue.edu/kak/dist/BitVector-3.3.1.html"
__copyright__ = "(C) 2014 Avinash Kak. Python Software Foundation."

__doc__ = (
    """

    BitVector.py

    Version: """
    + __version__
    + """

    Author: Avinash Kak (kak@purdue.edu)

    Date: """
    + __date__
    + """


@endofdocs
"""
)


import array
import operator
from functools import reduce

_hexdict = {
    "0": "0000",
    "1": "0001",
    "2": "0010",
    "3": "0011",
    "4": "0100",
    "5": "0101",
    "6": "0110",
    "7": "0111",
    "8": "1000",
    "9": "1001",
    "a": "1010",
    "b": "1011",
    "c": "1100",
    "d": "1101",
    "e": "1110",
    "f": "1111",
}


def _readblock(blocksize, bitvector):
    """
    If this function can read all blocksize bits, it peeks ahead to see
    if there is anything more to be read in the file. It uses
    tell-read-seek mechanism for this in lines (R18) through (R21).  If
    there is nothing further to be read, it sets the more_to_read attribute
    of the bitvector object to False.  Obviously, this can only be done for
    seekable streams such as those connected with disk files.  According to
    Blair Houghton, a similar feature could presumably be implemented for
    socket streams by using recv() or recvfrom() if you set the flags
    argument to MSG_PEEK.
    """
    global _hexdict
    bitstring = ""
    i = 0
    while i < blocksize / 8:
        i += 1
        byte = bitvector.FILEIN.read(1)
        if byte == b"":
            if len(bitstring) < blocksize:
                bitvector.more_to_read = False
            return bitstring
        hexvalue = f"{byte[0]:02x}"
        bitstring += _hexdict[hexvalue[0]]
        bitstring += _hexdict[hexvalue[1]]
    file_pos = bitvector.FILEIN.tell()
    # peek at the next byte; moves file position only if a
    # byte is read
    next_byte = bitvector.FILEIN.read(1)
    if next_byte:
        # pretend we never read the byte
        bitvector.FILEIN.seek(file_pos)
    else:
        bitvector.more_to_read = False
    return bitstring


# --------------------  BitVector Class Definition   ----------------------


class BitVector:
    def __init__(self, *args, **kwargs):
        if args:
            raise ValueError(
                """BitVector constructor can only be called with
                         keyword arguments for the following keywords:
                         filename, fp, size, intVal, bitlist, bitstring,
                         hexstring, textstring, and rawbytes)"""
            )
        allowed_keys = (
            "bitlist",
            "bitstring",
            "filename",
            "fp",
            "intVal",
            "size",
            "textstring",
            "hexstring",
            "rawbytes",
        )
        keywords_used = list(kwargs.keys())
        for keyword in keywords_used:
            if keyword not in allowed_keys:
                raise ValueError("Wrong keyword used --- check spelling")
        filename = fp = intVal = size = bitlist = bitstring = textstring = hexstring = (
            rawbytes
        ) = None
        if "filename" in kwargs:
            filename = kwargs.pop("filename")
        if "fp" in kwargs:
            fp = kwargs.pop("fp")
        if "size" in kwargs:
            size = kwargs.pop("size")
        if "intVal" in kwargs:
            intVal = kwargs.pop("intVal")
        if "bitlist" in kwargs:
            bitlist = kwargs.pop("bitlist")
        if "bitstring" in kwargs:
            bitstring = kwargs.pop("bitstring")
        if "hexstring" in kwargs:
            hexstring = kwargs.pop("hexstring")
        if "textstring" in kwargs:
            textstring = kwargs.pop("textstring")
        if "rawbytes" in kwargs:
            rawbytes = kwargs.pop("rawbytes")
        self.filename = None
        self.size = 0
        self.FILEIN = None
        self.FILEOUT = None
        if filename:
            if (
                fp
                or size
                or intVal
                or bitlist
                or bitstring
                or hexstring
                or textstring
                or rawbytes
            ):
                raise ValueError("""When filename is specified, you cannot give values
                                    to any other constructor args""")
            self.filename = filename
            self.FILEIN = open(filename, "rb")
            self.more_to_read = True
            return
        elif fp:
            if (
                filename
                or size
                or intVal
                or bitlist
                or bitstring
                or hexstring
                or textstring
                or rawbytes
            ):
                raise ValueError("""When fileobject is specified, you cannot give
                                    values to any other constructor args""")
            bits = self.read_bits_from_fileobject(fp)
            bitlist = list(map(int, bits))
            self.size = len(bitlist)
        elif intVal or intVal == 0:
            if (
                filename
                or fp
                or bitlist
                or bitstring
                or hexstring
                or textstring
                or rawbytes
            ):
                raise ValueError("""When intVal is specified, you can only give a
                                    value to the 'size' constructor arg""")
            if intVal == 0:
                bitlist = [0]
                if size is None:
                    self.size = 1
                elif size == 0:
                    raise ValueError("""The value specified for size must be at least
                                        as large as for the smallest bit vector possible
                                        for intVal""")
                else:
                    if size < len(bitlist):
                        raise ValueError("""The value specified for size must be at least
                                            as large as for the smallest bit vector
                                            possible for intVal""")
                    n = size - len(bitlist)
                    bitlist = [0] * n + bitlist
                    self.size = len(bitlist)
            else:
                hexVal = hex(intVal).lower().rstrip("l")
                hexVal = hexVal[2:]
                if len(hexVal) == 1:
                    hexVal = "0" + hexVal
                bitlist = "".join([_hexdict[x] for x in hexVal])
                bitlist = list(map(int, bitlist))
                i = 0
                while i < len(bitlist):
                    if bitlist[i] == 1:
                        break
                    i += 1
                del bitlist[0:i]
                if size is None:
                    self.size = len(bitlist)
                elif size == 0:
                    if size < len(bitlist):
                        raise ValueError("""The value specified for size must be at least
                                            as large as for the smallest bit vector possible
                                            for intVal""")
                else:
                    if size < len(bitlist):
                        raise ValueError("""The value specified for size must be at least
                                            as large as for the smallest bit vector possible
                                            for intVal""")
                    n = size - len(bitlist)
                    bitlist = [0] * n + bitlist
                    self.size = len(bitlist)
        elif size is not None and size >= 0:
            if (
                filename
                or fp
                or intVal
                or bitlist
                or bitstring
                or hexstring
                or textstring
                or rawbytes
            ):
                raise ValueError("""When size is specified (without an intVal), you cannot
                                    give values to any other constructor args""")
            self.size = size
            two_byte_ints_needed = (size + 15) // 16
            self.vector = array.array("H", [0] * two_byte_ints_needed)
            return
        elif bitstring or bitstring == "":
            if (
                filename
                or fp
                or size
                or intVal
                or bitlist
                or hexstring
                or textstring
                or rawbytes
            ):
                raise ValueError("""When a bitstring is specified, you cannot give
                                    values to any other constructor args""")
            bitlist = list(map(int, list(bitstring)))
            self.size = len(bitlist)
        elif bitlist:
            if (
                filename
                or fp
                or size
                or intVal
                or bitstring
                or hexstring
                or textstring
                or rawbytes
            ):
                raise ValueError("""When bits are specified, you cannot give values
                                    to any other constructor args""")
            self.size = len(bitlist)
        elif textstring or textstring == "":
            if (
                filename
                or fp
                or size
                or intVal
                or bitlist
                or bitstring
                or hexstring
                or rawbytes
            ):
                raise ValueError("""When bits are specified through textstring, you
                                    cannot give values to any other constructor args""")
            hexlist = "".join(
                [x[2:] for x in list(map(hex, list(map(ord, list(textstring)))))]
            )
            bitlist = list(
                map(int, list("".join([_hexdict[x] for x in list(hexlist)])))
            )
            self.size = len(bitlist)
        elif hexstring or hexstring == "":
            if (
                filename
                or fp
                or size
                or intVal
                or bitlist
                or bitstring
                or textstring
                or rawbytes
            ):
                raise ValueError("""When bits are specified through hexstring, you
                                    cannot give values to any other constructor args""")
            bitlist = list(
                map(int, list("".join([_hexdict[x] for x in list(hexstring)])))
            )
            self.size = len(bitlist)
        elif rawbytes:
            if (
                filename
                or fp
                or size
                or intVal
                or bitlist
                or bitstring
                or textstring
                or hexstring
            ):
                raise ValueError("""When bits are specified through rawbytes, you
                                    cannot give values to any other constructor args""")
            import binascii

            hexlist = binascii.hexlify(rawbytes)
            bitlist = list(
                map(
                    int,
                    list("".join([_hexdict[x] for x in list(map(chr, list(hexlist)))])),
                )
            )
            self.size = len(bitlist)
        else:
            raise ValueError("wrong arg(s) for constructor")
        two_byte_ints_needed = (len(bitlist) + 15) // 16
        self.vector = array.array("H", [0] * two_byte_ints_needed)
        list(map(self._setbit, list(range(len(bitlist))), bitlist))

    def _setbit(self, posn, val):
        "Set the bit at the designated position to the value shown"
        if val not in (0, 1):
            raise ValueError("incorrect value for a bit")
        if isinstance(posn, (tuple)):
            posn = posn[0]
        if posn >= self.size or posn < -self.size:
            raise ValueError("index range error")
        if posn < 0:
            posn = self.size + posn
        block_index = posn // 16
        shift = posn & 15
        cv = self.vector[block_index]
        if (cv >> shift) & 1 != val:
            self.vector[block_index] = cv ^ (1 << shift)

    def _getbit(self, pos):
        "Get the bit from the designated position"
        if not isinstance(pos, slice):
            if pos >= self.size or pos < -self.size:
                raise ValueError("index range error")
            if pos < 0:
                pos = self.size + pos
            return (self.vector[pos // 16] >> (pos & 15)) & 1
        else:
            bitstring = ""
            start = 0 if pos.start is None else pos.start
            stop = self.size if pos.stop is None else pos.stop
            for i in range(start, stop):
                bitstring += str(self[i])
            return BitVector(bitstring=bitstring)

    def __xor__(self, other):
        """
        Take a bitwise 'XOR' of the bit vector on which the method is
        invoked with the argument bit vector.  Return the result as a new
        bit vector.  If the two bit vectors are not of the same size, pad
        the shorter one with zeros from the left.
        """
        if self.size < other.size:
            bv1 = self._resize_pad_from_left(other.size - self.size)
            bv2 = other
        elif self.size > other.size:
            bv1 = self
            bv2 = other._resize_pad_from_left(self.size - other.size)
        else:
            bv1 = self
            bv2 = other
        res = BitVector(size=bv1.size)
        lpb = list(map(operator.__xor__, bv1.vector, bv2.vector))
        res.vector = array.array("H", lpb)
        return res

    def __and__(self, other):
        """
        Take a bitwise 'AND' of the bit vector on which the method is
        invoked with the argument bit vector.  Return the result as a new
        bit vector.  If the two bit vectors are not of the same size, pad
        the shorter one with zeros from the left.
        """
        if self.size < other.size:
            bv1 = self._resize_pad_from_left(other.size - self.size)
            bv2 = other
        elif self.size > other.size:
            bv1 = self
            bv2 = other._resize_pad_from_left(self.size - other.size)
        else:
            bv1 = self
            bv2 = other
        res = BitVector(size=bv1.size)
        lpb = list(map(operator.__and__, bv1.vector, bv2.vector))
        res.vector = array.array("H", lpb)
        return res

    def __or__(self, other):
        """
        Take a bitwise 'OR' of the bit vector on which the method is
        invoked with the argument bit vector.  Return the result as a new
        bit vector.  If the two bit vectors are not of the same size, pad
        the shorter one with zero's from the left.
        """
        if self.size < other.size:
            bv1 = self._resize_pad_from_left(other.size - self.size)
            bv2 = other
        elif self.size > other.size:
            bv1 = self
            bv2 = other._resize_pad_from_left(self.size - other.size)
        else:
            bv1 = self
            bv2 = other
        res = BitVector(size=bv1.size)
        lpb = list(map(operator.__or__, bv1.vector, bv2.vector))
        res.vector = array.array("H", lpb)
        return res

    def __invert__(self):
        """
        Invert the bits in the bit vector on which the method is invoked
        and return the result as a new bit vector.
        """
        res = BitVector(size=self.size)
        lpb = list(map(operator.__inv__, self.vector))
        res.vector = array.array("H")
        for i in range(len(lpb)):
            res.vector.append(lpb[i] & 0x0000FFFF)
        return res

    def __add__(self, other):
        """
        Concatenate the argument bit vector with the bit vector on which
        the method is invoked.  Return the concatenated bit vector as a new
        BitVector object.
        """
        i = 0
        outlist = []
        while i < self.size:
            outlist.append(self[i])
            i += 1
        i = 0
        while i < other.size:
            outlist.append(other[i])
            i += 1
        return BitVector(bitlist=outlist)

    def _getsize(self):
        "Return the number of bits in a bit vector."
        return self.size

    def read_bits_from_file(self, blocksize):
        """
        Read blocksize bits from a disk file and return a BitVector object
        containing the bits.  If the file contains fewer bits than
        blocksize, construct the BitVector object from however many bits
        there are in the file.  If the file contains zero bits, return a
        BitVector object of size attribute set to 0.
        """
        error_str = """You need to first construct a BitVector
        object with a filename as  argument"""
        if not self.filename:
            raise SyntaxError(error_str)
        if blocksize % 8 != 0:
            raise ValueError("block size must be a multiple of 8")
        bitstr = _readblock(blocksize, self)
        if len(bitstr) == 0:
            return BitVector(size=0)
        else:
            return BitVector(bitstring=bitstr)

    def read_bits_from_fileobject(self, fp):
        """
        This function is meant to read a bit string from a file like
        object.
        """
        bitlist = []
        while 1:
            bit = fp.read()
            if bit == "":
                return bitlist
            bitlist += bit

    def write_bits_to_fileobject(self, fp):
        """
        This function is meant to write a bit vector directly to a file
        like object.  Note that whereas 'write_to_file' method creates a
        memory footprint that corresponds exactly to the bit vector, the
        'write_bits_to_fileobject' actually writes out the 1's and 0's as
        individual items to the file object.  That makes this method
        convenient for creating a string representation of a bit vector,
        especially if you use the StringIO class, as shown in the test
        code.
        """
        for bit_index in range(self.size):
            # For Python 3.x:
            if self[bit_index] == 0:
                fp.write("0")
            else:
                fp.write("1")

    def divide_into_two(self):
        """
        Divides an even-sized bit vector into two and returns the two
        halves as a list of two bit vectors.
        """
        if self.size % 2 != 0:
            raise ValueError("must have even num bits")
        i = 0
        outlist1 = []
        while i < self.size / 2:
            outlist1.append(self[i])
            i += 1
        outlist2 = []
        while i < self.size:
            outlist2.append(self[i])
            i += 1
        return [BitVector(bitlist=outlist1), BitVector(bitlist=outlist2)]

    def permute(self, permute_list):
        """
        Permute a bit vector according to the indices shown in the second
        argument list.  Return the permuted bit vector as a new bit vector.
        """
        if max(permute_list) > self.size - 1:
            raise ValueError("Bad permutation index")
        outlist = []
        i = 0
        while i < len(permute_list):
            outlist.append(self[permute_list[i]])
            i += 1
        return BitVector(bitlist=outlist)

    def unpermute(self, permute_list):
        """
        Unpermute the bit vector according to the permutation list supplied
        as the second argument.  If you first permute a bit vector by using
        permute() and then unpermute() it using the same permutation list,
        you will get back the original bit vector.
        """
        if max(permute_list) > self.size - 1:
            raise ValueError("Bad permutation index")
        if self.size != len(permute_list):
            raise ValueError("Bad size for permute list")
        out_bv = BitVector(size=self.size)
        i = 0
        while i < len(permute_list):
            out_bv[permute_list[i]] = self[i]
            i += 1
        return out_bv

    def write_to_file(self, file_out):
        """
        Write the bitvector to the file object file_out.  (A file object is
        returned by a call to open()). Since all file I/O is byte oriented,
        the bitvector must be multiple of 8 bits. Each byte treated as MSB
        first (0th index).
        """
        err_str = """Only a bit vector whose length is a multiple of 8 can
            be written to a file.  Use the padding functions to satisfy
            this constraint."""
        if not self.FILEOUT:
            self.FILEOUT = file_out
        if self.size % 8:
            raise ValueError(err_str)
        for byte in range(int(self.size / 8)):
            value = 0
            for bit in range(8):
                value += self._getbit(byte * 8 + (7 - bit)) << bit
            file_out.write(bytes(chr(value), "utf-8"))

    def close_file_object(self):
        """
        For closing a file object that was used for reading the bits into
        one or more BitVector objects.
        """
        if not self.FILEIN:
            raise SyntaxError("No associated open file")
        self.FILEIN.close()

    def int_val(self):
        "Return the integer value of a bitvector"
        intVal = 0
        for i in range(self.size):
            intVal += self[i] * (2 ** (self.size - i - 1))
        return intVal

    intValue = int_val

    def get_text_from_bitvector(self):
        """
        Return the text string formed by dividing the bitvector into bytes
        from the left and replacing each byte by its ASCII character (this
        is a useful thing to do only if the length of the vector is an
        integral multiple of 8 and every byte in your bitvector has a print
        representation)
        """
        if self.size % 8:
            raise ValueError("""\nThe bitvector for get_text_from_bitvector()
                                  must be an integral multiple of 8 bits""")
        return "".join(
            map(chr, list(map(int, [self[i : i + 8] for i in range(0, self.size, 8)])))
        )

    getTextFromBitVector = get_text_from_bitvector

    def get_hex_string_from_bitvector(self):
        """
        Return a string of hex digits by scanning the bits from the left
        and replacing each sequence of 4 bits by its corresponding hex
        digit (this is a useful thing to do only if the length of the
        vector is an integral multiple of 4)
        """
        if self.size % 4:
            raise ValueError("""\nThe bitvector for get_hex_string_from_bitvector()
                                  must be an integral multiple of 4 bits""")
        return "".join(
            [
                x.replace("0x", "")
                for x in list(
                    map(
                        hex,
                        list(
                            map(int, [self[i : i + 4] for i in range(0, self.size, 4)])
                        ),
                    )
                )
            ]
        )

    getHexStringFromBitVector = get_hex_string_from_bitvector

    def __lshift__(self, n):
        "For an in-place left circular shift by n bit positions"
        if self.size == 0:
            raise ValueError("""Circular shift of an empty vector
                                makes no sense""")
        if n < 0:
            return self >> abs(n)
        for _i in range(n):
            self.circular_rotate_left_by_one()
        return self

    def __rshift__(self, n):
        "For an in-place right circular shift by n bit positions."
        if self.size == 0:
            raise ValueError("""Circular shift of an empty vector
                                makes no sense""")
        if n < 0:
            return self << abs(n)
        for _i in range(n):
            self.circular_rotate_right_by_one()
        return self

    def circular_rotate_left_by_one(self):
        "For a one-bit in-place left circular shift"
        size = len(self.vector)
        bitstring_leftmost_bit = self.vector[0] & 1
        left_most_bits = list(map(operator.__and__, self.vector, [1] * size))
        left_most_bits.append(left_most_bits[0])
        del left_most_bits[0]
        self.vector = list(map(operator.__rshift__, self.vector, [1] * size))
        self.vector = list(
            map(
                operator.__or__,
                self.vector,
                list(map(operator.__lshift__, left_most_bits, [15] * size)),
            )
        )

        self._setbit(self.size - 1, bitstring_leftmost_bit)

    def circular_rotate_right_by_one(self):
        "For a one-bit in-place right circular shift"
        size = len(self.vector)
        bitstring_rightmost_bit = self[self.size - 1]
        right_most_bits = list(map(operator.__and__, self.vector, [0x8000] * size))
        self.vector = list(map(operator.__and__, self.vector, [~0x8000] * size))
        right_most_bits.insert(0, bitstring_rightmost_bit)
        right_most_bits.pop()
        self.vector = list(map(operator.__lshift__, self.vector, [1] * size))
        self.vector = list(
            map(
                operator.__or__,
                self.vector,
                list(map(operator.__rshift__, right_most_bits, [15] * size)),
            )
        )

        self._setbit(0, bitstring_rightmost_bit)

    def circular_rot_left(self):
        """
        This is merely another implementation of the method
        circular_rotate_left_by_one() shown above.  This one does NOT use
        map functions.  This method carries out a one-bit left circular
        shift of a bit vector.
        """
        max_index = (self.size - 1) // 16
        left_most_bit = self.vector[0] & 1
        self.vector[0] = self.vector[0] >> 1
        for i in range(1, max_index + 1):
            left_bit = self.vector[i] & 1
            self.vector[i] = self.vector[i] >> 1
            self.vector[i - 1] |= left_bit << 15
        self._setbit(self.size - 1, left_most_bit)

    def circular_rot_right(self):
        """
        This is merely another implementation of the method
        circular_rotate_right_by_one() shown above.  This one does NOT use
        map functions.  This method does a one-bit right circular shift of
        a bit vector.
        """
        max_index = (self.size - 1) // 16
        right_most_bit = self[self.size - 1]
        self.vector[max_index] &= ~0x8000
        self.vector[max_index] = self.vector[max_index] << 1
        for i in range(max_index - 1, -1, -1):
            right_bit = self.vector[i] & 0x8000
            self.vector[i] &= ~0x8000
            self.vector[i] = self.vector[i] << 1
            self.vector[i + 1] |= right_bit >> 15
        self._setbit(0, right_most_bit)

    def shift_left_by_one(self):
        """
        For a one-bit in-place left non-circular shift.  Note that
        bitvector size does not change.  The leftmost bit that moves
        past the first element of the bitvector is discarded and
        rightmost bit of the returned vector is set to zero.
        """
        size = len(self.vector)
        left_most_bits = list(map(operator.__and__, self.vector, [1] * size))
        left_most_bits.append(left_most_bits[0])
        del left_most_bits[0]
        self.vector = list(map(operator.__rshift__, self.vector, [1] * size))
        self.vector = list(
            map(
                operator.__or__,
                self.vector,
                list(map(operator.__lshift__, left_most_bits, [15] * size)),
            )
        )
        self._setbit(self.size - 1, 0)

    def shift_right_by_one(self):
        """
        For a one-bit in-place right non-circular shift.  Note that
        bitvector size does not change.  The rightmost bit that moves
        past the last element of the bitvector is discarded and
        leftmost bit of the returned vector is set to zero.
        """
        size = len(self.vector)
        right_most_bits = list(map(operator.__and__, self.vector, [0x8000] * size))
        self.vector = list(map(operator.__and__, self.vector, [~0x8000] * size))
        right_most_bits.insert(0, 0)
        right_most_bits.pop()
        self.vector = list(map(operator.__lshift__, self.vector, [1] * size))
        self.vector = list(
            map(
                operator.__or__,
                self.vector,
                list(map(operator.__rshift__, right_most_bits, [15] * size)),
            )
        )
        self._setbit(0, 0)

    def shift_left(self, n):
        "For an in-place left non-circular shift by n bit positions"
        for _i in range(n):
            self.shift_left_by_one()
        return self

    def shift_right(self, n):
        "For an in-place right non-circular shift by n bit positions."
        for _i in range(n):
            self.shift_right_by_one()
        return self

    # Allow array like subscripting for getting and setting:
    __getitem__ = _getbit

    def __setitem__(self, pos, item):
        """
        This is needed for both slice assignments and for index
        assignments.  It checks the types of pos and item to see if the
        call is for slice assignment.  For slice assignment, pos must be of
        type 'slice' and item of type BitVector.  For index assignment, the
        argument types are checked in the _setbit() method.
        """
        # The following section is for slice assignment:
        if isinstance(pos, slice):
            if not isinstance(item, BitVector):
                raise TypeError("""For slice assignment,
                    the right hand side must be a BitVector""")
            if not pos.start and not pos.stop:
                return item.deep_copy()
            elif not pos.start:
                if pos.stop != len(item):
                    raise ValueError("incompatible lengths for slice assignment")
                for i in range(pos.stop):
                    self[i] = item[i]
                return
            elif not pos.stop:
                if (len(self) - pos.start) != len(item):
                    raise ValueError("incompatible lengths for slice assignment")
                for i in range(len(item) - 1):
                    self[pos.start + i] = item[i]
                return
            else:
                if (pos.stop - pos.start) != len(item):
                    raise ValueError("incompatible lengths for slice assignment")
                for i in range(pos.start, pos.stop):
                    self[i] = item[i - pos.start]
                return
        # For index assignment use _setbit()
        self._setbit(pos, item)

    def __getslice__(self, i, j):
        "Fetch slices with [i:j], [:], etc."
        if self.size == 0:
            return BitVector(bitstring="")
        if i == j:
            return BitVector(bitstring="")
        slicebits = []
        j = min(j, self.size)
        for x in range(i, j):
            slicebits.append(self[x])
        return BitVector(bitlist=slicebits)

    # Allow len() to work:
    __len__ = _getsize
    # Allow int() to work:
    __int__ = intValue

    def __iter__(self):
        """
        To allow iterations over a bit vector by supporting the 'for bit in
        bit_vector' syntax:
        """
        return BitVectorIterator(self)

    def __str__(self):
        "To create a print representation"
        if self.size == 0:
            return ""
        return "".join(map(str, self))

    # Compare two bit vectors:
    def __eq__(self, other):
        if self.size != other.size:
            return False
        i = 0
        while i < self.size:
            if self[i] != other[i]:
                return False
            i += 1
        return True

    def __ne__(self, other):
        return not self == other

    def __lt__(self, other):
        return self.intValue() < other.intValue()

    def __le__(self, other):
        return self.intValue() <= other.intValue()

    def __gt__(self, other):
        return self.intValue() > other.intValue()

    def __ge__(self, other):
        return self.intValue() >= other.intValue()

    def deep_copy(self):
        "Make a deep copy of a bit vector"
        copy = str(self)
        return BitVector(bitstring=copy)

    _make_deep_copy = deep_copy

    def _resize_pad_from_left(self, n):
        """
        Resize a bit vector by padding with n 0's from the left. Return the
        result as a new bit vector.
        """
        new_str = "0" * n + str(self)
        return BitVector(bitstring=new_str)

    def _resize_pad_from_right(self, n):
        """
        Resize a bit vector by padding with n 0's from the right. Return
        the result as a new bit vector.
        """
        new_str = str(self) + "0" * n
        return BitVector(bitstring=new_str)

    def pad_from_left(self, n):
        "Pad a bit vector with n zeros from the left"
        new_str = "0" * n + str(self)
        bitlist = list(map(int, list(new_str)))
        self.size = len(bitlist)
        two_byte_ints_needed = (len(bitlist) + 15) // 16
        self.vector = array.array("H", [0] * two_byte_ints_needed)
        list(map(self._setbit, enumerate(bitlist), bitlist))

    def pad_from_right(self, n):
        "Pad a bit vector with n zeros from the right"
        new_str = str(self) + "0" * n
        bitlist = list(map(int, list(new_str)))
        self.size = len(bitlist)
        two_byte_ints_needed = (len(bitlist) + 15) // 16
        self.vector = array.array("H", [0] * two_byte_ints_needed)
        list(map(self._setbit, enumerate(bitlist), bitlist))

    def __contains__(self, otherBitVec):
        """
        This supports 'if x in y' and 'if x not in y' syntax for bit
        vectors.
        """
        if self.size == 0:
            raise ValueError("First arg bitvec has no bits")
        elif self.size < otherBitVec.size:
            raise ValueError("First arg bitvec too short")
        max_index = self.size - otherBitVec.size + 1
        for i in range(max_index):
            if self[i : i + otherBitVec.size] == otherBitVec:
                return True
        return False

    def reset(self, val):
        """
        Resets a previously created BitVector to either all zeros or all
        ones depending on the argument val.  Returns self to allow for
        syntax like
               bv = bv1[3:6].reset(1)
        or
               bv = bv1[:].reset(1)
        """
        if val not in (0, 1):
            raise ValueError("Incorrect reset argument")
        bitlist = [val for i in range(self.size)]
        list(map(self._setbit, enumerate(bitlist), bitlist))
        return self

    def count_bits(self):
        """
        Return the number of bits set in a BitVector instance.
        """

        return reduce(lambda x, y: int(x) + int(y), self)

    def set_value(self, *args, **kwargs):
        """
        Changes the bit pattern associated with a previously constructed
        BitVector instance.  The allowable modes for changing the internally
        stored bit pattern are the same as for the constructor.
        """
        self.__init__(*args, **kwargs)

    setValue = set_value

    def count_bits_sparse(self):
        """
        For sparse bit vectors, this method, contributed by Rhiannon, will
        be much faster.  She estimates that if a bit vector with over 2
        millions bits has only five bits set, this will return the answer
        in 1/18 of the time taken by the count_bits() method.  Note
        however, that count_bits() may work much faster for dense-packed
        bit vectors.  Rhianon's implementation is based on an algorithm
        generally known as the Brian Kernighan's way, although its
        antecedents predate its mention by Kernighan and Ritchie.
        """
        num = 0
        for intval in self.vector:
            if intval == 0:
                continue
            c = 0
            iv = intval
            while iv > 0:
                iv = iv & (iv - 1)
                c = c + 1
            num = num + c
        return num

    def jaccard_similarity(self, other):
        """
        Computes the Jaccard similarity coefficient between two bit vectors
        """
        assert self.intValue() > 0 or other.intValue() > 0, (
            "Jaccard called on two zero vectors --- NOT ALLOWED"
        )
        assert self.size == other.size, "vectors of unequal length"
        intersect = self & other
        union = self | other
        return intersect.count_bits_sparse() / float(union.count_bits_sparse())

    def jaccard_distance(self, other):
        """
        Computes the Jaccard distance between two bit vectors
        """
        assert self.size == other.size, "vectors of unequal length"
        return 1 - self.jaccard_similarity(other)

    def hamming_distance(self, other):
        """
        Computes the Hamming distance between two bit vectors
        """
        assert self.size == other.size, "vectors of unequal length"
        diff = self ^ other
        return diff.count_bits_sparse()

    def next_set_bit(self, from_index=0):
        """
        This method, contributed originally by Jason Allum and updated
        subsequently by John Gleeson, calculates the position of the next
        set bit at or after the current position index. It returns -1 if
        there is no next set bit.
        """
        assert from_index >= 0, "from_index must be nonnegative"
        i = from_index
        v = self.vector
        l = len(v)
        o = i >> 4
        s = i & 0x0F
        i = o << 4
        while o < l:
            h = v[o]
            if h:
                i += s
                m = 1 << s
                while m != (1 << 0x10):
                    if h & m:
                        return i
                    m <<= 1
                    i += 1
            else:
                i += 0x10
            s = 0
            o += 1
        return -1

    def rank_of_bit_set_at_index(self, position):
        """
        For a bit that is set at the argument 'position', this method
        returns how many bits are set to the left of that bit.  For
        example, in the bit pattern 000101100100, a call to this method
        with position set to 9 will return 4.
        """
        assert self[position] == 1, "the arg bit not set"
        bv = self[0 : position + 1]
        return bv.count_bits()

    def is_power_of_2(self):
        """
        Determines whether the integer value of a bit vector is a power of
        2.
        """
        if self.intValue() == 0:
            return False
        bv = self & BitVector(intVal=self.intValue() - 1)
        return bv.intValue() == 0

    isPowerOf2 = is_power_of_2

    def is_power_of_2_sparse(self):
        """
        Faster version of is_power_of2() for sparse bit vectors
        """
        return self.count_bits_sparse() == 1

    isPowerOf2_sparse = is_power_of_2_sparse

    def reverse(self):
        """
        Returns a new bit vector by reversing the bits in the bit vector on
        which the method is invoked.
        """
        reverseList = []
        i = 1
        while i < self.size + 1:
            reverseList.append(self[-i])
            i += 1
        return BitVector(bitlist=reverseList)

    def gcd(self, other):
        """
        Using Euclid's Algorithm, returns the greatest common divisor of
        the integer value of the bit vector on which the method is invoked
        and the integer value of the argument bit vector.
        """
        a = self.intValue()
        b = other.intValue()
        if a < b:
            a, b = b, a
        while b != 0:
            a, b = b, a % b
        return BitVector(intVal=a)

    def multiplicative_inverse(self, modulus):
        """
        Calculates the multiplicative inverse of a bit vector modulo the
        bit vector that is supplied as the argument. Code based on the
        Extended Euclid's Algorithm.
        """
        MOD = mod = modulus.intValue()
        num = self.intValue()
        x, x_old = 0, 1
        y, y_old = 1, 0
        while mod:
            quotient = num // mod
            num, mod = mod, num % mod
            x, x_old = x_old - x * quotient, x
            y, y_old = y_old - y * quotient, y
        if num != 1:
            return None
        else:
            MI = (x_old + MOD) % MOD
            return BitVector(intVal=MI)

    def length(self):
        return self.size

    def gf_multiply(self, b):
        """
        In the set of polynomials defined over GF(2), multiplies
        the bitvector on which the method is invoked with the
        bitvector b.  Returns the product bitvector.
        """
        a = self.deep_copy()
        b_copy = b.deep_copy()
        a.length() - a.next_set_bit(0) - 1
        b.length() - b_copy.next_set_bit(0) - 1
        result = BitVector(size=a.length() + b_copy.length())
        a.pad_from_left(result.length() - a.length())
        b_copy.pad_from_left(result.length() - b_copy.length())
        for i, bit in enumerate(b_copy):
            if bit == 1:
                power = b_copy.length() - i - 1
                a_copy = a.deep_copy()
                a_copy.shift_left(power)
                result ^= a_copy
        return result

    def gf_divide(self, mod, n):
        """
        Carries out modular division of a bitvector by the
        modulus bitvector mod in GF(2^n) finite field.
        Returns both the quotient and the remainder.
        """
        num = self
        if mod.length() > n + 1:
            raise ValueError("Modulus bit pattern too long")
        quotient = BitVector(intVal=0, size=num.length())
        remainder = num.deep_copy()
        i = 0
        while 1:
            i = i + 1
            if i == num.length():
                break
            mod_highest_power = mod.length() - mod.next_set_bit(0) - 1
            if remainder.next_set_bit(0) == -1:
                remainder_highest_power = 0
            else:
                remainder_highest_power = (
                    remainder.length() - remainder.next_set_bit(0) - 1
                )
            if (remainder_highest_power < mod_highest_power) or int(remainder) == 0:
                break
            else:
                exponent_shift = remainder_highest_power - mod_highest_power
                quotient[quotient.length() - exponent_shift - 1] = 1
                quotient_mod_product = mod.deep_copy()
                quotient_mod_product.pad_from_left(remainder.length() - mod.length())
                quotient_mod_product.shift_left(exponent_shift)
                remainder = remainder ^ quotient_mod_product
        if remainder.length() > n:
            remainder = remainder[remainder.length() - n :]
        return quotient, remainder

    def gf_multiply_modular(self, b, mod, n):
        """
        Multiplies a bitvector with the bitvector b in GF(2^n)
        finite field with the modulus bit pattern set to mod
        """
        a = self
        a_copy = a.deep_copy()
        b_copy = b.deep_copy()
        product = a_copy.gf_multiply(b_copy)
        _quotient, remainder = product.gf_divide(mod, n)
        return remainder

    def gf_MI(self, mod, n):
        """
        Returns the multiplicative inverse of a vector in the GF(2^n)
        finite field with the modulus polynomial set to mod
        """
        num = self
        NUM = num.deep_copy()
        MOD = mod.deep_copy()
        x = BitVector(size=mod.length())
        x_old = BitVector(intVal=1, size=mod.length())
        y = BitVector(intVal=1, size=mod.length())
        y_old = BitVector(size=mod.length())
        while int(mod):
            quotient, remainder = num.gf_divide(mod, n)
            num, mod = mod, remainder
            x, x_old = x_old ^ quotient.gf_multiply(x), x
            y, y_old = y_old ^ quotient.gf_multiply(y), y
        if int(num) != 1:
            return (
                "NO MI. However, the GCD of ",
                str(NUM),
                " and ",
                str(MOD),
                " is ",
                str(num),
            )
        else:
            z = x_old ^ MOD
            quotient, remainder = z.gf_divide(MOD, n)
            return remainder

    def runs(self):
        """
        Returns a list of the consecutive runs of 1's and 0's in
        the bit vector.  Each run is either a string of all 1's or
        a string of all 0's.
        """
        if self.size == 0:
            raise ValueError("""An empty vector has no runs""")
        allruns = []
        run = ""
        previous_bit = self[0]
        run = "0" if previous_bit == 0 else "1"
        for bit in list(self)[1:]:
            if bit == 0 and previous_bit == 0:
                run += "0"
            elif bit == 1 and previous_bit == 0:
                allruns.append(run)
                run = "1"
            elif bit == 0 and previous_bit == 1:
                allruns.append(run)
                run = "0"
            else:
                run += "1"
            previous_bit = bit
        allruns.append(run)
        return allruns

    def test_for_primality(self):
        """
        Check if the integer value of the bitvector is a prime through the
        Miller-Rabin probabilistic test of primality.  If not found to be a
        composite, estimate the probability of the bitvector being a prime
        using this test.
        """
        p = int(self)
        probes = [2, 3, 5, 7, 11, 13, 17]
        for a in probes:
            if a == p:
                return 1
        if any(p % a == 0 for a in probes):
            return 0
        k, q = 0, p - 1
        while not q & 1:
            q >>= 1
            k += 1
        for a in probes:
            a_raised_to_q = pow(a, q, p)
            if a_raised_to_q == 1 or a_raised_to_q == p - 1:
                continue
            a_raised_to_jq = a_raised_to_q
            primeflag = 0
            for _j in range(k - 1):
                a_raised_to_jq = pow(a_raised_to_jq, 2, p)
                if a_raised_to_jq == p - 1:
                    primeflag = 1
                    break
            if not primeflag:
                return 0
        probability_of_prime = 1 - 1.0 / (4 ** len(probes))
        return probability_of_prime

    def gen_rand_bits_for_prime(self, width):
        """
        The bulk of the work here is done by calling random.getrandbits(
        width) which returns an integer whose binary code representation
        will not be larger than the argument 'width'.  However, when random
        numbers are generated as candidates for primes, you often want to
        make sure that the random number thus created spans the full width
        specified by 'width' and that the number is odd.  This we do by
        setting the two most significant bits and the least significant
        bit.  If you only want to set the most significant bit, comment out
        the statement in line (pr29).
        """
        import secrets

        candidate = secrets.randbits(width)
        candidate |= 1
        candidate |= 1 << width - 1
        candidate |= 2 << width - 3
        return BitVector(intVal=candidate)


# -----------------------  BitVectorIterator Class -----------------------


class BitVectorIterator:
    def __init__(self, bitvec):
        self.items = []
        for i in range(bitvec.size):
            self.items.append(bitvec._getbit(i))
        self.index = -1

    def __iter__(self):
        return self

    def __next__(self):
        self.index += 1
        if self.index < len(self.items):
            return self.items[self.index]
        else:
            raise StopIteration

    next = __next__


# ------------------------  End of Class Definition -----------------------

# ------------------------     Test Code Follows    -----------------------

if __name__ == "__main__":
    # Construct an EMPTY bit vector (a bit vector of size 0):
    print("\nConstructing an EMPTY bit vector (a bit vector of size 0):")
    bv1 = BitVector(size=0)
    print(bv1)  # no output

    # Construct a bit vector of size 2:
    print("\nConstructing a bit vector of size 2:")
    bv2 = BitVector(size=2)
    print(bv2)  # 00

    # Joining two bit vectors:
    print("\nOutput concatenation of two previous bit vectors:")
    result = bv1 + bv2
    print(result)  # 00

    # Construct a bit vector with a tuple of bits:
    print("\nThis is a bit vector from a tuple of bits:")
    bv = BitVector(bitlist=(1, 0, 0, 1))
    print(bv)  # 1001

    # Construct a bit vector with a list of bits:
    print("\nThis is a bit vector from a list of bits:")
    bv = BitVector(bitlist=[1, 1, 0, 1])
    print(bv)  # 1101

    # Construct a bit vector from an integer
    bv = BitVector(intVal=5678)
    print("\nBit vector constructed from integer 5678:")
    print(bv)  # 1011000101110
    print("\nBit vector constructed from integer 0:")
    bv = BitVector(intVal=0)
    print(bv)  # 0
    print("\nBit vector constructed from integer 2:")
    bv = BitVector(intVal=2)
    print(bv)  # 10
    print("\nBit vector constructed from integer 3:")
    bv = BitVector(intVal=3)
    print(bv)  # 11
    print("\nBit vector constructed from integer 123456:")
    bv = BitVector(intVal=123456)
    print(bv)  # 11110001001000000
    print("\nInt value of the previous bit vector as computed by int_val():")
    print(bv.int_val())  # 123456
    print("\nInt value of the previous bit vector as computed by int():")
    print(int(bv))  # 123456

    # Construct a bit vector from a very large integer:
    x = 12345678901234567890123456789012345678901234567890123456789012345678901234567890
    bv = BitVector(intVal=x)
    print("\nHere is a bit vector constructed from a very large integer:")
    print(bv)
    print(f"The integer value of the above bit vector is:{int(bv)}")

    # Construct a bit vector directly from a file-like object:
    import io

    x = "111100001111"
    x = ""
    x = "111100001111"
    fp_read = io.StringIO(x)
    bv = BitVector(fp=fp_read)
    print("\nBit vector constructed directed from a file like object:")
    print(bv)  # 111100001111

    # Construct a bit vector directly from a bit string:
    bv = BitVector(bitstring="00110011")
    print("\nBit Vector constructed directly from a bit string:")
    print(bv)  # 00110011

    bv = BitVector(bitstring="")
    print("\nBit Vector constructed directly from an empty bit string:")
    print(bv)  # nothing
    print("\nInteger value of the previous bit vector:")
    print(bv.int_val())  # 0

    print("\nConstructing a bit vector from the textstring 'hello':")
    bv3 = BitVector(textstring="hello")
    print(bv3)
    mytext = bv3.get_text_from_bitvector()
    print("Text recovered from the previous bitvector: ")
    print(mytext)  # hello

    print("\nConstructing a bit vector from the hexstring '68656c6c6f':")
    bv4 = BitVector(hexstring="68656c6c6f")
    print(bv4)
    myhexstring = bv4.get_hex_string_from_bitvector()
    print("Hex string recovered from the previous bitvector: ")
    print(myhexstring)  # 68656c6c6f

    print(
        "\nDemonstrating the raw bytes mode of constructing a bit vector (useful for reading public and private keys):"
    )
    mypubkey = "ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEA5amriY96HQS8Y/nKc8zu3zOylvpOn3vzMmWwrtyDy+aBvns4UC1RXoaD9rDKqNNMCBAQwWDsYwCAFsrBzbxRQONHePX8lRWgM87MseWGlu6WPzWGiJMclTAO9CTknplG9wlNzLQBj3dP1M895iLF6jvJ7GR+V3CRU6UUbMmRvgPcsfv6ec9RRPm/B8ftUuQICL0jt4tKdPG45PBJUylHs71FuE9FJNp01hrj1EMFObNTcsy9zuis0YPyzArTYSOUsGglleExAQYi7iLh17pAa+y6fZrGLsptgqryuftN9Q4NqPuTiFjlqRowCDU7sSxKDgU7bzhshyVx3+pzXO4D2Q== kak@pixie"
    import base64

    keydata = base64.b64decode(bytes(mypubkey.split(None)[1], "utf-8"))
    bv = BitVector(rawbytes=keydata)
    print(bv)

    # Test array-like indexing for a bit vector:
    bv = BitVector(bitstring="110001")
    print("\nPrints out bits individually from bitstring 110001:")
    print((bv[0], bv[1], bv[2], bv[3], bv[4], bv[5]))  # 1 1 0 0 0 1
    print("\nSame as above but using negative array indexing:")
    print((bv[-1], bv[-2], bv[-3], bv[-4], bv[-5], bv[-6]))  # 1 0 0 0 1 1

    # Test setting bit values with positive and negative
    # accessors:
    bv = BitVector(bitstring="1111")
    print("\nBitstring for 1111:")
    print(bv)  # 1111

    print("\nReset individual bits of above vector:")
    bv[0] = 0
    bv[1] = 0
    bv[2] = 0
    bv[3] = 0
    print(bv)  # 0000
    print("\nDo the same as above with negative indices:")
    bv[-1] = 1
    bv[-2] = 1
    bv[-4] = 1
    print(bv)  # 1011

    print("\nCheck equality and inequality ops:")
    bv1 = BitVector(bitstring="00110011")
    bv2 = BitVector(bitlist=[0, 0, 1, 1, 0, 0, 1, 1])
    print(bv1 == bv2)  # True
    print(bv1 != bv2)  # False
    print(bv1 < bv2)  # False
    print(bv1 <= bv2)  # True
    bv3 = BitVector(intVal=5678)
    print(bv3.int_val())  # 5678
    print(bv3)  # 10110000101110
    print(bv1 == bv3)  # False
    print(bv3 > bv1)  # True
    print(bv3 >= bv1)  # True

    # Write a bit vector to a file like object
    fp_write = io.StringIO()
    bv.write_bits_to_fileobject(fp_write)
    print("\nGet bit vector written out to a file-like object:")
    print(fp_write.getvalue())  # 1011

    print("\nExperiments with bitwise logical operations:")
    bv3 = bv1 | bv2
    print(bv3)  # 00110011
    bv3 = bv1 & bv2
    print(bv3)  # 00110011
    bv3 = bv1 + bv2
    print(bv3)  # 0011001100110011
    bv4 = BitVector(size=3)
    print(bv4)  # 000
    bv5 = bv3 + bv4
    print(bv5)  # 0011001100110011000
    bv6 = ~bv5
    print(bv6)  # 1100110011001100111
    bv7 = bv5 & bv6
    print(bv7)  # 0000000000000000000
    bv7 = bv5 | bv6
    print(bv7)  # 1111111111111111111

    print("\nTry logical operations on bit vectors of different sizes:")
    print(BitVector(intVal=6) ^ BitVector(intVal=13))  # 1011
    print(BitVector(intVal=6) & BitVector(intVal=13))  # 0100
    print(BitVector(intVal=6) | BitVector(intVal=13))  # 1111

    print(BitVector(intVal=1) ^ BitVector(intVal=13))  # 1100
    print(BitVector(intVal=1) & BitVector(intVal=13))  # 0001
    print(BitVector(intVal=1) | BitVector(intVal=13))  # 1101

    print("\nExperiments with setbit() and len():")
    bv7[7] = 0
    print(bv7)  # 1111111011111111111
    print(len(bv7))  # 19
    bv8 = (bv5 & bv6) ^ bv7
    print(bv8)  # 1111111011111111111

    print("\nConstruct a bit vector from what is in the file testinput1.txt:")
    bv = BitVector(filename="TestBitVector/testinput1.txt")
    # print bv                                    # nothing to show
    bv1 = bv.read_bits_from_file(64)
    print("\nPrint out the first 64 bits read from the file:")
    print(bv1)
    # 0100000100100000011010000111010101101110011001110111001001111001
    print("\nRead the next 64 bits from the same file:")
    bv2 = bv.read_bits_from_file(64)
    print(bv2)
    # 0010000001100010011100100110111101110111011011100010000001100110
    print("\nTake xor of the previous two bit vectors:")
    bv3 = bv1 ^ (bv2)
    print(bv3)
    # 0110000101000010000110100001101000011001000010010101001000011111

    print("\nExperiment with dividing an even-sized vector into two:")
    [bv4, bv5] = bv3.divide_into_two()
    print(bv4)  # 01100001010000100001101000011010
    print(bv5)  # 00011001000010010101001000011111

    # Permute a bit vector:
    print("\nWe will use this bit vector for experiments with permute()")
    bv1 = BitVector(bitlist=[1, 0, 0, 1, 1, 0, 1])
    print(bv1)  # 1001101

    bv2 = bv1.permute([6, 2, 0, 1])
    print("\nPermuted and contracted form of the previous bit vector:")
    print(bv2)  # 1010

    print(
        "\nExperiment with writing an internally generated bit vector out to a disk file:"
    )
    bv1 = BitVector(bitstring="00001010")
    FILEOUT = open("TestBitVector/test.txt", "wb")
    bv1.write_to_file(FILEOUT)
    FILEOUT.close()
    bv2 = BitVector(filename="TestBitVector/test.txt")
    bv3 = bv2.read_bits_from_file(32)
    print(
        "\nDisplay bit vectors written out to file and read back from the file and their respective lengths:"
    )
    print(str(bv1) + " " + str(bv3))
    print(str(len(bv1)) + " " + str(len(bv3)))

    print("\nExperiments with reading a file from the beginning to end:")
    bv = BitVector(filename="TestBitVector/testinput4.txt")
    print("\nHere are all the bits read from the file:")
    while bv.more_to_read:
        bv_read = bv.read_bits_from_file(64)
        print(bv_read)
    print("\n")

    print(
        "\nExperiment with closing a file object and start extracting bit vectors from the file from the beginning again:"
    )
    bv.close_file_object()
    bv = BitVector(filename="TestBitVector/testinput4.txt")
    bv1 = bv.read_bits_from_file(64)
    print(
        "\nHere are all the first 64 bits read from the file again after the file object was closed and opened again:"
    )
    print(bv1)
    FILEOUT = open("TestBitVector/testinput5.txt", "wb")
    bv1.write_to_file(FILEOUT)
    FILEOUT.close()

    print(
        "\nExperiment in 64-bit permutation and unpermutation of the previous 64-bit bitvector:"
    )
    print(
        "The permutation array was generated separately by the Fisher-Yates shuffle algorithm:"
    )
    bv2 = bv1.permute(
        [
            22,
            47,
            33,
            36,
            18,
            6,
            32,
            29,
            54,
            62,
            4,
            9,
            42,
            39,
            45,
            59,
            8,
            50,
            35,
            20,
            25,
            49,
            15,
            61,
            55,
            60,
            0,
            14,
            38,
            40,
            23,
            17,
            41,
            10,
            57,
            12,
            30,
            3,
            52,
            11,
            26,
            43,
            21,
            13,
            58,
            37,
            48,
            28,
            1,
            63,
            2,
            31,
            53,
            56,
            44,
            24,
            51,
            19,
            7,
            5,
            34,
            27,
            16,
            46,
        ]
    )
    print("Permuted bit vector:")
    print(bv2)

    bv3 = bv2.unpermute(
        [
            22,
            47,
            33,
            36,
            18,
            6,
            32,
            29,
            54,
            62,
            4,
            9,
            42,
            39,
            45,
            59,
            8,
            50,
            35,
            20,
            25,
            49,
            15,
            61,
            55,
            60,
            0,
            14,
            38,
            40,
            23,
            17,
            41,
            10,
            57,
            12,
            30,
            3,
            52,
            11,
            26,
            43,
            21,
            13,
            58,
            37,
            48,
            28,
            1,
            63,
            2,
            31,
            53,
            56,
            44,
            24,
            51,
            19,
            7,
            5,
            34,
            27,
            16,
            46,
        ]
    )
    print("Unpurmute the bit vector:")
    print(bv3)

    print(
        "\nTry circular shifts to the left and to the right for the following bit vector:"
    )
    print(bv3)  # 0100000100100000011010000111010101101110011001110111001001111001
    print("\nCircular shift to the left by 7 positions:")
    bv3 << 7
    print(bv3)  # 1001000000110100001110101011011100110011101110010011110010100000

    print("\nCircular shift to the right by 7 positions:")
    bv3 >> 7
    print(bv3)  # 0100000100100000011010000111010101101110011001110111001001111001

    print("Test len() on the above bit vector:")
    print(len(bv3))  # 64

    print("\nTest forming a [5:22] slice of the above bit vector:")
    bv4 = bv3[5:22]
    print(bv4)  # 00100100000011010

    print("\nTest the iterator:")
    for bit in bv4:
        print(bit)  # 0 0 1 0 0 1 0 0 0 0 0 0 1 1 0 1 0

    print("\nDemonstrate padding a bit vector from left:")
    bv = BitVector(bitstring="101010")
    bv.pad_from_left(4)
    print(bv)  # 0000101010

    print("\nDemonstrate padding a bit vector from right:")
    bv.pad_from_right(4)
    print(bv)  # 00001010100000

    print("\nTest the syntax 'if bit_vector_1 in bit_vector_2' syntax:")
    try:
        bv1 = BitVector(bitstring="0011001100")
        bv2 = BitVector(bitstring="110011")
        if bv2 in bv1:
            print(f"{bv2} is in {bv1}")
        else:
            print(f"{bv2} is not in {bv1}")
    except ValueError as arg:
        print("Error Message: " + str(arg))

    print(
        "\nTest the size modifier when a bit vector is initialized with the intVal method:"
    )
    bv = BitVector(intVal=45, size=16)
    print(bv)  # 0000000000101101
    bv = BitVector(intVal=0, size=8)
    print(bv)  # 00000000
    bv = BitVector(intVal=1, size=8)
    print(bv)  # 00000001

    print("\nTesting slice assignment:")
    bv1 = BitVector(size=25)
    print("bv1= " + str(bv1))  # 0000000000000000000000000
    bv2 = BitVector(bitstring="1010001")
    print("bv2= " + str(bv2))  # 1010001
    bv1[6:9] = bv2[0:3]
    print("bv1= " + str(bv1))  # 0000001010000000000000000
    bv1[:5] = bv1[5:10]
    print("bv1= " + str(bv1))  # 0101001010000000000000000
    bv1[20:] = bv1[5:10]
    print("bv1= " + str(bv1))  # 0101001010000000000001010
    bv1[:] = bv1[:]
    print("bv1= " + str(bv1))  # 0101001010000000000001010
    bv3 = bv1[:]
    print("bv3= " + str(bv3))  # 0101001010000000000001010

    print("\nTesting reset function:")
    bv1.reset(1)
    print("bv1= " + str(bv1))  # 1111111111111111111111111
    print(bv1[3:9].reset(0))  # 000000
    print(bv1[:].reset(0))  # 0000000000000000000000000

    print("\nTesting count_bit():")
    bv = BitVector(intVal=45, size=16)
    y = bv.count_bits()
    print(y)  # 4
    bv = BitVector(bitstring="100111")
    print(bv.count_bits())  # 4
    bv = BitVector(bitstring="00111000")
    print(bv.count_bits())  # 3
    bv = BitVector(bitstring="001")
    print(bv.count_bits())  # 1
    bv = BitVector(bitstring="00000000000000")
    print(bv.count_bits())  # 0

    print("\nTest set_value idea:")
    bv = BitVector(intVal=7, size=16)
    print(bv)  # 0000000000000111
    bv.set_value(intVal=45)
    print(bv)  # 101101

    print("\nTesting count_bits_sparse():")
    bv = BitVector(size=2000000)
    bv[345234] = 1
    bv[233] = 1
    bv[243] = 1
    bv[18] = 1
    bv[785] = 1
    print("The number of bits set: " + str(bv.count_bits_sparse()))  # 5

    print("\nTesting Jaccard similarity and distance and Hamming distance:")
    bv1 = BitVector(bitstring="11111111")
    bv2 = BitVector(bitstring="00101011")
    print("Jaccard similarity: " + str(bv1.jaccard_similarity(bv2)))  # 0.5
    print("Jaccard distance: " + str(bv1.jaccard_distance(bv2)))  # 0.5
    print("Hamming distance: " + str(bv1.hamming_distance(bv2)))  # 4

    print("\nTesting next_set_bit():")
    bv = BitVector(bitstring="00000000000001")
    print(bv.next_set_bit(5))  # 13
    bv = BitVector(bitstring="000000000000001")
    print(bv.next_set_bit(5))  # 14
    bv = BitVector(bitstring="0000000000000001")
    print(bv.next_set_bit(5))  # 15
    bv = BitVector(bitstring="00000000000000001")
    print(bv.next_set_bit(5))  # 16

    print("\nTesting rank_of_bit_set_at_index():")
    bv = BitVector(bitstring="01010101011100")
    print(bv.rank_of_bit_set_at_index(10))  # 6

    print("\nTesting is_power_of_2():")
    bv = BitVector(bitstring="10000000001110")
    print("int value: " + str(int(bv)))  # 826
    print(bv.is_power_of_2())  # False
    print("\nTesting is_power_of_2_sparse():")
    print(bv.is_power_of_2_sparse())  # False

    print("\nTesting reverse():")
    bv = BitVector(bitstring="0001100000000000001")
    print("original bv: " + str(bv))  # 0001100000000000001
    print("reversed bv: " + str(bv.reverse()))  # 1000000000000011000

    print("\nTesting Greatest Common Divisor (gcd):")
    bv1 = BitVector(bitstring="01100110")
    print("first arg bv: " + str(bv1) + " of int value: " + str(int(bv1)))  # 102
    bv2 = BitVector(bitstring="011010")
    print("second arg bv: " + str(bv2) + " of int value: " + str(int(bv2)))  # 26
    bv = bv1.gcd(bv2)
    print("gcd bitvec is: " + str(bv) + " of int value: " + str(int(bv)))  # 2

    print("\nTesting multiplicative_inverse:")
    bv_modulus = BitVector(intVal=32)
    print(
        "modulus is bitvec: "
        + str(bv_modulus)
        + " of int value: "
        + str(int(bv_modulus))
    )
    bv = BitVector(intVal=17)
    print("bv: " + str(bv) + " of int value: " + str(int(bv)))
    result = bv.multiplicative_inverse(bv_modulus)
    if result is not None:
        print("MI bitvec is: " + str(result) + " of int value: " + str(int(result)))
    else:
        print("No multiplicative inverse in this case")
        # 17
    print("\nTest multiplication in GF(2):")
    a = BitVector(bitstring="0110001")
    b = BitVector(bitstring="0110")
    c = a.gf_multiply(b)
    print("Product of a=" + str(a) + " b=" + str(b) + " is " + str(c))
    # 00010100110

    print("\nTest division in GF(2^n):")
    mod = BitVector(bitstring="100011011")  # AES modulus
    n = 8
    a = BitVector(bitstring="11100010110001")
    quotient, remainder = a.gf_divide(mod, n)
    print(
        "Dividing a="
        + str(a)
        + " by mod="
        + str(mod)
        + " in GF(2^8) returns the quotient "
        + str(quotient)
        + " and the remainder "
        + str(remainder)
    )
    # 10001111

    print("\nTest modular multiplication in GF(2^n):")
    modulus = BitVector(bitstring="100011011")  # AES modulus
    n = 8
    a = BitVector(bitstring="0110001")
    b = BitVector(bitstring="0110")
    c = a.gf_multiply_modular(b, modulus, n)
    print(
        "Modular product of a=" + str(a) + " b=" + str(b) + " in GF(2^8) is " + str(c)
    )
    # 10100110

    print(
        "\nTest multiplicative inverses in GF(2^3) with "
        + "modulus polynomial = x^3 + x + 1:"
    )
    print("Find multiplicative inverse of a single bit array")
    modulus = BitVector(bitstring="100011011")  # AES modulus
    n = 8
    a = BitVector(bitstring="00110011")
    mi = a.gf_MI(modulus, n)
    print("Multiplicative inverse of " + str(a) + " in GF(2^8) is " + str(mi))

    print(
        "\nIn the following three rows shown, the first row shows the "
        + "\nbinary code words, the second the multiplicative inverses,"
        + "\nand the third the product of a binary word with its"
        + "\nmultiplicative inverse:\n"
    )
    mod = BitVector(bitstring="1011")
    n = 3
    bitarrays = [BitVector(intVal=x, size=n) for x in range(1, 2**3)]
    mi_list = [x.gf_MI(mod, n) for x in bitarrays]
    mi_str_list = [str(x.gf_MI(mod, n)) for x in bitarrays]
    print("bit arrays in GF(2^3): " + str([str(x) for x in bitarrays]))
    print("multiplicati_inverses: " + str(mi_str_list))

    products = [
        str(bitarrays[i].gf_multiply_modular(mi_list[i], mod, n))
        for i in range(len(bitarrays))
    ]
    print("bit_array * multi_inv: " + str(products))

    # UNCOMMENT THE FOLLOWING LINES FOR
    # DISPLAYING ALL OF THE MULTIPLICATIVE
    # INVERSES IN GF(2^8) WITH THE AES MODULUS:

    #    print("\nMultiplicative inverses in GF(2^8) with "  + \
    #                      "modulus polynomial x^8 + x^4 + x^3 + x + 1:")
    #    print("\n(This may take a few seconds)\n")
    #    mod = BitVector(bitstring = '100011011')
    #    n = 8
    #    bitarrays = [BitVector(intVal=x, size=n) for x in range(1,2**8)]
    #    mi_list = [x.gf_MI(mod,n) for x in bitarrays]
    #    mi_str_list = [str(x.gf_MI(mod,n)) for x in bitarrays]
    #    print("\nMultiplicative Inverses:\n\n" + str(mi_str_list))
    #    products = [ str(bitarrays[i].gf_multiply_modular(mi_list[i], mod, n)) \
    #                        for i in range(len(bitarrays)) ]
    #    print("\nShown below is the product of each binary code word " +\
    #                     "in GF(2^3) and its multiplicative inverse:\n\n")
    #    print(products)

    print("\nExperimenting with runs():")
    bv = BitVector(bitlist=(1, 0, 0, 1))
    print("For bit vector: " + str(bv))
    print("       the runs are: " + str(bv.runs()))
    bv = BitVector(bitlist=(1, 0))
    print("For bit vector: " + str(bv))
    print("       the runs are: " + str(bv.runs()))
    bv = BitVector(bitlist=(0, 1))
    print("For bit vector: " + str(bv))
    print("       the runs are: " + str(bv.runs()))
    bv = BitVector(bitlist=(0, 0, 0, 1))
    print("For bit vector: " + str(bv))
    print("       the runs are: " + str(bv.runs()))
    bv = BitVector(bitlist=(0, 1, 1, 0))
    print("For bit vector: " + str(bv))
    print("       the runs are: " + str(bv.runs()))

    print("\nExperiments with chained invocations of circular shifts:")
    bv = BitVector(bitlist=(1, 1, 1, 0, 0, 1))
    print(bv)
    bv >> 1
    print(bv)
    bv >> 1 >> 1
    print(bv)
    bv = BitVector(bitlist=(1, 1, 1, 0, 0, 1))
    print(bv)
    bv << 1
    print(bv)
    bv << 1 << 1
    print(bv)

    print("\nExperiments with chained invocations of NON-circular shifts:")
    bv = BitVector(bitlist=(1, 1, 1, 0, 0, 1))
    print(bv)
    bv.shift_right(1)
    print(bv)
    bv.shift_right(1).shift_right(1)
    print(bv)
    bv = BitVector(bitlist=(1, 1, 1, 0, 0, 1))
    print(bv)
    bv.shift_left(1)
    print(bv)
    bv.shift_left(1).shift_left(1)
    print(bv)

    # UNCOMMENT THE FOLLOWING LINES TO TEST THE
    # PRIMALITY TESTING METHOD. IT SHOULD SHOW
    # THAT ALL OF THE FOLLOWING NUMBERS ARE PRIME:
    #    print("\nExperiments with primality testing. If a number is not prime, its primality " +
    #          "test output must be zero.  Otherwise, it should a number very close to 1.0.")
    #    primes = [179, 233, 283, 353, 419, 467, 547, 607, 661, 739, 811, 877, \
    #              947, 1019, 1087, 1153, 1229, 1297, 1381, 1453, 1523, 1597, \
    #              1663, 1741, 1823, 1901, 7001, 7109, 7211, 7307, 7417, 7507, \
    #              7573, 7649, 7727, 7841]
    #    for p in primes:
    #        bv = BitVector(intVal = p)
    #        check = bv.test_for_primality()
    #        print("The primality test for " + str(p) + ": " + str(check))

    print("\nGenerate 32-bit wide candidate for primality testing:")
    bv = BitVector(intVal=0)
    bv = bv.gen_rand_bits_for_prime(32)
    print(bv)
    check = bv.test_for_primality()
    print("The primality test for " + str(int(bv)) + ": " + str(check))
