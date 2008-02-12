#
#  tokenizer.py
#  
#
#  Created by Antonio on 2/10/08.
#  Copyright (c) 2008 __MyCompanyName__. All rights reserved.
#


trit_interger = {"i":-1, "0":0, "1":1}
trit_bool = {"i":False, "0":None, "1":True}
trit_value = (None, True, False)

trit_char = ("i", "1", "0")
symbols = ("(", ")", ",", ";", ":")
keywords = ("entity", "is", "port", "in", "out", "trit", "end")

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
   while (not not value) & (value.isspace()):
      value = infile.read(1)

   if (not value):
      return (None, value)
   else:
      return (True, value)
      
def isKeyword(infile, value):
   '''isKeyword: identifies token as keyword or symbol
      infile: object file
      value: string to identify
      return: keyword or identifier
   '''
   if (value in keywords): #string is a keyword
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
   if (not next):
      return (True, value)
   elif (next in trit_char):
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
   if (not next):
      return isKeyword(infile, value)
   elif (next.isalnum()):
      value = value + next
      return tokenizeString(infile, value)
   else:
      infile.seek(infile.tell() - 1)
      return isKeyword(infile, value)

def nextToken(infile):
   '''nextToken: read the next token from the given file
      infile: reference to file 
      return: next token in the file: False if no more tokens, else True.
   '''
   (result, value) = removeWhiteSpace(infile)
   
   if (result == None):   #EOF if no more tokens
      return (None, value)
   elif (value in trit_char):
      return tokenizeTrit(infile, value)
   elif (value.isalnum()):
      return tokenizeString(infile, value)
   elif (value in symbols):
      return (True, value)
   else: #invalid symbol detected
      return (False, value) 
      
      
