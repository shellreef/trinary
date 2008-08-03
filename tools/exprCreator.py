#!env python
# vim: set fileencoding=utf8
# Created: April 22, 2008
#
# Expression creator
#   Currently produces list of functions to apply.
#   Use get_unary to find a unary funcion.
#       ie. get_unary("ii0")
#   Use get_dyadic to find a dyadic funcion.
#       ie. get_dyadic("ii0111001")
#   Todo: add utf support names and return string expression

import sys, os
import Trits

sd  = Trits.Trits("ii0") # shift down	
su  = Trits.Trits("011") # shift up
s01 = Trits.Trits("i10") # swap 0/1
si0 = Trits.Trits("0i1") # swap i/0
ru  = Trits.Trits("01i") # rotate up
rd  = Trits.Trits("1i0") # rotate down
inv = Trits.Trits("10i") # inverter

buf = Trits.Trits("i01") # identity
ci  = Trits.Trits("iii") # constant i
c0  = Trits.Trits("000") # constant 0
c1  = Trits.Trits("111") # constant 1

valid_chars = ("i", "0", "1")
map_t = {False:0, None:1, True:2}
map_str = {False:"i", None:"0", True:"1"}

basic = {"}":sd, "{":su, ">":s01, "<":si0, "[":ru,
             "]":rd, "/":inv}
easy = {"B":buf, "i":ci, "0":c0, "1":c1}


def get_dyadic(desired):
    ''' get_dyadic: get expression for a dyadic function
        desired: string representation of desired function
        returns: Returns a tuple.  True or false (if function was not found).
            A list of expressions for each unary function needed to build
            the desired function.
    '''

    if len(desired) != 9:
        print "truth table must be 9 chars wide"
        raise SystemExit

    for i in range(0, 9):
        if not desired[i] in valid_chars:
            print "%s not a valid character" % desired[i]
            raise SystemExit

    goal_1 = desired[0:3]
    goal_2 = desired[3:6]
    goal_3 = desired[6:9]

    result_1, gates_1 = get_unary(goal_1)
    result_2, gates_2 = get_unary(goal_2)
    result_3, gates_3 = get_unary(goal_3)

    if result_1 and result_2 and result_3:
        return True, gates_1, gates_2, gates_3

    return False, [], [], []


def get_unary(desired):
    ''' get_unary: get expression for a unary function
        desired: string representation of desired function
        returns: Returns a tuple. True or false (if function was not found)
            and a list of functions to apply to get the desired function.
            The list is read from left to right.
    '''

    # do some input error checking
    if len(desired) != 3:
        print "truth table must be 3 chars wide"
        raise SystemExit

    for i in range(0, 3):
        if not desired[i] in valid_chars:
            print "%s not a valid character" % desired[i]
            raise SystemExit

    goal = Trits.Trits(desired)
    crnt = Trits.Trits("i01")
    l_gates = []

    for i in easy:
        if goal.equals(easy[i]):
            return True, [i]

    count = 0
    end_cond = True
    while end_cond and count < 4:
        end_cond, l_gates = recurse_unary(crnt, goal, [], count)
        end_cond = not end_cond
        count = count + 1

    return (not end_cond, l_gates)

def recurse_unary(crnt, goal, l_gates, depth):
    ''' recurse_unary: attempt to locate a function sequence that makes the
            goal function
        crnt: current function result
        goal: the desired function result
        l_gates: list of gates to apply to get to crnt
        count: the number of gate levels
        returns: true and list of gates if goal is met, else false and []
    '''

    # check the basic gates for an answer
    if depth == 0:
        return test_all(crnt, goal, l_gates)

    else:
        # for each basic gate attempt to find the desired function
        for i in basic:
            cndt = eval_one(crnt, i)
            l_gates.append(i)

            if cndt.equals(goal):
                return True, l_gates

            status, gates = recurse_unary(cndt, goal, l_gates, depth - 1)

            if status:
                return True, gates

            l_gates.pop()

    return (False, [])

def test_all(crnt, goal, l_gates):
    ''' test_all: attempt to find a basic function that fulfills the desired
            gate.
        crnt: the current evaluation of the function
        goal: the desired function result
        l_gates: list of gates currently applied to crnt
        returns: true and list of gates if goal is met, else false and []
    '''

    for i in basic:
        cndt = eval_one(crnt, i)

        # if desired function is found then return true and the list of gates
        # to apply
        if cndt.equals(goal):
            l_gates.append(i)
            return True, l_gates

    return False, []

def eval_one(crnt, func):
    ''' eval_one: the input given in crnt with function 'func'
        crnt: Trits object as input
        func: function to apply
        return: Trist object containing result
    '''

    next = ""
    for i in range(0, 3):
        next = next + map_str[basic[func][map_t[crnt[i]]]]

    return Trits.Trits(next)

if __name__ == "__main__":
    result, gates = get_unary("11i")
    if result:
        print gates

    result, gates1, gates2, gates3 = get_dyadic("i0111000i")
    if result:
        print gates1, gates2, gates3

    print "At prompt '>>' type unary (010) or dyadic (1010i1ii0)"

    while True:
        valid = True
        print ">> ",
        line = sys.stdin.readline()
        line = line.strip()
        print

        if len(line) == 3 or len(line) == 9:

            for i in range(0, len(line)):
                if not line[i] in valid_chars:
                    valid = False

            if valid:
                if len(line) == 3:
                    result, gates = get_unary(line)
                    print gates
                if len(line) == 9:
                    result, gates1, gates2, gates3 = get_dyadic(line)
                    print gates1, gates2, gates3

