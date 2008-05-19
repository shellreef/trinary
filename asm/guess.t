init:  lwi -3         ; random number to guess   (0i0)
check: cmp in, a      ; did they guess right?    (ii1)
       be init, check ; reinit if correct, loop  (1i0)
