firstloop:
	./toolChain/bin/riscv32-unknown-elf-as ./assembly_examples/firstloop.s -o example.o
	./utils/elf2hex/elf2hex --bit-width 32 --input example.o  --output data_hex.txt
even_number:
	./toolChain/bin/riscv32-unknown-elf-as ./assembly_examples/even_number.s -o example.o
	./utils/elf2hex/elf2hex --bit-width 32 --input example.o  --output data_hex.txt
four_divide:
	./toolChain/bin/riscv32-unknown-elf-as ./assembly_examples/four_divide.s -o example.o
	./utils/elf2hex/elf2hex --bit-width 32 --input example.o  --output data_hex.txt
