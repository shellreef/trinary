#!env python
from tokenizer import parseTritVector

class Trits(object):
    def __init__(self, s):
        if isinstance(s, str):          # "i01", for example
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
        return s

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

