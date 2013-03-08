def encode(o,name,type,numbits,required=None,arraylen=1,unavailable=None, verbose=False):
    '''
    Build the encoder for unsigned integer variables

    @type o: file like obj
    @param o: where write the code 
    @type name: str
    @param name: field name
    @type type: str
    @param type: uint, bool, etc.
    @type numbits: int >= 1
    @param numbits: How many bits per unit datum (must be 1..32)
    @type required: bool or None
    @param required: If not None, then the value must be set to this.
    @type arraylen: int >= 1
    @param arraylen: many unsigned ints will there be?  FIX: handle variable
    @type unavailable: bool or None
    @param unavailable: the default value to use if none given (if not None)
    @return: None
    '''
    if verbose: print '  encodeUInt:',name,type,numbits,'Req:',required,'alen:',arraylen,unavailable

    assert type=='uint'
    assert numbits>=1 and numbits<=32
    if arraylen != 1: assert False # FIX... handle arrays
    if verbose: o.write('\t### FIELD: '+name+' (type='+type+')\n')

    if None != required:
	if verbose: print '  required:',required
	required=int(required)
	o.write('\tbvList.append(binary.setBitVectorSize(BitVector(intVal='+str(required)+'),'+str(numbits)+'))\n')
	if verbose: o.write('\n')
	return

    if None==unavailable:
	o.write('\tbvList.append(binary.setBitVectorSize(BitVector(intVal=params[\''+name+'\']),'+str(numbits)+'))\n')
    else: # Have a default value that can be filled in
	#assert type(unavailable)==
	int(unavailable) # Make sure unavailable is a number object
	o.write("\tif '"+name+"' in params:\n")
	o.write('\t\tbvList.append(binary.setBitVectorSize(BitVector(intVal=params[\''+name+'\']'+'),'+str(numbits)+'))\n')
	o.write('\telse:\n')
	o.write('\t\tbvList.append(binary.setBitVectorSize(BitVector(intVal='+str(unavailable)+'),'+str(numbits)+'))\n')

    if verbose: o.write('\n')


def decode(o,name,type,startindex,numbits,required=None,arraylen=1,unavailable=None,
           bv='bv',dataDict='r',verbose=False, decodeOnly=False):
    '''
    Build the decoder for unsigned integer variables

    @type o: file like obj
    @param o: where write the code 
    @type name: str
    @param name: field name
    @type type: str
    @param type: uint, etc.
    @type startindex: int
    @param startindex: bit that begins the uint(s)
    @type numbits: int >= 1
    @param numbits: How many bits per unit datum
    @type required: int or None
    @param required: If not None, then the value must be set to this.
    @type arraylen: int >= 1
    @param arraylen: many ints will there be?  FIX: handle variable
    @type unavailable: int or None
    @param unavailable: the default value to use if none given (if not None)
    @type bv: str
    @param bv: BitVector containing the incoming data
    @type dataDict: str
    @param dataDict: dictionary in which to place the results
    @type decodeOnly: bool
    @param decodeOnly: Set to true to only get the code for decoding
    @rtype: int
    @return: index one past the end of where this read
    '''
    if verbose: print type,'decode',name,': unvail=',unavailable,'  numbits:',numbits, '  startindex=',startindex
    if None==arraylen: arraylen=1
    assert arraylen == 1 # FIX... handle arrays
    assert numbits>=1
    if not decodeOnly: verbose=False

    if None != required:
	int(required) # Make sure required is a number
	if not decodeOnly: o.write('\t'+dataDict+'[\''+name+'\']=')
	o.write(str(required))
	if not decodeOnly: o.write('\n')
	return startindex+numbits

    if not decodeOnly: o.write('\t'+dataDict+'[\''+name+'\']=')
    o.write('int('+bv+'['+str(startindex)+':'+str(startindex+int(numbits)*int(arraylen))+'])')
    if not decodeOnly: o.write('\n')
    if verbose: o.write('\n')
    
    return startindex+numbits
