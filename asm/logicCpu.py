
trit_integer = {"i": -1, "0":0, "1":1}

def Decoder(tritstream):
    """ Decode a single instruction. 
        tristream: stream of trits will only process the first 3 trits.
        return: dictionary containing the operation
    """
    inst = {"op":trit_integer[tritstream[0]]}

    if inst["op"] == -1 or inst["op"] == 1:
        inst["src1"] = trit_integer[tritstream[1]]
        inst["src2"] = trit_integer[tritstream[2]]
    elif inst["op"] == 0:
        print "hi"
        inst["src1"] = trit_integer[tritstream[1]]
        inst["src2"] = trit_integer[tritstream[2]]
        inst["immed"] = 3*inst["src1"] + inst["src2"]

    return inst

def Execute(memory, registers, pc):
    """ Execute one instruction. 
        memory: were decoded instructions are stored
        registers: contains registers and their values
        pc: program counter
    """

    op = (memory[pc])["op"]

    # cmp
    if op == -1:
        src1 = (memory[pc])["src1"]
        src2 = (memory[pc])["src1"]
        if (registers[src1] - registers[src2]) == 0:
            registers["S"] = 0
        else:
            registers["S"] = 1
    #lwi
    elif op == 0:
        registers[1] = (memory[pc])["immed"]
    #be
    elif op == 1:
        if registers["S"] == 0:
            op = (memory[pc])["src1"]
        else:
            op = (memory[pc])["src2"]

