# Ternary NAND, implemented with CD4007
#

nodes = ("A", "B", "TNAND_Out")

# Dual MOSFET Complementary Pair + Binary Inverter
parts_generated = ["CD4007"]
parts_consumed = ["MP1", "MP2", "MN1", "MN2"]
parts_kept = ["RP", "RN"]

# Based on pinout from http://www.cedmagic.com/tech-info/data/cd4016.pdf
pins = [ 
        { 
            "A": ("CD4007", 3),
            "B": ("CD4007", 6),
            "$G_Vdd": [("CD4007", 2), ("CD4007", 14)], 
            "TNOR_Out": "TNOR_Out",
            "$G_Vss": ("CD4007", 7),

            # Internal nodes

            # Connect these two nodes together
            "NI": [("CD4007", 4), ("CD4007", 8)],
            # Connects to resistors
            "NP": [("CD4007", 1), ("CD4007", 13)],
            "NN": ("CD4007", 5),
        }
       ]

# Always connected once if use once or more
global_pins = {
        # TODO: always connect binary inverter, since we'll never be using it,
        # but to prevent MOSFETs from switching on and off, wasting power?
        # May need a change in this data structure to support multiple connections to $G_Vdd/Vss
        }

