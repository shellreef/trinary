
import icode

def run_simulation(decoded_inst, labels, regs, memory, pc)

    inst = decoded_inst[pc]


    if inst.type == R_TYPE:
        if inst.alu_type == 0:
            regs[inst.dest] = regs[inst.src1] & regs[inst.src2]
        elif inst.alu_type == 1:
            regs[inst.dest] = regs[inst.src1] | regs[inst.src2]
        elif inst.alu_type == 2:
            regs[inst.dest] = regs[inst.src1] ^ regs[inst.src2]
        elif inst.alu_type == 3:
            regs[inst.dest] = regs[inst.src1] + regs[inst.src2]
        elif inst.alu_type == 4:
            regs[inst.dest] = regs[inst.src1] - regs[inst.src2]
        elif inst.alu_type == 5:
            regs[inst.dest] = regs[inst.src1] * regs[inst.src2]
        elif inst.alu_type == 6:
            regs[inst.dest] = regs[inst.src1] / regs[inst.src2]
        elif inst.alu_type == 7:
            regs[inst.dest] = regs[inst.src1] < regs[inst.src2]
        elif inst.alu_type == 8:
            regs[inst.dest] = regs[inst.src1] <= regs[inst.src2]
        elif inst.alu_type == 9:
            regs[inst.dest] = regs[inst.src1] == regs[inst.src2]

    if inst.type == I_TYPE:
        if inst.alu_type == 0:
            regs[inst.dest] = regs[inst.src1] + inst.imdt1
        elif inst.alu_type == 1:
            regs[inst.dest] = regs[inst.src1] - inst.imdt1
        elif inst.alu_type == 2:
            regs[inst.dest] = regs[inst.src1] * inst.imdt1
        elif inst.alu_type == 3:
            regs[inst.dest] = regs[inst.src1] / inst.imdt1
        elif inst.alu_type == 4:
            regs[inst.dest] = regs[inst.src1] - inst.imdt1
        elif inst.alu_type == 5:
            regs[inst.dest] = regs[inst.src1] - inst.imdt1
        elif inst.alu_type == 6:
            regs[inst.dest] = regs[inst.src1] - inst.imdt1
        elif inst.alu_type == 7:
            regs[inst.dest] = regs[inst.src1] - inst.imdt1

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
    labels       = {}
    address      = 0
    for i in stream_inst:
        decoded_inst.append(icode.ICode(i, labels, address))
        address = address + 1

    if "main" in labels:
        print """main function not found"""
        raise SystemExit

    pc = labels["main"]

    while pc != -1:
        pc = run_simulation(decoded_inst, labels, pc)

