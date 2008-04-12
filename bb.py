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
    """Partially rewrite subcircuit 's', using rules from a module of the same name.

    Removes parts in mod.parts_consumed, keeps parts in mod.parts_kept. 

    Does not generate any new parts."""

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

next_floating = -1
def get_floating(n=None):
    """Return a unique disconnected (floating) node name.
    
    If n is given, return a dict of n floating node names. Otherwise returns one in a string."""
    global next_floating

    if n is not None:
        return get_floating_n(n)

    next_floating += 1
    return "NC_%s_" % (next_floating, )

def get_floating_n(n):
    """Get n floating nodes, see get_floating()."""
    fs = {}
    for x in range(1, n + 1):
        fs[x] = get_floating()
    return fs

def is_floating(node_name):
    """Return whether the given node name is probably not connected;
    generated from get_floating()."""
    return node_name.startswith("NC_") 

def chip_has_pins_available(pins_needed, pins):
    """Return whether 'pins' has not-connected pins, all those required in pins_needed."""
    for p in pins_needed:
        if not is_floating(pins[p]):
            return False
    return True

def find_chip(chips, model_needed, pins_needed):
    """Return an index into the chips array, with the given model and the pins free."""
    for i, chip in enumerate(chips):
        model, pins = chip
        if model != model_needed:
            continue

        if chip_has_pins_available(pins_needed, pins):
            print "Found model %s with pins %s free: chip #%s" % (model_needed, pins_needed, i)
            return i

    print "! No chips found with model %s and with pins %s free" % (model_needed, pins_needed)

def find_pins_needed(pins):
    """From a mod.pins[x] dict, return the pins needed for each model, for find_chip()"""
    need = {}
    for x in pins.values():
        if type(x) == types.TupleType:
            model, pin = x
            if not need.has_key(model):
                need[model] = []

            need[model].append(pin)

    return need

def assign_part(chips, mod):
    # Store new pin assignments
    assignments = {}
    for p in mod.parts_generated:
        assignments[p] = {}

    # TODO: find mod.pins[1] too!!!!! Other complementary pair.
    need = find_pins_needed(mod.pins[0])
    if len(need) > 1:
        raise "Sorry, more than one model is needed: %s, but only one is supported right now." % (need,)

    chip_num = find_chip(chips, need.keys()[0], need.values()[0])
    print "FOUND CHIP:",chip_num

    for node, pin in combine_dicts(mod.global_pins, mod.pins[0]).iteritems():
        if type(pin) == types.TupleType:
            part, pin = pin
        else:
            part = None

        print "* %s -> %s:%s" % (node, part, pin)

        if part is not None:
            assignments[part][pin] = node

    for part in assignments:
        #print "* --%s--" % (part,)
        for pin in range(1, max(assignments[part].keys()) + 1):
            node = assignments[part].get(pin, get_floating())
            #print "* ", (pin,node)

            # Assign nodes to this pin on this chip. TODO: assign _external_ nodes!!!
            chips[chip_num][1][pin] = node
    return chips

mod, subckt_defns, pos2node = rewrite_subckt(subckt_defns, "tinv")
chips = [
        ("CD4007", get_floating(14) ),
        ("CD4007", get_floating(14) ),
        ("CD4007", get_floating(14) )
        ]

chips = assign_part(chips, mod)
chips = assign_part(chips, mod)
for i, c in enumerate(chips):
    m, p = c
    print "---%s #%s---" % (m, i)
    for k, v in p.iteritems():
        print "\t%s: %s" % (k, v)


# sti
line = "XX1 IN NC_01 OUT NC_02 tinv"


