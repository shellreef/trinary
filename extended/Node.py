
class Node(object):

    def __init__(self, label = False):
        self.iloc_inst   = []
        self.sparc_inst  = []
        self.entry_nodes = []
        self.exit_nodes  = []
        self.labels      = []

        if label != False:
            self.labels.append(label)

        self.num_locals = 0

    def add_entry_node(self, node):
        self.entry_nodes.append(node)

    def add_exit_node(self, node):
        self.exit_node.append(node)

    def add_label(self, label):
        self.labels.append(label)

    def add_iloc_inst(self, inst):
        self.iloc_inst.append(inst)

    def add_sparc_inst(self, inst):
        self.sparc_inst.append(int)

    def set_num_locals(self, num):
        self.num_locals = num

    def get_num_locals(self):
        return self.num_locals
