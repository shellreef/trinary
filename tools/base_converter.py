#!env python
# vim: set fileencoding=utf8
# Created: April 29, 2008
# Created by: Antonio Chavez
#
# Base converter

LOW_BOUND = ord('A') + 10

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
            not balanced.
    '''

    sum = 0
    tmp = 0
    neg = 1
    sign = 1
    count = 1

    for i in range(len(value) - 1, -1, -1):

        if value[i].isdigit():
            tmp = int(value[i])
        elif value[i] == '-' and i == len(value) - 1:
            sign = -1
        elif value[i] == 'i':
            neg = -1
        elif value[i].isalpha():
            tmp = ord(value[i].upper()) - LOW_BOUND
            sum = sum + tmp*neg


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
