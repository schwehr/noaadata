#!/usr/bin/env python

__version__ = '3.1.1'
__author__  = "Avinash Kak (kak@purdue.edu)"
__date__    = '2012-June-9'
__url__     = 'https://engineering.purdue.edu/kak/dist/BitVector-3.1.1.html'
__copyright__ = "(C) 2012 Avinash Kak. Python Software Foundation."

__doc__ = '''See https://engineering.purdue.edu/kak/dist/ for docs.'''

import array
import operator

_hexdict = { '0' : '0000', '1' : '0001', '2' : '0010', '3' : '0011',
             '4' : '0100', '5' : '0101', '6' : '0110', '7' : '0111',
             '8' : '1000', '9' : '1001', 'a' : '1010', 'b' : '1011',
             'c' : '1100', 'd' : '1101', 'e' : '1110', 'f' : '1111' }

def _readblock( blocksize, bitvector ):                              #(R1)
    ''' 
    If this function can read all blocksize bits, it peeks ahead to see
    if there is anything more to be read in the file. It uses
    tell-read-seek mechanism for this in lines (R18) through (R21).  If
    there is nothing further to be read, it sets the more_to_read attribute
    of the bitvector object to False.  Obviously, this can only be done for
    seekable streams such as those connected with disk files.  According to
    Blair Houghton, a similar feature could presumably be implemented for
    socket streams by using recv() or recvfrom() if you set the flags
    argument to MSG_PEEK.
    '''
    import binascii
    global _hexdict                                                  #(R2)
    bitstring = ''                                                   #(R3)
    i = 0                                                            #(R4)
    while ( i < blocksize / 8 ):                                     #(R5)
        i += 1                                                       #(R6)
        byte = bitvector.FILEIN.read(1)                              #(R7)
        if byte == b'':                                              #(R8)
            if len(bitstring) < blocksize:                           #(R9)
                bitvector.more_to_read = False                      #(R10)
            return bitstring                                        #(R11)
        import sys                                                  #(R12)
        if sys.version_info[0] == 3:                                #(R13)
            hexvalue = '%02x' % byte[0]                             #(R14)
        else:                                                       #(R15)
            hexvalue = hex( ord( byte ) )                           #(R16)
            hexvalue = hexvalue[2:]                                 #(R17)
            if len( hexvalue ) == 1:                                #(R18)
                hexvalue = '0' + hexvalue                           #(R19)
        bitstring += _hexdict[ hexvalue[0] ]                        #(R20)
        bitstring += _hexdict[ hexvalue[1] ]                        #(R21)
    file_pos = bitvector.FILEIN.tell()                              #(R22)
    # peek at the next byte; moves file position only if a
    # byte is read
    next_byte = bitvector.FILEIN.read(1)                            #(R23)
    if next_byte:                                                   #(R24)
        # pretend we never read the byte                   
        bitvector.FILEIN.seek( file_pos )                           #(R25)
    else:                                                           #(R26)
        bitvector.more_to_read = False                              #(R27)
    return bitstring                                                #(R28)


#--------------------  BitVector Class Definition   ----------------------

class BitVector( object ):                                           #(A1)

    def __init__( self, *args, **kwargs ):                           #(A2)
        if args:                                                     #(A3)
               raise ValueError(                                     #(A4)
                      '''BitVector constructor can only be called with
                         keyword arguments for the following keywords:
                         filename, fp, size, intVal, bitlist, and
                         bitstring)''')                              
        allowed_keys = 'bitlist','bitstring','filename','fp','intVal','size'
                                                                     #(A5)
        keywords_used = kwargs.keys()                                #(A6)
        for keyword in keywords_used:                                #(A7)
            if keyword not in allowed_keys:                          #(A8)
                raise ValueError("Wrong keyword used --- check spelling")
                                                                     #(A9)
        filename = fp = intVal = size = bitlist = bitstring = None  #(A10)

        if 'filename' in kwargs  : filename=kwargs.pop('filename')  #(A11)
        if 'fp' in kwargs        : fp = kwargs.pop('fp')            #(A12)
        if 'size' in kwargs      : size = kwargs.pop('size')        #(A13)
        if 'intVal' in kwargs    : intVal = kwargs.pop('intVal')    #(A14)
        if 'bitlist' in kwargs   : bitlist = kwargs.pop('bitlist')  #(A15)
        if 'bitstring' in kwargs : bitstring = kwargs.pop('bitstring')  
                                                                    #(A16)
        self.filename = None                                        #(A17)
        self.size = 0                                               #(A18)
        self.FILEIN = None                                          #(A19)
        self.FILEOUT = None                                         #(A20)
        
        if filename:                                                #(A21)
            if fp or size or intVal or bitlist or bitstring:        #(A22)
                raise ValueError(                                   #(A23)
                  '''When filename is specified, you cannot
                     give values to any other constructor args''')
            self.filename = filename                                #(A24)
            self.FILEIN = open( filename, 'rb' )                    #(A25)
            self.more_to_read = True                                #(A26)
            return                                                  #(A27)
        elif fp:                                                    #(A28)
            if filename or size or intVal or bitlist or bitstring:  #(A29)
                raise ValueError(                                   #(A30)
                  '''When fileobject is specified, you cannot      
                     give values to any other constructor args''')
            bits = self.read_bits_from_fileobject( fp )             #(A31)
            bitlist =  list(map( int, bits ))                       #(A32)
            self.size = len( bitlist )                              #(A33)
        elif intVal or intVal == 0:                                 #(A34)
            if filename or fp or bitlist or bitstring:              #(A35)
                raise ValueError(                                   #(A36)
                  '''When intVal is specified, you can only give
                     a value to the 'size' constructor arg''')
            if intVal == 0:                                         #(A37)
                bitlist = [0]                                       #(A38)
                if size is None:                                    #(A39)
                    self.size = 1                                   #(A40)
                elif size == 0:                                     #(A41)
                    raise ValueError(                               #(A42)
                      '''The value specified for size must be at least
                         as large as for the smallest bit vector
                         possible for intVal''')                   
                else:                                               #(A43)
                    if size < len(bitlist):                         #(A44)
                        raise ValueError(                           #(A45)
                          '''The value specified for size must be at least
                             as large as for the smallest bit vector
                             possible for intVal''')
                    n = size - len(bitlist)                         #(A46)
                    bitlist = [0]*n + bitlist                       #(A47)
                    self.size = len( bitlist )                      #(A48)
            else:                                                   #(A49)
                hexVal = hex( intVal ).lower().rstrip('l')          #(A50)
                hexVal = hexVal[2:]                                 #(A51)
                if len( hexVal ) == 1:                              #(A52)
                    hexVal = '0' + hexVal                           #(A53)
                bitlist = ''.join(map(lambda x: _hexdict[x],hexVal))#(A54)
                bitlist =  list(map( int, bitlist ))                #(A55)
                i = 0                                               #(A56)
                while ( i < len( bitlist ) ):                       #(A57)
                    if bitlist[i] == 1: break                       #(A58)
                    i += 1                                          #(A59)
                del bitlist[0:i]                                    #(A60)
                if size is None:                                    #(A61)
                    self.size = len( bitlist )                      #(A62)
                elif size == 0:                                     #(A63)
                    if size < len(bitlist):                         #(A64)
                        raise ValueError(                           #(A65)
                          '''The value specified for size must be at least
                             as large as for the smallest bit vector
                             possible for intVal''')
                else:                                               #(A66)
                    if size < len(bitlist):                         #(A67)
                        raise ValueError(                           #(A68)
                          '''The value specified for size must be at least
                             as large as for the smallest bit vector
                             possible for intVal''')
                    n = size - len(bitlist)                         #(A69)
                    bitlist = [0]*n + bitlist                       #(A70)
                    self.size = len( bitlist )                      #(A71)
        elif size is not None and size >= 0:                        #(A72)
            if filename or fp or intVal or bitlist or bitstring:    #(A73)
                raise ValueError(                                   #(A74)
                  '''When size is specified (without an intVal), you 
                     cannot give values to any other constructor args''')
            self.size = size                                        #(A75)
            two_byte_ints_needed = (size + 15) // 16                #(A76)
            self.vector = array.array('H', [0]*two_byte_ints_needed)#(A77)
            return                                                  #(A78)
        elif bitstring or bitstring == '':                          #(A79)
            if filename or fp or size or intVal or bitlist:         #(A80)
                raise ValueError(                                   #(A81)
                  '''When a bitstring is specified, you cannot
                     give values to any other constructor args''')
            bitlist =  list(map( int, list(bitstring) ))            #(A82)
            self.size = len( bitlist )                              #(A83)
        elif bitlist:                                               #(A84)
            if filename or fp or size or intVal or bitstring:       #(A85)
                raise ValueError(                                   #(A86)
                  '''When bits are specified, you cannot give values
                     to any other constructor args''')
            self.size = len( bitlist )                              #(A87)
        else:                                                       #(A88)
            raise ValueError("wrong arg(s) for constructor")        #(A89) 
        two_byte_ints_needed = (len(bitlist) + 15) // 16            #(A90)
        self.vector = array.array( 'H', [0]*two_byte_ints_needed )  #(A91)
        list( map( self._setbit, range(len(bitlist)), bitlist) )    #(A92)

    def _setbit( self, posn, val ):                                  #(B1)
        'Set the bit at the designated position to the value shown'
        if val not in (0, 1):                                        #(B2)
            raise ValueError( "incorrect value for a bit" )          #(B3)
        if isinstance( posn, (tuple) ):                              #(B4)
            posn = posn[0]                                           #(B5)
        if  posn >= self.size or posn < -self.size:                  #(B6)
            raise ValueError( "index range error" )                  #(B7)   
        if posn < 0: posn = self.size + posn                         #(B8)
        block_index = posn // 16                                     #(B9)
        shift = posn & 15                                           #(B10)
        cv = self.vector[block_index]                               #(B11)
        if ( cv >> shift ) & 1 != val:                              #(B12)
            self.vector[block_index] = cv ^ (1 << shift)            #(B13)

    def _getbit( self, pos ):                                       #(C1)
        'Get the bit from the designated position'
        if not isinstance( pos, slice ):                            #(C2)
            if  pos >= self.size or pos < -self.size:               #(C3)
                raise ValueError( "index range error" )             #(C4)
            if pos < 0: pos = self.size + pos                       #(C5)
            return ( self.vector[pos//16] >> (pos&15) ) & 1         #(C6)
        else:                                                       #(C7)
            bitstring = ''                                          #(C8)
            if pos.start is None:                                   #(C9)
                start = 0                                          #(C10)
            else:                                                  #(C11)
                start = pos.start                                  #(C12)
            if pos.stop is None:                                   #(C13)
                stop = self.size                                   #(C14)
            else:                                                  #(C15)
                stop = pos.stop                                    #(C16)
            for i in range( start, stop ):                         #(C17)
                bitstring += str(self[i])                          #(C18)
            return BitVector( bitstring  = bitstring )             #(C19)

    def __xor__(self, other):                                       #(E1)
        '''
        Take a bitwise 'XOR' of the bit vector on which the method is
        invoked with the argument bit vector.  Return the result as a new
        bit vector.  If the two bit vectors are not of the same size, pad
        the shorter one with zeros from the left.
        '''
        if self.size < other.size:                                   #(E2)
            bv1 = self._resize_pad_from_left(other.size - self.size) #(E3)
            bv2 = other                                              #(E4)
        elif self.size > other.size:                                 #(E5)
            bv1 = self                                               #(E6)
            bv2 = other._resize_pad_from_left(self.size - other.size)#(E7)
        else:                                                        #(E8)
            bv1 = self                                               #(E9)
            bv2 = other                                             #(E10)
        res = BitVector( size = bv1.size )                          #(E11)
        lpb = map(operator.__xor__, bv1.vector, bv2.vector)         #(E12) 
        res.vector = array.array( 'H', lpb )                        #(E13)
        return res                                                  #(E14)

    def __and__(self, other):                                        #(F1)
        '''
        Take a bitwise 'AND' of the bit vector on which the method is
        invoked with the argument bit vector.  Return the result as a new
        bit vector.  If the two bit vectors are not of the same size, pad
        the shorter one with zeros from the left.
        '''      
        if self.size < other.size:                                   #(F2)
            bv1 = self._resize_pad_from_left(other.size - self.size) #(F3)
            bv2 = other                                              #(F4)
        elif self.size > other.size:                                 #(F5)
            bv1 = self                                               #(F6)
            bv2 = other._resize_pad_from_left(self.size - other.size)#(F7)
        else:                                                        #(F8)
            bv1 = self                                               #(F9)
            bv2 = other                                             #(F10)
        res = BitVector( size = bv1.size )                          #(F11)
        lpb = map(operator.__and__, bv1.vector, bv2.vector)         #(F12) 
        res.vector = array.array( 'H', lpb )                        #(F13)
        return res                                                  #(F14)

    def __or__(self, other):                                         #(G1)
        '''
        Take a bitwise 'OR' of the bit vector on which the method is
        invoked with the argument bit vector.  Return the result as a new
        bit vector.  If the two bit vectors are not of the same size, pad
        the shorter one with zero's from the left.
        '''
        if self.size < other.size:                                   #(G2)
            bv1 = self._resize_pad_from_left(other.size - self.size) #(G3)
            bv2 = other                                              #(G4)
        elif self.size > other.size:                                 #(G5)
            bv1 = self                                               #(G6)
            bv2 = other._resize_pad_from_left(self.size - other.size)#(G7)
        else:                                                        #(G8)
            bv1 = self                                               #(G9)
            bv2 = other                                             #(G10)
        res = BitVector( size = bv1.size )                          #(G11)
        lpb = map(operator.__or__, bv1.vector, bv2.vector)          #(G12) 
        res.vector = array.array( 'H', lpb )                        #(G13)
        return res                                                  #(G14)

    def __invert__(self):                                            #(H1)
        '''
        Invert the bits in the bit vector on which the method is invoked
        and return the result as a new bit vector.
        '''
        res = BitVector( size = self.size )                          #(H2)
        lpb = list(map( operator.__inv__, self.vector ))             #(H3) 
        res.vector = array.array( 'H' )                              #(H3)
        for i in range(len(lpb)):                                    #(H4)
            res.vector.append( lpb[i] & 0x0000FFFF )                 #(H5)
        return res                                                   #(H6)

    def __add__(self, other):                                        #(J1)
        '''
        Concatenate the argument bit vector with the bit vector on which
        the method is invoked.  Return the concatenated bit vector as a new
        BitVector object.
        '''
        i = 0                                                        #(J2)
        outlist = []                                                 #(J3)
        while ( i < self.size ):                                     #(J4)
            outlist.append( self[i] )                                #(J5)
            i += 1                                                   #(J6)
        i = 0                                                        #(J7)
        while ( i < other.size ):                                    #(J8)
            outlist.append( other[i] )                               #(J9)
            i += 1                                                  #(J10)
        return BitVector( bitlist = outlist )                       #(J11)

    def _getsize(self):                                              #(K1)
        'Return the number of bits in a bit vector.'
        return self.size                                             #(K2)

    def read_bits_from_file(self, blocksize):                        #(L1)
        '''
        Read blocksize bits from a disk file and return a BitVector object
        containing the bits.  If the file contains fewer bits than
        blocksize, construct the BitVector object from however many bits
        there are in the file.  If the file contains zero bits, return a
        BitVector object of size attribute set to 0.
        '''
        error_str = '''You need to first construct a BitVector
        object with a filename as  argument'''                       #(L2)
        if not self.filename:                                        #(L3)
            raise SyntaxError( error_str )                           #(L4)
        if blocksize % 8 != 0:                                       #(L5)
            raise ValueError( "block size must be a multiple of 8" ) #(L6)
        bitstr = _readblock( blocksize, self )                       #(L7)
        if len( bitstr ) == 0:                                       #(L8)
            return BitVector( size = 0 )                             #(L9)
        else:                                                       #(L10)
            return BitVector( bitstring = bitstr )                  #(L11)

    def read_bits_from_fileobject( self, fp ):                       #(M1)
        '''
        This function is meant to read a bit string from a file like
        object.
        '''
        bitlist = []                                                 #(M2)
        while 1:                                                     #(M3)
            bit = fp.read()                                          #(M4)
            if bit == '': return bitlist                             #(M5)
            bitlist += bit                                           #(M6)

    def write_bits_to_fileobject( self, fp ):                        #(N1)
        '''
        This function is meant to write a bit vector directly to a file
        like object.  Note that whereas 'write_to_file' method creates a
        memory footprint that corresponds exactly to the bit vector, the
        'write_bits_to_fileobject' actually writes out the 1's and 0's as
        individual items to the file object.  That makes this method
        convenient for creating a string representation of a bit vector,
        especially if you use the StringIO class, as shown in the test
        code.
        '''
        for bit_index in range(self.size):                           #(N2)
            import sys                                               #(N3)
            # For Python 3.x:
            if sys.version_info[0] == 3:                             #(N4)
                if self[bit_index] == 0:                             #(N5)
                    fp.write( str('0') )                             #(N6)
                else:                                                #(N7)
                    fp.write( str('1') )                             #(N8)
            # For Python 2.x:
            else:                                                    #(N9)
                if self[bit_index] == 0:                            #(N10)
                    fp.write( unicode('0') )                        #(N11)
                else:                                               #(N12)
                    fp.write( unicode('1') )                        #(N13)

    def divide_into_two(self):                                       #(P1)
        '''
        Divides an even-sized bit vector into two and returns the two
        halves as a list of two bit vectors.
        '''
        if self.size % 2 != 0:                                       #(P2)
            raise ValueError( "must have even num bits" )            #(P3)
        i = 0                                                        #(P4)
        outlist1 = []                                                #(P5)
        while ( i < self.size /2 ):                                  #(P6)
            outlist1.append( self[i] )                               #(P7)
            i += 1                                                   #(P8)
        outlist2 = []                                                #(P9)
        while ( i < self.size ):                                    #(P10)
            outlist2.append( self[i] )                              #(P11)
            i += 1                                                  #(P12)
        return [ BitVector( bitlist = outlist1 ),
                 BitVector( bitlist = outlist2 ) ]                  #(P13)

    def permute(self, permute_list):                                 #(Q1)
        '''
        Permute a bit vector according to the indices shown in the second
        argument list.  Return the permuted bit vector as a new bit vector.
        '''
        if max(permute_list) > self.size -1:                         #(Q2)
            raise ValueError( "Bad permutation index" )              #(Q3)
        outlist = []                                                 #(Q4)
        i = 0                                                        #(Q5)
        while ( i < len( permute_list ) ):                           #(Q6)
            outlist.append( self[ permute_list[i] ] )                #(Q7)
            i += 1                                                   #(Q8)
        return BitVector( bitlist = outlist )                        #(Q9)

    def unpermute(self, permute_list):                               #(S1)
        '''
        Unpermute the bit vector according to the permutation list supplied
        as the second argument.  If you first permute a bit vector by using
        permute() and then unpermute() it using the same permutation list,
        you will get back the original bit vector.
        '''
        if max(permute_list) > self.size -1:                         #(S2)
            raise ValueError( "Bad permutation index" )              #(S3)
        if self.size != len( permute_list ):                         #(S4)
            raise ValueError( "Bad size for permute list" )          #(S5)
        out_bv = BitVector( size = self.size )                       #(S6)
        i = 0                                                        #(S7)
        while ( i < len(permute_list) ):                             #(S8)
            out_bv[ permute_list[i] ] = self[i]                      #(S9)
            i += 1                                                  #(S10)
        return out_bv                                               #(S11)

    def write_to_file(self, file_out):                               #(T1)
        '''
        Write the bitvector to the file object file_out.  (A file object is
        returned by a call to open()). Since all file I/O is byte oriented,
        the bitvector must be multiple of 8 bits. Each byte treated as MSB
        first (0th index).
        '''
        err_str = '''Only a bit vector whose length is a multiple of 8 can
            be written to a file.  Use the padding functions to satisfy
            this constraint.'''                                      #(T2)
        if not self.FILEOUT:                                         #(T3)
            self.FILEOUT = file_out                                  #(T4)
        if self.size % 8:                                            #(T5)
            raise ValueError( err_str )                              #(T6)
        import sys                                                   #(T7)
        for byte in range( int(self.size/8) ):                       #(T8)
            value = 0                                                #(T9)
            for bit in range(8):                                    #(T10)
                value += (self._getbit( byte*8+(7 - bit) ) << bit ) #(T11)
            if sys.version_info[0] == 3:                            #(T12)
                file_out.write( bytes(chr(value), 'utf-8') )        #(T13)
            else:                                                   #(T14)
                file_out.write( chr(value) )                        #(T15)

    def close_file_object(self):                                     #(U1)
        '''
        For closing a file object that was used for reading the bits into
        one or more BitVector objects.
        '''
        if not self.FILEIN:                                          #(U2)
            raise SyntaxError( "No associated open file" )           #(U3)
        self.FILEIN.close()                                          #(U4)

    def intValue(self):                                              #(V1)
        'Return the integer value of a bitvector'
        intVal = 0                                                   #(V2)
        for i in range(self.size):                                   #(V3)
            intVal += self[i] * (2 ** (self.size - i - 1))           #(V4)
        return intVal                                                #(V5)
            
    def __lshift__( self, n ):                                       #(W1)
        'For an in-place left circular shift by n bit positions'
        if self.size == 0:                                           #(W2)
            raise ValueError('''Circular shift of an empty vector
                                makes no sense''')                   #(W3)
        if n < 0:                                                    #(W4)
            return self >> abs(n)                                    #(W5)
        for i in range(n):                                           #(W6)
            self.circular_rotate_left_by_one()                       #(W7)
        return self                                                  #(W8)
    def __rshift__( self, n ):                                       #(W9)
        'For an in-place right circular shift by n bit positions.'
        if self.size == 0:                                          #(W10)
            raise ValueError('''Circular shift of an empty vector
                                makes no sense''')                  #(W11)
        if n < 0:                                                   #(W12)
            return self << abs(n)                                   #(W13)
        for i in range(n):                                          #(W14)
            self.circular_rotate_right_by_one()                     #(W15)
        return self                                                 #(W16)

    def circular_rotate_left_by_one(self):                           #(X1)
        'For a one-bit in-place left circular shift'
        size = len(self.vector)                                      #(X2)
        bitstring_leftmost_bit = self.vector[0] & 1                  #(X3)
        left_most_bits =                 \
                list(map(operator.__and__, self.vector, [1]*size))   #(X4)
        left_most_bits.append(left_most_bits[0])                     #(X5)
        del(left_most_bits[0])                                       #(X6)
        self.vector = list(map(operator.__rshift__, \
                                           self.vector, [1]*size))   #(X7)
        self.vector = list(map( operator.__or__, self.vector, \
           list( map(operator.__lshift__, left_most_bits, [15]*size) )))   
                                                                     #(X8)
        self._setbit(self.size -1, bitstring_leftmost_bit)           #(X9)

    def circular_rotate_right_by_one(self):                          #(Y1)
        'For a one-bit in-place right circular shift'
        size = len(self.vector)                                      #(Y2)
        bitstring_rightmost_bit = self[self.size - 1]                #(Y3)
        right_most_bits = list(map( operator.__and__,
                               self.vector, [0x8000]*size ))         #(Y4)
        self.vector = \
         list(map( operator.__and__, self.vector, [~0x8000]*size ))  #(Y5)
        right_most_bits.insert(0, bitstring_rightmost_bit)           #(Y6)
        right_most_bits.pop()                                        #(Y7)
        self.vector = \
              list(map(operator.__lshift__, self.vector, [1]*size))  #(Y8)
        self.vector = list(map( operator.__or__, self.vector, \
           list(map(operator.__rshift__, right_most_bits, [15]*size))))  
                                                                     #(Y9)
        self._setbit(0, bitstring_rightmost_bit)                    #(Y10)

    def circular_rot_left(self):                                     #(Z1)
        '''
        This is merely another implementation of the method
        circular_rotate_left_by_one() shown above.  This one does NOT use
        map functions.  This method carries out a one-bit left circular
        shift of a bit vector.
        '''
        max_index = (self.size -1)  // 16                            #(Z2)
        left_most_bit = self.vector[0] & 1                           #(Z3)
        self.vector[0] = self.vector[0] >> 1                         #(Z4)
        for i in range(1, max_index + 1):                            #(Z5)
            left_bit = self.vector[i] & 1                            #(Z6)
            self.vector[i] = self.vector[i] >> 1                     #(Z7)
            self.vector[i-1] |= left_bit << 15                       #(Z8)
        self._setbit(self.size -1, left_most_bit)                    #(Z9)

    def circular_rot_right(self):                                    #(a1)
        '''
        This is merely another implementation of the method
        circular_rotate_right_by_one() shown above.  This one does NOT use
        map functions.  This method does a one-bit right circular shift of
        a bit vector.
        '''
        max_index = (self.size -1)  // 16                            #(a2)
        right_most_bit = self[self.size - 1]                         #(a3)
        self.vector[max_index] &= ~0x8000                            #(a4)
        self.vector[max_index] = self.vector[max_index] << 1         #(a5)
        for i in range(max_index-1, -1, -1):                         #(a6)
            right_bit = self.vector[i] & 0x8000                      #(a7)
            self.vector[i] &= ~0x8000                                #(a8)
            self.vector[i] = self.vector[i] << 1                     #(a9)
            self.vector[i+1] |= right_bit >> 15                     #(a10)
        self._setbit(0, right_most_bit)                             #(a11)

    def shift_left_by_one(self):                                     #(b1)
        '''
        For a one-bit in-place left non-circular shift.  Note that
        bitvector size does not change.  The leftmost bit that moves
        past the first element of the bitvector is discarded and 
        rightmost bit of the returned vector is set to zero.
        '''
        size = len(self.vector)                                      #(b2)
        left_most_bits = \
                list(map(operator.__and__, self.vector, [1]*size))   #(b3)
        left_most_bits.append(left_most_bits[0])                     #(b4)
        del(left_most_bits[0])                                       #(b5)
        self.vector = \
              list(map(operator.__rshift__, self.vector, [1]*size))  #(b6)
        self.vector = list(map( operator.__or__, self.vector, \
          list(map(operator.__lshift__, left_most_bits, [15]*size))))#(b7)
        self._setbit(self.size -1, 0)                                #(b8)

    def shift_right_by_one(self):                                    #(c1)
        '''
        For a one-bit in-place right non-circular shift.  Note that
        bitvector size does not change.  The rightmost bit that moves
        past the last element of the bitvector is discarded and 
        leftmost bit of the returned vector is set to zero.
        '''
        size = len(self.vector)                                      #(c2)
        right_most_bits = list(map( operator.__and__,\
                               self.vector, [0x8000]*size ))         #(c3)
        self.vector = \
          list(map( operator.__and__, self.vector, [~0x8000]*size )) #(c4)
        right_most_bits.insert(0, 0)                                 #(c5)
        right_most_bits.pop()                                        #(c6)
        self.vector = \
            list(map(operator.__lshift__, self.vector, [1]*size))    #(c7)
        self.vector = list(map( operator.__or__, self.vector, \
          list(map(operator.__rshift__,right_most_bits, [15]*size))))#(c8)
        self._setbit(0, 0)                                           #(c9)


    def shift_left( self, n ):                                       #(d1)
        'For an in-place left non-circular shift by n bit positions'
        for i in range(n):                                           #(d2)
            self.shift_left_by_one()                                 #(d3)
        return self                                                  #(d4)
    def shift_right( self, n ):                                      #(d5)
        'For an in-place right non-circular shift by n bit positions.'
        for i in range(n):                                           #(d6)
            self.shift_right_by_one()                                #(d7)
        return self                                                  #(d8)

    # Allow array like subscripting for getting and setting:
    __getitem__ = _getbit                                            #(e1)

    def __setitem__(self, pos, item):                                #(e2)
        '''
        This is needed for both slice assignments and for index
        assignments.  It checks the types of pos and item to see if the
        call is for slice assignment.  For slice assignment, pos must be of
        type 'slice' and item of type BitVector.  For index assignment, the
        argument types are checked in the _setbit() method.
        '''      
        # The following section is for slice assignment:
        if isinstance( pos, slice ):                                 #(e3)
            if (not isinstance( item, BitVector )):                  #(e4)
                raise TypeError('For slice assignment, ' +
                       'the right hand side must be a BitVector')    #(e5)
            if (not pos.start and not pos.stop):                     #(e6)
                return item.deep_copy()                              #(e7)
            elif not pos.start:                                      #(e9)
                if (pos.stop != len(item)):                         #(e10)
                    raise ValueError('incompatible lengths for ' +
                                              'slice assignment')   #(e11)
                for i in range(pos.stop):                           #(e12)
                    self[i] = item[ i ]                             #(e13)
                return                                              #(e14)
            elif not pos.stop:                                      #(e15)
                if ((len(self) - pos.start) != len(item)):          #(e16)
                    raise ValueError('incompatible lengths for ' +
                                              'slice assignment')   #(e17)
                for i in range(len(item)-1):                        #(e18)
                    self[pos.start + i] = item[ i ]                 #(e19)
                return                                              #(e20)
            else:                                                   #(e21)
                if ( (pos.stop - pos.start) != len(item) ):         #(e22)
                    raise ValueError('incompatible lengths for ' +
                                              'slice assignment')   #(e23)
                for i in range( pos.start, pos.stop ):              #(e24)
                    self[i] = item[ i - pos.start ]                 #(e25)
                return                                              #(e26)
        # For index assignment use _setbit()
        self._setbit( pos, item )                                   #(e27)

    def __getslice__(self, i, j):                                    #(f1)
        'Fetch slices with [i:j], [:], etc.'
        if self.size == 0:                                           #(f2)
            return BitVector( bitstring = '' )                       #(f3)
        slicebits = []                                               #(f4)
        if j > self.size: j = self.size                              #(f5)
        for x in range(i,j):                                         #(f6)
            slicebits.append( self[x] )                              #(f7)
        return BitVector( bitlist = slicebits )                      #(f8)

    # Allow len() to work:
    __len__ = _getsize                                               #(g1)
    # Allow int() to work:
    __int__ = intValue                                               #(g2)

    def __iter__( self ):                                            #(g3)
        '''
        To allow iterations over a bit vector by supporting the 'for bit in
        bit_vector' syntax:
        '''
        return BitVectorIterator( self )                             #(g4)


    def __str__( self ):                                             #(h1)
        'To create a print representation'
        if self.size == 0:                                           #(h2)
            return ''                                                #(h3)
        return ''.join( map( str, self ) )                           #(h4)

    # Compare two bit vectors:
    def __eq__(self, other):                                         #(i1)
        if self.size != other.size:                                  #(i2)
            return False                                             #(i3)
        i = 0                                                        #(i4)
        while ( i < self.size ):                                     #(i5)
            if (self[i] != other[i]): return False                   #(i6)
            i += 1                                                   #(i7)
        return True                                                  #(i8)
    def __ne__(self, other):                                         #(i9)
        return not self == other                                    #(i10)
    def __lt__(self, other):                                        #(i11)
        return self.intValue() < other.intValue()                   #(i12)
    def __le__(self, other):                                        #(i13)
        return self.intValue() <= other.intValue()                  #(i14)
    def __gt__(self, other):                                        #(i15)
        return self.intValue() > other.intValue()                   #(i16)
    def __ge__(self, other):                                        #(i17)
        return self.intValue() >= other.intValue()                  #(i18)

    def _make_deep_copy( self ):                                     #(j1)
        'Make a deep copy of a bit vector'
        copy = str( self )                                           #(j2)
        return BitVector( bitstring = copy )                         #(j3)

    def _resize_pad_from_left( self, n ):                            #(j4)
        '''
        Resize a bit vector by padding with n 0's from the left. Return the
        result as a new bit vector.
        '''
        new_str = '0'*n + str( self )                                #(j5)
        return BitVector( bitstring = new_str )                      #(j6)

    def _resize_pad_from_right( self, n ):                           #(j7)
        '''
        Resize a bit vector by padding with n 0's from the right. Return
        the result as a new bit vector.
        '''
        new_str = str( self ) + '0'*n                                #(j8)
        return BitVector( bitstring = new_str )                      #(j9)

    def pad_from_left( self, n ):                                   #(j10)
        'Pad a bit vector with n zeros from the left'
        new_str = '0'*n + str( self )                               #(j11)
        bitlist =  list(map( int, list(new_str) ))                  #(j12)
        self.size = len( bitlist )                                  #(j13)
        two_byte_ints_needed = (len(bitlist) + 15) // 16            #(j14)
        self.vector = array.array( 'H', [0]*two_byte_ints_needed )  #(j15)
        list(map( self._setbit, enumerate(bitlist), bitlist))       #(j16)

    def pad_from_right( self, n ):                                  #(j17)
        'Pad a bit vector with n zeros from the right'
        new_str = str( self ) + '0'*n                               #(j18)
        bitlist =  list(map( int, list(new_str) ))                  #(j19)
        self.size = len( bitlist )                                  #(j20)
        two_byte_ints_needed = (len(bitlist) + 15) // 16            #(j21)
        self.vector = array.array( 'H', [0]*two_byte_ints_needed )  #(j22)
        list(map( self._setbit, enumerate(bitlist), bitlist))       #(j23)

    def __contains__( self, otherBitVec ):                           #(k1)
        '''
        This supports 'if x in y' and 'if x not in y' syntax for bit
        vectors.
        '''
        if self.size == 0:                                           #(k2)
              raise ValueError("First arg bitvec has no bits")       #(k3)
        elif self.size < otherBitVec.size:                           #(k4)
              raise ValueError("First arg bitvec too short")         #(k5)
        max_index = self.size - otherBitVec.size + 1                 #(k6)
        for i in range(max_index):                                   #(k7)
              if self[i:i+otherBitVec.size] == otherBitVec:          #(k8)
                    return True                                      #(k9)
        return False                                                #(k10)

    def reset( self, val ):                                          #(m1)
        '''
        Resets a previously created BitVector to either all zeros or all
        ones depending on the argument val.  Returns self to allow for
        syntax like
               bv = bv1[3:6].reset(1)
        or
               bv = bv1[:].reset(1)
        '''
        if val not in (0,1):                                         #(m2)
            raise ValueError( "Incorrect reset argument" )           #(m3)
        bitlist = [val for i in range( self.size )]                  #(m4)
        list(map( self._setbit, enumerate(bitlist), bitlist ))       #(m5)
        return self                                                  #(m6)

    def count_bits( self ):                                          #(n1)
        '''
        Return the number of bits set in a BitVector instance.
        '''
        from functools import reduce                                 #(n2)
        return reduce( lambda x, y: int(x)+int(y), self )            #(n3)


    def setValue(self, *args, **kwargs ):                            #(p1)
        '''
        Changes the bit pattern associated with a previously constructed
        BitVector instance.  The allowable modes for changing the internally
        stored bit pattern are the same as for the constructor.
        '''
        self.__init__( *args, **kwargs )                             #(p2)

    def count_bits_sparse( self ):                                   #(q1)
        '''
        For sparse bit vectors, this method, contributed by Rhiannon, will
        be much faster.  She estimates that if a bit vector with over 2
        millions bits has only five bits set, this will return the answer
        in 1/18 of the time taken by the count_bits() method.  Note
        however, that count_bits() may work much faster for dense-packed
        bit vectors.  Rhianon's implementation is based on an algorithm
        generally known as the Brian Kernighan's way, although its
        antecedents predate its mention by Kernighan and Ritchie.
        '''
        num = 0                                                      #(q2)
        for intval in self.vector:                                   #(q3)
            if intval == 0: continue                                 #(q4)
            c = 0; iv = intval                                       #(q5)
            while iv > 0:                                            #(q6)
                iv = iv & (iv -1)                                    #(q7)
                c = c + 1                                            #(q8)
            num = num + c                                            #(q9)
        return num                                                  #(q10)

    def jaccard_similarity( self, other ):                           #(r1)
        ''' 
        Computes the Jaccard similarity coefficient between two bit vectors
        '''
        assert self.size == other.size, 'vectors of unequal length'  #(r2)
        intersect = self & other                                     #(r3)
        union = self | other                                         #(r4)
        return ( intersect.count_bits_sparse()\
                  / float( union.count_bits_sparse() ) )             #(r5)
    def jaccard_distance( self, other ):                             #(r6)
        ''' 
        Computes the Jaccard distance between two bit vectors
        '''
        assert self.size == other.size, 'vectors of unequal length'  #(r7)
        return 1 - self.jaccard_similarity( other )                  #(r8)
    def hamming_distance( self, other ):                             #(r9)
        '''
        Computes the Hamming distance between two bit vectors
        '''
        assert self.size == other.size, 'vectors of unequal length' #(r10)
        diff = self ^ other                                         #(r11)
        return diff.count_bits_sparse()                             #(r12)


    def next_set_bit(self, from_index=0):                            #(s1)
        '''
        This method, contributed by Jason Allum, calculates the number of
        bit positions from the current position index to the next set bit.
        '''
        assert from_index >= 0, 'from_index must be nonnegative'     #(s2)
        i = from_index                                               #(s3)
        v = self.vector                                              #(s4)
        l = len(v)                                                   #(s5)
        o = i >> 4                                                   #(s6)
        m = 1 << (i & 0x0F)                                          #(s7)
        while o < l:                                                 #(s8)
            h = v[o]                                                 #(s9)
            if h:                                                   #(s10)
                while m != (1 << 0x10):                             #(s11)
                    if h & m: return i                              #(s12)
                    m <<= 1                                         #(s13)
                    i += 1                                          #(s14)
            else:                                                   #(s15)
                i += 0x10                                           #(s16)
            m = 1                                                   #(s17)
            o += 1                                                  #(s18)
        return -1                                                   #(s19)

    def rank_of_bit_set_at_index( self, position ):                  #(t1)
        '''
        For a bit that is set at the argument 'position', this method
        returns how many bits are set to the left of that bit.  For
        example, in the bit pattern 000101100100, a call to this method
        with position set to 9 will return 4.
        '''
        assert self[position] == 1, 'the arg bit not set'
        bv = self[0:position+1]                                      #(t2)
        return bv.count_bits()                                       #(t3)

    def isPowerOf2( self ):                                          #(t4)
        '''
        Determines whether the integer value of a bit vector is a power of
        2.
        '''
        if self.intValue() == 0: return False                        #(t5)
        bv = self & BitVector( intVal = self.intValue() - 1 )        #(t6)
        if bv.intValue() == 0: return True                           #(t7)
        return False                                                 #(t7)

    def isPowerOf2_sparse( self ):                                   #(t8)
        '''
        Faster version of isPowerOf2() for sparse bit vectors
        '''
        if self.count_bits_sparse() == 1: return True                #(t9)
        return False                                                #(t10)


    def reverse( self ):                                             #(u1)
        '''
        Returns a new bit vector by reversing the bits in the bit vector on
        which the method is invoked.
        '''
        reverseList = []                                             #(u2)
        i = 1                                                        #(u3)
        while ( i < self.size + 1 ):                                 #(u4)
            reverseList.append( self[ -i ] )                         #(u5)
            i += 1                                                   #(u6)
        return BitVector( bitlist = reverseList )                    #(u7)


    def gcd( self, other ):                                          #(v1)
        ''' 
        Using Euclid's Algorithm, returns the greatest common divisor of
        the integer value of the bit vector on which the method is invoked
        and the integer value of the argument bit vector.
        '''
        a = self.intValue(); b = other.intValue()                    #(v2)
        if a < b: a,b = b,a                                          #(v3)
        while b != 0:                                                #(v4)
            a, b = b, a % b                                          #(v5)
        return BitVector( intVal = a )                               #(v6)

    def multiplicative_inverse( self, modulus ):                     #(v7)
        '''
        Calculates the multiplicative inverse of a bit vector modulo the
        bit vector that is supplied as the argument. Code based on the
        Extended Euclid's Algorithm.
        '''
        MOD = mod = modulus.intValue(); num = self.intValue()        #(v8)
        x, x_old = 0, 1                                              #(v9)
        y, y_old = 1, 0                                             #(v10)
        while mod:                                                  #(v11)
            quotient = num // mod                                   #(v12)
            num, mod = mod, num % mod                               #(v13)
            x, x_old = x_old - x * quotient, x                      #(v14)
            y, y_old = y_old - y * quotient, y                      #(v15)
        if num != 1:                                                #(v16)
            return None                                             #(v17)
        else:                                                       #(v18)
            MI = (x_old + MOD) % MOD                                #(v19)
            return BitVector( intVal = MI )                         #(v20)


    def length(self):                                                #(w1)
        return self.size                                             #(w2)
    def deep_copy(self):                                             #(w3)
        return self._make_deep_copy()                                #(w4)


    def gf_multiply(self, b):                                        #(x1)
        '''
        In the set of polynomials defined over GF(2), multiplies
        the bitvector on which the method is invoked with the 
        bitvector b.  Returns the product bitvector.
        '''
        a = self.deep_copy()                                         #(x2)
        b_copy = b.deep_copy()                                       #(x3)
        a_highest_power = a.length() - a.next_set_bit(0) - 1         #(x4)
        b_highest_power = b.length() - b_copy.next_set_bit(0) - 1    #(x5)
        result = BitVector( size = a.length()+b_copy.length() )      #(x6)
        a.pad_from_left( result.length() - a.length() )              #(x7)
        b_copy.pad_from_left( result.length() - b_copy.length() )    #(x8)
        for i,bit in enumerate(b_copy):                              #(x9)
            if bit == 1:                                            #(x10)
                power = b_copy.length() - i - 1                     #(x11)
                a_copy = a.deep_copy()                              #(x12)
                a_copy.shift_left( power )                          #(x13)
                result ^=  a_copy                                   #(x14)
        return result                                               #(x15)


    def gf_divide(self, mod, n):                                    #(y1)
        '''
        Carries out modular division of a bitvector by the 
        modulus bitvector mod in GF(2^n) finite field.
        Returns both the quotient and the remainder.
        '''
        num = self                                                  #(y2)
        if mod.length() > n+1:                                      #(y3)
            raise ValueError("Modulus bit pattern too long")        #(y4)
        quotient = BitVector( intVal = 0, size = num.length() )     #(y5)
        remainder = num.deep_copy()                                 #(y6)
        i = 0                                                       #(y7)
        while 1:                                                    #(y8)
            i = i+1                                                 #(y9)
            if (i==num.length()): break                            #(y10)
            mod_highest_power = mod.length()-mod.next_set_bit(0)-1 #(y11)
            if remainder.next_set_bit(0) == -1:                    #(y12)
                remainder_highest_power = 0                        #(y13)
            else:                                                  #(y14)
                remainder_highest_power = remainder.length() \
                                  - remainder.next_set_bit(0) - 1  #(y15)
            if (remainder_highest_power < mod_highest_power) \
                  or int(remainder)==0:                            #(y16)
                break                                              #(y17)
            else:                                                  #(y18)
                exponent_shift = remainder_highest_power \
                                            - mod_highest_power    #(y19)
                quotient[quotient.length()-exponent_shift-1] = 1   #(y20)
                quotient_mod_product = mod.deep_copy();            #(y21)
                quotient_mod_product.pad_from_left(remainder.length() - \
                                              mod.length() )       #(y22)
                quotient_mod_product.shift_left(exponent_shift)    #(y23)
                remainder = remainder ^ quotient_mod_product       #(y24)
        if remainder.length() > n:                                 #(y25)
            remainder = remainder[remainder.length()-n:]           #(y26)
        return quotient, remainder                                 #(y27)


    def gf_multiply_modular(self, b, mod, n):                       #(z1)
        '''
        Multiplies a bitvector with the bitvector b in GF(2^n)
        finite field with the modulus bit pattern set to mod
        '''
        a = self                                                    #(z2)
        a_copy = a.deep_copy()                                      #(z3)
        b_copy = b.deep_copy()                                      #(z4)
        product = a_copy.gf_multiply(b_copy)                        #(z5)
        quotient, remainder = product.gf_divide(mod, n)             #(z6)
        return remainder                                            #(z7)

    def gf_MI(self, mod, n):                                       #(gf1)
        '''
        Returns the multiplicative inverse of a vector in the GF(2^n)
        finite field with the modulus polynomial set to mod
        '''
        num = self                                                  #(gf2)
        NUM = num.deep_copy(); MOD = mod.deep_copy()                #(gf3)
        x = BitVector( size=mod.length() )                          #(gf3)
        x_old = BitVector( intVal=1, size=mod.length() )            #(gf4)
        y = BitVector( intVal=1, size=mod.length() )                #(gf5)
        y_old = BitVector( size=mod.length() )                      #(gf6)
        while int(mod):                                             #(gf7)
            quotient, remainder = num.gf_divide(mod, n)             #(gf8)
            num, mod = mod, remainder                               #(gf9)
            x, x_old = x_old ^ quotient.gf_multiply(x), x          #(gf10)
            y, y_old = y_old ^ quotient.gf_multiply(y), y          #(gf11)
        if int(num) != 1:                                          #(gf12)
            return "NO MI. However, the GCD of ", str(NUM), " and ", \
                                 str(MOD), " is ", str(num)        #(gf13)
        else:                                                      #(gf14)
            z = x_old ^ MOD                                        #(gf15)
            quotient, remainder = z.gf_divide(MOD, n)              #(gf16)
            return remainder                                       #(gf17)

    def runs(self):                                                 #(ru1)
        '''
        Returns a list of the consecutive runs of 1's and 0's in
        the bit vector.  Each run is either a string of all 1's or
        a string of all 0's.
        '''
        if self.size == 0:                                          #(ru2)
            raise ValueError('''An empty vector has no runs''')     #(ru3)
        allruns = []                                                #(ru4)
        run = ''                                                    #(ru5)
        previous_bit = self[0]                                      #(ru6)
        if previous_bit == 0:                                       #(ru7)
            run = '0'                                               #(ru8)
        else:                                                       #(ru9)
            run = '1'                                              #(ru10)
        for bit in list(self)[1:]:                                 #(ru11)
            if bit == 0 and previous_bit == 0:                     #(ru12)
                run += '0'                                         #(ru13)
            elif bit == 1 and previous_bit == 0:                   #(ru14)
                allruns.append( run )                              #(ru15)
                run = '1'                                          #(ru16)
            elif bit == 0 and previous_bit == 1:                   #(ru17)
                allruns.append( run )                              #(ru18)
                run = '0'                                          #(ru19)
            else:                                                  #(ru20)
                run += '1'                                         #(ru21)
            previous_bit = bit                                     #(ru22)
        allruns.append( run )                                      #(ru23)
        return allruns                                             #(ru24)

    def test_for_primality(self):                                   #(pr1)
        ''' 
        Check if the integer value of the bitvector is a prime through the
        Miller-Rabin probabilistic test of primality.  If not found to be a
        composite, estimate the probability of the bitvector being a prime
        using this test.
        '''
        p = int(self)                                               #(pr2)
        probes = [2,3,5,7,11,13,17]                                 #(pr3)
        for a in probes:                                            #(pr4)
            if a == p: return 1                                     #(pr5)
        if any([p % a == 0 for a in probes]): return 0              #(pr6)
        k, q = 0, p-1                                               #(pr7)
        while not q&1:                                              #(pr8)
            q >>= 1                                                 #(pr9)
            k += 1                                                 #(pr10)
        for a in probes:                                           #(pr11)
            a_raised_to_q = pow(a, q, p)                           #(pr12)
            if a_raised_to_q == 1 or a_raised_to_q == p-1: continue#(pr13)
            a_raised_to_jq = a_raised_to_q                         #(pr14)
            primeflag = 0                                          #(pr15)
            for j in range(k-1):                                   #(pr16)
                a_raised_to_jq = pow(a_raised_to_jq, 2, p)         #(pr17)
                if a_raised_to_jq == p-1:                          #(pr18)
                    primeflag = 1                                  #(pr19)
                    break                                          #(pr20)
            if not primeflag: return 0                             #(pr21)
        probability_of_prime = 1 - 1.0/(4 ** len(probes))          #(pr22)
        return probability_of_prime                                #(pr23)

    def gen_rand_bits_for_prime(self, width):                      #(pr24)
        '''
        The bulk of the work here is done by calling random.getrandbits(
        width) which returns an integer whose binary code representation
        will not be larger than the argument 'width'.  However, when random
        numbers are generated as candidates for primes, you often want to
        make sure that the random number thus created spans the full width
        specified by 'width' and that the number is odd.  This we do by
        setting the two most significant bits and the least significant
        bit.  If you only want to set the most significant bit, comment out
        the statement in line (pr29).
        '''
        import random                                              #(pr25)
        candidate = random.getrandbits( width )                    #(pr26)
        candidate |= 1                                             #(pr27)
        candidate |= (1 << width-1)                                #(pr28)
        candidate |= (2 << width-3)                                #(pr29)
        return BitVector( intVal = candidate )                     #(pr30)


#-----------------------  BitVectorIterator Class -----------------------

class BitVectorIterator:                                            #(IT1)
    def __init__( self, bitvec ):                                   #(IT2)
        self.items = []                                             #(IT3)
        for i in range( bitvec.size ):                              #(IT4)
            self.items.append( bitvec._getbit(i) )                  #(IT5)
        self.index = -1                                             #(IT6)
    def __iter__( self ):                                           #(IT7)
        return self                                                 #(IT8)
    def next( self ):                                               #(IT9)
        self.index += 1                                            #(IT10)
        if self.index < len( self.items ):                         #(IT11)
            return self.items[ self.index ]                        #(IT12)
        else:                                                      #(IT13)
            raise StopIteration                                    #(IT14)
    __next__ = next                                                #(IT15)

#------------------------  End of Class Definition -----------------------

#------------------------     Test Code Removed    -----------------------

# Test code removed.  See https://engineering.purdue.edu/kak/dist/
