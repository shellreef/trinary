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
from Identifier import *
from Port import *
from Entity import *

def compareIdentifiers(current, expected, infile):
    '''compare current identifier with expected identifier. If they are equal then return
       the next token. If they are not then an raise and exeption and exit the program.
    '''
    if not isinstance(current, Identifier):
        raise "Expected '%s', found '%s'" % (expected, current)
    else:
        print "parsed: %s" % current #for debugging
        return nextToken(infile)

def compareTokens(current, expected, infile):
    '''compare token current with expected token.  If they are equal then return the next
    token, if they are not then an raise exeption and exit program.
    '''
    if not isinstance(current, Token) or  current.name != expected.name:
        raise "Expected '%s', found '%s'" % (expected, current)
    else:
        print "parsed: %s" % current #for debugging
        return nextToken(infile)

def compareKeywords(current, expected, infile):
    '''compare current keyword with expected keyword. If they are equal then return
       the next token. If they are not then an raise and exeption and exit the program.
    '''
    if not isinstance(current, Keyword) or  current.name != expected.name:
        raise "Expected '%s', found '%s'" % (expected, current)
    else:
        print "parsed: %s" % current #for debugging
        return nextToken(infile)

def printError(current, expected):
    '''Function prints an error message and raises an exeption
    '''
    raise "Expected '%s', found '%s'\n" % (expected, current)

def parse_datatype(current, infile):
    '''parse the datatype and return Trit object that identifies the datatype
    '''
    if isinstance (current, Keyword):
        if current.name == "trit":
            return (nextToken(infile), "trit", 0)
        next =  compareKeywords(current, Keyword("trit_vector"), infile)

        valueOne = compareTokens(next, Token("("), infile)

        if not isinstance(valueOne, Literal):
            printError(valueOne, Literal("integer"))
        elif valueOne.value <= 0:
            printError(valueOne, Literal("greater than zero"))
        valueTwo = nextToken(infile)

        length = valueOne.value + 1

        valueThree = compareTokens(valueTwo, Keyword("downto"), infile)
        if not isinstance(valueThree, Literal):
            printError(valueThree, Literal("integer"))
        elif valueThree.value != 0:
            printError(valueThree, Literal(0))
        valueFour = nextToken(infile)
        
        valueFive = compareTokens(valueFour, Token(")"), infile)
        
        # construct datatype object for trit_vector and return it
        # along with the next token
        return (valueFive, "trit_vector", length)

    printError(current, Keyword("trit|trit_vector"))

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

def parse_port(next, infile, entity):
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
    (valueTwo, flow) = parse_flow(valueOne, infile)
    (valueThree, type, length) = parse_datatype(valueTwo, infile)

    # store derived port information into Entity
    for i in names:
        if flow == "in":
            entity.IN.append(Port.Port(i, Port.IN, type, length))
        elif flow == "out":
            entity.OUT.append(Port.Port(i, Port.OUT, type, length))
        else:
            entity.INOUT.append(Port.Port(i, Port.INOUT, type, length))

    # recurse if there are more ports defined
    if isinstance (valueThree, Token) and valueThree.name == ";":
        return parse_port(nextToken(infile), infile, entity)
    else:
        return (valueThree, entity)
        
def parse_entitytype(current, infile, entity):
    '''parse the type of the entity
    '''
    value1 = compareKeywords(current, Keyword("port"), infile)
    value2 = compareTokens(value1, Token("("), infile)
    (value3, rtn) = parse_port(value2, infile, entity)
    value4 = compareTokens(value3, Token(")"), infile)
        
    return (value4, entity);

def parse_entity(current, infile):
    '''Parse the entity'''
    value1 = compareKeywords(current, Keyword("entity"), infile)
    value2 = compareIdentifiers(value1, Identifier(" "), infile)

    # create entity object
    entity = Entity(value1.name, [])

    value3 = compareKeywords(value2, Keyword("is"), infile)
    (value4, rtn) = parse_entitytype(value3, infile, entity)
    value5 = compareTokens(value4, Token(";"), infile)
    value6 = compareKeywords(value5, Keyword("end"), infile)
    value7 = compareIdentifiers(value6, Identifier(" "), infile)

    # identifier names must match
    if value6.name != value1.name:
        printError(value6, value1)

    value8 = compareTokens(value7, Token(";"), infile)
    
    # return Entity object
    return (value8, entity)

def parse_architecture(current, infile):
    '''Parse the archtecture component.'''
    value1 = compareKeywords(current, Keyword("architecture"), infile)
    value2 = compareKeywords(value1, Keyword("dataflow"), infile)
    value3 = compareKeywords(value2, Keyword("of"), infile)
    value4 = compareIdentifiers(value3, Identifier(" "), infile)

    archi = Architecture(value3.name)

    value5 = compareKeywords(value4, Keyword("is"), infile)
    value6 = compareKeywords(value5, Keyword("begin"), infile)
    value7 = compareKeywords(value6, Keyword("end"), infile)
    value8 = compareKeywords(value7, Keyword("dataflow"), infile)
    value9 = compareTokens(value8, Token(";"), infile)

    return (value9, archi)
    
def parse_program(current, infile):
    '''parse the individual components of the program'''
    while isinstance(current, Keyword):
        if current.name == "entity":
            (current, entity) = parse_entity(current, infile)
            print "Parsed Entity: %s" % entity
        elif current.name == "architecture":
            (current, architecture) = parse_architecture(current, infile)
            print "Parsed Architecture: %s" % architecture
        
def Parser(filename):
    '''Parse a file into components.
       Arguments (1): filename of the file to parse.
    '''
    infile = file(filename, "r")
    parse_program(nextToken(infile), infile)
    
if __name__ == "__main__":
    Parser("testParser");

