#!/usr/bin/python
# vim: set fileencoding=utf8
# Created: April 5, 2008
# By: Antonio Chavez
#
# Extended Trinary Evaluator: Evaluates trinary expression containing unary
#   and dyadic gates
#

from Expr import *
from Trits import *

import sys
import doctest
import traceback

dyadic_functions = {
    u"!" : {False:"i01", None:"001", True:"111"},    # TOR
    u"@" : {False:"iii", None:"i00", True:"i01"},    # TAND
    u"#" : {False:"111", None:"100", True:"10i"},    # TNAND
    u"$" : {False:"10i", None:"00i", True:"111"},    # TNOR

    # Alternate notation, sometimes easier to type
    u"+" : {False:"i01", None:"001", True:"111"},
    u"*" : {False:"iii", None:"i00", True:"i01"},

    # Grubb's notation
    u"%" : {False:"i01", None:"001", True:"111"},    # max
    u"^" : {False:"iii", None:"i00", True:"i01"},    # min
    u"&" : {False:"i01", None:"0i1", True:"11i"},    # exclusive max

}

def expr_dyadic(expression, variables):
    ''' This function applies a dyatic function.
        Recurses down string by calling expr_recurse.
    '''
    if not expression[0] in trit_char:
        first = variables[expression[0]]
    else:
        first = expression[0]

    f_value = trit_bool[first]

    if len(expression) == 1:
        return (f_value, "")

    f_next = expression[1]

    # found dyatic function. apply the function
    if f_next in dyadic_functions:
        f_apply = dyadic_functions[f_next]
        result, next_expr = expr_recurse(expression[2:], variables)

        t_func = Trits(f_apply[f_value])
        t_sec = Trits(trit_string[result])
        return (evaluate_unary(t_func, t_sec))[0], next_expr

    # found left paren. apply */AND
    elif f_next == "(":
        # first ( something ) => first AND something

        # apply AND to 'first' variable
        f_apply = dyadic_functions["*"]
        t_func = Trits(f_apply[f_value])

        # grab the expr to apply AND next
        result, next_expr = expr_recurse(expression[2:], variables)
        if next_expr[0] != ")":
            raise ("Expected \")\", found \"%s\"" % (next_expr[0])).encode("utf8")

        # evaluate: first AND (something)
        t_sec = Trits(trit_string[result])
        result = (evaluate_unary(t_func, t_sec))[0]
        next_expr =  next_expr[1:]

        # evaluate: (first AND something)(AND (next))*
        while len(next_expr) > 1:
            t_func = Trits(f_apply[result])
            result, next_expr = expr_recurse(next_expr, variables)
            t_sec = Trits(trit_string[result])
            result = (evaluate_unary(t_func, t_sec))[0]

        return result, next_expr

    elif f_next.isalpha():
        # first * second

        # grab function to use and grab the name of the second variable
        f_apply = dyadic_functions["*"]
        second = variables[f_next]

        # apply * to 'first' variable and parse second to trit
        t_func = Trits(f_apply[f_value])
        t_sec = Trits(trit_string[trit_bool[second]])

        # apply first * second, return (result, remaining expression string)
        return (evaluate_unary(t_func, t_sec))[0], expression[2:]

    else:
        return (f_value, expression[1:])

def expr_unary(expression, variables):
    count = 0
    while expression[count] in unary_functions:
        count = count + 1

    func = expression[:count]
    func = func + "a"

    result, next = expr_recurse(expression[count:], variables)
    e = Expr(func)
    return ((e.evaluate(Trits(trit_string[result])))[0], next)

def expr_recurse(expression, variables):
    if expression[0] in unary_functions:
        return expr_unary(expression, variables)
    elif expression[0].isalpha():
        return expr_dyadic(expression, variables)
    elif expression[0].isdigit():
        return expr_dyadic(expression, variables)
    elif expression[0] == "(":
        expression = expression[1:]
        result, next = expr_recurse(expression, variables)
        if next[0] != ")":
            raise ("Expected \")\", found \"%s\"" % (next[0])).encode("utf8")

        next = next[1:]
        f_apply = dyadic_functions["*"]

        # evaluate: (result)(AND (next))*
        while len(next) > 1:
            t_func = Trits(f_apply[result])
            result, next = expr_recurse(next, variables)
            t_sec = Trits(trit_string[result])
            result = (evaluate_unary(t_func, t_sec))[0]

        return result, next
    else:
        raise ("Unexpected character found \"%s\"" % (expression[0])).encode("utf8")

def trinary_eval(expression, variables):
    u'''Evaluates trinary expression.  Unary and Dyadic functions supported:
        Unary: /, ?, ?, Â¬, ?, ?, ?, ?, ?, ?
        Dyadic: see 'dyadic_functions' module global
       expression: String containing expression to evalutate
       variables: dictionary of variables and their values
       returns: The result of evaluating the expression.

>>> print trinary_eval("//A+B", {"A" : "i01", "B" : "1"})
111
>>> print trinary_eval("//A+B", {"A" : "1", "B" : "0"})
1
>>> print trinary_eval("//A+B", {"A" : "i", "B" : "0"})
0
>>> print trinary_eval("//A+B", {"A" : "0", "B" : "0"})
0
>>> print trinary_eval("//A+B", {"A" : "0", "B" : "1"})
1
>>> print trinary_eval("/(A+/B*C)",{"A":"0","B":"0","C":"1"})
0
>>> print trinary_eval("A$(/B*C)",{"A":"0","B":"0","C":"1"})
0
>>> print trinary_eval("A$(/B?C)",{"A":"0","B":"0","C":"1"})
0
    '''

    max_len = 1
    for i in expression:
        if i in variables:
            if len(variables[i]) > max_len:
                max_len = len(variables[i])

    if max_len == 1:
        result, lo = expr_recurse(expression, variables)
        return trit_string[result]

    func_vars = {}
    func_vars["i"] = "i"
    result = ""

    for i in range(max_len):
        for j in expression:
            if j in variables:
                if len(variables[j]) > 1:
                    func_vars[j] = variables[j][i]
                else:
                    func_vars[j] = variables[j]
        tmp, lo = expr_recurse(expression, func_vars)
        result += trit_string[tmp]

    return result


if __name__ == "__main__":
    # self-test
    doctest.testmod()

    variables = {}
    variables["i"] = "i"

    while True:
        flag = True
        print ">> ",
        line = unicode(sys.stdin.readline(), "utf8")
        if len(line) == 0:
            break
        line = line.strip()
        print
        if "=" in line:
            assignments = line.split(",")
            for a in assignments:
                name, value = a.split("=")

                if name == "i":
                    print "i is reserved, cannot be used as a variable name"
                else:
                    for k in value:
                        if not k in trit_char:
                            print u"%s, not a valid value" % (k)
                            flag = False
                    if flag:
                        print u"Assigning %s to %s" % (name, value)
                        variables[name] = value

        elif line == "":
            for k, v in variables.iteritems():
                print u"%s: %s" % (k, v)
        elif line in trit_char:
            print line
        else:
            try:
                print trinary_eval(line, variables)
            except:
                print "An error occured:"
                traceback.print_exc()

