#!env python
# vim: set fileencoding=utf8
# Created: April 29, 2008
# Created by: Antonio Chavez
#
# Base converter

LOW_BOUND = ord('A') - 10

int_cnvrt(value, from, to):
    ''' int_cvrt: convert the number to the left of the decimal place
        value: string containing value to convert
        from: what base to convert from. Can be positive and negative.
            Negative numbers will represent balanced base.  Positive
            will represent unbalanced base.
        to: what base to convert to.
    '''

''' NOTES 
    useful things to know for implementation
    char to int: ord('a')
    int to char: chr(97)
    a = "hi6"
    a[0].isalpha() => true
    a[2].isdigit() => true
    a[0].upper()   => "H"
    a[2].upper()   => "1"

    s.split(".")   => returns list of strings broken up by "."
    "1010.3930"    => ["1010", "3930"]

    s = ".".join(lis_digits) => combine elements in list by "."
'''
