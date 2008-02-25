#
# vim: set fileencoding=utf8
#  Identifier.py
#  Creates identifier object.
#
#  Created by Antonio on 2/16/08.
#

from Trits import Trits

class Identifier(object):
    def __init__(self, name, value = ""):
        '''Initialize Identifier object.
        length field will be used to index vector from n to 0
        '''

        self.name = name
        self.value = Trits(value)
        self.length = len(self.value)
        if self.length > 1: self.type = "vector"
        else: self.type = "trit"
        
    def __str__(self):
        return "<Identifier:%s>" % (self.name,)
        
    def setValue(self, value):
        self.value = Trits(value)
        self.length = len(self.value)
        if self.length < 1 : self.type = "vector"
        else: self.type = "trit"
        
    def getValue(self):
        return self.value
        
        
if __name__ == "__main__":
    a = Identifier("one", "i")
    b = Identifier("two", "0")
    c = Identifier("three", "01i01")
    d = Identifier("four")
    
    print a, b, c, d
