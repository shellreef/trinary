#!/usr/bin/python
# vim: set fileencoding=utf8
# Created:20080211
# By Jeff Connelly

IN = "in"
OUT = "out"
INOUT = "inout"


class Port(object):
    def __init__(self, name, direction, type):
        self.name = name
        assert direction in [IN, OUT, INOUT], \
                "Port direction %s is invalid" % (direction,)

        self.direction = direction
        self.type = type

    def __str__(self):
        return "<Port: %s, %s, %s>" % (self.name, self.direction, self.type)

if __name__ == "__main__":
    a = Port("a", IN, None)
    b = Port("b", IN, None)
    c = Port("c", OUT, None)

    print a
    print b
    print c
