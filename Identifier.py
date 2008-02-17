#
# vim: set fileencoding=utf8
#  token.py
#  
#
#  Created by Antonio on 2/16/08.
#

class Identifier(object):
   def __init__(self, name):
      self.name = name
   
   def __str__(self):
      return "<Identifier:%s>" % (self.name,)
      
if __name__ == "__main__":
   a = Identifier("a")
   b = Identifier("b")
   
   print a, b
