#!env python
# vim: set fileencoding=utf8

import base_converter, Trits

class ICode(object):
    def __init__(self, s):
        if isinstance(s, str):
            if s[0] in trit_char:
                # decode trit instrucion code
                decode_code(self, s)
            else:
                # decode string instruction
                decode_inst(self, s)
        else:
            assert "ICode __init__, unable to parse:", s

def decode_code(self, s):
    """ Decode:

        R-Type:
        -----------------------------------------------------------
        | opcode(6) | rs(3) | rt(3) | rd(3) | sa(3) | function(9) |
        -----------------------------------------------------------
        I-Type:
        -----------------------------------------------------------
        | opcode(6) | rs(3) | rt(3) | immediate(15)               |
        -----------------------------------------------------------
        J-Type:
        -----------------------------------------------------------
        | opcode(6) | rs(3) | label0(9) | label(9)                |
        -----------------------------------------------------------
    """

    opcode = int(base_convert(s[0:6], -3, 10)) 
    # R-Type
    if opcode == 0:
        self.MemWr     = 0
        self.MemToReg  = 0
        self.ALUSource = 0
        self.BType     = 0
        self.RegDest   = 1
        self.RegWr     = 1

        self.immediate = 0
        self.src1      = int(base_convert(s[6:9], -3, 10))
        self.src2      = int(base_convert(s[9:12], -3, 10))
        self.dest      = int(base_convert(s[12:15], -3, 10))

        self.ALUOp     = int(base_convert(s[18:27], -3, 10))


