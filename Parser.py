#
#  Parser.py
#  
#
#  Created by Antonio on 2/17/08.
#  Trinary Research Project: Digital logic simulator
#

from tokenizer import nextToken

def compareTokens(current, expected, infile):
   '''compare current with expected.  If they are equal then return the next
   token, if they are not then raise exeption and exit program.
   '''
   if current[0] is None or current[1] != expected:
      printError(current, expected)
   else:
      return nextToken(infile)
      
def printError(current, expected):
   '''Function prints an error message and raises an exeption
   '''
   print "Expected '"
   print expected
   print "', found '"
   print current[1]
   print "'\n"
   # raise exception   
   
def parse_entitytype(current, infile):
   '''parse the type of the entity
   '''
   if current[1] == "port": 
      return (nextToken(infile), "port")
   else:
      printError(current[1], "port")
   
def parse_datatype(current, infile):
   '''parse the datatype and return Trit object that identifies the datatype
   '''
   if current[1] == "trit": 
      return (nextToken(infile), "trit")
   elif current[1] != "trit_vector": 
      printError(current[1], "trit|trit_vector")
   else:
      next = nextToken(infile)
      
      valueOne = compareTokens(next, "(", infile)
      if not isinstance(valueOne[1], int): 
         printError(valueOne[1], "integer")
      valueTwo = nextToken(infile)
      
      valueThree = compareTokens(valueTwo, "downto", infile)
      if not isinstance(valueThree[1], int): 
         printError(valueThree[1], "integer")
      valueFour = nextToken(infile)
      
      valueFive = compareTokens(valueFour, ")", infile)
      
   # construct datatype object for trit_vector and return it
   # along with the next token
   return (valueFive, "trit_vector")

def parse_flow(current, infile):
   '''identify the direction of the flow
   '''
   if current[1] == "in": 
      return (nextToken(infile), "in")
   elif current[1] == "out": 
      return (nextToken(infile), "out")
   elif current[1] == "inout": 
      return (nextToken(infile), "inout")
   else: 
      printError(current[1], "in|out|inout")      

def parse_port(current, infile):
   '''parse the port and return a 'port' object
   '''
   while True:
      # put identifier (current[1]) in 'port' object
      current = nextToken(f)
      if current[0] is None or not isinstance(current[1], str):
         break
         
   valueOne = compareTokens(current, ":", infile)
   valueTwo = parse_flow((valueOne[0], valueOne[1]), infile)
   valueThree = parse_datatype((valueTwo[0], valueTwo[1]), infile)

   if valueThree[1] == ";":
      parse_port(nextToken(infile), infile)
      
def parse_entity(current, infile):
   value1 = compareTokens(current, "entity", infile)
   
   if not isinstance(value1[1], str):
      printError(value1[1], "identifier")
   value2 = nextToken(infile)
   
   value3 = compareTokens(value2, "is", infile)
   value4 = parse_entitytype(value3, infile)
   value5 = compareTokens(value4, "(", infile)
   value6 = parse_port(value5, infile)
   value7 = compareTokens(value6, ")", infile)
   value8 = compareTokens(value7, "end", infile)
   
   if not isinstance(value8[1], str):
      printError(value8[1], "identifier")
   value9 = nextToken(infile)
   
   value9 = compareTokens(value8, ";", infile)
   
   # create entity object and return it
   return (value9, "entity")
   
def parse_program(current, infile):
   while current[1] == "entity":
      parse_entity(current, infile)
      
def Parser(filename):
   infile = file(filename, "r")
   parse_program(nextToken(infile), infile)
   
if __name__ == "__main__":
   Parser("ParserTest");
      

   