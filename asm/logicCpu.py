#!env python
# Created:20080415
# By Antonio Chavez
#
# 3-trit computer disassembler

import sys, os, threading, time

trit_integer = {"i": -1, "0":0, "1":1}

registers = {-1:0, 0:0, 1:0, 'S':1}

# Thread that gets input from user
class CPUInput (threading.Thread):

    def run (self):
        while True:
            print "Register Status: %s :" % registers,
            user_input = input('Input value for IN:')

            if user_input >= -4 and user_input <= 4:
                registers[-1] = user_input
                time.sleep(0.25)
            else:
                print """invalid input: %s""" % user_input

def main():

    # check arguments
    if len(sys.argv) < 2 or len(sys.argv) > 2:
        print """usage: %s program.3
input file: program.3 - machine code
""" % (sys.argv[0])
        raise SystemExit

    if (sys.argv[1])[len(sys.argv[1])-1:] != "3":
         print """\'%s\' is an invalid filetype""" % sys.argv[1]
         raise SystemExit

    # retrive file
    codefile = file(sys.argv[1], "rt")
    tritstream = codefile.read()

    # check for errors in file
    for i in tritstream:
        if not i in trit_integer:
            print """invalid char \'%s\' in file \'%s\'""" % (i, sys.argv[1])
            raise SystemExit

    if len(tritstream) != 9:
        print """3 instructions must be provided in \'%s\'""" % (sys.argv[1])
        raise SystemExit

    # memory, registers, and program counter
    memory = {}
    pc = 0

    # decode instructions from file
    for i in range(-1, 2):
        print "%2d: " % (i),
        memory[i] = Decoder(tritstream)
        tritstream = tritstream[3:]

    CPUInput().start()

    # execute instructions
    while pc in (-1, 0, 1):
        pc = Execute(memory, pc)

def Decoder(tritstream):
    """ Decode a single instruction.
        tristream: stream of trits will only process the first 3 trits.
        return: dictionary containing the operation
    """
    inst = {"op":trit_integer[tritstream[0]]}

    # cmp and be
    if inst["op"] == -1 or inst["op"] == 1:

        if inst["op"] == -1:
            print "cmp ",
        else:
            print "be  ",

        inst["src1"] = trit_integer[tritstream[1]]
        print "%2d," % inst["src1"],
        inst["src2"] = trit_integer[tritstream[2]]
        print "%2d" % inst["src2"]

    # lwi
    elif inst["op"] == 0:
        print "lwi ",
        inst["src1"] = trit_integer[tritstream[1]]
        inst["src2"] = trit_integer[tritstream[2]]
        inst["immed"] = 3*inst["src1"] + inst["src2"]
        print "%2d" % inst["immed"]

    return inst

def Execute(memory, pc):
    """ Execute one instruction.
        memory: were decoded instructions are stored
        registers: contains registers and their values
        pc: program counter
    """

    op = (memory[pc])["op"]

    # cmp
    if op == -1:
        src1 = (memory[pc])["src1"]
        src2 = (memory[pc])["src2"]
        if (registers[src1] - registers[src2]) == 0:
            registers["S"] = 0
        else:
            registers["S"] = 1
        pc = pc + 1
    # lwi
    elif op == 0:
        registers[1] = (memory[pc])["immed"]
        pc = pc + 1
    # be
    elif op == 1:
        if registers["S"] == 0:
            pc = (memory[pc])["src1"]
        else:
            pc = (memory[pc])["src2"]

    if pc > 1:
       pc = -1
    return pc

if __name__ == "__main__":
    main()
