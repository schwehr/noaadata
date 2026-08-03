def encode(
    o, name, type, numbits, required=None, arraylen=1, unavailable=None, verbose=False
):
    """
    Build the encoder for boolean variables
    @type o: file like obj
    Args:
        o: where write the code
    @type name: str
        name: field name
    @type type: str
        type: bool, etc.
    @type numbits: int = 1
        numbits: How many bits per unit datum (must be 1 for bools)
    @type required: bool or None
        required: If not None, then the value must be set to this.
    @type arraylen: int >= 1
        arraylen: many bools will there be?  FIX: handle variable
    @type unavailable: bool or None
        unavailable: the default value to use if none given (if not None)
    Returns:
        None
    """

    if verbose:
        print("bool encode", name, ": unvail=", unavailable)

    assert type.lower() == "bool"
    assert numbits == 1
    if arraylen != 1:
        raise AssertionError()  # FIX... handle arrays
    if verbose:
        o.write("\t### FIELD: " + name + " (type=bool)\n")
    if required is not None:
        assert type(required) == bool
        if required:
            o.write("\t\tbvList.append(TrueBV)\n")
        else:
            o.write("\t\tbvList.append(FalseBV)\n")
        if verbose:
            o.write("\n")
        return

    if unavailable is None:
        o.write('\tif params["' + name + '"]: bvList.append(TrueBV)\n')
        o.write("\telse: bvList.append(FalseBV)\n")
    else:  # Have a default value that can be filled in
        assert type(unavailable) == bool
        o.write("\tif '" + name + "' in params:\n")
        o.write('\t\tif params["' + name + '"]: bvList.append(TrueBV)\n')
        o.write("\t\telse: bvList.append(FalseBV)\n")
        o.write("\telse:\n")
        if unavailable:
            o.write("\t\tbvList.append(TrueBV)\n")
        else:
            o.write("\t\tbvList.append(FalseBV)\n")
    if verbose:
        o.write("\n")


def decode(
    o,
    name,
    type,
    startindex,
    numbits,
    required=None,
    arraylen=1,
    unavailable=None,
    bv="bv",
    dataDict="r",
    verbose=False,
    decodeOnly=False,
):
    """
    Build the decoder for boolean variables

    @type o: file like obj
    Args:
        o: where write the code
    @type name: str
        name: field name
    @type type: str
        type: uint, bool, etc.
    @type startindex: int
        startindex: bit that begins the bool(s)
    @type numbits: int = 1
        numbits: How many bits per unit datum (must be 1 for bools)
    @type required: bool or None
        required: If not None, then the value must be set to this.
    @type arraylen: int >= 1
        arraylen: many bools will there be?  FIX: handle variable
    @type unavailable: bool or None
        unavailable: the default value to use if none given (if not None)
    @type bv: str
        bv: BitVector containing the incoming data
    @type dataDict: str
        dataDict: dictionary in which to place the results
    @type decodeOnly: bool
        decodeOnly: Set to true to only get the code for decoding
    Returns:
        int
        index one past the end of where this read
    """
    assert type == "bool"
    if verbose:
        print(
            type,
            "decode",
            name,
            ": unvail=",
            unavailable,
            "  numbits:",
            numbits,
            "  startindex=",
            startindex,
        )
    # int(startindex); int(numbits)  # Make sure it is a number
    assert numbits == 1
    assert arraylen == 1  # FIX... handle arrays

    if required is not None:
        assert type(required) == bool
        if not decodeOnly:
            o.write("\t" + dataDict + "['" + name + "']=")
        if required:
            o.write("True\n")
        else:
            o.write("False\n")
        if not decodeOnly:
            o.write("\n")
        return int(startindex) + int(numbits)

    if not decodeOnly:
        o.write("\t" + dataDict + "['" + name + "']=")
    o.write(
        "bool(int("
        + bv
        + "["
        + str(startindex)
        + ":"
        + str(startindex + int(numbits) * int(arraylen))
        + "]))"
    )
    if not decodeOnly:
        o.write("\n")

    return int(startindex) + int(numbits)
