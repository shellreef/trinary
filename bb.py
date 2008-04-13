#!/usr/bin/env python
# Created:20080411
# By Jeff Connelly
#
# Breadboard/circuit pin layout program

import copy
import types
import time

import tg
import tinv

PROGRAM_NAME = "bb.py"

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
    toplevel = []
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
            else:
                # Top-level elements, skip blank lines, commands and comments
                if len(line.strip()) != 0 and line[0] not in ('.', '*'):
                    toplevel.append(line)

    print "* Converted from netlist %s by %s on %s" % (filename, PROGRAM_NAME, time.asctime())
    return subckt_nodes, subckt_defns, toplevel

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
            # Note: I do not yet check if the chip has pins that are used, but are assigned to 
            # the same node that is required. The pins must be unused.
            if chip_has_pins_available(option, pins):
                #print "* Found model %s with pins %s free: chip #%s" % (model_needed, option, i)
                return i, option_num

    raise "* No chips found with model %s and with pins %s free. Maybe you need more chips." % (model_needed, 
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

    #print "* Searching for model %s with one of pins: %s" % (the_model, need_options)
    chip_num, option_num  = find_chip(chips, the_model, need_options)
    #print "* FOUND CHIP:",chip_num
    #print "* WITH PINS (option #%s):" % (option_num,), mod.pins[option_num]

    for node, pin in combine_dicts(mod.global_pins, mod.pins[option_num]).iteritems():
        if type(pin) == types.TupleType:
            part, pin = pin
        else:
            part = None

        #print "* %s -> %s:%s" % (node, part, pin)

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

def any_pins_used(pins):
    """Return whether any of the pins on a chip are used. If False, chip isn't used."""
    for p in pins.values():
        if not is_floating(p):
            return True
    return False

def dump_chips(chips):
    """Show the current chips and their pin connections."""
    for i, c in enumerate(chips):
        m, p = c

        if not any_pins_used(p):
            print "* Chip #%s - %s no pins used, skipping" % (i, m)
            continue

        print "* Chip #%s - %s pinout:" % (i, m)
        for k, v in p.iteritems():
            print "* \t%s: %s" % (k, v)

        print "X_IC_%s " % (i, ),
        # Assumes all chips are 14-pin, arguments from 1 to 14 positional
        for k in range(1, 14+1):
            print p[k],
        print m
        print

def dump_extra(extra):
    """Shows the extra, supporting subcircuit parts that support the IC and are part of the subcircuit."""
    print "* Parts to support subcircuits:"
    for e in extra:
        print e

def make_node_mapping(internal, external):
    """Make a node mapping dictionary from internal to external nodes.
    Keys of the returned dictionary are internal nodes (of subcircuit), values are external."""
    d = {}
    d.update(zip(internal, external))
    return d

def rewrite_refdesg(original, prefix):
    """Prefix a reference designator, preserving the first character."""
    return "%s%s$%s" % (original[0], prefix, original)

def expand(subckt_defns, line, prefix):
    """Expand a subcircuit instantiation if needed."""
    words = line.split()
    refdesg = words[0]
    if words[0][0] == 'X':
        model = words[-1]
        args = words[1:-1]

        nodes = make_node_mapping(subckt_defns[model], args)
        new_lines = []
        #new_lines.append(("* Instance of subcircuit %s" % (model,)))
        for sline in subckt_defns[model]:
            words = sline.split()
            if words[0][0] == 'X' and words[-1] not in ('tg', 'tinv', 'tnor', 'tnor3', 'tnand', 'tnand3'):
                new_lines.extend(expand(subckt_defns, sline, "%s$" % (words[0]),))
            else:
                new_words = []
                # Nest reference designator
                new_words.append("%s%s$%s" % (prefix, refdesg, words[0]))
                #new_words.append(rewrite_refdesg(rewrite_refdesg(words[0], refdesg), prefix)) # XXX TODO
                # Map internal to external nodes
                for word in words[1:]:
                    if word in nodes.keys():
                        new_words.append(nodes[word])
                    else:
                        new_words.append(word)
                new_lines.append(" ".join(new_words))
            #new_lines.append("")
    else:
        new_lines = [line]

    return new_lines

def test_flatten():
    """Demonstrate flattening of a hierarchical subcircuit."""
    subckt_nodes, subckt_defns, toplevel = read_netlist("mux3-1_test.net")

    for line in toplevel:
        print "\n".join(expand(subckt_defns, line, ""))

def main():
    subckt_nodes, subckt_defns, toplevel = read_netlist("mux3-1_test.net")

    mod_tinv, subckt_defns, pos2node_tinv = rewrite_subckt(subckt_defns, "tinv")
    tg_tinv, subckt_defns, pos2node_tg = rewrite_subckt(subckt_defns, "tg")

    # First semi-flatten the circuit 
    flat_toplevel = []
    for line in toplevel:
        flat_toplevel.extend((expand(subckt_defns, line, "")))

    #print "\n".join(flat_toplevel)
    #raise SystemExit

    # Available chips
    chips = [
            ("CD4007", get_floating(14) ),
            ("CD4016", get_floating(14) ),
            ]

    extra = []
    for line in flat_toplevel:
        words = line.split()
        if words[0][0] == 'X':
            model = words[-1]
            args = words[1:-1]

            #print "MODEL=%s, args=%s" % (model, args)

            #print subckt_defns[model]
            #print subckt_nodes[model]

            if model in ('tg', 'tinv'):
                nodes = make_node_mapping(subckt_nodes[model], args)
                chips, extra = assign_part(chips, subckt_defns, extra, model, nodes)
            else:
                raise "Cannot synthesis model: %s, line: %s" % (model, line)
        else:
            print line

    dump_chips(chips)
    dump_extra(extra)

def test_assignment():
    """Demonstrate subcircuit assignment."""
    subckt_nodes, subckt_defns, toplevel = read_netlist("mux3-1_test.net")

    mod_tinv, subckt_defns, pos2node_tinv = rewrite_subckt(subckt_defns, "tinv")
    tg_tinv, subckt_defns, pos2node_tg = rewrite_subckt(subckt_defns, "tg")


    # Available chips
    chips = [
            ("CD4007", get_floating(14) ),
            ("CD4016", get_floating(14) ),
            #("CD4007", get_floating(14) )
            ]

    # TODO: parse from SPICE files, assigning nodes based on pos2node_*
    # TODO: sti
    # line = "XX1 IN NC_01 OUT NC_02 tinv"

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

if __name__ == "__main__":
    #test_flatten()
    #test_assignment()
    main()
