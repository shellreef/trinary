#!env python
# vim: set fileencoding=utf8
# Created: April 29, 2008
# Created by: Antonio Chavez
#
# Base converter

import sys, os, string
import Trits

MIN_VAL    = 10
LOW_BOUND  = ord('A') + MIN_VAL
BASE_3     = 3
BALANCED_3 = 3

class BaseError(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return "BaseError: %s" % (self.msg,)

def int_cnvrt(value, base_frm, base_to):
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
        raise BaseError("bases must have magnitude greater than 1")

    # check for a balanced negative base and derive magnitude
    if base_frm < 0 and base_frm*-1%2 != 1:
        raise BaseError("base_from is even: negative bases must be odd integers")
    elif base_frm < 0:
        magnitude_f = (base_frm*-1 - 1)/2
    else:
        magnitude_f = base_frm
    #magnitude_f = abs(base_frm)

    if base_to < 0 and base_to*-1%2 != 1:
        raise BaseError("base_to is even: negative bases must be odd integers")
    elif base_to < 0:
        magnitude_t = (base_to*-1 - 1)/2
    else:
        magnitude_t = base_to
    #magnitude_t = abs(base_to)

    sum   = 0   # base 10 equivalent summation
    neg   = 1   # used when 'i' is encountered, it negates the previous digit
    sign  = 1   # sign of summation
    count = 1   # amount to multiply next digit by
    prev  = 1   # the value of the next digit
    cur   = 0   # current digit

    if magnitude_f >= MIN_VAL:
        max_val = magnitude_f - MIN_VAL

    for i in range(len(value) - 1, -1, -1):

        if base_frm == -3:
            # Base 3 conversion
            if value[i] in Trits.trit_integer:
                sum = sum + (Trits.trit_integer[value[i]])*count
                count = count*abs(base_frm)
            else:
                raise BaseError("0: invalid input %s" % (value[i],))

        elif value[i].isdigit():
            # 0 <-> 9
            cur = int(value[i])

            if cur > magnitude_f:
                raise BaseError("1: invalid input %s" % (value[i],))
            if i != len(value) -1:
                sum = sum + prev*neg*count

                # reset variables to appropiate values
                neg = 1
                count = count*abs(base_frm)

            prev = cur

        elif value[i] == '-' and i == 0:
            # negate the whole number
            sign = -1
        elif value[i] == 'i':
            # negate prev number
            neg = -1
        elif magnitude_f >= MIN_VAL and value[i].isalpha():
            # 10 <-> magnitude_f
            cur = ord(value[i].upper()) - LOW_BOUND

            if cur > magnitude_f:
                raise BaseError("2: invalid input %s" % (value[i],))

            if i != len(value) -1:
                sum = sum + prev*neg*count

                # reset variables to appropriate values
                neg = 1
                count = count*abs(base_frm)

            prev = cur

        else:
            raise BaseError("3: invalid input %s at index = %s" % (value[i], i))

    # sum up remaining digit
    if base_frm != -3:
        sum = sum + prev*neg*count
        sum = sign*sum

    # if requested base 10, then we are done
    if base_to == 10 or sum == 0:
        return "" + str(sum)

    if base_to == -3:
        rslt = balanced_conversion(sum, base_to)
        return rslt
    # return base 10 if desired base is balanced
    elif base_to < 0:   
        return "" + str(sum)

    # compute unbalanced conversion
    result    = ""
    quotient  = sum
    remainder = 0

    while quotient != 0:
        remainder = quotient%magnitude_t
        quotient  = quotient/magnitude_t
        result    = str(remainder) + result

    return result

def balanced_conversion(sum, base_to):

    #check for no need for conversion
    if sum == 0:
        return "0"

    tmp_sum =  0
    if sum > 0:
        count  = 1   
        result = [] 
        while tmp_sum < sum:
            tmp_sum = tmp_sum + count
            result.insert(0, "1")
            count   = count*BASE_3

        #if max value then we are  done
        if tmp_sum == sum:
            tmp_str = string.join(result, '')
            return tmp_str

        found, rslt = find_balanced_3(sum, result, len(result) - 1)
        tmp_str = string.join(result, '')
        return tmp_str

    elif sum < 0:
        count  = -1   
        result = [] 
        while tmp_sum > sum:
            tmp_sum = tmp_sum + count
            result.insert(0, "i")
            count   = count*BASE_3

        #if max value then we are  done
        if tmp_sum == sum:
            tmp_str = string.join(result, '')
            return tmp_str

        found, rslt = find_balanced_3(sum, result, len(result) - 1)
        tmp_str = string.join(result, '')
        return tmp_str


def find_balanced_3(value, result, iteration):
    
    if iteration < 0:
        return False, ""

    # set result[iteration] to "0"
    result.pop(iteration)
    result.insert(iteration, "0")
    tmp_sum = balanced_3_value(result)
    if tmp_sum == value:
        return True, result
    # iterate down to lower indexes
    found, str_rslt = find_balanced_3(value, result, iteration - 1)
    if found:
        return True, str_rslt

    # set result[iteration] to "i"
    result.pop(iteration)
    result.insert(iteration, "i")
    tmp_sum = balanced_3_value(result)
    if tmp_sum == value:
        return True, result
    # iterate down to lower indexes
    found, str_rslt = find_balanced_3(value, result, iteration - 1)
    if found:
        return True, str_rslt

    # set result[iteration] to "1"
    result.pop(iteration)
    result.insert(iteration, "1")
    tmp_sum = balanced_3_value(result)
    if tmp_sum == value:
        return True, result
    # iterate down to lower indexes
    found, str_rslt = find_balanced_3(value, result, iteration - 1)
    if found:
        return True, str_rslt

    return False, ""

def balanced_3_value(value):

    sum   = 0
    count = 1

    for i in range(len(value) - 1, -1, -1):
        # Base 3 conversion
        sum   = sum + (Trits.trit_integer[value[i]])*count
        count = count*BASE_3

    return sum

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

if __name__ == "__main__":
    print int_cnvrt("8", 10, 2)

    while True:
        print ">> ",
        line = unicode(sys.stdin.readline(), "utf8")
        if len(line) == 0:
            break
        line = line.strip()
        print

        try:
            val, frm, to = line.split(",")
            frm = int(frm)
            to  = int(to)

            print int_cnvrt(val, frm, to)
        except Exception, e:
            print "Failed: %s %s" % (type(e), e,)

