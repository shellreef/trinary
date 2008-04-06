#!/usr/bin/python
# vim: set fileencoding=utf8
# Created: April 5, 2008
# By: Antonio Chavez
#
# Extended Trinary Evaluator: Evaluates trinary expression containing unary
#   and dyatic gates
#

from Trits import *
from Expr import *

dyatic_functions = {
    "+" : {False:"i01", None:"001", True:"111"},
    "*" : {False:"iii", None:"i00", True:"i01"}
}    

def expr_unary(expression, variables):
    count = 0
    while expression[count] in Expr.unary_functions:
        count++

    func = expression[:count]
    func = func + "a"

    result, next = expr_recurse(expression[count:], variables)
    e = Expr.Expr(func)
    return (e.evaluate(result), next)

def expr_recurse(expression, variables):
    if expression[0] in Expr.unary_functions:
        return expr_unary(expression, variables)
    elif isalpha(expression[0]):
        return expr_dyatic(expression, variables)
    elif expression == "(":
        expression = expression[1:]
        result, next = expr_recurse(expression, variables)
        if next[0] != ")":
            raise "Expected \")\", found \"%s\"" % (next[0])
        return result, next[1:]
    else:
        raise "Unexpected character found \"%s\"" % (expression[0]) 

def trinary_eval(expression, variables):
    '''Evaluates trinary expression.  Unary and Dyatic functions supported:
        Unary: /, ∇, ∆, ¬, ⌐, ↘, ↗, ∩, ∪, ♨
        Dyatic: + (max), * (min)
       expression: String containing expression to evalutate (ie "♨(A+/B*C)").
       variables: dictionary of variables and their values 
         (ie {"A" = "i", "B" = "1", "C" = "0"}).
       returns: The result of evaluating the expression.
    '''
    (result, lo) = expr_recurse(expression, variables)
    return result
    
