# Ternary NOR, implemented with CD4007
#
# INCOMPLETE - TODO

nodes = ("A", "B", "TNOR_Out")

# Dual MOSFET Complementary Pair + Binary Inverter
parts_generated = ["CD4007"]
parts_consumed = ["MP1", "MP2", "MN1", "MN2"]
parts_kept = ["RP", "RN"]

# Based on pinout from http://www.cedmagic.com/tech-info/data/cd4016.pdf
pins = [ 
        { 
            "A": ("CD4007", 3),
            "B": ("CD4007", 6),
            "TNOR_Out": "TNOR_Out",
        }
       ]

# TODO:
# 14 to $G_Vdd
# 6 to A
# 13 to 2
# 1 to RP+
# RP- to TNOR_Out to RN-
# 8 to RN+ to 5
# 7 to 4 to $G_Vss
# 3 to B

# Always connected once if use once or more
global_pins = { 
        # Power connections
        "$G_Vdd": ("CD4007", 14), 
        "$G_Vss": ("CD4007", 7),

        # TODO: always connect binary inverter, since we'll never be using it,
        # but to prevent MOSFETs from switching on and off, wasting power?
        # May need a change in this data structure to support multiple connections to $G_Vdd/Vss
        }

