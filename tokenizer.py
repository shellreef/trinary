# vim: set fileencoding=utf8
#  tokenizer.py
#  
#
#  Created by Antonio on 2/10/08.
#  Trinary Research Project: Digital logic simulator
#  Update (02.17.2008) : Tokenizer will now identify integers.
#

import sys

from Keyword import *
from Identifier import *
from Token import *
from Trits import *
from Literal import *

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
        return value
    else:
        return value
        
def isKeyword(infile, value):
    '''isKeyword: identifies token as keyword or symbol
        infile: object file
        value: string to identify
        return: keyword or identifier
    '''
    infile.seek(infile.tell() - 1)
    if value in keywords: #string is a keyword
        return Keyword(value)
    else: #string is an identifier
        return Identifier(value)

def tokenizeVector(infile, value):
    '''tokenizeVector: find the next trit vector in the file
       infile: object file
       value: current value of trit vector
       return: Trit object containing the vector
    '''
    next = infile.read(1)

    if not next:
        raise "EOF file before end of vector."
    if next in trit_char:
        value = value + next
        return tokenizeVector(infile, value)
    elif next == "\"":
        return Trits(value)
    else:
        raise "Invalid symbol detected: |%s|" % (next, )

def tokenizeTrit(infile):
    '''tokenizeTrit: find the next trit or trit vector in the file
        infile: object file
        return: Trit object containing the trit
    '''
    next = infile.read(1)
    assert next in trit_char
    trit = Trits(next)

    next = infile.read(1)
    assert next == "'"
    return trit

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
        return Literal(str(value))

def nextToken(infile):
    '''nextToken: read the next token from the given file
        infile: reference to file 
        return: next token in the file: False if no more tokens, else True.
    '''
    value = removeWhiteSpace(infile)
    
    if value is None or len(value) == 0:      # None if no more tokens
        return None
    elif value == "'":
        return tokenizeTrit(infile)       # returns a Trit
    elif value == "\"":
        return tokenizeVector(infile, "")     # returns a Trit vector
    elif value.isalpha():
        return tokenizeString(infile, value)  # returns an Identifier
    elif value.isdigit():
        return tokenizeNumber(infile, value)  # returns a Literal
    elif value in symbols:
        return Token(value)
    else: #invalid symbol detected
        raise "Invalid symbol detected: |%s|" % (value, )
        
if __name__ == "__main__":
     f = file("testParser", "r")#sys.stdin
     while True:
          token = nextToken(f)
          print token
          if token is None:
                break

