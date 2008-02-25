#
#  Parser.py
#  
#
#  Created by Antonio on 2/17/08.
#  Trinary Research Project: Digital logic simulator
#  Upon testing the first phase of this program, correct input means no output.
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
    print "Expected '%s', found '%s'\n" % (expected, current[1])
    # raise exception    
    
def parse_datatype(current, infile):
    '''parse the datatype and return Trit object that identifies the datatype
    '''
    if current[1] == "trit": 
        temp = nextToken(infile)
        return (temp[0], temp[1], "trit")
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
    return (valueFive[0], valueFive[1], "trit_vector")

def parse_flow(current, infile):
    '''identify the direction of the flow
    '''
    temp = nextToken(infile)
    if current[1] == "in": 
        return (temp[0], temp[1], "in")
    elif current[1] == "out": 
        return (temp[0], temp[1], "out")
    elif current[1] == "inout": 
        return (temp[0], temp[1], "inout")
    else: 
        printError(current[1], "in|out|inout")        

def parse_port(next, infile):
    '''parse the port and return a 'port' object
    '''
    while 1:
        if not isinstance(next[1], str):
            printError(next[1], "identifier")
        cont = nextToken(infile)
        if cont[1] != ",":
            break
        else:
            next = nextToken(infile)
            
    valueOne = compareTokens(cont, ":", infile)
    valueTwo = parse_flow(valueOne, infile)
    valueThree = parse_datatype(valueTwo, infile)

    if valueThree[1] == ";":
        return parse_port(nextToken(infile), infile)
    
    return (valueThree[0], valueThree[1], "port",)
        
def parse_entitytype(current, infile):
    '''parse the type of the entity
    '''
    if current[1] == "port": 
        value1 = nextToken(infile)
        value2 = compareTokens(value1, "(", infile)
        value3 = parse_port(value2, infile)
        value4 = compareTokens(value3, ")", infile)
    else:
        printError(current[1], "entity type")        
        
    return (value4[0], value4[1], "port");

def parse_entity(current, infile):
    value1 = compareTokens(current, "entity", infile)
    
    if not isinstance(value1[1], str):
        printError(value1[1], "identifier")
    value2 = nextToken(infile)
    
    value3 = compareTokens(value2, "is", infile)
    value4 = parse_entitytype(value3, infile)
    value5 = compareTokens(value4, ";", infile)
    value6 = compareTokens(value5, "end", infile)
    
    if not isinstance(value6[1], str):
        printError(value6[1], "identifier")
    value7 = nextToken(infile)
    
    value8 = compareTokens(value7, ";", infile)
    
    # create entity object and return it
    return (value8[0], value8[1], "entity")
    
def parse_program(current, infile):
    while current[1] == "entity":
        current = parse_entity(current, infile)
        
def Parser(filename):
    infile = file(filename, "r")
    parse_program(nextToken(infile), infile)
    
if __name__ == "__main__":
    Parser("ParserTest");
        

