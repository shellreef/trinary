#!/usr/bin/python
# vim: set fileencoding=utf8
# Created:20080211
# By Jeff Connelly

import Port

class Entity(object):

    def __init__(self, name, ports):
        self.name = name
        self.ports = ports

    def __str__(self):
        s = "<Entity: %s, %d ports" % (self.name, len(self.ports))
        i = 0
        for p in self.ports:
            i += 1
            s += "\n%d. %s" % (i, p)
        s += ">"
        return s

if __name__ == "__main__":
    a = Port.Port("a", Port.IN, None)
    b = Port.Port("b", Port.IN, None)
    c = Port.Port("c", Port.OUT, None)

    max = Entity("max", [a,b,c])
    print max
