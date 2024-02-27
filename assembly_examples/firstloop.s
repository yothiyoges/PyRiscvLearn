.global _boot
.text

_boot:                   
    li x1 , 1 
    li x2,10
    li x3,10000

_loop:
    beq x1,x2, _infinite_loop
    sw x1,0(x3)
    addi x1,x1,1
    j _loop

_infinite_loop:
	j _infinite_loop