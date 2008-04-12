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

next_serial = -1
def get_serial():
    """Get a unique, increasing number."""
    global next_serial

    next_serial += 1
    return next_serial

def get_floating(n=None):
    """Return a unique disconnected (floating) node name.
    
    If n is given, return a dict of n floating node names. Otherwise returns one in a string."""
    if n is not None:
        return get_floating_n(n)

    return "NC_%s_" % (get_serial(), )

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

def find_chip(chips, model_needed, pins_needed_options):
    """Return an index into the chips array, and what pins, with the given model and the pins free.
    
    pins_needed_options is a list of lists, of any acceptable set of pins to use."""
    for i, chip in enumerate(chips):
        model, pins = chip
        if model != model_needed:
            continue

        for option_num, option in enumerate(pins_needed_options):
            if chip_has_pins_available(option, pins):
                print "Found model %s with pins %s free: chip #%s" % (model_needed, option, i)
                return i, option_num

    raise "No chips found with model %s and with pins %s free. Maybe you need more chips." % (model_needed, 
            pins_needed_options)

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

def assign_part(chips, subckt_defns, extra, model_name, external_nodes):
    """Assign a given model to a physical chip, using the names of the external nodes.
    
    chips: array of existing physical chips that can be assigned from
    mod: logical model to map to, like 'tinv'
    external_nodes: dict mapping internal nodes in the model, to external nodes in the world
    """

    mod = globals()[model_name]
    subckt_lines = subckt_defns[model_name]


    # Store new pin assignments
    assignments = {}
    for p in mod.parts_generated:
        assignments[p] = {}

    need_options = []
    the_model = None
    for p in mod.pins:
        need = find_pins_needed(p)
        if len(need) > 1:
            raise "Sorry, more than one model is needed: %s, but only one is supported right now." % (need,)
        if the_model is None:
            the_model = need.keys()[0]
        else:
            if the_model != need.keys()[0]:
                raise "Sorry, different models are needed: %s, but already decided on %s earlier. This is not yet supported." % (the_model, need[0])

        need_options.append(need.values()[0])

    print "Searching for model %s with one of pins: %s" % (the_model, need_options)
    chip_num, option_num  = find_chip(chips, the_model, need_options)
    print "FOUND CHIP:",chip_num
    print "WITH PINS (option #%s):" % (option_num,), mod.pins[option_num]

    for node, pin in combine_dicts(mod.global_pins, mod.pins[option_num]).iteritems():
        if type(pin) == types.TupleType:
            part, pin = pin
        else:
            part = None

        print "* %s -> %s:%s" % (node, part, pin)

        if part is not None:
            if node.startswith("$G_") or node == "0":
                external_node = node                    # global node (LTspice)
            else:
                external_node = external_nodes[node]    # map internal to external node

            chips[chip_num][1][pin] = external_node

    # Now place any additional parts (resistors, etc.) within the subcircuit model
    # that connect to the chip, but are not part of the chip.
    for line in subckt_lines:
        words = line.split()
        new_words = []

        name = "%s_%s_%s_%s" % (words[0], model_name, chip_num, get_serial())

        new_words.append(name)

        # Replace internal nodes with external nodes.
        for w in words[1:]:
            if w in external_nodes.keys():
                new_words.append(external_nodes[w])
            else:
                new_words.append(w)
        extra.append(" ".join(new_words))
        # TODO: get new part names!!!!!!!!

    return chips, extra

def dump_chips(chips):
    """Show the current chips and their pin connections."""
    for i, c in enumerate(chips):
        m, p = c
        print "---#%s - %s---" % (i, m)
        for k, v in p.iteritems():
            print "\t%s: %s" % (k, v)

def dump_extra(extra):
    """Shows the extra, supporting subcircuit parts that support the IC and are part of the subcircuit."""
    print "++ Additional parts:"
    for e in extra:
        print e


# TODO: do something with this
subckt_nodes, subckt_defns = read_netlist("../code/circuits/mux3-1_test.net")
mod_tinv, subckt_defns, pos2node_tinv = rewrite_subckt(subckt_defns, "tinv")
tg_tinv, subckt_defns, pos2node_tg = rewrite_subckt(subckt_defns, "tg")

# Available chips
chips = [
        ("CD4007", get_floating(14) ),
        ("CD4016", get_floating(14) ),
        #("CD4007", get_floating(14) )
        ]

# TODO: parse from SPICE files, assigning nodes based on pos2node_*
extra = []
chips, extra = assign_part(chips, subckt_defns, extra, "tinv", 
        {
            "Vin": "IN_1", 
            "PTI_Out": "PTI_Out_1",
            "NTI_Out": "NTI_Out_1",
            "STI_Out": "STI_Out_1",
        })

chips, extra = assign_part(chips, subckt_defns, extra, "tinv", 
        {
            "Vin": "IN_2", 
            "PTI_Out": "PTI_Out_2",
            "NTI_Out": "NTI_Out_2",
            "STI_Out": "STI_Out_2",
        })

chips, extra = assign_part(chips, subckt_defns, extra, "tg",
        {
            "IN_OUT": "IN_1",
            "OUT_IN": "OUT_1",
            "CONTROL": "CTRL_1",
        })
chips, extra = assign_part(chips, subckt_defns, extra, "tg",
        {
            "IN_OUT": "IN_2",
            "OUT_IN": "OUT_2",
            "CONTROL": "CTRL_2",
        })
chips, extra = assign_part(chips, subckt_defns, extra, "tg",
        {
            "IN_OUT": "IN_3",
            "OUT_IN": "OUT_3",
            "CONTROL": "CTRL_3",
        })
chips, extra = assign_part(chips, subckt_defns, extra, "tg",
        {
            "IN_OUT": "IN_4",
            "OUT_IN": "OUT_4",
            "CONTROL": "CTRL_4",
        })


dump_chips(chips)
dump_extra(extra)

# sti
line = "XX1 IN NC_01 OUT NC_02 tinv"


