
import sys
import Node

class Records(object):

    def __init__(self):
        self.global_table  = {}
        self.local_table   = {}
        self.counter       = 0
        self.label_counter = 0
        self.start_node    = Node()
        self.end_node      = Node()
        self.crnt_node     = self.start_node

    # counter access functions
    def increment_counter(self):
        self.counter = self.counter + 1

    def reset_counter(self):
        self.counter = 0

    def get_counter(self):
        return self.counter

    def increment_label_counter(self):
        self.label_counter = self.label_counter + 1

    def get_label_counter(self):
        return self.label_counter

    # add to table functions
    def add_to_global(self, key, value):
        if key in self.global_table:
            return False
        self.global_table[key] = value
        return True

    def add_to_local(self, key, value):
        return self.crnt_function.add_to_members(key, value)

    # set local table
    def set_local(self, function):
        self.local_table = function.get_table()
        self.crnt_function = function

    # return the value of 'key' (if present) from the tables
    def get_value(self, key, structure = False):

        # find in structure
        if structure != False and key in structure.in_members(key):
            return structure.get_member(key)

        # find in local table
        elif key in self.local_table:
            return self.local_table[key]

        # find in global table
        elif key in self.global_table:
            return self.global_table[key]

        else:
            print "id '" + key + "' not defined"
            raise SystemExit

    # Function return value access functions
    def get_func_ret(self):
        return self.function_return_type

    def set_func_ret(self, rtn_type):
        self.fuction_return_type = rtn_type

    # Number of parameters access functions
    def set_num_params(self, num_params):
        self.crnt_function.set_num_params(num_params)

    def get_num_params(self):
        return self.crnt_fuctions.get_num_params()

    # current node access methods
    def set_crnt_node(self, node):
        self.crnt_node = node

    def get_crnt_node(self):
        return self.crnt_node

    def get_start_node(self):
        return self.start_node

    def get_end_node(self):
        return self.end_node



