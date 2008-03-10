#
#  Parser.py
#  
#
#  Created by Antonio on 2/17/08.
#  Trinary Research Project: Digital logic simulator
#  Upon testing the first phase of this program, correctly defined programs generate
#    no output.
#

from tokenizer import nextToken
from Keyword import *
from Token import *
from Trits import *
from Literal import *

def compareIdentifiers(current, expected, infile):
    '''compare current identifier with expected identifier. If they are equal then return
       the next token. If they are not then an raise and exeption and exit the program.
    '''
    if not isinstance(current, Identifier):
        raise "Expected '%s', found '%s'" % (expected, current)
    else:
        return nextToken(infile)

def compareTokens(current, expected, infile):
    '''compare token current with expected token.  If they are equal then return the next
    token, if they are not then an raise exeption and exit program.
    '''
    if not isinstance(current, Token) or  current.name != expected.name:
        raise "Expected '%s', found '%s'" % (expected, current)
    else:
        return nextToken(infile)

def compareKeywords(current, expected, infile):
    '''compare current keyword with expected keyword. If they are equal then return
       the next token. If they are not then an raise and exeption and exit the program.
    '''
    if not isinstance(current, Keyword) or  current.name != expected.name:
        raise "Expected '%s', found '%s'" % (expected, current)
    else:
        return nextToken(infile)

def printError(current, expected):
    '''Function prints an error message and raises an exeption
    '''
    raise "Expected '%s', found '%s'\n" % (expected, current)

def parse_datatype(current, infile):
    '''parse the datatype and return Trit object that identifies the datatype
    '''
    if isinstance (current, Identifier):
        if compareTokens(current, Identifier("trit")):
            temp = nextToken(infile)
            return (temp[0], temp[1], "trit")
        elif not isinstance (current, Identifier("trit_vector")):
            printError(current[1], Identifier("trit|tritvector"))
        else:
            next = nextToken(infile)
        
        valueOne = compareTokens(next, Token("("), infile)
        if not isinstance(valueOne, Literal):
            printError(valueOne, Literal("integer"))
        valueTwo = nextToken(infile)
        
        valueThree = compareTokens(valueTwo, Keyword("downto"), infile)
        if not isinstance(valueThree, Literal):
            printError(valueThree, Literal("integer"))
        valueFour = nextToken(infile)
        
        valueFive = compareTokens(valueFour, Token(")"), infile)
        
    # construct datatype object for trit_vector and return it
    # along with the next token
    return (valueFive, "trit_vector")

def parse_flow(current, infile):
    '''identify the direction of the flow of the port
    '''
    if isinstance(current, Keyword):
        if current.name == "in":
            return (nextToken(infile), "in")
        elif current.name == "out":
            return (nextToken(infile), "out")
        elif current.name == "inout":
            return (nextToken(infile), "inout")

    printError(current, Keyword("in|out|inout"))

def parse_port(next, infile):
    '''parse the port and return a 'port' object
    '''
    names = []

    while 1:
        cont = compareIdentifiers(next, Identifier(" "), infile)
        names.append(next.name)
        if not isinstance(cont, Token) or cont.name != ",":
            break
        else:
            next = nextToken(infile)
            
    valueOne = compareTokens(cont, Token(":"), infile)
    (valueTwo, type) = parse_flow(valueOne, infile)
    valueThree = parse_datatype(valueTwo, infile)

    if isinstance (valueThree[0], Token) and valueThree[0].name == ";":
        return parse_port(nextToken(infile), infile)
    else:
        return (valueThree[0], "port")
        
def parse_entitytype(current, infile):
    '''parse the type of the entity
    '''
    value1 = compareKeywords(current, Keyword("port"), infile)
    value2 = compareTokens(value1, Token("("), infile)
    value3 = parse_port(value2, infile)
    value4 = compareTokens(value3, Token(")"), infile)
        
    return (value4, Port("port"));

def parse_entity(current, infile):
    value1 = compareKeywords(current, Keyword("entity"), infile)
    value2 = compareIdentifiers(value1, Identifier(" "), infile)
    value3 = compareKeywords(value2, Keyword("is"), infile)
    value4 = parse_entitytype(value3, infile)
    value5 = compareTokens(value4, Token(";"), infile)
    value6 = compareKeywords(value5, Keyword("end"), infile)
    value7 = compareIdentifiers(value6, Identifier(" "), infile)
    value8 = compareTokens(value7, Token(";"), infile)
    
    # create entity object and return it
    return (value8, Entity("entity"))
    
def parse_program(current, infile):
    while isinstance(current, Keyword):
        if current.name == "entity":
            current = parse_entity(current, infile)
        
def Parser(filename):
    '''Parse a file into components.
       Arguments: filename of file
    '''
    infile = file(filename, "r")
    parse_program(nextToken(infile), infile)
    
if __name__ == "__main__":
    Parser("ParserTest");

