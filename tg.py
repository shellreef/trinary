# Transmission gate, implemented with CD4016 

nodes = ("IN_OUT", "OUT_IN", "CONTROL")

# Quad transmission gate IC
parts_generated = "CD4016"
parts_consumed = ["M1", "M2", "M3", "M4", "M5", "M6"]
parts_kept = []

# Based on http://www.cedmagic.com/tech-info/data/cd4016.pdf
pins = [ 
        { "IN_OUT": ("CD4016", 1), "OUT_IN": ("CD4016", 2), "CONTROL": ("CD4016", 13) }, # SW A
        { "IN_OUT": ("CD4016", 4), "OUT_IN": ("CD4016", 3), "CONTROL": ("CD4016", 5) },  # SW B
        { "IN_OUT": ("CD4016", 8), "OUT_IN": ("CD4016", 9), "CONTROL": ("CD4016", 6) },  # SW C
        { "IN_OUT": ("CD4016", 4), "OUT_IN": ("CD4016", 3), "CONTROL": ("CD4016", 5) },  # SW D
       ]

global_pins = { "$G_Vdd": ("CD4016", 14), "$G_Vss": ("CD4016", 7) }
