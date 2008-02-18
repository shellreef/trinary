# vim: set fileencoding=utf8
#  tokenizer.py
#  
#
#  Created by Antonio on 2/10/08.
#  Trinary Research Project: Digital logic simulator
#  Update (02.17.2008) : Tokenizer will now identify integers.
#


trit_interger = {"i":-1, "0":0, "1":1}
trit_bool = {"i":False, "0":None, "1":True}
trit_value = (None, True, False)

trit_char = ("i", "1", "0")
symbols = ("(", ")", ",", ";", ":", "'", "{", "}", "^")
keywords = ("entity", "is", "port", "in", "out", "trit", "end", "inout", 
            "downto" )

def parseTrit(trit):
   '''This function returns the boolean value of a trit.
      trit: trit represented by a characater
      return: boolean value
   '''
   return trit_bool[trit]
   
def parseTritVector(trit_string):
   '''parseTritVector: take a string of trits and return a trit vector
      trit_string: string to parse into a trit vector
      return: trit vector
   '''
   result = []
   for i in range(len(trit_string)):
      result.append(parseTrit(trit_string[i]))
   return tuple(result)

# tokenizer

def removeWhiteSpace(infile):
   '''removeWhiteSpace: remove preceding white space in the buffer
      infile: file containing the chars to read
      return: False if no more 
          valid chars are in the buffer or True if there are still valid
         chars in the buffer
   '''
   value = infile.read(1)
   while value and value.isspace():
      value = infile.read(1)

   if not value:
      return (None, value)
   else:
      return (True, value)
      
def isKeyword(infile, value):
   '''isKeyword: identifies token as keyword or symbol
      infile: object file
      value: string to identify
      return: keyword or identifier
   '''
   infile.seek(infile.tell() - 1)
   if value in keywords: #string is a keyword
      return (True, value)
   else: #string is an identifier
      return (True, value)
   
def tokenizeTrit(infile, value):
   '''tokenizeTrit: find the next trit or trit vector in the file
      infile: object file
      value: current value of trit/trit vector
      return: string containing a trit/trit vector
   '''
   next = infile.read(1)
   if not next:
      return (True, value)
   elif next in trit_char:
      value = value + next
      return tokenizeTrit(infile, value)
   else:
      infile.seek(infile.tell() - 1)
      return (True, value)
      
def tokenizeString(infile, value):
   '''tokenizeString: find the next keyword or identifier in the file
      infile: object file
      value: current value of the keyword/identifier
      return: string containing the keyword/identifier
   '''
   next = infile.read(1)
   if next.isalnum():
      value = value + next
      return tokenizeString(infile, value)
   else:
      return isKeyword(infile, value)
      
def tokenizeNumber(infile, value):
   '''tokenizeNumber: identify the next integer in the file
   '''
   next = infile.read(1)
   if next.isdigit():
      value = value + next
      return tokenizeNumber(infile, value)
   else:
      infile.seek(infile.tell() - 1)
      return (True, str(value))

def nextToken(infile):
   '''nextToken: read the next token from the given file
      infile: reference to file 
      return: next token in the file: False if no more tokens, else True.
   '''
   result, value = removeWhiteSpace(infile)
   
   if result is None:   #EOF if no more tokens
      return (None, "EOF")
   elif value == "'":
      return tokenizeTrit(infile, value)
   elif value.isalpha():
      return tokenizeString(infile, value)
   elif value.isdigit():
      return tokenizeNumber(infile, value)
   elif value in symbols:
      return (True, value)
   else: #invalid symbol detected
      return (None, value) 
      
if __name__ == "__main__":
    f = file("ParserTest", "r")
    while True:
        token = nextToken(f)
        print token
        if token[0] is None or token[1] == "":
            break
