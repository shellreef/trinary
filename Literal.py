# vim: set fileencoding=utf8
#  Integer.py
#
# A literal is an integer.
#

class Literal(object):
    def __init__(self, value = 0):
        '''Initialize Literal object.
           value: integer value given to object. '''

        if not isinstance(value, int):
            raise "Invalid integer value detected: |%s|" % (value, )
        self.value = value

    def __str__(self):
        return "<Literal:%d>" % (self.value,)

if __name__ == "__main__":
    a = Literal(4)
    b = Literal(5)

    print a, b