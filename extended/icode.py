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
        --------------------------------------------------------
        | type(2) | opcode(13) | rs(3) | rt(3) | rd(3) | sa(3) |
        --------------------------------------------------------
        I-Type:
        --------------------------------------------------------
        | type(2) | opcode(5) | rs(3) | rt(3) | immediate(14)  |
        --------------------------------------------------------
        B-Type:
        --------------------------------------------------------
        | type(2) | opcode(4) | rs(3) | label0(9) | label(9)   |
        --------------------------------------------------------
        J-Type:
        --------------------------------------------------------
        | type(2) | opcode(4) | address(21)                    |
        --------------------------------------------------------
    """

    type = int(base_convert(s[0:2], -3, 10))
    # R-Type
    if type == 0:
        self.alu_op = int(base_convert(s[2:15], -3, 10))
        self.src1   = int(base_convert(s[15:18], -3, 10))
        self.src2   = int(base_convert(s[18:21], -3, 10))
        self.dest   = int(base_convert(s[21:24], -3, 10))
        self.imdt1  = int(base_convert(s[24:27], -3, 10))

        self.imdt2  = 0

    # I-Type
    elif type == 1:
        self.alu_op = int(base_convert(s[2:7], -3, 10))
        self.src1   = int(base_convert(s[7:10], -3, 10))
        self.src2   = int(base_convert(s[10:13], -3, 10))
        self.imdt1  = int(base_convert(s[13:27], -3, 10))

        self.dest   = 0
        self.imdt2  = 0

    # B-Type
    elif type == 2:
        self.alu_op = int(base_convert(s[2:6], -3, 10))
        self.src1   = int(base_convert(s[6:9], -3, 10))
        self.imdt1  = int(base_convert(s[9:18], -3, 10))
        self.imdt2  = int(base_convert(s[18:27], -3, 10))

        self.src2   = 0
        self.dest   = 0

    # J-Type
    elif type == 3:
        self.alu_op = int(base_convert(s[2:6], -3, 10))
        self.imdt1  = int(base_convert(s[6:27], -3, 10))

        self.src1   = 0
        self.src2   = 0
        self.dest   = 0
        self.imdt2  = 0

    # Uknown type
    else:
        raise DecodeError("invalid type code = %s" % (type, ))


