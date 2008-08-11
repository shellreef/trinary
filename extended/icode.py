#!env python
# vim: set fileencoding=utf8

import base_converter, Trits

WORD_SIZE = 27
R_TYPE    = 0
I_TYPE    = 1
B_TYPE    = 2
J_TYPE    = 3

class ICode(object):
    def __init__(self, s, labels, address):
        if isinstance(s, str):
            if s[0] in trit_char and len(s) == WORD_SIZE:
                # decode trit instrucion code
                decode_code(self, s)
            else:
                # decode string instruction
                decode_inst(self, s, labels, address)
        else:
            assert "ICode __init__, unable to parse:", s

def decode_code(self, s):
    """ Decode Assembled Code:

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
    if type == R_TYPE:
        self.alu_op = int(base_convert(s[2:15], -3, 10))
        self.src1   = int(base_convert(s[15:18], -3, 10))
        self.src2   = int(base_convert(s[18:21], -3, 10))
        self.dest   = int(base_convert(s[21:24], -3, 10))
        self.imdt1  = int(base_convert(s[24:27], -3, 10))

        self.imdt2  = 0

    # I-Type
    elif type == R_TYPE:
        self.alu_op = int(base_convert(s[2:7], -3, 10))
        self.src1   = int(base_convert(s[7:10], -3, 10))
        self.dest   = int(base_convert(s[10:13], -3, 10))
        self.imdt1  = int(base_convert(s[13:27], -3, 10))

        self.src2   = 0
        self.imdt2  = 0

    # B-Type
    elif type == R_TYPE:
        self.alu_op = int(base_convert(s[2:6], -3, 10))
        self.src1   = int(base_convert(s[6:9], -3, 10))
        self.imdt1  = int(base_convert(s[9:18], -3, 10))
        self.imdt2  = int(base_convert(s[18:27], -3, 10))

        self.src2   = 0
        self.dest   = 0

    # J-Type
    elif type == R_TYPE:
        self.alu_op = int(base_convert(s[2:6], -3, 10))
        self.imdt1  = int(base_convert(s[6:27], -3, 10))

        self.src1   = 0
        self.src2   = 0
        self.dest   = 0
        self.imdt2  = 0

    # Uknown type
    else:
        raise DecodeError("invalid type code = %s" % (type, ))

r_type_instructions = ('and', 'or', 'xor', 'add', 'sub', 'mul', 'div', 'cmpLT', 'cmpLE', 'cmpEQ')
i_type_instructions = ('addi', 'subi', 'multi', 'divi', 'st', 'ld', 'set', 'mov')
b_type_instructions = ('cbr')
j_type_instructions = ('ba', 'call', 'ret')

register_names      = ('i0', 'i1', 'i2', 'i3', 'i4', 'i5', 'i6', 'o0', 'o1', 'o2', 'o3', 'o4', 'o5', 'o6', 'l0', 'l1', 'l2', 'l3', 'l4', 'l5', 'l6', 'sp', 'fp', 'ra')

library_functions == ('print', 'scanf', 'malloc', 'free')

def decode_inst(self, s, labels, address):
    """ Decode Assembled Code:

        Decode instruction from Trinary-RISC
        s: example = "add i0 i1 i2"
            operands are separated by spaces no other chars are allowed
        labels: dictionary of labels with corresponding addresses
        address: address in memory of the instruction/label to decode
    """

    parts = s.split(" ")
    self.string  = s
    self.address = address

    # R-Type
    if parts[0] in r_type_instructions:
        self.type   = R_TYPE
        self.alu_op = r_type_instructions.index(parts[0])
        self.src1   = register_names.index(parts[1])
        self.src2   = register_names.index(parts[2])
        self.dest   = register_names.index(parts[3])

        self.imdt2  = 0

        # sa field
        assem = base_10_to_b3(0, 3)
        # destination register field
        assem = assem + base_10_to_3(self.dest, 3)
        # target register field
        assem = assem + base_10_to_3(self.src2, 3)
        # source register field
        assem = assem + base_10_to_3(self.src1, 3)
        # opcode field
        assem = assem + base_10_to_3(self.alu_op, 13)
        # type field
        self.assembled = assem + base_10_to_3(self.type, 2)

    # I-Type
    elif parts[0] in i_type_instructions:
        self.type   = R_TYPE
        self.alu_op = i_type_instructions.index(parts[0])
        self.src1   = register_names.index(parts[1])

        if self.alu_op != i_type_instructions.index('set')
            self.dest = register_names.index(parts[2])
        else:
            self.dest = 0

        if self.alu_op != i_type_instructions.index('mov'):
            self.imdt1 = parts[3]
        else:
            self.imdt1 = 0
            
        self.src2   = 0
        self.imdt2  = 0

        # immediate field
        assem = base_10_to_b3(self.imdt1, 14)
        # target register field
        assem = assem + base_10_to_3(self.src2, 3)
        # source register field
        assem = assem + base_10_to_3(self.src1, 3)
        # opcode field
        assem = assem + base_10_to_3(self.alu_op, 5)
        # type field
        self.assembled = assem + base_10_to_3(self.type, 2)

    # B-Type
    elif parts[0] in b_type_instructions:
        self.type   = R_TYPE
        self.alu_op = b_type_instructions.index(parts[0])
        self.src1   = register_names.index(parts[1])

        if parts[2] in labels and not parts[2] in library_fuctions:
            self.imdt1  = labels[parts[2]]
        else:
            print "%s: label undefined" % parts[2]

        if parts[3] in labels and not parts[3] in library_fuctions:
            self.imdt2  = labels[parts[3]]
        else:
            print "%s: label undefined" % parts[2]

        self.src2   = 0
        self.dest   = 0

        # false destination label field
        assem = base_10_to_b3(self.imdt1, 9)
        # true destination label field
        assem = assem + base_10_to_3(self.imdt, 9)
        # source register field
        assem = assem + base_10_to_3(self.src1, 3)
        # opcode field
        assem = assem + base_10_to_3(self.alu_op, 4)
        # type field
        self.assembled = assem + base_10_to_3(self.type, 2)

    # J-Type
    elif parts[0] in j_type_instructions:
        self.type   = R_TYPE
        self.alu_op = j_type_instructions.index(parts[0])
        if self.alu_op != j_type_instructions.index('ret'):
            if parts[1] in library_functions and parts[0] != 'ba':
                self.imdt1 = -library_functions.index(parts[1])
            elif parts[1] in labels:
                self.imdt1 = labels[parts[1]]
            else:
                print "%s: label undefined" % parts[1]
                raise SystemExit
        else:
            self.imdt1 = 0

        self.src1   = 0
        self.src2   = 0
        self.dest   = 0
        self.imdt2  = 0

        # destination field
        assem = base_10_to_3(self.src1, 21)
        # opcode field
        assem = assem + base_10_to_3(self.alu_op, 4)
        # type field
        self.assembled = assem + base_10_to_3(self.type, 2)

    elif len(parts) == 1 and s.strip() != 0:
        if parts[0] in labels:
            raise DecodeError("label redefined = %s" % (parts[0], ))
        else:
            labels[parts[0]] = address
            self.assembled = parts[0]

    elif s.strip() != 0:
        raise DecodeError("invalid instruction = %s" % (s, ))


def base_10_to_b3(base_10, length):
    """ base_10_to_b3:
        base_10: integer value
        length:  desired length of resulting string

        convert from base 10 to base -3 w/base_convert
        and fill in leading zeros

        return: balanced base 3 string with length of 'length'
    """

    result = base_convert(str(base_10), 10, -3)
    if len(result) != length:
        add = length - len(result)
        for i in range(0, add):
            result = '0' + result

    return result


