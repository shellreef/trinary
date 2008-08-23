
import icode
import sys

def run_simulation(decoded_inst, labels, regs, memory, pc):

    inst = decoded_inst[pc]

    if inst.type == icode.R_TYPE:
        if inst.alu_op == icode.r_type_instructions.index('and'):
            regs[inst.dest] = regs[inst.src1] & regs[inst.src2]
        elif inst.alu_op == icode.r_type_instructions.index('or'):
            regs[inst.dest] = regs[inst.src1] | regs[inst.src2]
        elif inst.alu_op == icode.r_type_instructions.index('xor'):
            regs[inst.dest] = regs[inst.src1] ^ regs[inst.src2]
        elif inst.alu_op == icode.r_type_instructions.index('add'):
            regs[inst.dest] = regs[inst.src1] + regs[inst.src2]
        elif inst.alu_op == icode.r_type_instructions.index('sub'):
            regs[inst.dest] = regs[inst.src1] - regs[inst.src2]
        elif inst.alu_op == icode.r_type_instructions.index('mul'):
            regs[inst.dest] = regs[inst.src1] * regs[inst.src2]
        elif inst.alu_op == icode.r_type_instructions.index('div'):
            regs[inst.dest] = regs[inst.src1] / regs[inst.src2]
        elif inst.alu_op == icode.r_type_instructions.index('cmpLT'):
            regs[inst.dest] = regs[inst.src1] < regs[inst.src2]
        elif inst.alu_op == icode.r_type_instructions.index('cmpLE'):
            regs[inst.dest] = regs[inst.src1] <= regs[inst.src2]
        elif inst.alu_op == icode.r_type_instructions.index('cmpEQ'):
            regs[inst.dest] = regs[inst.src1] == regs[inst.src2]
        else:
            print "invalid r_type"
            raise SystemExit
        pc = pc + 1

    elif inst.type == icode.I_TYPE:
        if inst.alu_op == icode.i_type_instructions.index('andi'):
            regs[inst.dest] = regs[inst.src1] & inst.imdt1
        elif inst.alu_op == icode.i_type_instructions.index('ori'):
            regs[inst.dest] = regs[inst.src1] | inst.imdt1
        elif inst.alu_op == icode.i_type_instructions.index('xori'):
            regs[inst.dest] = regs[inst.src1] ^ inst.imdt1
        elif inst.alu_op == icode.i_type_instructions.index('addi'):
            regs[inst.dest] = regs[inst.src1] + inst.imdt1
        elif inst.alu_op == icode.i_type_instructions.index('subi'):
            regs[inst.dest] = regs[inst.src1] - inst.imdt1
        elif inst.alu_op == icode.i_type_instructions.index('multi'):
            regs[inst.dest] = regs[inst.src1] * inst.imdt1
        elif inst.alu_op == icode.i_type_instructions.index('divi'):
            regs[inst.dest] = regs[inst.src1] / inst.imdt1
        elif inst.alu_op == icode.i_type_instructions.index('st'):
            memory[regs[inst.dest] + inst.imdt1] = regs[inst.src1]
        elif inst.alu_op == icode.i_type_instructions.index('ld'):
            regs[inst.dest] = memory[regs[inst.src1] + inst.imdt1]
        elif inst.alu_op == icode.i_type_instructions.index('set'):
            regs[inst.src1] = inst.imdt1
        elif inst.alu_op == icode.i_type_instructions.index('mov'):
            regs[inst.dest] = regs[inst.src1]
        else:
            print "invalid i_type"
            raise SystemExit
        pc = pc + 1

    elif inst.type == icode.B_TYPE:
        if inst.alu_op == icode.b_type_instruction.index('cbr'):
            if regs[inst.src1] != 0:
                pc = inst.imdt1
            else:
                pc = inst.imdt2
        else:
            print "invalid b_type"
            raise SystemExit

    elif inst.type == icode.J_TYPE:
        if inst.alu_op == icode.j_type_instructions.index('ba'):
            pc = self.imdt1
        elif inst.alu_op == icode.j_type_instruction.index('ret'):
            pc = regs[register_names.index('ra')]
        elif inst.alu_op == icode.j_type_instruction.index('call'):
            if inst.imdt1 < 0:
                if inst.imdt1 == -1:
                    print regs[register_names.index('o0')]
                if inst.imdt1 == -2:
                    regs[register_names.index('i0')] = int(input(''))
                # TODO malloc & free
                if inst.imdt1 == -3:
                    print 'malloc'
                if inst.imdt1 == -4:
                    print 'free'
            pc = pc + 1
        else:
            print "invalid j_type"
            raise SystemExit

    else:
        print "%d: invalid instruction type" % inst.type
        raise SystemExit

    return pc


def main():

    #check arguments
    if len(sys.argv) != 2:
        print """usage: %s program.3c
input file: program.3c - Trinary RISC
""" % (sys.argv[0])
        raise SystemExit

    if (sys.argv[1])[len(sys.argv[1])-2:] != "3c":
        print """\'%s\' is an invalid filetype""" % sys.argv[1]
        raise SystemExit

    # retrieve file
    codefile = file(sys.argv[1], "rt")

    # check for empty file
    if codefile == []:
        print """\'%s\' file is empty""" % (sys.argv[1])
        raise SystemExit

    stream_inst  = codefile.readlines()
    decoded_inst = []
    memory       = []
    labels       = {}
    address      = 0

    regs = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    labels['print']  = -1
    labels['scanf']  = -2
    labels['malloc'] = -3
    labels['free']   = -4
    regs[icode.register_names.index('ra')] = -1

    for i in stream_inst:
        decoded_inst.append(icode.ICode(i, labels, address))
        address = address + 1

    if not "main" in labels:
        print """main function not found"""
        raise SystemExit

    pc = labels["main"]

    while pc != -1:
        pc = run_simulation(decoded_inst, labels, regs, memory, pc)


if __name__ == "__main__":

    # TEST
    regs = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    decoded_inst = []
    decoded_inst.append(icode.ICode("add i0 i1 i2", {}, 0))
    memory = []
    labels = {}
    pc = 0
    pc = run_simulation(decoded_inst, labels, regs, memory, pc)

    main()

