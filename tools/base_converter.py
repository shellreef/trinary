#!env python
# vim: set fileencoding=utf8
# Created: April 29, 2008
# Created by: Antonio Chavez
#
# Base converter

import sys, os
import Trits

MIN_VAL = 10
LOW_BOUND = ord('A') + MIN_VAL

int_cnvrt(value, base_frm, base_to):
    ''' int_cvrt: convert the number to the left of the decimal place
        value: string containing value to convert
        from: what base to convert from. Can be positive and negative.
            Negative numbers will represent balanced base.  Positive
            will represent unbalanced base.
        to: what base to convert to.

        Example: 3 = unbalanced base 3 (0, 1, 2)
                -3 = balanced base 3 (-1, 0, 1)
        Balanced bases can only be odd integers, for the obivious reason
            that even numbers are not good candidates for balanced numbering
            Example: -4 = (-1, 0, 1, 2) or (-2, -1, 0, 1).  Either system is
            not balanced.  Bases must also have a magnitude greater than 1.
        For balanced bases greater than 3, a negative number is represented
            with an 'i' next to it.
            Example: 4i21 => 4(-2)1
        Currently conversion balanced bases is not supported.  If balanced
            base is entered, the result will be returned in base 10.
        A negative sign before the number will negate the result.
    '''

    # check for magnitude greater than 1
    if abs(base_frm) < 2 or abs(base_to) < 2:
        print "bases must have magnitude greater than 1"
        raise SystemExit

    # check for a balanced negative base and derive magnitude
    if base_frm < 0 and base_frm*-1%2 != 1:
        print "base_from is even: negative bases must be odd integers"
        raise SystemExit
    elif base_frm < 0:
        magnitude_f = (base_frm*-1 - 1)/2
    else:
        magnitude_f = base_frm

    if base_to < 0 and base_to*-1%2 != 1:
        print "base_to is even: negative bases must be odd integers"
        raise SystemExit
    elif base_to < 0:
        magnitude_t = (base_to*-1 - 1)/2
    else:
        magnitude_t = base_to

    sum   = 0   # base 10 equivalent summation
    neg   = 1   # used when 'i' is encountered, it negates the previous digit
    sign  = 1   # sign of summation
    count = 1   # amount to multiply next digit by
    prev  = 1   # the value of the next digit
    cur   = 0   # current digit

    if magnitude_f >= MIN_VAL
        max_val = magnitude_f - MIN_VAL

    for i in range(len(value) - 1, -1, -1):

        if abs(base_frm) == 3:
            # Base 3 conversion
            if value[i] in Trits.trit_integer:
                sum = sum + Trits.trit_integer[value[i]]*count
                count = count*abs(base_frm)
            else:
                print "%s invalid input", value[i]
                raise SystemExit

        elif value[i].isdigit():
            # 0 <-> 9
            cur = int(value[i])

            if cur > magnitude_f:
                print "%s: invalid input", value[i]
                raise SystemExit

            sum = sum + prev*neg*count

            # reset variables to appropiate values
            prev = cur
            neg = 1
            count = count*abs(base_frm)

        elif value[i] == '-' and i == len(value) - 1:
            # negate the whole number
            sign = -1
        elif value[i] == 'i':
            # negate prev number
            neg = -1
        elif magnitude_f >= MIN_VAL and value[i].isalpha():
            # 10 <-> magnitude_f
            cur = ord(value[i].upper()) - LOW_BOUND

            if cur > magnitude_f:
                print "%s: invalid input", value[i]
                raise SystemExit

            sum = sum + prev*neg*count

            # reset variables to appropriate values
            prev = cur
            neg = 1
            count = count*abs(base_frm)

        else:
            print "%s: invalid input", value[i]
            raise SystemExit

    # sum up remaining digit
    sum = sum + prev*neg*count
    sum = sign*sum

    # return base 10 if desired base is balanced
    if base_f < 0:
        return "" + sum

    # compute unbalanced conversion
    result = ""
    quotient = sum
    remainder = 0

    while quotient != 0:
        remainder = quotient%magnitude_t
        quotient = quotient/magnitude_t
        result = "" + remainder + result

    return result

''' NOTES
    useful things to know for implementation
    char to int: ord('a') = 97 ASCII
    int to char: chr(97)  ASCII
    char to int: int('4')
    a = "hi6"
    a[0].isalpha() => true
    a[2].isdigit() => true
    a[0].upper()   => "H"
    a[2].upper()   => "1"

    s.split(".")   => returns list of strings broken up by "."
    "1010.3930"    => ["1010", "3930"]

    s = ".".join(lis_digits) => combine elements in list by "."
'''
