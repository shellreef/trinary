#!env python
# vim: set fileencoding=utf8
# Created: April 22, 2008
#
# Expression manipulator

import sys, os
import Trits

sd  = {"i":"i", "0":"i", "1":"0"}
su  = {"i":"0", "0":"1", "1":"1"}
s01 = {"i":"i", "0":"1", "1":"0"}
si0 = {"i":"0", "0":"i", "1":"1"}
ru  = {"i":"0", "0":"1", "1":"i"}
rd  = {"i":"1", "0":"i", "1":"0"}
inv = {"i":"1", "0":"0", "1":"i"}

sd_t  = Trits.Trits("ii0")
su_t  = Trits.Trits("011")
s01_t = Trits.Trits("i10")
si0_t = Trits.Trits("0i1")
ru_t  = Trits.Trits("01i")
rd_t  = Trits.Trits("1i0")
inv_t = Trits.Trits("10i")

buf_t = Trits.Trits("i01")
ci_t  = Trits.Trits("iii")
c0_t  = Trits.Trits("000")
c1_t  = Trits.Trits("111")

basic_funcs = {"sd":sd, "su":su, "s01":s01, "si0":si0, "ru":ru, "rd":rd, "inv":inv}
basic_f_t = {"sd":sd_t, "su":su_t, "s01":s01_t, "si0":si0_t, "ru":ru_t, "rd":rd_t, "inv":inv_t}

def get_expr(desired):
    if len(desired) != 3:
        print "truth table must be 3 chars wide"
        raise SystemExit

    end = Trits.Trits(desired)
    crnt = Trits.Trits("i01")
    functions = []
