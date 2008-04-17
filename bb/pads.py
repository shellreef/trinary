#!/usr/bin/env python
# Created:20080412
# By Jeff Connelly
#
# Created PADS-PCB netlist file, for FreePCB at http://www.freepcb.com/ , 
# or any other PCB layout program that supports the PADS-PCB format.

import time
import sys

PROGRAM_NAME = "pads.py"

footprint_map = {
        "CD4007": "14DIP300",
        "CD4016": "14DIP300",
        "R": "RC07",            # 1/4 resistor
        "V": "1X2HDR-100",
        }

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
print "*%s %s*" % (filename, time.asctime())

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
    refdesg = words[0]
    args = words[1:-1]
    if refdesg[0] == 'V':
        # Voltage sources only have two pins, other arguments
        # may be PWL or other values (really one argument, but
        # separated by spaces, so we'll see it as more than one).
        args = [args[0], args[1]]

    # Make nets list
    for i, arg in enumerate(args):
        if arg.startswith("NC_"):
            continue

        #if arg == "0":
        #    arg = "GND"

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


print "*NET*"
for signal, pins in nets.iteritems():
    print "*SIGNAL* %s" % (signal,)
    print " ".join(pins)

# Print a newline at the end for picky layout programs (ExpressPCB)
print
