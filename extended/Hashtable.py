
import sys

class Hashtable(object):
    def __init__(self):
        self.table = {}

    # check if key already defined, if not insert it
    def check_and_insert(self, key, value):
        if key in self.table:
            print "id '" + key + "' already defined"
            raise SystemExit
        self.table[id] = value

    # used for checking for valid assignments
    def assign_value(self, key, value):
        if key in self.table:
            print "id '" + key + "' already defined"
            raise SystemExit
        if self.table[key].compare_types(value, "assignment"):
            self.table[key] = value
