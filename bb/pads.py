#!/usr/bin/env python
# Created:20080412
# By Jeff Connelly
#
# Created PADS-PCB netlist file, for FreePCB at http://www.freepcb.com/ , 
# or any other PCB layout program that supports the PADS-PCB format.

import sys

PROGRAM_NAME = "pads.py"

footprint_map = {
        "CD4007": "14DIP300",
        "CD4016": "14DIP300",
        "R": "RC07",             # 1/4 resistor
        "V": "1X2HDR-100",
        "sp3t-1": "SS14MDP2",      # NKK switch, in position 1
        "sp3t-2": "SS14MDP2",      # NKK switch, in position 2
        "sp3t-3": "SS14MDP2",      # NKK switch, in position 3
        #"1N4148": "DO-35",       # Diode
        "D": "DO-35",           # All diodes (note: should really be specific!)
        }

# If enabled, name resistors numerically R1, R2, ... instead of hierarchically.
SERIAL_RESISTORS = True

# If enabled, anything containing Vdd or Vss will be named Vdd or Vss--
# effectively disabling hierarchy for these power sources. **Note that if
# there are multiple Vdd and Vss, this will cause duplicate parts!**
SHORT_VDD_VSS = True

# If enabled, RX$Xflipflop$XX<n>$Xinv$R{P,N} will be mapped to ${P,N}<n>.
# Useful for laying out a single dtflop-ms_test, but may cause serious
# errors otherwise!
SHORT_DTFLOP_RP_RN = False

# TODO: remove these limitations on FreePCB, so that
# USE_SHORT_NAMES and BREAK_LONG_LINES can be turned off!

# If true, reference designators and node names will be assigned
# sequentially, instead of using their hierarchical name
# from the net2 file. Some PCB programs have length limits
# on reference designators (FreePCB).
USE_SHORT_NAMES = True

# Split long nets over multiple lines.
BREAK_LONG_LINES = True

# If not false, nodes with only one connection will have a
# testpoint attached, using the given footprint.
#NAKED_NODE_FOOTPRINT = "HOLE_100_RND_200"
NAKED_NODE_FOOTPRINT = None


def usage():
    print """usage: %s input-filename [output-filename]

input-filename      A chip-level SPICE netlist (.net2) 
output-filename     PADS-PCB layout netlist (.pads)

If output-filename is omitted, input-filename is used but
with a .pads extension instead of .net2, or .pads appended.

Either filenames can be "-" for stdin or stdout, respectively.
""" % (PROGRAM_NAME, )
    raise SystemExit 

# MAX_NET_NAME_SIZE and FMAX_PIN_NAME_SIZE from 
# svn://svn.berlios.de/freepcb/trunk/Shape.h and Netlist.h
# (TODO: remove these arbitrary limits in FreePCB)
MAX_SIZE = 39

long2short = {
         # Names to preserve, if USE_SHORT_NAMES is True.
         # Would be nice to preserve all/more net names, but
         # some are just too long and hierarchical.
        "$G_Vss": "$G_Vss",
        "$G_Vdd": "$G_Vdd",
        "0": "0",
        }
next_serial = { 
        "R": 1, 
        "NX": 1, 
        "X": 1,
        }

resistor_serial = 0

def shorten(long, is_netname):
    global resistor_serial

    if SHORT_VDD_VSS:
        if "Vdd" in long:
            return "Vdd"
        if "Vss" in long:
            return "Vss"

    if long.startswith("R") and SERIAL_RESISTORS:
        resistor_serial += 1
        return "R%d" % (resistor_serial,)

    if not USE_SHORT_NAMES:
        return long

    if SHORT_DTFLOP_RP_RN and long.startswith("RX$Xflipflop$XX"):
        short = long[len("RX$Xflipflop$XX"):][0]
        if long.endswith("RP"):
            short = "RP" + short
        elif long.endswith("RN"):
            short = "RN" + short
        else:
            sys.stderr.write("dtflop RP/RN mapping enabled, but not RP/RN!")
            raise SystemExit
        return short

    if len(long) <= MAX_SIZE:
        # We got away with it this time.
        return long

    # Resistors are what you have to watch our for
    if long2short.has_key(long):
        short = long2short[long]
    else:
        # id = first letter, 'R', etc.
        # Net names get a prefix of "NX" (for node extended;
        # the name was too long so it was shortened)
        if is_netname:
            id = "NX"
        else:
            id = long[0]


        #sys.stderr.write("%s\n" % (long,))
        short = "%s%d" % (id, next_serial[id])
        long2short[long] = short
        next_serial[id] += 1

    return short

if len(sys.argv) < 2:
    usage()
filename = sys.argv[1]

# Redirect stdout to output file
if len(sys.argv) > 2:
    output_filename = sys.argv[2]
else:
    output_filename = filename.replace(".net2", ".pads")
    if output_filename == filename:
        output_filename = filename + ".pads"
if output_filename != "-":
    sys.stdout = file(output_filename, "wt")

print "*PADS-PCB*"
print "*%s*" % (filename, )

parts = []
nets = {}
if filename == "-":
    infile = sys.stdin
else:
    infile = file(filename, "rt")
for line in infile.readlines():
    if line[0] == '*':
        continue

    line = line.strip()
    if len(line) == 0:
        continue

    words = line.split()
    long_refdesg = words[0]

    refdesg = shorten(long_refdesg, is_netname=False)

    args = words[1:-1]
    if refdesg[0] == 'V':
        # Voltage sources only have two pins, other arguments
        # may be PWL or other values (really one argument, but
        # separated by spaces, so we'll see it as more than one).
        args = [args[0], args[1]]

    # Make nets list
    for i, long_arg in enumerate(args):
        if long_arg.startswith("NC_"):
            continue

        #if arg == "0":
        #    arg = "GND"
   
        #sys.stderr.write("-> %s" % (line,))
        arg = shorten(long_arg, is_netname=True)

        if arg not in nets.keys():
            nets[arg] = []

        nets[arg].append("%s.%s" % (refdesg, i + 1))

    model = words[-1]

    # Make parts list
    parts.append((refdesg, model))

# Map models to footprints
print "*PART*"
for part in parts:
    refdesg, model = part
    if footprint_map.has_key(model):
        package = footprint_map[model]
    elif footprint_map.has_key(refdesg[0]):
        package = footprint_map[refdesg[0]]
    else:
        raise "Part name %s, model %s unknown, couldn't find in map: %s" % (refdesg, model, footprint_map)
    print "%s %s" % (refdesg, package)

# Nets with only one node get testpoints for free (also appends to parts list)
if NAKED_NODE_FOOTPRINT:
    for signal_name, nodes in nets.iteritems():
        if len(nodes) == 1:
            testpoint = "%s_tp" % (signal_name,)
            print "%s %s" % (testpoint, NAKED_NODE_FOOTPRINT)
            nets[signal_name].append(testpoint)


# Dump all nets
print "*NET*"
for signal, pins in nets.iteritems():
    print "*SIGNAL* %s" % (signal,)
    if BREAK_LONG_LINES:
        i = 0
        for p in pins:
            print p,
            # Break lines every so many pins
            # (would be nice if didn't have to do this)
            if i % 5 == 0:
                print
            i += 1
        print
    else:
        print " ".join(pins)

# Print a newline at the end for picky layout programs (ExpressPCB)
print
