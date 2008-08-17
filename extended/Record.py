
import sys

class Records(object):
    def __init__(self):
        self.global_table = {}
        self.local_table  = {}
        self.counter      = 0

    def increment_counter(self):
        self.counter = self.counter + 1

    def reset_counter(self):
        self.counter = 0

    def add_to_global(self, key, value):
        if key in self.global_table:
            return False
        self.global_table[key] = value
        return True

    def add_to_local(self, key, value):
        if key in self.local_table:
            return False
        self.local_table[key] = value
        return True

    # clear local table
    def reset_local(self):
        self.local_table.clear()

    # return the value of 'key' (if present) from the tables
    def return_value(self, key, structure = False):

        # find in global table
        if key in self.global_table:
            return self.global_table[key]

        # find in local table
        elif key in self.local_table:
            return self.local_table[key]

        # find in structure
        elif structure != False and key in structure.in_members(key):
            return structure.get_member(key)

        else:
            print "id '" + key + "' not defined"
            raise SystemExit

