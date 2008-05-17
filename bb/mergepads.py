#!env python
# Created:20080516
# By Jeff Connelly
#
# Merge two PADS-PCB files

import sys, os

SHARED_SIGNALS = ("$G_Vdd", "$G_Vss", "0")

def load_pads(f):
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
        part = f.readline()
        if len(part) == 0:
            print "Unexpected end-of-file while reading parts"
            raise SystemExit
            break

        part = part.strip()
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

def save_pads(parts, net, name):
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

parts, nets = load_pads(f1)
parts2, nets2 = load_pads(f2)

# Merge part list
for p in parts2:
    name, package = p.split()
    if name in parts:
        name += "_2"
        assert name not in parts, "Name %s in both netlists, even after suffixing" % (name,)
    parts.append("%s %s" % (name, package))

# Merge nets
for signal in nets2:
    new_signal = signal
    if signal in nets and signal not in SHARED_SIGNALS:
        new_signal += "_2"
        # If this happens, improve suffixing (try alternatives)
        assert new_signal not in nets, "Signal %s in both netlists, even after suffix" % (new_signal,)

    if new_signal in SHARED_SIGNALS:
        nets[new_signal].extend(nets2[signal])
    else:
        nets[new_signal] = nets2[signal]

print save_pads(parts, nets, "%s + %s" % (sys.argv[1], sys.argv[2]))

