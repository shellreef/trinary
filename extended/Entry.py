
import sys

INT_TYPE      = 0
BOOL_TYPE     = 1
STRUCT_TYPE   = 2
FUNCTION_TYPE = 3
NULL_TYPE     = 4

class Entry(object):
    def __init__(self, value = False, rtn_type = False):

        self.num_params  = 0
        self.name        = ""
        self.params_list = []

        # NULL TYPE
        if value == False:
            self.type        = NULL_TYPE
            self.string_name = "null"

        # INTEGER TYPE
        elif isinstance(value, int):
            self.type        = INT_TYPE
            self.string_name = "int"

        # BOOLEAN TYPE
        elif isinstace(value, Boolean):
            self.type        = BOOL_TYPE
            self.string_name = "boolean"

        # STRUCTURE TYPE
        elif isinstance(value, str) and rtn_type == False:
            self.type        = STRUCT_TYPE
            self.name        = value
            self.string_name = "struct " + value
            self.members     = {}

        # FUNCTION TYPE
        elif isinstance(value, str):
            self.type        = FUNCTION_TYPE
            self.name        = value
            self.string_name = "function " + value
            self.rtn_type    = rtn_type
            self.members     = {}

        else:
            raise Entry_Error("Entry constructor: invalid arguments")

    def __str__(self):
        return self.string_name

    def set_return_type(self, rtn):
        self.rtn_type = rtn

    def get_return_type(self):
        return self.rtn_type

    def get_type(self):
        return self.type

    def get_name(self):
        return self.name

    def add_to_members(self, key, value):
        if key in self.members:
            return False
        self.members[key] = value
        return True

    def in_members(self, key):
        if key in self.members:
            return True
        else:
            return False

    def get_table(self):
        return self.members

    def compare_types(self, other, operation):
        if self.get_type() == other.get_type() and self.get_name() == other.get_name():
            return True
        elif self.get_type() == STRUCT_TYPE and other.get_type() == NULL_TYPE:
            return True
        elif other.get_type() == STRUCT_TYPE and self.get_type() == NULL_TYPE:
            return True
        else:
            print "cannot apply '" + operation + "' to '" self "' and '" + other + "'"
            raise SystemExit

    def expr_compare_types(self, other, operation, type):
        if self.get_type() == type:
            self.compare_types(other, operation)
        else:
            print "cannot apply '" + operation + "' to '" self "' and '" + other + "'"
            raise SystemExit

    # parameter access functions
    def set_num_params(self, num_params):
        self.num_params = num_params

    def get_num_params(self):
        self.num_params

    def add_to_params(self, value):
        self.params_list.append(value)

    def get_param_by_ndx(self, ndx):
        return self.params_list[ndx]


