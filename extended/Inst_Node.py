
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

    def set_imd(self, imd):
        self.imd = imd

    def get_imd(self):
        return self.imd

    def set_arg_num(self, arg_num):
        self.arg_num = arg_num

    def get_arg_num(self):
        return self.arg_num

    def set_val_name(self, name):
        self.val_name = name

    def get_val_name(self):
        return self.val_name

    def add_label(self, label):
        self.label.append(label)

    def get_label_by_ndx(self, ndx):
        return self.label[ndx]

