# vim: set fileencoding=utf8
#  Token.py
#
# A generic token is a semicolon, comma, etc.
# 

symbols = ("(", ")", ",", ";", ":", "'", "{", "}", "^")

class Token(object):
   def __init__(self, name):
      '''Initialize Token object.  '''

      # TODO: validate that 'name' is a valid token
      self.name = name
      
   def __str__(self):
      return "<Token:%s>" % (self.name,)
      
if __name__ == "__main__":
   a = Token(";")
   b = Token(",")
   
   print a, b, c, d
