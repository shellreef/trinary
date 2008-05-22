#!env python
# Created:20080415
# By Antonio Chavez
#
# 3-trit Computer Simulator
# usage: logicCpu program.3
# This program simulates the hardware of the 3 trit computer we are
#    developing. Input to the program is a ".3" file which should contain
#    three encoded instructions to simulate on the first line.  Once started,
#    the user may interactively change the "IN" register at any time.
#    Execution begins with instruction at program counter 0.

import sys, os, threading, time, signal

# for safe termination
CONTINUE = 0
TERMINATE = 1
global cont_exec
cont_exec = CONTINUE

# for concurency
global locked
locked = False

TRACE = False
DELAY = 1                   # second(s)
USER_INPUT_THREAD = True    # ask for user input?
USER_INPUT_INIT = 8         # initialize input to this

trit_integer = {"i": -1, "0":0, "1":1}

# Lookup a register's name by address
register_name = {
        -1: "IN",
         0: "OUT",
         1: "A"
    }

# Register contents
registers = {
        "IN":  0,
        "OUT": 0,
        "A":   0,
        "S":   1
    }

# Thread that gets input from user
class CPUInput (threading.Thread):
    def run (self):
        while True:
            print "Register Status: %s :" % registers,

            try:
                user_input = raw_input('Input value for IN:')
            except EOFError, e:
                get_lock()
                global cont_exec
                cont_exec = TERMINATE
                release_lock()
                sys.exit()

            get_lock()
            global cont_exec
            if cont_exec == TERMINATE:
                sys.exit()
            release_lock()

            try:
                digit = int(user_input)
            except ValueError, e:
                print "invalid input: %s (%s)" % (user_input, e)
                continue

            if digit >= -4 and digit <= 4:
                registers["IN"] = digit
            else:
                print """invalid input: %s""" % user_input

def get_lock():
    ''' Busy wait lock to avoid race conditions.
        This function retrieves the lock.
    '''

    global locked
    while locked:
        a = 1
    locked = True

def release_lock():
    ''' This function releases the lock.
    '''
    global locked
    locked = False


def main():
    global cont_exec

    # check arguments
    if len(sys.argv) < 2 or len(sys.argv) > 2:
        print """usage: %s program.3
input file: program.3 - machine code
""" % (sys.argv[0])
        raise SystemExit

    if (sys.argv[1])[len(sys.argv[1])-1:] != "3":
         print """\'%s\' is an invalid filetype""" % sys.argv[1]
         raise SystemExit

    # retrieve file
    codefile = file(sys.argv[1], "rt")
    tritstream = codefile.readline()

    # check for errors in file
    if codefile == []:
        print """\'%s\' files is empty""" % (sys.argv[1])
        raise SystemExit

    for i in tritstream:
        if not i in trit_integer:
            print """invalid char \'%s\' in file \'%s\'""" % (i, sys.argv[1])
            raise SystemExit

    if len(tritstream) != 9:
        print """3 instructions must be provided in \'%s\'""" % (sys.argv[1])
        raise SystemExit

    # memory, registers, and program counter
    memory = {}

    get_lock()
    registers["PC"] = 0
    release_lock()

    # decode instructions from file
    for i in range(-1, 2):
        print "%2d: " % (i),
        memory[i] = Decoder(tritstream)
        tritstream = tritstream[3:]

    # start user input thread
    if USER_INPUT_THREAD:
        CPUInput().start()

    get_lock()
    registers["IN"] = USER_INPUT_INIT
    release_lock()

    # execute instructions
    while True:

        get_lock()
        registers["PC"] = Execute(memory)
        release_lock()

        get_lock()
        if cont_exec == TERMINATE:
            sys.exit()
        release_lock()

        if TRACE:
            get_lock()
            print registers
            release_lock()

        time.sleep(DELAY)

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

def Execute(memory):
    """ Execute one instruction.
        memory: were decoded instructions are stored
        registers: contains registers and their values
        returns: new program counter, to be stored in registers["PC"]
    """

    op = (memory[registers["PC"]])["op"]

    # cmp
    if op == -1:
        src1 = (memory[registers["PC"]])["src1"]
        src2 = (memory[registers["PC"]])["src2"]
        if registers[register_name[src1]] < registers[register_name[src2]]:
            registers["S"] = -1
        elif registers[register_name[src1]] > registers[register_name[src2]]:
            registers["S"] = 1
        else:
            registers["S"] = 0
        new_pc = registers["PC"] + 1
    # lwi
    elif op == 0:
        registers["A"] = (memory[registers["PC"]])["immed"]
        new_pc = registers["PC"] + 1
    # be
    elif op == 1:
        if registers["S"] == 0:
            new_pc = (memory[registers["PC"]])["src1"]
        else:
            new_pc = (memory[registers["PC"]])["src2"]

    if new_pc > 1:
       new_pc = -1

    return new_pc

if __name__ == "__main__":
    main()
