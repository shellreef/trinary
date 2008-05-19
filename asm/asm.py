#!env python
# Created:20080312
# By Jeff Connelly
#
# 3-trit computer assembler

import sys, os

def main():
    if len(sys.argv) < 2:
        print """usage: %s program.t 
input file: program.t - assembly code
outputs: 
\tprogram.3 - assembled tritstream
\tprogram.sp - SPICE file suitable for use with swrom-fast
""" % (sys.argv[0])

        raise SystemExit

    asmfile = file(sys.argv[1], "rt")
    tritstream_filename = sys.argv[1].replace(".t", ".3")
    tritstream_file = file(tritstream_filename, "wt")
    spice_filename = sys.argv[1].replace(".t", ".sp")
    spice_file = file(spice_filename, "wt")

    tritstream = assemble(asmfile)
    tritstream_file.write(tritstream)
    spice_file.write(tospice(tritstream))

def tospice(tritstream):
    """Convert tritstream to SPICE source for 3x3 swrom-fast."""

    # Read down, then across (one instruction per _column_, not row)
    code = [
            [None,None,None],
            [None,None,None],
            [None,None,None]
           ]

    all_instr = []
    for i in range(0,3):
        all_instr.append(tritstream[i*3:i*3+3])
        code[0][i] = tritstream[i*3 + 0]
        code[1][i] = tritstream[i*3 + 1]
        code[2][i] = tritstream[i*3 + 2]

    s = "; swrom-fast include file, generated to by asm/asm.py, for tritstream:\n"
    for instr in all_instr:
        s += "; " + instr + "\n"
    s += "\n" 

    s += """; Select a voltage value based on the logic input at A
.func choose(A,for_n,for_z,for_p) {if(A<={V_N_max},for_n,if(A>={V_P_min},for_p,for_z))}

; Threshold voltages
.param V_N_max=-2
.param V_P_min=2

"""

    i = 0
    for row in code:
        s += ".func program_%s(A) {choose(A," % ({0:"i", 1:0, 2:1}[i],)
        i += 1
        voltages = []
        for col in row:
            v = "V("
            if col == "i":
                v += "_1"
            elif col == "1":
                v += "1"
            else:
                v += "0"
            v += ")"
            voltages.append(v)
        s += ",".join(voltages)
        s += ")}\n"
    return s 

def assemble(asmfile):
    """Return a serialized tritstream of asmfile assembled."""
    pc = 0   # PC goes 0, 1, -1 _NOT_ -1, 0, 1 (0 on power-up)
    labels = {}
    opcode_map = { "lwi": [0], "cmp": [-1], "be": [1] }
    register_map = { "in": [-1], "out": [0], "a": [1] }
    # TODO: balanced trinary conversion routines
    literal_map = { 
            "4": [1, 1],
            "3": [1, 0],
            "2": [1, -1],
            "1": [0, 1],
            "0": [0, 0],
            "-1": [0, -1],
            "-2": [-1, 1],
            "-3": [-1, 0],
            "-4": [-1, -1]
            }

    tritstream = []
    while True:
        line = asmfile.readline()
        # End on EOF
        if len(line) == 0:
            break

        # Skip blank lines
        line = line.strip()
        if len(line) == 0:
            continue

        label, opcode, operands = parse_line(line)
        if opcode == None:
            continue

        #print [label, opcode, operands]
        machine_code = []

        if label is not None:
            labels[label] = [pc]

        machine_code.extend(opcode_map[opcode])
        for op in operands:
            x = register_map.get(op,
                    labels.get(op,
                        literal_map.get(op)))
            if x is None:
                print "Bad register, label, or literal: %s" % (op, )
                raise SystemExit
            else:
                machine_code.extend(x)
    
        #print machine_code
        tritstream.extend(machine_code)
        pc += 1
        if pc > 3:
            print "Too many instructions, need exactly 3 but pc=%d" % (pc,)
            raise SystemExit

    if pc != 3:
        print "Too few instructions, need exactly 3 but pc=%d" % (pc,)
        raise SystemExit

    #print labels

    # Execution goes 0, 1, i
    # but we ordered i, 0, 1.
    # Arrange the instructions so that the first
    # instruction written is placed at 0, next at
    # 1, then the last instruction at i--since
    # execution begins at 0, this will perserve the order.
    tritstream_ordered = (
            tritstream[3*2:3*2+3] +     # last instruction executed
            tritstream[3*0:3*0+3] +     # <-- PC starts here (0)
            tritstream[3*1:3*1+3]       # second instruction executed
            )

    # Serialize tritstream
    s = ""
    for t in tritstream_ordered:
        if t == -1:
            s += "i"
        else:
            s += str(t)

    return s

def parse_line(line):
    # Strip comments
    without_comment = line.split(";", 1)[0]
    if len(without_comment) == 0:
        return (None, None, None)

    # Separate label from instruction
    label_and_instruction = without_comment.split(":", 1)
    if len(label_and_instruction) > 1:
        label, instruction = label_and_instruction
        label = label.strip()
    else:
        instruction, = label_and_instruction
        label = None

    instruction = instruction.strip()

    # Separate opcode from operands
    tokens = instruction.split()
    opcode = tokens[0]
    operands = []
    for token in tokens[1:]:
        token = token.replace(",", "")
        operands.append(token)

    return (label, opcode, operands)

if __name__ == "__main__":
    main()
