; Test cmp (compare) instruction and lwi (load word immediate)
lwi -3          ; load A with 0i0
cmp in, a       ; compare A to IN (probably 10i)
cmp a, in       ; now S should be opposite
