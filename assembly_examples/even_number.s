.global _boot
.text

_boot:                   
    li x1 , 1  
    li x2,20   
    li x3,10000 
    li x5,1 

_loop:
    beq x1,x2, _infinite_loop /*if(x1=x2) -> infinite_loop{ */
    andi x4,x1,1 /* e = x1 & 1*/

    beq x4,x5, _skip /* if(x4==1) -> skip*/
    sw x1,0(x3) /* (print x1) by storing x1 in address(0 + x3)*/
    
_skip:
    addi x1,x1,1 /* x1 = x1 + 1 */
    j _loop /*goto _loop*/

_infinite_loop:       /*while(1); jump to the same pc*/
	j _infinite_loop