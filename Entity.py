#!/usr/bin/python
# vim: set fileencoding=utf8
# Created:20080211
# By Jeff Connelly

import Port

class Entity(object):

    def __init__(self, name, ports):
        """Create a new black box entity.
        name: name of entity
        ports: a sequence of Port objects
        """
        self.name = name
        self.IN = []
        self.OUT = []
        self.INOUT = []

        for p in ports:
           if p.direction == "in":
              self.IN.append(p)
           elif p.direction == "out":
              self.OUT.append(p)
           else:
              self.INOUT.append(p)

    def __str__(self):
        s = "<Entity: %s, %d ports" % (self.name, len(self.IN))
        i = 0
        for p in self.IN:
            i += 1
            s += "\n%d. %s" % (i, p)
        for p in self.OUT:
            i += 1
            s += "\n%d. %s" % (i, p)
        for p in self.INOUT:
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
