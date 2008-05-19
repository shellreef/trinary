; This will fail to assemble because the labels refer to future instructions.
; TCA2's asm.py doesn't currently allow this, but it is possible by using
; a two-pass assembler to first resolve the labels, then assemble.
        be below, below2
below:  lwi -3
below2: cmp in, a
