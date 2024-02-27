.global _boot
.text

_boot:                   
    li x1 , 1 
    li x2,100
    li x3,10000

_loop:
    beq x1,x2, _infinite_loop
    andi x4,x1,3 /* to get last 2 digits of binary value -> we and by 3 */
    bne x4,x0, _skip /* if(x4 != x0) -> go to _skip , x0 = 0 */
    /* bnez x4, _skip */
    sw x1,0(x3)

_skip:
    addi x1,x1,1
    j _loop

_infinite_loop:
	j _infinite_loop