# Created:200803010
# By Jeff Connelly
#
# Trinary Simon Says (very high level, prototype for asm)

import sys
import random

print "(Enter what Simon Says as [0,-1,1], for example)\n"

while True:
    said = [
            random.randint(-1,1),
            random.randint(-1,1),
            random.randint(-1,1)]
    print "Simon Says:",said
    user = None
    while user != said:
        try:
            user = input()
        except:
            continue
    print "Correct!\n"

