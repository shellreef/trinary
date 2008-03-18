# vim: set fileencoding=utf8
#  Architecture.py
#
# Architecture object.
#

class Architecture(object):
    def __init__(self, name):
        '''Initialize Architecture object.  '''

        self.name = name

    def __str__(self):
        return "<Architecture:%s>" % (self.name,)

if __name__ == "__main__":
    a = Architecture("architecture")

    print a