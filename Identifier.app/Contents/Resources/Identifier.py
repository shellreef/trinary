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
      self.name = name
      self.value = Trits(value)
      
   def __str__(self):
      return "<Identifier:%s>" % (self.name,) % "<Value:%s>" 
      
   def setValue(self, value):
      self.value = Trits(value)
      
   def getValue(self):
      return self.value
      
      
if __name__ == "__main__":
   a = Identifier("a", "i")
   b = Identifier("b", "0")
   
   print a, b
