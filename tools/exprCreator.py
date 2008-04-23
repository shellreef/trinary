#!env python
# vim: set fileencoding=utf8
# Created: April 22, 2008
#
# Expression manipulator

import sys, os

sd = {"i":"i", "0":"i", "1":"0"}
su = {"i":"0", "0":"1", "1":"1"}
s01 = {"i":"i", "0":"1", "1":"0"}
si0 = {"i":"0", "0":"i", "1":"1"}
ru = {"i":"0", "0":"1", "1":"i"}
rd = {"i":"1", "0":"i", "1":"0"}
inv = {"i":"1", "0":"0", "1":"i"}

basic_funcs = {"sd":sd, "su":su, "s01":s01, "si0":si0, "ru":ru, "rd":rd, "inv":inv}


def get_expr(desired):
    if len(desired) != 3:
        print "truth table must be 3 chars wide"
        raise SystemExit

