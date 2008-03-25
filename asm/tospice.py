#!env python
# Created:20080325
# By Jeff Connelly
#
# Convert tritstream to SPICE source for swrom-fast
import sys

# Read down, then across (one instruction per _column_, not row)
code = [
        [None,None,None],
        [None,None,None],
        [None,None,None]
       ];

all_instr = []
for i in range(0,3):
    instr = sys.stdin.read(3)
    all_instr.append(instr)
    code[0][i] = instr[0]
    code[1][i] = instr[1]
    code[2][i] = instr[2]

print "; swrom-fast include file, generated to by asm/tospice.py, for program:"
for instr in all_instr:
    print "; " + instr
print

print """; Select a voltage value based on the logic input at A
.func choose(A,for_n,for_z,for_p) {if(A<={V_N_max},for_n,if(A>={V_P_min},for_p,for_z))}

; Threshold voltages
.param V_N_max=-2
.param V_P_min=2
"""

i = 0
for row in code:
    s = ".func program_D%d(A) {choose(A," % (i,)
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
    s += ")}"

    print s

