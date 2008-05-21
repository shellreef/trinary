#!env python
# Created:20080516
# By Jeff Connelly
#
# Run chip mapper/PADS-PCB tool suite
#
import os, sys

if len(sys.argv) < 2:
    print "usage: %s circuit-name" % (sys.argv[0])
    print 
    print "Where circuit-name is an LTspice circuit name, which reads"
    print "../circuits/<circuit-name>.net. The extension need not be "
    print "given. To generate this file in LTspice, SPICE Netlist."
    print
    print "Output file is a .pads PADS-PCB netlist, you can import into"
    print "FreePCB or other PCB layout programs."
    raise SystemExit

name = sys.argv[1]
if "." in name:
    print "You don't need to specify an extension. Try again."
    raise SystemExit
netfile = "../circuits/%s.net" % (name,)
if not os.access(netfile, os.R_OK):
    print "No such file: %s" % (netfile,)
    if os.access("../circuits/%s.asc" % (name,), os.R_OK):
        print "But the corresponding .asc file exists."
        print "To generate .net, in LTspice go to: View -> SPICE Netlist."
    raise SystemExit
if os.access("../circuit/%s.asy" % (name,), os.R_OK):
    print "Warning! A corresponding symbol exists for this circuit!"
    print "Are you sure it is the right circuit? Generally, PCBs should be"
    print "made from *_test.asc files, not the components they test, so that"
    print "power is supplied."
    raise SystemExit

print "Found netlist: %s" % (netfile,)

if "-q" not in sys.argv:
    # Get parameters on the circuit, to help with unique identifiers,
    # so multiple circuits can easily be merged.
    print "\nConfiguration Questions (to skip, pass -q next time)\n"
    try:
        os.environ["JC_CHIP_START"] = str(int(raw_input("Start chip numbering at: ")))
    except ValueError:
        print "(Using default)"

    try:
        os.environ["JC_NETNAME_SUFFIX"] = raw_input("Netname suffix: ")
    except ValueError:
        print "(Using default)"

    try:
        os.environ["JC_RESISTOR_SERIAL_START"] = str(int(raw_input("Start resistor numbering at: ")))
    except ValueError:
        print "(Using default)"

# Copy here so files are saved locally, in 'bb' instead of 'circuits'
os.system("cp -v %s ." % (netfile,))
os.system("python bb.py %s.net -p" % (name,))

if os.access("%s.pads" % (name,), os.R_OK):
    print "Your PADS-PCB netlist file is now available at %s.pads for importing into FreePCB." % (name,)
else:
    print "Seems there was a problem generating %s.pads." % (name,)
