#!/usr/bin/env python
# Created:20080411
# By Jeff Connelly
#
# Breadboard/circuit pin layout program

import copy
import types

import tg
import tinv

def combine_dicts(dict1, dict2):
    """Combine two dictionaries; dict2 takes priority over dict1."""
    ret = copy.deepcopy(dict1)
    ret.update(dict2)
    return ret

def read_netlist(filename):
    """Read a SPICE input deck, returning subcircuit nodes and definitions."""

    f = file(filename, "rt")
    subckt_nodes = {}
    subckt_defns = {}
    name = None
    while True:
        line = f.readline()
        if len(line) == 0:
            break

        line = line.strip()

        if line.startswith(".subckt"):
            words = line.split()
            name = words[1]
            nodes = words[2:]

            subckt_nodes[name] = nodes
        elif line.startswith(".ends"):
            name = None
        else:
            if name is not None:
                if not subckt_defns.has_key(name):
                    subckt_defns[name] = []
                subckt_defns[name].append(line)

    return subckt_nodes, subckt_defns

subckt_nodes, subckt_defns = read_netlist("../code/circuits/mux3-1_test.net")

print subckt_nodes
print subckt_defns

def rewrite_subckt(subckt_defns, s):
    mod = globals()[s]
    lines = []
    for line in subckt_defns[s]:
        words = line.split()
        name = words[0]
        args = words[1:]

        if name in mod.parts_consumed:
            # Skip this line
            pass
        elif name in mod.parts_kept:
            lines.append(line)
        else:
            raise "Subcircuit %s defined in module %s has parts consumed list: %s and parts kept list: %s, but the name '%s' is in neither. Add it to either." % (s, name, mod.parts_consumed, mod.parts_kept, name)

    # Map node positions in arguments list (subckt invocation, X..), to node names
    pos2node = {}
    for i in range(0, len(mod.nodes)):
        pos2node[mod.nodes[i]] = i

    # Rewrite
    subckt_defns[s] = lines

    return mod, subckt_defns, pos2node

mod, subckt_defns, pos2node = rewrite_subckt(subckt_defns, "tinv")

# Store new pin assignments
assignments = {}
for p in mod.parts_generated:
    assignments[p] = {}

# TODO: choose next available component in part, instead of always 0
for node, pin in combine_dicts(mod.global_pins, mod.pins[0]).iteritems():
    if type(pin) == types.TupleType:
        part, pin = pin
    else:
        part = None

    print "* %s -> %s:%s" % (node, part, pin)

    if part is not None:
        assignments[part][pin] = node

for part in assignments:
    print "* --%s--" % (part,)
    for pin in range(1, max(assignments[part].keys()) + 1):
        node = assignments[part].get(pin, "NC")
        print "* ", (pin,node)

rewrite_subckt(subckt_defns, "tinv")

# sti
line = "XX1 IN NC_01 OUT NC_02 tinv"


