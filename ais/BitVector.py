#!/usr/bin/env python

__version__ = '1.3'
__author__  = "Avinash Kak (kak@purdue.edu)"
__date__    = '2006-Dec-26'
__url__     = 'http://RVL4.ecn.purdue.edu/~kak/dist/BitVector-1.3.html'
__copyright__ = "(C) 2006 Avinash Kak. GNU GPL 2."

__doc__ = '''

    BitVector.py

    Version: ''' + __version__ + '''
   
    Author: Avinash Kak (kak@purdue.edu)

    Date: ''' + __date__ + '''


    CHANGE LOG:

       Version 1.3:

           (a) One more constructor mode included: When initializing a
           new bit vector with an integer value, you can now also
           specify a size for the bit vector.  The constructor zero-pads
           the bit vector from the left with zeros. (b) The BitVector
           class now supports 'if x in y' syntax to test if the bit
           pattern 'x' is contained in the bit pattern 'y'. (c) Improved
           syntax to conform to well-established Python idioms. (d) What
           used to be a comment before the beginning of each method
           definition is now a docstring.

       Version 1.2:

           (a) One more constructor mode included: You can now construct
           a bit vector directly from a string of 1's and 0's.  (b) The
           class now constructs a shortest possible bit vector from an
           integer value.  So the bit vector for the integer value 0 is
           just one bit of value 0, and so on. (c) All the rich
           comparison operators are now overloaded. (d) The class now
           includes a new method 'intValue()' that returns the unsigned
           integer value of a bit vector.  This can also be done through
           '__int__'. (e) The package now includes a unittest based
           framework for testing out an installation.  This is in a
           separate directory called "TestBitVector".
       
       Version 1.1.1:

           The function that does block reads from a disk file now peeks
           ahead at the end of each block to see if there is anything
           remaining to be read in the file.  If nothing remains, the
           more_to_read attribute of the BitVector object is set to
           False.  This simplifies reading loops. This version also
           allows BitVectors of size 0 to be constructed


       Version 1.1:

           I have changed the API significantly to provide more ways for
           constructing a bit vector.  As a result, it is now necessary
           to supply a keyword argument to the constructor.
       


    INTRODUCTION:
   
       The BitVector class for a memory-efficient packed representation
       of bit arrays and for logical operations on such arrays.  The
       core idea used in this Python script for bin packing is based on
       an internet posting by Josiah Carlson to the Pyrex mailing list.

       Operations supported on bit vectors:

              __getitem__
              __setitem__
              __len__
              __iter__
              __contains__
              __getslice__
              __str__
              __int__
              __add__
              __eq__, __ne__, __lt__, __le__, __gt__, __ge__
              |            for bitwise or
              &            for bitwise and              
              ^            for bitwise xor
              ~            for bitwise inversion
              <<           for circular rotation to the left
              >>           for circular rotation to the right
              +            for concatenation
              intValue()   for returning the integer value 
              divide_into_two
              permute
              unpermute
              pad_from_left
              pad_from_right
              read_bits_from_file
              write_to_file
              read_bits_from_fileobject
              write_bits_to_fileobject




    CONSTRUCTING BIT VECTORS:


        You can construct a bit vector in six different ways.
   
        (1) You can construct a bit vector directly from either a tuple
            or a list of bits, as in

               bv =  BitVector( bitlist = [1,0,1,0,0,1,0,1,0,0,1,0,1,0,0,1] )   
 
        (2) You can construct a bit vector from an integer by

               bv =  BitVector( intVal = 56789 )

            The bits stored now will correspond to the binary
            representation of the integer.  The resulting bit vector is
            the shortest possible bit vector for the integer value
            supplied.  For example, when intVal is 0, the bit vector
            constructed will consist of just the bit 0.


        (3) When initializing a bit vector with an intVal as shown
            above, you can also specify a size for the bit vector:

               bv = BitVector( intVal = 0, size = 8 )

            will return the bit vector consisting of the bit pattern
            00000000.  The zero padding needed for meeting the size
            requirement is always on the left.  If the size supplied is
            smaller than what it takes to create the shortest possible
            bit vector for intVal, an exception is thrown.

                
        (4) You can create a zero-initialized bit vector of a given size
            by

               bv  = BitVector( size = 62 )

            This bit vector will hold exactly 62 bits, all initialized to
            the 0 bit value.

        (5) You can construct a bit vector from a disk file by a two-step
            procedure. First you construct an instance of bit vector by
   
               bv  =  BitVector( filename = 'somefile' )   

            This bit vector itself is incapable of holding the bits.  To
            now create bit vectors that actually hold the bits, you need
            to make the following sort of a call on the above variable
            bv:
 
               bv1 =  bv.read_bits_from_file( 64 )    

            bv1 will be a regular bit vector containing 64 bits from the
            disk file. If you want to re-read a file from the beginning
            for some reason, you must obviously first close the file
            object that was acquired with a call to the BitVector
            constructor with a filename argument.  This can be
            accomplished by

              bv.close_file_object()

        (6) You can construct a bit vector from a string of 1's and 0's
            by
 
               bv  =  BitVector( bitstring = '110011110000' )      
   
        (7) Yet another way to construct a bit vector is to read the bits
            directly from a file-like object, as in
  
               x = "111100001111"
               fileobj = StringIO.StringIO( x )
               bv = BitVector( fp = fileobj )


   
    OPERATIONS SUPPORTED BY THE BITVECTOR CLASS:
    
    DISPLAYING BIT VECTORS:


        1)  Since the BitVector class implements the __str__ method, a
            bit vector can be displayed on a terminal by

                  print bitvec

            Basically, you can always obtain the string representation
            of a bit vector by

                  str( bitvec )

            and integer value by

                  int( bitvec )



    ACCESSING AND SETTING INDIVIDUAL BITS AND SLICES:

   
        2)  Any single bit of a bit vector bv can be set to 1 or 0 by
 
                  bv[M] = 1_or_0
                  print bv[M]

            for accessing (and setting) the bit at the position that is
            indexed M.  You can retrieve the bit at position M by bv[M].

        3)  A slice of a bit vector obtained by

                  bv[i:j]

            is a bit vector constructed from the bits at index positions
            from i through j-1.

        4)  You can iterate over a bit vector, as illustrated by

                  for bit in bitvec:
                      print bit,   

            This is made possible by the override definition for the
            special __iter__() method.

        5)  Negative subscripts for array-like indexing are supported.
            Therefore,

                  bitvec[ -i ]

            is legal assuming that the index range is not violated.



    LOGICAL OPERATIONS ON BIT VECTORS:

   
        6) Given two bit vectors bv1 and bv2, you can perform bitwise
           logical operations on them by

                  result_bv  =  bv1 ^ bv2
                  result_bv  =  bv1 & bv2
                  result_bv  =  bv1 | bv2
                  result_bv  =  ~bv1



    COMPARING BIT VECTORS:

        7) Given two bit vectors bv1 and bv2, you can carry out the
           following comparisons that return Boolean values:

                  bv1 ==  bv2
                  bv1 !=  bv2
                  bv1 <   bv2
                  bv1 <=  bv2
                  bv1 >   bv2
                  bv1 >=  bv2

           The equalities and inequalities are determined by the integer
           values associated with the bit vectors.


   

    OTHER SUPPORTED OPERATIONS:

   
        8)  You can permute and un-permute bit vectors:

                  bv_permuted   =  bv.permute( permutation_list )

                  bv_unpermuted =  bv.unpermute( permutation_list )


        9)  Left and right circular rotations can be carried out by
 
                  bitvec  << N 

                  bitvec  >> N

            for circular rotations to the left and right by N bit
            positions.


       10)  A bit vector containing an even number of bits can be
            divided into two equal parts by

                  [left_half, right_half] = bitvec.divide_into_two()

             where left_half and right_half hold references to the two
             returned bit vectors.


       11)  You can find the integer value of a bit array by

                  bitvec.invValue()

            or by

                  int( bitvec )


       12)  You can convert a bit vector into its string representation
            by

                  str( bitvec )


       13)  Because __add__ is supplied, you can always join two
            bit vectors by

                  bitvec3  =  bitvec1  +  bitvec2

            bitvec3 is a new bit vector that contains all the
            bits of bitvec1 followed by all the bits of bitvec2.

             
       14)  You can write a bit vector directly to a file, as
            illustrated by the following example that reads one bit
            vector from a file and then writes it to another
            file

                  bv = BitVector( filename = 'input.txt' )
                  bv1 = bv.read_bits_from_file(64)        
                  print bv1           
                  FILEOUT = open( 'output.txt', 'w' )
                  bv1.write_to_file( FILEOUT )
                  FILEOUT.close()

             IMPORTANT:  The size of bit vector must be a multiple of
                         of 8 for this write function to work.  If this
                         condition is not met, the function throws an
                         exception.

       15)  You can also write a bit vector directly to a stream
            object, as illustrated by

                  fp_write = StringIO.StringIO()
                  bitvec.write_bits_to_fileobject( fp_write )
                  print fp_write.getvalue()         # 111100001111 
             

       16)  You can pad a bit vector from the left or from the
            right with a designated number of zeros

                  bitvec.pad_from_left( n )

                  bitvec.pad_from_right( n )

            In the first case, the new bit vector will be the same
            as the old bit vector except for the additional n zeros
            on the left.  The same thing happens in the second
            case except that now the additional n zeros will be on
            the right.

       17)  You can test if a bit vector x is contained in another bit
            vector y by using the syntax 'if x in y'.  This is made
            possible by the override definition for the special
            __contains__() method.



    HOW THE BIT VECTORS ARE STORED:

   
        The bits of a bit array are stored in 16-bit unsigned ints.
        After resolving the argument with which the constructor is
        called (which happens in lines (A2) through (A68) of the file
        BitVector.py), the very first thing that the constructor does is
        to figure out in line (A69) as to how many of those 2-byte ints
        it needs for the bits.  For example, if you wanted to store a
        64-bit array, the variable 'two_byte_ints_needed' in line (A69)
        would be set to 4. (This does not mean that the size of a bit
        vector must be a multiple of 16.  Any sized bit vectors can
        constructed using the required number of two-byte ints.) Line
        (A70) then creates an array of 2-byte ints and initializes it
        with the required number of zeros.  Lines (A71) then shifts the
        bits into the array of two-byte ints.

        As mentioned above, note that it is not necessary for the size
        of the vector to be a multiple of 16 even though we are using
        C's unsigned short as as a basic unit for storing the bit
        arrays.  The class BitVector keeps track of the actual number of
        bits in the bit vector through the "size" instance attribute.

        With regard to the code in lines (A2) through (A68) of the file
        BitVector.py, note that, except for one case, the constructor
        must be called with a single keyword argument, which determines
        how the bit vector will be constructed.  The single exception to
        this rule is for the keyword argument 'intVal' which can be used
        along with the 'size' keyword argument.  When 'intVal' is used
        with the 'size' option, the bit vector constructed for the
        integer is the shortest possible bit vector.  On the other hand,
        when 'size' is also specified, the bit vector is padded with
        zeroes from the left so that it has the specified size.

        Lines (A14) through (A20) are for the following sort of a call

               bv = BitVector( filename = 'myfilename' )

        This call returns a bit vector on which you must subsequently
        invoke the 'read_bits_from_file()' method to actually obtain a
        bit vector consisting of the bits that constitute the
        information stored in the file.

        Lines (A21) through (A26) are for the case when you want to
        construct a bit vector by reading the bits off a file-like
        object, as in

              x = "111100001111"
              fileobj = StringIO.StringIO( x )
              bv = BitVector( fp = fileobj )

        Lines (A27) through (A52) are for the case when you want to
        construct a bit vector from an integer, as in

              bv = BitVector( intVal = 123456 )

        The bits stored in the bit vector will correspond to the binary
        representation of the integer argument provided.  The bit vector
        constructed with the above call will be the shortest possible
        bit vector for the integer supplied.  As a case in point, when
        the intVal is 0, the bit vector will consist of a single bit
        which will be 0 also.  The code in lines (A27) through (A52) can
        also handle the following sort of a call

              bv = BitVector( intVal = 46, size = 16 )        

        which returns a bit vector of a specfic size by padding the
        shortest possible bit vector the the intVal with zeros from the
        left.
        
        Lines (A53) through (A57) are for constructing a bit vector with
        just the size information, as in

              bv = BitVector( size = 61 )

        This returns a bit vector that will hold exactly 61 bits, all
        initialized to the zero value.

        Lines (A58) through (A62) are for constructing a bit vector from
        a bitstring, as in

              bv = BitVector( bitstring = '00110011111' )

        Finally, lines (A63) through (A66) are for constructing a bit
        vector from a list or a tuple of the individual bits:
          
              bv = BitVector( bitlist = (1, 0, 1, 1, 0, 0, 1) )

        The bit vector constructed is initialized with the supplied
        bits.

   

    ACKNOWLEDGEMENTS:

        The author is grateful to Oleg Broytmann for suggesting many
        improvements that were incorporated in Version 1.1 of this
        package.  The author would like to thank Kurt Schwehr whose
        email resulted in the creation of Version 1.2.  Kurt also caught
        an error in my earlier version of 'setup.py' and suggested a
        unittest based approach to the testing of the package.  Kurt
        also supplied the Makefile that is included in this
        distribution.  The author would also like to thank all (Scott
        Daniels, Blair Houghton, and Steven D'Aprano) for their
        responses to my comp.lang.python query concerning how to make a
        Python input stream peekable.  This feature was included in
        Version 1.1.1.

        With regard to the changes incorporated in Version 1.3, thanks
        are owed to Kurt Schwehr and Gabriel Ricardo for bringing to my
        attention the bug related to the intVal method of initializing a
        bit vector when the value of intVal exceeded sys.maxint. This
        problem is fixed in Version 1.3.  Version 1.3 also includes many
        other improvements that make the syntax better conform to the
        standard idioms of Python.  These changes and the addition of
        the new constructor mode (that allows a bit vector of a given
        size to be constructed from an integer value) are also owing to
        Kurt's suggestions.
   


    ABOUT THE AUTHOR:

        Avi Kak is the author of "Programming with Objects: A
        Comparative Presentation of Object-Oriented Programming
        with C++ and Java", published by John-Wiley in 2003. This
        book presents a new approach to the combined learning of
        two large object-oriented languages, C++ and Java.  It is
        being used as a text in a number of educational programs
        around the world.  This book has also been translated into
        Chinese.  For further information, please visit
        www.programming-with-objects.com
        


    SOME EXAMPLE CODE:

        #!/usr/bin/env python
        import BitVector

        # Construct a bit vector from a list or tuple of bits:
        bv = BitVector.BitVector( bitlist = (1, 0, 0, 1) )
        print bv                                # 1001

        # Construct a bit vector from an integer:
        bv = BitVector.BitVector( intVal = 5678 )
        print bv                                # 0001011000101110

        # Construct a bit vector of a given size from a given
        # integer:
        bv = BitVector( intVal = 45, size = 16 )
        print bv                                # 0000000000101101

        # Construct a zero-initialized bit vector of a given size:
        bv = BitVector.BitVector( size = 5 )
        print bv                                # 00000

        # Construct a bit vector from a bit string:
        bv = BitVector.BitVector( bitstring = '110001' )     
        print bv[0], bv[1], bv[2], bv[3], bv[4], bv[5]       # 1 1 0 0 0 1
        print bv[-1], bv[-2], bv[-3], bv[-4], bv[-5], bv[-6] # 1 0 0 0 1 1

        # Construct a bit vector from a file like object:
        import StringIO
        x = "111100001111"
        fp_read = StringIO.StringIO( x )
        bv = BitVector.BitVector( fp = fp_read )
        print bv                                    # 111100001111 

        # Experiments with bit-wise logical operations:
        bv3 = bv1 | bv2                              
        bv3 = bv1 & bv2
        bv3 = bv1 ^ bv2
        bv6 = ~bv5

        # Find the length of a bit vector
        print len( bitvec )

        # Find the integer value of a bit vector
        print int( bitvec )

        # Open a file for reading bit vectors from
        bv = BitVector.BitVector( filename = 'TestBitVector/testinput1.txt' )
        print bv                                    # nothing yet
        bv1 = bv.read_bits_from_file(64)    
        print bv1                            # first 64 bits from the file

        # Divide a bit vector into two equal sub-vectors:
        [bv1, bv2] = bitvec.divide_into_two()

        # Permute and Un-Permute a bit vector:
        bv2 = bitvec.permute( permutation_list )
        bv2 = bitvec.unpermute( permutation_list )

        # Try circular shifts to the left and to the right
        bitvec << 7
        bitvec >> 7

        # Try 'if x in y' syntax for bit vectors:
        bv1 = BitVector( bitstring = '0011001100' )
        bv2 = BitVector( bitstring = '110011' )
        if bv2 in bv1:
            print "%s is in %s" % (bv2, bv1)
        else:
            print "%s is not in %s" % (bv2, bv1)

        .....
        .....

        (For a more complete working example, see the example code in
         the BitVectorDemo.py file in the Examples sub-directory.)

'''


import sys
import array
import exceptions
import operator

_hexdict = { '0' : '0000', '1' : '0001', '2' : '0010', '3' : '0011',
             '4' : '0100', '5' : '0101', '6' : '0110', '7' : '0111',
             '8' : '1000', '9' : '1001', 'a' : '1010', 'b' : '1011',
             'c' : '1100', 'd' : '1101', 'e' : '1110', 'f' : '1111' }

def _readblock( blocksize, bitvector ):                              #(R1)
    '''If this function can read all blocksize bits, it peeks ahead to
    see if there is anything more to be read in the file. It uses
    tell-read-seek mechanism for this in lines (R18) through (R21).  If
    there is nothing further to be read, it sets the more_to_read
    attribute of the bitvector object to False.  Obviously, this can
    only be done for seekable streams such as those connected with disk
    files.  According to Blair Houghton, a similar feature could
    presumably be implemented for socket streams by using recv() or
    recvfrom() if you set the flags argument to MSG_PEEK.
    '''
    global hexdict                                                   #(R2)
    bitstring = ''                                                   #(R3)
    i = 0                                                            #(R4)
    while ( i < blocksize / 8 ):                                     #(R5)
        i += 1                                                       #(R6)
        byte = bitvector.FILEIN.read(1)                              #(R7)
        if byte == '':                                               #(R8)
            if len(bitstring) < blocksize:                           #(R9)
                bitvector.more_to_read = False                      #(R10)
            return bitstring                                        #(R11)
        hexvalue = hex( ord( byte ) )                               #(R12)
        hexvalue = hexvalue[2:]                                     #(R13)
        if len( hexvalue ) == 1:                                    #(R14)
            hexvalue = '0' + hexvalue                               #(R15)
        bitstring += _hexdict[ hexvalue[0] ]                        #(R16)
        bitstring += _hexdict[ hexvalue[1] ]                        #(R17)
    file_pos = bitvector.FILEIN.tell()                              #(R18)
    # peek at the next byte; moves file position only if a
    # byte is read
    next_byte = bitvector.FILEIN.read(1)                            #(R19)
    if next_byte:                                                   #(R20)
        # pretend we never read the byte                   
        bitvector.FILEIN.seek( file_pos )                           #(R21)
    else:                                                           #(R22)
        bitvector.more_to_read = False                              #(R23)
    return bitstring                                                #(R24)


#--------------------  BitVector Class Definition   ----------------------

class BitVector( object ):                                           #(A1)

    def __init__( self, *args, **kwargs ):                           #(A2)
        if args:                                                     #(A3)
               raise ValueError(                                     #(A4)
                      '''BitVector constructor can only be called
                         with keyword arguments for the following
                         keywords: filename, fp (for fileobject),
                         size, intValue, bitlist (for a list or
                         tuple of bits, or bitstring)''')
        filename = fp = intVal = size = bitlist = bitstring = None   #(A5)
        if kwargs.has_key('filename'):filename=kwargs.pop('filename')#(A6)
        if kwargs.has_key('fp'):           fp = kwargs.pop('fp')     #(A7)
        if kwargs.has_key('size'):       size = kwargs.pop('size')   #(A8)
        if kwargs.has_key('intVal'):   intVal = kwargs.pop('intVal') #(A9)
        if kwargs.has_key('bitlist'):
                               bitlist = kwargs.pop('bitlist')      #(A10)
        if kwargs.has_key('bitstring') :
                               bitstring = kwargs.pop('bitstring')  #(A11)
        self.filename = None                                        #(A12)
        self.size = 0                                               #(A13)
        
        if filename:                                                #(A14)
            if fp or size or intVal or bitlist or bitstring:        #(A15)
                raise ValueError(                                   #(A16)
                  '''When filename is specified, you cannot
                     give values to any other constructor args''')
            self.filename = filename                                #(A17)
            self.FILEIN = open( filename, 'rb' )                    #(A18)
            self.more_to_read = True                                #(A19)
            return                                                  #(A20)
        elif fp:                                                    #(A21)
            if filename or size or intVal or bitlist or bitstring:  #(A22)
                raise ValueError(                                   #(A23)
                  '''When fileobject is specified, you cannot      
                     give values to any other constructor args''')
            bits = self.read_bits_from_fileobject( fp )             #(A24)
            bitlist =  map( int, bits )                             #(A25)
            self.size = len( bitlist )                              #(A26)
        elif intVal or intVal == 0:                                 #(A27)
            if filename or fp or bitlist or bitstring:              #(A28)
                raise ValueError(                                   #(A29)
                  '''When intVal is specified, you can only give
                     a value to the 'size' constructor arg''')
            if intVal == 0:                                         #(A30)
                bitlist = [0]                                       #(A31)
                self.size = 1                                       #(A32)
            else:                                                   #(A33)
                hexVal = hex( intVal ).lower().rstrip('l')          #(A34)
                hexVal = hexVal[2:]                                 #(A35)
                if len( hexVal ) == 1:                              #(A36)
                    hexVal = '0' + hexVal                           #(A37)
                bitlist = ''.join(map(lambda x: _hexdict[x],hexVal))#(A38)
                bitlist =  map( int, bitlist )                      #(A39)
                i = 0                                               #(A40)
                while ( i < len( bitlist ) ):                       #(A41)
                    if bitlist[i] == 1: break                       #(A42)
                    i += 1                                          #(A43)
                del bitlist[0:i]                                    #(A44)
                if not size:                                        #(A45)
                    self.size = len( bitlist )                      #(A46)
                else:                                               #(A47)
                    if size < len(bitlist):                         #(A48)
                        raise ValueError(                           #(A49)
                          '''The value specified for size must be
                             at least as large as for the smallest
                             bit vector possible for intVal''')
                    n = size - len(bitlist)                         #(A50)
                    bitlist = [0]*n + bitlist                       #(A51)
                    self.size = len( bitlist )                      #(A52)
        elif size >= 0:                                             #(A53)
            if filename or fp or intVal or bitlist or bitstring:    #(A54)
                raise ValueError(                                   #(A55)
                  '''When size is specified (without an intVal),
                     you cannot give values to any other
                     constructor args''')
            self.size = size                                        #(A56)
            bitlist = tuple( [0] * size )                           #(A57)
        elif bitstring or bitstring == '':                          #(A58)
            if filename or fp or size or intVal or bitlist:         #(A59)
                raise ValueError(                                   #(A60)
                  '''When a bitstring is specified, you cannot
                     give values to any other constructor args''')
            bitlist =  map( int, list(bitstring) )                  #(A61)
            self.size = len( bitlist )                              #(A62)
        elif bitlist:                                               #(A63)
            if filename or fp or size or intVal or bitstring:       #(A64)
                raise ValueError(                                   #(A65)
                  '''When bits are specified, you cannot
                     give values to any other constructor args''')
            self.size = len( bitlist )                              #(A66)
        else:                                                       #(A67)
            raise ValueError("wrong arg(s) for constructor")        #(A68) 
        two_byte_ints_needed = (len(bitlist) + 15) // 16            #(A69)
        self.vector = array.array( 'H', [0]*two_byte_ints_needed )  #(A70)
        map( self._setbit, enumerate(bitlist), bitlist)             #(A71)


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


    def _getbit( self, posn ):                                       #(C1)
        'Get the bit from the designated position'
        if  posn >= self.size or posn < -self.size:                  #(C2)
            raise ValueError( "index range error" )                  #(C3)   
        if posn < 0: posn = self.size + posn                         #(C4)
        return ( self.vector[posn//16] >> (posn&15) ) & 1            #(C5)


    def __xor__(self, other):                                        #(E1)
        '''
        Take a bitwise 'xor' of the bit vector on which
        the method is invoked with the argument bit vector.
        Return the result as a new bit vector.  If the two
        bit vectors are not of the same size, pad the shorter
        one with zero's from the left.
        '''
        if self.size < other.size:                                   #(E2)
            bv1 = self._resize_pad_from_left(other.size - self.size) #(E3)
            bv2 = other                                              #(E4)
        else:                                                        #(E5)
            bv1 = self                                               #(E6)
            bv2 = other._resize_pad_from_left(self.size - other.size)#(E7)
        res = BitVector( size = bv1.size )                           #(E8)
        res.vector = map(operator.__xor__, bv1.vector, bv2.vector)   #(E9) 
        return res                                                  #(E10)


    def __and__(self, other):                                        #(F1)
        '''
        Take a bitwise 'and' of the bit vector on which the method is
        invoked with the argument bit vector.  Return the result as a
        new bit vector.  If the two bit vectors are not of the same
        size, pad the shorter one with zero's from the left.
        '''      
        if self.size < other.size:                                   #(F2)
            bv1 = self._resize_pad_from_left(other.size - self.size) #(F3)
            bv2 = other                                              #(F4)
        else:                                                        #(F5)
            bv1 = self                                               #(F6)
            bv2 = other._resize_pad_from_left(self.size - other.size)#(F7)
        res = BitVector( size = bv1.size )                           #(F8)
        res.vector = map(operator.__and__, bv1.vector, bv2.vector)   #(F9)
        return res                                                  #(F10)


    def __or__(self, other):                                         #(G1)
        '''
        Take a bitwise 'or' of the bit vector on which the
        method is invoked with the argument bit vector.  Return
        the result as a new bit vector.  If the two bit vectors
        are not of the same size, pad the shorter one with
        zero's from the left.
        '''
        if self.size < other.size:                                   #(G2)
            bv1 = self._resize_pad_from_left(other.size - self.size) #(G3)
            bv2 = other                                              #(G4)
        else:                                                        #(G5)
            bv1 = self                                               #(G6)
            bv2 = other._resize_pad_from_left(self.size - other.size)#(G7)
        res = BitVector( size = bv1.size )                           #(G8)
        res.vector = map( operator.__or__, bv1.vector, bv2.vector)   #(G9)
        return res                                                  #(G10)


    def __invert__(self):                                            #(H1)
        '''
        Invert the bits in the bit vector on which the
        method is invoked and return the result as a new
        bit vector.
        '''
        res = BitVector( size = self.size )                          #(H2)
        res.vector = map( operator.__inv__, self.vector )            #(H3)
        return res                                                   #(H4)


    def __add__(self, other):                                        #(J1)
        '''
        Concatenate the argument bit vector with the bit
        vector on which the method is invoked.  Return the
        concatenated bit vector as a new BitVector object.
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
        Read blocksize bits from a disk file and return a
        BitVector object containing the bits.  If the file
        contains fewer bits than blocksize, construct the
        BitVector object from however many bits there are
        in the file.  If the file contains zero bits, return
        a BitVector object of size attribute set to 0.
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
        This function is meant to read a bit string from a 
        file like object.
        '''
        bitlist = []                                                 #(M2)
        while 1:                                                     #(M3)
            bit = fp.read()                                          #(M4)
            if bit == '': return bitlist                             #(M5)
            bitlist += bit                                           #(M6)


    def write_bits_to_fileobject( self, fp ):                        #(N1)
        '''
        This function is meant to write a bit vector directly to
        a file like object.  Note that whereas 'write_to_file'
        method creates a memory footprint that corresponds exactly
        to the bit vector, the 'write_bits_to_fileobject' actually
        writes out the 1's and 0's as individual items to the
        file object.  That makes this method convenient for
        creating a string representation of a bit vector,
        especially if you use the StringIO class, as shown in
        the test code.
        '''
        for bit_index in range(self.size):                           #(N2)
            if self[bit_index] == 0:                                 #(N3)
                fp.write( '0' )                                      #(N4)
            else:                                                    #(N5)
                fp.write( '1' )                                      #(N6)


    def divide_into_two(self):                                       #(P1)
        '''
        Divides an even-sized bit vector into two and returns
        the two halves as a list of two bit vectors.
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
        Permute a bit vector according to the indices
        shown in the second argument list.  Return the
        permuted bit vector as a new bit vector.
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
        Unpermute the bit vector according to the
        permutation list supplied as the second argument.
        If you first permute a bit vector by using permute()
        and then unpermute() it using the same permutation
        list, you will get back the original bit vector.
        '''
        if max(permute_list) > self.size -1:                         #(S2)
            raise exceptions.ValueError, "Bad permutation index"     #(S3)
        if self.size != len( permute_list ):                         #(S4)
            raise exceptions.ValueError,"Bad size for permute list"  #(S5)
        out_bv = BitVector( size = self.size )                       #(S6)
        i = 0                                                        #(S7)
        while ( i < len(permute_list) ):                             #(S8)
            out_bv[ permute_list[i] ] = self[i]                      #(S9)
            i += 1                                                  #(S10)
        return out_bv                                               #(S11)


    def write_to_file(self, file_out):                               #(T1)
        '''
        (Contributed by Joe Davidson) Write the bitvector
        to the file object file_out.  (A file object is
        returned by a call to open()). Since all file I/O
        is byte oriented, the bitvector must be multiple
        of 8 bits. Each byte treated as MSB first (0th index).
        '''
        err_str = '''Only a bit vector whose length is a multiple of 8
            can be written to a file.  Use the padding functions
            to satisfy this constraint.'''                           #(T2)
        if self.size % 8:                                            #(T3)
            raise exceptions.ValueError, err_str                     #(T4)
        for byte in range(self.size/8 ):                             #(T5)
            value = 0                                                #(T6)
            for bit in range(8):                                     #(T7)
                value += (self._getbit( byte*8 + (7 - bit) ) << bit )#(T8)
            file_out.write( chr(value) )                             #(T9)


    def close_file_object(self):                                     #(U1)
        '''
        For closing a file object that was used for reading
        the bits into one or more BitVector objects.
        '''
        if not self.filename:                                        #(U2)
            raise exceptions.SyntaxError, "No associated open file"  #(U3)
        self.FILEIN.close()                                          #(U4)


    def intValue(self):                                              #(V1)
        'Return the integer value of a bitvector'
        intVal = 0                                                   #(V2)
        for i in range(self.size):                                   #(V3)
            intVal += self[i] * (2 ** (self.size - i - 1))           #(V4)
        return intVal                                                #(V5)

            
    def __lshift__( self, n ):                                       #(W1)
        'For an in-place left circular shift by n bit positions'
        for i in range(n):                                           #(W2)
            self.circular_rotate_left_by_one()                       #(W3)


    def __rshift__( self, n ):                                       #(W4)
        'For an in-place right circular shift by n bit positions.'
        for i in range(n):                                           #(W5)
            self.circular_rotate_right_by_one()                      #(W6)


    def circular_rotate_left_by_one(self):                           #(X1)
        'For a one-bit in-place left circular shift'
        size = len(self.vector)                                      #(X2)
        bitstring_leftmost_bit = self.vector[0] & 1                  #(X3)
        left_most_bits = map(operator.__and__, self.vector, [1]*size)#(X4)
        left_most_bits.append(left_most_bits[0])                     #(X5)
        del(left_most_bits[0])                                       #(X6)
        self.vector = map(operator.__rshift__, self.vector, [1]*size)#(X7)
        self.vector = map( operator.__or__, self.vector, \
             map(operator.__lshift__, left_most_bits, [15]*size) )   #(X8)
        self._setbit(self.size -1, bitstring_leftmost_bit)           #(X9)


    def circular_rotate_right_by_one(self):                          #(Y1)
        'For a one-bit in-place right circular shift'
        size = len(self.vector)                                      #(Y2)
        bitstring_rightmost_bit = self[self.size - 1]                #(Y3)
        right_most_bits = map( operator.__and__,
                               self.vector, [0x8000]*size )          #(Y4)
        map( operator.__and__, self.vector, [~0x8000]*size )         #(Y5)
        right_most_bits.insert(0, bitstring_rightmost_bit)           #(Y6)
        right_most_bits.pop()                                        #(Y7)
        self.vector = map(operator.__lshift__, self.vector, [1]*size)#(Y8)
        self.vector = map( operator.__or__, self.vector, \
             map(operator.__rshift__, right_most_bits, [15]*size) )  #(Y9)
        self._setbit(0, bitstring_rightmost_bit)                    #(Y10)


    def circular_rot_left(self):                                     #(Z1)
        '''
        This is merely another implementation of the method
        circular_rotate_left_by_one() shown above.  This one
        does NOT use map functions.  This method carries out a
        one-bit left circular shift of a bit vector.
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
        circular_rotate_right_by_one() shown above.  This one
        does NOT use map functions.  This method does a one-bit
        right circular shift of a bit vector.
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


    # Allow array like subscripting for getting and setting:
    __getitem__ = _getbit                                            #(b1)
    __setitem__ = _setbit                                            #(b2)


    def __getslice__(self, i, j):                                    #(c1)
        'Allow slicing with [i:j], [:], etc.'
        slicebits = []                                               #(c2)
        if j > self.size: j = self.size                              #(c3)
        for x in range(i,j):                                         #(c4)
            slicebits.append( self[x] )                              #(c5)
        return BitVector( bitlist = slicebits )                      #(c6)


    # Allow len() to work:
    __len__ = _getsize                                               #(d1)
    # Allow int() to work:
    __int__ = intValue                                               #(d2)

    def __iter__( self ):                                            #(d3)
        '''
        To allow iterations over a bit vector by supporting the
        'for bit in bit_vector' syntax:
        '''
        return BitVectorIterator( self )                             #(d4)


    def __str__( self ):                                             #(e1)
        'To create a print representation'
        if self.size == 0:                                           #(e2)
            return ''                                                #(e3)
        return ''.join( map( str, self ) )                           #(e4)


    # Compare two bit vectors:

    def __eq__(self, other):                                         #(f1)
        if self.size != other.size:                                  #(f2)
            return False                                             #(f3)
        i = 0                                                        #(f4)
        outlist = []                                                 #(f5)
        while ( i < self.size ):                                     #(f6)
            if (self[i] != other[i]): return False                   #(f7)
            i += 1                                                   #(f8)
        return True                                                  #(f9)
    def __ne__(self, other):                                        #(f10)
        return not self == other                                    #(f11)
    def __lt__(self, other):                                        #(f12)
        return self.intValue() < other.intValue()                   #(f13)
    def __le__(self, other):                                        #(f14)
        return self.intValue() <= other.intValue()                  #(f15)
    def __gt__(self, other):                                        #(f16)
        return self.intValue() > other.intValue()                   #(f17)
    def __ge__(self, other):                                        #(f18)
        return self.intValue() >= other.intValue()                  #(f19)

    # Some additional utility functions:

    def _make_deep_copy( self ):                                     #(g1)
        'Make a deep copy of a bit vector'
        copy = str( self )                                           #(g2)
        return BitVector( bitstring = copy )                         #(g3)


    def _resize_pad_from_left( self, n ):                            #(g4)
        '''
        Resize a bit vector by padding with n 0's
        from the left. Return the result as a new bit
        vector.
        '''
        new_str = '0'*n + str( self )                                #(g5)
        return BitVector( bitstring = new_str )                      #(g6)


    def _resize_pad_from_right( self, n ):                           #(g7)
        '''
        Resize a bit vector by padding with n 0's
        from the right. Return the result as a new bit
        vector.
        '''
        new_str = str( self ) + '0'*n                                #(g8)
        return BitVector( bitstring = new_str )                      #(g9)


    def pad_from_left( self, n ):                                   #(g10)
        'Pad a bit vector with n zeros from the left'
        new_str = '0'*n + str( self )                               #(g11)
        bitlist =  map( int, list(new_str) )                        #(g12)
        self.size = len( bitlist )                                  #(g13)
        two_byte_ints_needed = (len(bitlist) + 15) // 16            #(g14)
        self.vector = array.array( 'H', [0]*two_byte_ints_needed )  #(g15)
        map( self._setbit, enumerate(bitlist), bitlist)             #(g16)


    def pad_from_right( self, n ):                                  #(g17)
        'Pad a bit vector with n zeros from the right'
        new_str = str( self ) + '0'*n                               #(g18)
        bitlist =  map( int, list(new_str) )                        #(g19)
        self.size = len( bitlist )                                  #(g20)
        two_byte_ints_needed = (len(bitlist) + 15) // 16            #(g21)
        self.vector = array.array( 'H', [0]*two_byte_ints_needed )  #(g22)
        map( self._setbit, enumerate(bitlist), bitlist)             #(g23)


    def __contains__( self, otherBitVec ):                           #(h1)
        '''
        This supports 'if x in y' and 'if x not in y'
        syntax for bit vectors.
        '''
        if self.size == 0:                                           #(h2)
              raise ValueError, "First arg bitvec has no bits"       #(h3)
        elif self.size < otherBitVec.size:                           #(h4)
              raise ValueError, "First arg bitvec too short"         #(h5)
        max_index = self.size - otherBitVec.size + 1                 #(h6)
        for i in range(max_index):                                   #(h7)
              testbv = self[i:i+otherBitVec.size]                    #(h8)
              if self[i:i+otherBitVec.size] == otherBitVec:          #(h9)
                    return True                                     #(h10)
        return False                                                #(h11)


#-----------------------  BitVectorIterator Class -----------------------

class BitVectorIterator:                                             #(j1)
    def __init__( self, bitvec ):                                    #(j2)
        self.items = []                                              #(j3)
        for i in range( bitvec.size ):                               #(j4)
            self.items.append( bitvec._getbit(i) )                   #(j5)
        self.index = -1                                              #(j6)
    def __iter__( self ):                                            #(j7)
        return self                                                  #(j8)
    def next( self ):                                                #(j9)
        self.index += 1                                             #(j10)
        if self.index < len( self.items ):                          #(j11)
            return self.items[ self.index ]                         #(j12)
        else:                                                       #(j13)
            raise StopIteration                                     #(j14)

       
#------------------------  End of Class Definition -----------------------


#------------------------     Test Code Follows    -----------------------

if __name__ == '__main__':

    # Construct a bit vector of size 0
    bv1 = BitVector( size = 0 )
    print bv1                                   # no output

    # Construct a bit vector of size 1
    bv2 = BitVector( size = 2 )
    print bv2                                   # 00

    # Joining two bit vectors:
    print bv1 + bv2                             # 0

    # Construct a bit vector with a tuple of bits:
    bv = BitVector( bitlist = (1, 0, 0, 1) )
    print bv                                    # 1001

    # Construct a bit vector with a list of bits:    
    bv = BitVector( bitlist = [1, 1, 0, 1] )
    print bv                                    # 1101
    
    # Construct a bit vector from an integer
    bv = BitVector( intVal = 5678 )
    print bv                                    # 1011000101110
    bv = BitVector( intVal = 0 )
    print bv                                    # 0
    bv = BitVector( intVal = 2 )
    print bv                                    # 10
    bv = BitVector( intVal = 3 )
    print bv                                    # 11
    bv = BitVector( intVal = 123456 )
    print bv                                    # 11110001001000000
    print bv.intValue()                         # 123456
    print int( bv )                             # 123456

    # Construct a bit vector directly from a file-like object:
    import StringIO
    x = "111100001111"
    fp_read = StringIO.StringIO( x )
    bv = BitVector( fp = fp_read )
    print bv                                    # 111100001111 

    # Construct a bit vector directly from a bit string:
    bv = BitVector( bitstring = '00110011' )
    print bv                                    # 00110011

    bv = BitVector( bitstring = '' )
    print bv                                    # nothing

    # Get the integer value of a bit vector:
    print bv.intValue()                         # 0

    # Test array-like indexing for a bit vector:
    bv = BitVector( bitstring = '110001' )
    print bv[0], bv[1], bv[2], bv[3], bv[4], bv[5]       # 1 1 0 0 0 1
    print bv[-1], bv[-2], bv[-3], bv[-4], bv[-5], bv[-6] # 1 0 0 0 1 1

    # Test setting bit values with positive and negative
    # accessors:
    bv = BitVector( bitstring = '1111' )
    print bv                                    # 1111
    bv[0]=0;bv[1]=0;bv[2]=0;bv[3]=0        
    print bv                                    # 0000
    bv[-1]=1;bv[-2]=1;bv[-4]=1
    print bv                                    # 1011

    # Check equality and inequality operators:
    bv1 = BitVector( bitstring = '00110011' )
    bv2 = BitVector( bitlist = [0,0,1,1,0,0,1,1] )
    print bv1 == bv2                            # True
    print bv1 != bv2                            # False
    print bv1 < bv2                             # False
    print bv1 <= bv2                            # True
    bv3 = BitVector( intVal = 5678 )
    print bv3.intValue()                        # 5678
    print bv3                                   # 10110000101110
    print bv1 == bv3                            # False
    print bv3 > bv1                             # True
    print bv3 >= bv1                            # True


    # Create a string representation of a bit vector:
    fp_write = StringIO.StringIO()
    bv.write_bits_to_fileobject( fp_write )
    print fp_write.getvalue()                   # 1011 

    # Experiments with bit-wise logical operations:
    bv3 = bv1 | bv2                              
    print bv3                                   # 00110011
    bv3 = bv1 & bv2
    print bv3                                   # 00110011
    bv3 = bv1 + bv2
    print bv3                                   # 0011001100110011
    bv4 = BitVector( size = 3 )
    print bv4                                   # 000
    bv5 = bv3 + bv4
    print bv5                                   # 0011001100110011000
    bv6 = ~bv5
    print bv6                                   # 1100110011001100111
    bv7 = bv5 & bv6
    print bv7                                   # 0000000000000000000
    bv7 = bv5 | bv6
    print bv7                                   # 1111111111111111111

    # Try logical operations on bit vectors of different sizes:
    print BitVector( intVal = 6 ) ^ BitVector( intVal = 13 )   # 1011
    print BitVector( intVal = 6 ) & BitVector( intVal = 13 )   # 0100
    print BitVector( intVal = 6 ) | BitVector( intVal = 13 )   # 1111

    print BitVector( intVal = 1 ) ^ BitVector( intVal = 13 )   # 1100
    print BitVector( intVal = 1 ) & BitVector( intVal = 13 )   # 0001
    print BitVector( intVal = 1 ) | BitVector( intVal = 13 )   # 1101

    # Try setbit and getsize:
    bv7[7] = 0
    print bv7                                   # 1111111011111111111
    print len( bv7 )                            # 19
    bv8 = (bv5 & bv6) ^ bv7
    print bv8                                   # 1111111011111111111
    
    # Construct a bit vector from a LIST of bits:
    bv = BitVector( bitlist= [0, 0, 1, 0, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 0, 1] )
    print bv                                    # 0010010100101001

    # Construct a bit vector from a file:
    bv = BitVector( filename = 'TestBitVector/testinput1.txt' )
    print bv                                    # nothing to show
    bv1 = bv.read_bits_from_file(64)    
    print bv1
         # 0100000100100000011010000111010101101110011001110111001001111001
    bv2 = bv.read_bits_from_file(64)    
    print bv2
         # 0010000001100010011100100110111101110111011011100010000001100110
    bv3 = bv1 ^ (bv2)
    print bv3
         # 0110000101000010000110100001101000011001000010010101001000011111

    # Divide into two bit vectors:
    [bv4, bv5] = bv3.divide_into_two()
    print bv4                            # 01100001010000100001101000011010
    print bv5                            # 00011001000010010101001000011111

    # Permute a bit vector:
    bv1 = BitVector( bitlist = [1, 0, 0, 1, 1, 0, 1] )
    print bv1                                    # 1001101
    
    bv2 = bv1.permute( [6, 2, 0, 1] )
    print bv2                                    # 1010
    bv3 = BitVector( bitlist = [1, 1, 0, 0, 0, 1, 1] )
    print bv3                                    # 1100011
    bv4 = bv1 & bv3 
    print bv4                                    # 1000001
    print

    # Read a file from the beginning to end:
    bv = BitVector( filename = 'TestBitVector/testinput4.txt' )
    while (bv.more_to_read):
        bv_read = bv.read_bits_from_file( 64 )
        print bv_read
    print

    # Experiment with closing a file object and start
    # extracting bit vectors from the file from
    # the beginning again:
    bv.close_file_object()
    bv = BitVector( filename = 'TestBitVector/testinput4.txt' )
    bv1 = bv.read_bits_from_file(64)        
    print bv1           
    FILEOUT = open( 'TestBitVector/testinput5.txt', 'w' )
    bv1.write_to_file( FILEOUT )
    FILEOUT.close()

    # Experiment in 64-bit permutation and unpermutation:
    # The permutation array was generated separately by the
    # Fisher-Yates shuffle algorithm:
    bv2 = bv1.permute( [22, 47, 33, 36, 18, 6, 32, 29, 54, 62, 4,
                        9, 42, 39, 45, 59, 8, 50, 35, 20, 25, 49,
                        15, 61, 55, 60, 0, 14, 38, 40, 23, 17, 41,
                        10, 57, 12, 30, 3, 52, 11, 26, 43, 21, 13,
                        58, 37, 48, 28, 1, 63, 2, 31, 53, 56, 44, 24,
                        51, 19, 7, 5, 34, 27, 16, 46] )
    print bv2

    bv3 = bv2.unpermute( [22, 47, 33, 36, 18, 6, 32, 29, 54, 62, 4,
                          9, 42, 39, 45, 59, 8, 50, 35, 20, 25, 49,
                          15, 61, 55, 60, 0, 14, 38, 40, 23, 17, 41,
                          10, 57, 12, 30, 3, 52, 11, 26, 43, 21, 13,
                          58, 37, 48, 28, 1, 63, 2, 31, 53, 56, 44, 24,
                          51, 19, 7, 5, 34, 27, 16, 46] )    
    print bv3

    print
    print
    
    # Try circular shifts to the left and to the right
    print bv3
    bv3 << 7
    print bv3
    bv3 >> 7
    print bv3

    # Test len()    
    print len( bv3 )                      # 64

    # Test slicing
    bv4 = bv3[5:22]
    print bv4                             # 00100100000011010

    # Test the iterator:
    for item in bv4:
        print item,                       # 0 0 1 0 0 1 0 0 0 0 0 0 1 1 0 1 0
    print
    
    # Demonstrate padding a bit vector from left
    bv = BitVector( bitstring = '101010' )
    bv.pad_from_left( 4 )
    print bv                              # 0000101010
    # Demonstrate padding a bit vector from right
    bv.pad_from_right( 4 )
    print bv                              # 00001010100000

    # Test the syntax 'if bit_vector_1 in bit_vector_2' syntax:
    try:
        bv1 = BitVector( bitstring = '0011001100' )
        bv2 = BitVector( bitstring = '110011' )
        if bv2 in bv1:
            print "%s is in %s" % (bv2, bv1)
        else:
            print "%s is not in %s" % (bv2, bv1)
    except ValueError, arg:
        print "Error Message: " + str(arg)

    # Test the size modifer when a bit vector is initialized
    # with the intVal method:
    bv = BitVector( intVal = 45, size = 16 )
    print bv                              # 0000000000101101
