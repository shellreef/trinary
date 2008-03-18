#!env python
# vim: set fileencoding=utf8

trit_integer = {"i":-1, "0":0, "1":1}
trit_bool = {"i":False, "0":None, "1":True}
trit_value = (None, True, False)

trit_char = ("i", "1", "0")

def parseTrit(trit):
    '''This function returns the boolean value of a trit.
        trit: trit represented by a characater
        return: boolean value
    '''
    return trit_bool[trit]
    
def parseTritVector(trit_string):
    '''parseTritVector: take a string of trits and return a trit vector
        trit_string: string to parse into a trit vector
        return: trit vector
    '''
    result = []
    for i in range(len(trit_string)):
        result.append(parseTrit(trit_string[i]))
    return tuple(result)


class Trits(object):
     def __init__(self, s):
          if isinstance(s, str):             # "i01", for example
                self.trits = parseTritVector(s)
          elif hasattr(s, "__getitem__"): # [False, None, True] for example
                self.trits = s
          else:
                assert "Trits __init__, unrecognized initial value:",s

     def __str__(self):
          s = ""
          for t in self.trits:
                s += {
                          False: "i",
                          None: "0",
                          True: "1"
                          }[t]
          return "<Trits:%s>" % (s,)

     def __repr__(self):
          return self.__str__()

     def __getitem__(self, n):
          # For now, all indexing is positive, unsigned, not balanced
          return self.trits[n]

     def __len__(self):
          return len(self.trits)

if __name__ == "__main__":
     ts = Trits("iiii1i01i1110000")
     print "Trit vector:", ts

     print "\nAll trits:"
     for t in ts:
          print t

