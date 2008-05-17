#!env python
# Created:20080516
# By Jeff Connelly
#
# Merge two PADS-PCB files

import sys, os

def read_pads(f):
    l = f.readline().strip()
    if l != "*PADS-PCB*":
        print "not PADS-PCB format, first line: %s" % (l,)
        raise SystemExit

    l = f.readline()

    l = f.readline().strip()
    if l != "*PART*":
        print "expected *PARTS*, got %s" % (l,)
        raise SystemExit

    # Read all parts until *NET*
    parts = []
    while True:
        part = f.readline().strip()
        if part == "*NET*":
            break
        parts.append(part)

    # Read signals
    signal = None
    pins = []
    nets = {}
    while True:
        line = f.readline()
        if len(line) == 0:
            break

        line = line.strip()
        if line.startswith("*SIGNAL*"):
            if signal:
                nets[signal] = pins

            signal = line.split()[1]
            pins = []
        else:
            pins.extend(line.split())
    # Add last signal
    nets[signal] = pins

    return parts, nets

def write_pads(parts, net, name):
    out = "*PADS-PCB*\n"
    out += "*%s*\n" % (name,)
    out += "*PART*\n"
    for p in parts:
        out += "%s\n" % (p,)
    out += "*NET*\n"
    for signal in net:
        out += "*SIGNAL* %s\n" % (signal,)
        for pin in net[signal]:
            out += "%s\n" % (pin,)
    return out 

if len(sys.argv) != 3:
    print "usage: python mergepads.py file-1.pads file-2.pads"
    raise SystemExit

f1 = file(sys.argv[1], "rt")
f2 = file(sys.argv[2], "rt")

parts, nets = read_pads(f1)
print write_pads(parts, nets, "main.pads")

