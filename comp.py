import os
import sys
# try:
# except:
# 	filename='new_test.c'
filename=str(sys.argv[1])
flag= './toolChain/bin/riscv32-unknown-elf-'
os.system(flag+'gcc '+filename+' printer.c -s -o K_1.elf -nostartfiles -march=rv32ima -mabi=ilp32 -fPIC');
os.system('./utils/elf2hex/elf2hex --bit-width 32 --input K_1.elf  --output data_hex.txt');
