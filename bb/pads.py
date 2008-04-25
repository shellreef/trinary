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
        "sp3t": "SS14MDP2",      # NKK switch
        }

# TODO: remove these limitations on FreePCB, so that
# use_short_names and break_long_lines can be turned off!

# If true, reference designators and node names will be assigned
# sequentially, instead of using their hierarchical name
# from the net2 file. Some PCB programs have length limits
# on reference designators (FreePCB).
use_short_names = True

# Split long nets over multiple lines.
break_long_lines = True

# If not false, nodes with only one connection will have a
# testpoint attached, using the given footprint.
#naked_node_footprint = "HOLE_100_RND_200"
naked_node_footprint = None


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
         # Names to preserve, if use_short_names is True.
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
def shorten(long, is_netname):
    if not use_short_names:
        return long

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
if naked_node_footprint:
    for signal_name, nodes in nets.iteritems():
        if len(nodes) == 1:
            testpoint = "%s_tp" % (signal_name,)
            print "%s %s" % (testpoint, naked_node_footprint)
            nets[signal_name].append(testpoint)


# Dump all nets
print "*NET*"
for signal, pins in nets.iteritems():
    print "*SIGNAL* %s" % (signal,)
    if break_long_lines:
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
