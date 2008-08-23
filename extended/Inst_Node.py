
class Inst_Node(object):

    def __init__(self, op, rs = False, rt = False, rd = False, imd = False):

        self.op = op
        if rs != False:
            self.rs = rs

        if rt != False:
            self.rt = rt

        if rd != False:
            self.rd = rd

        if imd != False:
            self.imd = imd

    def set_arg_num(self, arg_num):
        self.arg_num = arg_num

    def get_arg_num(self):
        return self.arg_num

    def set_val_name(self, name):
        self.val_name = name

    def get_val_name(self):
        return self.val_name

