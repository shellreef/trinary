#!/usr/bin/env python
# Created:20080411
# By Jeff Connelly
#
# Circuit pin layout program, for mapping sub-chip (or partially sub-chip)
# subcircuits to actual integrated circuit chips plus optional extra components,
# outside the chip. For example, the 'tinv' subcircuit has a complementary pair
# of MOSFETs, which this program maps to part of CD4007, assigning the pins,
# and mapping the other pair inside the CD4007 if another 'tinv' comes along.

import copy
import types
import sys

import tg
import tinv
import tnor
import tnand

PROGRAM_NAME = "bb.py"

# Subcircuits to map that should be mapped physical ICs
SUBCIRCUITS_TO_MAP = ('tg', 'tinv', 'tnor', 'tnor3', 'tnand', 'tnand3')
SUBCIRCUITS_CAN_MAP = ('tg', 'tinv', 'tnor', 'tnand')        # subcircuits we actually can map, as of yet

def combine_dicts(dict1, dict2):
    """Combine two dictionaries; dict2 takes priority over dict1."""
    ret = copy.deepcopy(dict1)
    ret.update(dict2)
    return ret

def read_netlist(filename):
    """Read a SPICE input deck, returning subcircuit nodes and definitions."""

    if filename == "-":
        f = sys.stdin
    else:
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

    return "NC__%s" % (get_serial(), )

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
        elif type(x) == types.ListType:
            for mp in x:
                model, pin = mp
                if not need.has_key(model):
                    need[model] = []

                need[model].append(pin)

    return need

def assign_part(chips, subckt_defns, extra, model_name, external_nodes, refdesg):
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

    findings = []
    for node_pin in combine_dicts(mod.global_pins, mod.pins[option_num]).iteritems():
        node, pin = node_pin

        if type(pin) == types.TupleType:
            part, pin = pin
            findings.append((node, part, pin))
        elif type(pin) == types.ListType:
            for pp in pin:
                part, p = pp
                findings.append((node, part, p))
        else:
            part = None
            findings.append((node, part, pin))

    for node, part, pin in findings:
        #print "* %s -> %s:%s" % (node, part, pin)

        if part is not None:
            if node.startswith("$G_") or node == "0":
                new_node = node                    # global node (LTspice)
            elif external_nodes.has_key(node):
                #sys.stderr.write("Mapping external node %s, map = %s\n" % (node, external_nodes))
                new_node = external_nodes[node]    # map internal to external node
            else:
                #sys.stderr.write("Mapping internal-only node %s\n" % (node,))
                new_node = rewrite_node("", refdesg, node)

            chips[chip_num][1][pin] = new_node

    internal_only_nodes = {}

    # Now place any ++additional parts++ (resistors, etc.) within the subcircuit model
    # that connect to the chip, but are not part of the chip.
    for line in subckt_lines:
        words = line.split()
        new_words = []

        if words[0][0] == "M":
            raise ("This line:\t%s\nIn the subcircuit '%s', has a MOSFET left " + 
                    "over that wasn't converted. Probably it was meant to be converted to an IC? " + 
                    "Comment out this line in %s if you are sure you want this, otherwise " + 
                    "double-check the model definition for '%s', specifically, " +
                    "parts_consumed and parts_kept.\nAlso, check if the model was rewritten!") % (line, model_name, PROGRAM_NAME, model_name)

        #name = "%s_%s_%s_%s" % (words[0], model_name, chip_num, refdesg)
        name = "%s%s$%s" % (words[0][0], refdesg, words[0])

        new_words.append(name)

        # Replace internal nodes with external nodes.
        for w in words[1:]:
            if w in external_nodes.keys():
                new_words.append(external_nodes[w])
            elif is_floating(w):
                # TODO ???
                new_words.append(get_floating())
            elif w[0].isdigit():   # value
                new_words.append(w)
            else:
                if not internal_only_nodes.has_key(w):
                    internal_only_nodes[w] = "%s$%s$%s" % (w[0], refdesg, w)
                new_words.append(internal_only_nodes[w])

                # TODO: comment this out, if the above works
                #raise "Could not map argument '%s' in subcircuit line %s, not found in %s" % (w, line, external_nodes)

        extra.append(" ".join(new_words))

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

        print "X_IC_%s_%s" % (i, m),
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

def rewrite_node(prefix, circuit_inside, original_node_name):
    """Rewrite a node name inside a subcircuit, prefixing it with
    prefix and the name of the circuit that it is inside (both
    are optional)."""

    # Globals never rewritten
    if original_node_name.startswith("$G_") or original_node_name == "0":
        return original_node_name

    new_name = original_node_name
    if circuit_inside:
        new_name = "%s$%s" % (circuit_inside, new_name)

    if prefix:
        new_name = "%s$%s" % (prefix, new_name)

    return new_name

def is_expandable_subcircuit(refdesg, model):
    """Return whether the SPICE reference designator and model is 
    a) a subcircuit, b) _and_ it can be hierarchically expanded further."""
    return refdesg[0] == 'X' and model not in SUBCIRCUITS_TO_MAP

def expand(subckt_defns, subckt_nodes, line, prefix, outer_nodes, outer_prefixes):
    """Recursively expand a subcircuit instantiation if needed."""
    words = line.split()
    outer_refdesg = words[0]
    outer_model = words[-1]
    outer_args = words[1:-1]
    if is_expandable_subcircuit(outer_refdesg, outer_model):
        nodes = make_node_mapping(subckt_nodes[outer_model], outer_args)
        new_lines = []
        new_lines.append(("* %s: Instance of subcircuit %s: %s" % (outer_refdesg, outer_model, " ".join(outer_args))))

        # Notes that are internal to the subcircuit, not exposed in any ports
        internal_only_nodes = {}  

        for sline in subckt_defns[outer_model]:
            swords = sline.split()
            inner_refdesg = swords[0]
            inner_model = swords[-1]
            inner_args = swords[1:-1]

            if is_expandable_subcircuit(inner_refdesg, inner_model):
                # Recursively expand subcircuits, to transistor-level subcircuits (SUBCIRCUITS_TO_MAP)
                nodes_to_pass = {}
                for n in nodes:
                    if outer_nodes.has_key(nodes[n]):
                        nodes_to_pass[n] = outer_nodes[nodes[n]]
                        outer_prefixes[nodes_to_pass[n]] = rewrite_node(prefix, outer_refdesg, "")
                    else:
                        nodes_to_pass[n] = nodes[n]
                # TODO: get the prefixes right!
                sys.stderr.write("PASSING NODES: %s (outer=%s)\n" % (nodes_to_pass, outer_nodes))
                sys.stderr.write("\tWITH PREFIXES: %s\n" % (outer_prefixes,))
                new_lines.extend(expand(subckt_defns, subckt_nodes, sline, outer_refdesg, 
                    nodes_to_pass, outer_prefixes))
            else:
                new_words = []
                # Nest reference designator
                new_words.append(rewrite_refdesg(inner_refdesg, prefix + "$" + outer_refdesg))

                # Map internal to external nodes
                for w in inner_args:
                    #print "****", word
                    if w in nodes.keys():
                        # XXX TODO: Need to follow up hierarchy! This leads to
                        # incomplete nets. For example, dtflop-ms_test.net maps:
                        #
                        # In nodes {'Q': 'Q', 'C': 'CLK', 'D': 'D'}, rewrite C -> CLK, prefix  [correct]
                        # In nodes {'Q': 'Q', 'C': 'CLK', 'D': 'D'}, rewrite C -> CLK, prefix  [correct]
                        #
                        # but because the 'nodes' dict is only for the parent, it
                        # doesn't map this correctly, leading to an unconnected node:
                        #
                        # In nodes {'OUT': '_C', 'IN': 'C'}, rewrite IN -> C, prefix Xflipflop [wrong]
                        #
                        # It should be CLK, not Xflipflop$C. These problems will occur
                        # with more nesting of subcircuits
                        if nodes[w] in outer_nodes:
                            # This is a port of this subcircuit, ascends hierarchy
                            #new_words.append(outer_prefixes[outer_nodes[nodes[w]]] + outer_nodes[nodes[w]])
                            # TODO: get the prefixes right! what if it isn't top-level?
                            new_words.append(outer_nodes[nodes[w]])
                        else:
                            new_words.append(rewrite_node(prefix, "", nodes[w]))

                    elif is_floating(w):
                        # This is a port, but that is not connected on the outside, but
                        # still may be internally-connected so it needs a node name.
                        # Name it what it is called inside, hierarchically nested.
                        inner_node_map = make_node_mapping(inner_args, subckt_nodes[inner_model])
                        new_words.append(rewrite_node(prefix, outer_refdesg, inner_node_map[w]))
                        #print "Floating:",w," now=",new_words,"node map=",inner_node_map
                    elif w[0].isdigit():
                        new_words.append(w)
                    else:
                        # A signal only connected within this subcircuit, but not a port.
                        # Make a new node name for it and replace it.
                        if not internal_only_nodes.has_key(w):
                            internal_only_nodes[w] = rewrite_node(prefix, outer_refdesg, w)
                            #print "* sline: %s, Subcircuit %s, mapping internal-only node %s -> %s" % (sline, outer_model, w, internal_only_nodes[w])

                        new_words.append(internal_only_nodes[w])
                        #new_words.append(w)
                        #raise "Expanding subcircuit line '%s' (for line '%s'), couldn't map word %s, nodes=%s" % (sline, line, w, nodes)

                new_words.append(inner_model)

                new_lines.append(" ".join(new_words))
            #new_lines.append("")
    else:
        new_lines = [line]

    return new_lines

def test_flatten():
    """Demonstrate flattening of a hierarchical subcircuit."""
    subckt_nodes, subckt_defns, toplevel = read_netlist("mux3-1_test.net")

    for line in toplevel:
        print "\n".join(expand(subckt_defns, subckt_nodes, line, "", {}))

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

def usage():
    print """usage: %s input-filename [output-filename | -p]

input-filename      A transistor-level SPICE netlist (.net) 
output-filename     Chip-level SPICE netlist (.net2)

If output-filename is omitted, input-filename is used but 
with '2' appended, so .net becomes .net2 by convention.

Either filenames can be "-" for stdin or stdout, respectively.

The -p flag, instead of an output filename will also run pads.py
so that both .net2 and .pads files will be generated.
""" % (PROGRAM_NAME, )
    raise SystemExit

def main():
    if len(sys.argv) < 2:
        usage()
    input_filename = sys.argv[1]

    generate_pads = len(sys.argv) > 2 and sys.argv[2] == "-p"

    subckt_nodes, subckt_defns, toplevel = read_netlist(input_filename)

    # Redirect stdout to output file
    if len(sys.argv) > 2 and sys.argv[2] != "-p":
        output_filename = sys.argv[2]
    else:
        output_filename = input_filename + "2"

    if output_filename != "-":
        sys.stdout = file(output_filename, "wt")

    print "* Chip-level netlist, converted from %s by %s" % (input_filename, PROGRAM_NAME)

    # Circuits to rewrite need to be loaded first. Any transistor-level circuits
    # you want to replace with ICs, are loaded here. 
    modules = pos2node = {}
    for s in SUBCIRCUITS_CAN_MAP:
        if subckt_defns.has_key(s):
            modules[s], subckt_defns, pos2node[s] = rewrite_subckt(subckt_defns, s)

    # First semi-flatten the circuit 
    flat_toplevel = []
    for line in toplevel:
        flat_toplevel.extend((expand(subckt_defns, subckt_nodes, line, "", {}, {})))

    print "* Flattened top-level, before part assignment:"
    for f in flat_toplevel:
        print "** %s" % (f,)
    print "* Begin converted circuit"
    print

    # XXX TEST
    raise SystemExit

    # Available chips
    chips = [
            ("CD4007", get_floating(14) ),
            ("CD4007", get_floating(14) ),
            ("CD4007", get_floating(14) ),
            ("CD4007", get_floating(14) ),
            ("CD4007", get_floating(14) ),
            ("CD4007", get_floating(14) ),
            ("CD4007", get_floating(14) ),
            ("CD4016", get_floating(14) ),
            ]

    extra = []
    for line in flat_toplevel:
        words = line.split()
        if words[0][0] == 'X':
            refdesg = words[0]
            model = words[-1]
            args = words[1:-1]

            #print "MODEL=%s, args=%s" % (model, args)

            #print subckt_defns[model]
            #print subckt_nodes[model]

            if model in SUBCIRCUITS_CAN_MAP:
                nodes = make_node_mapping(subckt_nodes[model], args)
                #print nodes
                chips, extra = assign_part(chips, subckt_defns, extra, model, nodes, refdesg)
            else:
                raise "Cannot synthesize model: %s, line: %s" % (model, line)
        else:
            print line

    dump_chips(chips)
    dump_extra(extra)

    sys.stdout = sys.stderr

    if generate_pads:
        import os
        os.system("python pads.py %s" % (output_filename,))

if __name__ == "__main__":
    #test_flatten()
    #test_assignment()
    main()
