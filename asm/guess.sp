; swrom-fast include file, generated to by asm/asm.py, for program:
; 0i0
; ii1
; 1i0

; Select a voltage value based on the logic input at A
.func choose(A,for_n,for_z,for_p) {if(A<={V_N_max},for_n,if(A>={V_P_min},for_p,for_z))}

; Threshold voltages
.param V_N_max=-2
.param V_P_min=2

.func program_D0(A) {choose(A,V(0),V(_1),V(1))}
.func program_D1(A) {choose(A,V(_1),V(_1),V(_1))}
.func program_D2(A) {choose(A,V(0),V(1),V(0))}
