#!env python
# Created:20080415
# By Antonio Chavez
#
# 3-trit computer disassembler

import sys, os, threading

trit_integer = {"i": -1, "0":0, "1":1}

in_reg = 0;

def main():
    if len(sys.argv) < 2:
        print """usage: %s program.3
input file: program.3 - machine code
""" % (sys.argv[0])
        raise SystemExit

    codefile = file(sys.argv[1], "rt")
    tritstream = codefile.read()

    for i in tritstream:
        if not i in trit_integer:
           print """invalid char \'%s\' in file \'%s\'""" % (i, sys.argv[1])

    if len(tritstream) != 9:
        print """3 instructions must be provided in \'%s\'""" % (sys.argv[1])

def Decoder(tritstream):
    """ Decode a single instruction.
        tristream: stream of trits will only process the first 3 trits.
        return: dictionary containing the operation
    """
    inst = {"op":trit_integer[tritstream[0]]}

    # cmp and be
    if inst["op"] == -1 or inst["op"] == 1:
        inst["src1"] = trit_integer[tritstream[1]]
        inst["src2"] = trit_integer[tritstream[2]]

    # lwi
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
    # lwi
    elif op == 0:
        registers[1] = (memory[pc])["immed"]
    # be
    elif op == 1:
        if registers["S"] == 0:
            op = (memory[pc])["src1"]
        else:
            op = (memory[pc])["src2"]


class CPUInput (threading.Thread):

    def run (self):
        input = raw_input('Input value for IN:')
        if input in trit_integer:
            in_reg = trit_integer[input]
        else:
            print """invalid input: %s""" % input
