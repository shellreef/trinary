# Transmission gate, implemented with CD4016 

nodes = ("IN_OUT", "OUT_IN", "CONTROL")

# Quad transmission gate IC
parts_generated = "CD4016"
parts_consumed = ["M1", "M2", "M3", "M4", "M5", "M6"]
parts_kept = []

# Based on http://www.cedmagic.com/tech-info/data/cd4016.pdf
pins = [ 
        { "IN_OUT": 1, "OUT_IN": 2, "CONTROL": 13 }, # SW A
        { "IN_OUT": 4, "OUT_IN": 3, "CONTROL": 5 },  # SW B
        { "IN_OUT": 8, "OUT_IN": 9, "CONTROL": 6 },  # SW C
        { "IN_OUT": 4, "OUT_IN": 3, "CONTROL": 5 },  # SW D
       ]

global_pins = { "$G_Vdd": 14, "$G_Vss": 7 }
