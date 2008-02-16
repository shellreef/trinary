#!/usr/bin/python
# Created:20080216
# By Jeff Connelly
#
# Trinary expression evaluator

from Symbols import *
from Trits import Trits

unary_functions = {
        NTI: Trits("1ii"),
        STI: Trits("10i"),
        PTI: Trits("11i"),
        FD: Trits("001"),
        RD: Trits("i00")
        }

def evaluate_unary(function, inputs):
    """Given a unary function number in a Trits object, f, pass
    all the trits in the inputs object through the function."""

    assert isinstance(function, Trits), \
            "Need to pass a Trits object as function"
    assert isinstance(inputs, Trits), \
            "You must pass a Trits object in inputs"

    outputs = []
    for t in inputs:
        outputs.append({
                False: function[0],
                None: function[1],
                True: function[2]
                }[t])

    return Trits(outputs)

class Expr(object):
    def __init__(self, s):
        assert len(s) > 0, "Empty string can't evaluate"

        variable = s[-1]
        assert variable.isalpha(), "Only accept expressions of form xxxxA, where x=unary operators, A=variable"
        print "Variable:", variable

        # Evaluate gates from right-to-left
        unary_gates = reversed(s[:-1])

        # Start with identity function
        total_unary = Trits("i01")

        # Evaluate with unary function on the identity
        for gate in unary_gates:
            print "Gate:", gate.encode('utf8')
            total_unary = evaluate_unary(unary_functions[gate], total_unary)

        # Now total_unary is the function# of all the unary gates
        self.total_unary = total_unary

    def evaluate(self, inputs):
        return evaluate_unary(self.total_unary, inputs)

if __name__ == "__main__":
    s = RD + NTI + "a"
    print "Expression:", s.encode('utf8')
    e = Expr(s)
    print "Total unary function is:", e.total_unary
    print

    ins = Trits("iiiiiiiii00000001111111")
    print "Passing in trit vector as 'a':"
    print "a:\t", ins
    print s.encode('utf8') + ":\t", e.evaluate(ins)

