program_counter = 0
output_address = 10000

opcode_mapping = {
    int('0110011', 2): 'R',
    int('0010011', 2): 'I',
    int('1100011', 2): 'B',
    int('0100011', 2): 'S',
    int('0000011', 2): 'L',
    int('1101111', 2): 'JAL',
    int('1100111', 2): 'JALR',
    int('0110111', 2): 'LUI',
    int('0010111', 2): 'AUIPC'
}

funct3_mapping_itype = {
    int('0b000', 2): 'addi',
    int('0b001', 2): 'slli',
    int('0b010', 2): 'slti',
    int('0b011', 2): 'sltiu',
    int('0b100', 2): 'xori',
    int('0b101', 2): 'srliOrSrai',
    int('0b110', 2): 'ori',
    int('0b111', 2): 'andi'
}

funct3_mapping_sType = {
    int('0b000', 2): 'sb',
    int('0b001', 2): 'sh',
    int('0b010', 2): 'sw'
}

funct3_mapping_bType = {
    int('0b000', 2): 'beq',
    int('0b001', 2): 'bne',
    int('0b100', 2): 'blt',
    int('0b101', 2): 'bge',
    int('0b110', 2): 'bltu',
    int('0b111', 2): 'bgeu'
}

funct3_mapping_rType = {
    int('0b000', 2): 'addOrSub',
    int('0b001', 2): 'sll',
    int('0b010', 2): 'slt',
    int('0b011', 2): 'sltu',
    int('0b100', 2): 'xor',
    int('0b101', 2): 'srlOrSra',
    int('0b110', 2): 'or',
    int('0b111', 2): 'and',
}

funct7_mapping_addOrSub = {
    int('0000000', 2): 'add',
    int('0100000', 2): 'sub',
}

funct7_mapping_srlOrSra = {
    int('0000000', 2): 'srl',
    int('0100000', 2): 'sra',
}

funct7_mapping_srliOrSrai = {
    int('0000000', 2): 'srli',
    int('0100000', 2): 'srai',
}

bitmask32 = int('1'*32, 2)
bitmask16 = int('1'*16, 2)
bitmask8 = int('1'*8, 2)

def bitextract(data,start,end):
    masklength = end -start +1
    mask = pow(2,masklength) - 1
    shifted_value = data >> start
    return shifted_value & mask

class Memory:
    def __init__(self, size):
        self.size = size
        self.memory = [0] * size

    def read(self, address):
        lineno = int(address/4)
        if 0 <= lineno < self.size:
            slot_no = address % 4
            if(slot_no > 0):
                raise ValueError("Unaligned access")
            return self.memory[lineno]
        else:
            raise ValueError("Invalid memory lineno")

    def read_8(self, address):
        lineno = int(address/4)
        if 0 <= lineno < self.size:
            slot_no = address % 4
            return bitextract(self.memory[lineno], slot_no*8, slot_no*8 + 7)
        else:
            raise ValueError("Invalid memory lineno")

    def read_8_s(self, address):
        read_val = self.read_8(address)
        imm_7 = bitextract(read_val,7,7)
        imm_8_31 = int(str(imm_7)*24,2)
        return (read_val) | (imm_8_31<< 8)

    def read_16(self, address):
        lineno = int(address/4)
        if 0 <= lineno < self.size:
            slot_no = address % 4
            if(slot_no == 3):
                raise ValueError("Unaligned access")
            return bitextract(self.memory[lineno], slot_no*8, slot_no*8 + 15)
        else:
            raise ValueError("Invalid memory lineno")
                
    def read_16_s(self, address):
        read_val = self.read_16(address)
        imm_15 = bitextract(read_val,15,15)
        imm_16_31 = int(str(imm_15)*16,2)
        return (read_val) | (imm_16_31<< 16)

    def write(self, address, data):
        lineno = int(address/4)
        if(address == output_address):
            print(data)
            return
        if 0 <= lineno < self.size:
            slot_no = address % 4
            if(slot_no > 0):
                raise ValueError("Unaligned access")
            self.memory[lineno] = data
        else:
            raise ValueError("Invalid memory lineno")

    def write_8(self, address, data):
        lineno = int(address/4)
        if 0 <= lineno < self.size:
            read_val = self.memory[lineno] #read existing val
            slot_no = address % 4 #seat no

            negate_mask = (~(bitmask8 << (slot_no * 8))) & bitmask32 #00000000 in slot_no and 11111111 in other place
            write_val = (read_val & negate_mask) | (data << (slot_no * 8))
            self.memory[lineno] = write_val                                                                                                   
        else:
            raise ValueError("Invalid memory lineno")       

    def write_16(self, address, data):
        lineno = int(address/4)
        if 0 <= lineno < self.size:
            read_val = self.memory[lineno]
            slot_no = address % 4 #seat no
            if(slot_no == 3):
                raise ValueError("Unaligned access")
            negate_mask = (~(bitmask16 << (slot_no * 8))) & bitmask32 #00000000 in slot_no and 11111111 in other place
            write_val = (read_val & negate_mask) | (data << (slot_no * 8))
            self.memory[lineno] = write_val
        else:
            raise ValueError("Invalid memory lineno")                

memory = Memory(256)

ins_file = open("data_hex.txt")
intrs = ins_file.readlines()

for i in range(0,len(intrs)):
    memory.write(i*4,int(intrs[i],16)) 

register_file = [0]*32

def twos_comp(val):
    if (val & (1 << (32 - 1))) != 0: # if sign bit is set e.g., 8bit: 128-255
        val = val - (1 << 32)        # compute negative value
    return val

class Instruction:
    def __init__(self, inst):
        self.inst = inst
        self.opcode = self.get_opcode()
        self.rs1  = self.get_rs1()
        self.rs2 = self.get_rs2()
        self.func3 = self.get_funct3()
        self.func7 = self.get_funct7()
        self.rd = self.get_rd()
        self.type = self.get_type()
        self.imm = self.get_immediate()
        self.shamt = self.rs2
        self.s_offset = self.get_immediate()


    def bitextract(self,start,end):
        return bitextract(self.inst,start,end)

    def get_opcode(self):
        return self.bitextract(0,6)

    def get_rd(self):
        return self.bitextract(7,11)

    def get_funct3(self):
        return self.bitextract(12,14)

    def get_funct7(self):
        return self.bitextract(25,31)    

    def get_rs1(self):
        return self.bitextract(15,19)

    def get_rs2(self):
        return self.bitextract(20,24)   

    def get_type(self):
        return opcode_mapping[self.opcode]

    def get_immediate(self):
        if(self.get_type() in  ['JAL','JALR']):
            imm_20 = self.bitextract(31,31)
            imm_10_1 = self.bitextract(21,30) 
            imm_11 = self.bitextract(20,20) 
            imm_19_12 = self.bitextract(12,19)
            imm_21_31 = int(str(imm_20)*11,2)
            return (imm_10_1 << 1) | (imm_11<< 11) | (imm_19_12<<12) | (imm_20<<20) | (imm_21_31<<21)

        elif(self.get_type() in  ['I','L']):
            imm_11_0 = self.bitextract(20,31)
            imm_11 = self.bitextract(31,31)
            imm_12_31 = int(str(imm_11)*20,2)
            return (imm_11_0) | (imm_12_31<< 12)

        elif(self.get_type()== 'S'):
            imm_4_0 = self.bitextract(7,11)
            imm_5_11 = self.bitextract(25,31)
            imm_11 = self.bitextract(31,31)
            imm_12_31 = int(str(imm_11)*20,2)
            return (imm_4_0) | (imm_5_11<< 5) | (imm_12_31<<12)

        elif(self.get_type() in ['LUI','AUIPC']):
            imm_31_12 = self.bitextract(12,31)
            return (imm_31_12<< 12)

        elif(self.get_type()== 'B'):
            imm_12 = self.bitextract(31,31)
            imm_11 = self.bitextract(7,7)
            imm_10_5 = self.bitextract(25,30)
            imm_4_1 = self.bitextract(8,11)
            imm_13_31 = int(str(imm_12)*19,2)
            return (imm_4_1<<1) | (imm_10_5<<5) | (imm_11<<11) | (imm_12<<12) |(imm_13_31<<13)

        else:
            print("underfined type")
            exit()   


while(1):
    next_pc = (program_counter + 4) & bitmask32
    inst =  memory.read(program_counter) #FETCH
    instruction = Instruction(inst)
    
    if(instruction.type == 'I'):
        if(funct3_mapping_itype[instruction.func3] == 'addi'):
            register_file[instruction.rd] = (register_file[instruction.rs1] + instruction.imm) & bitmask32
        elif(funct3_mapping_itype[instruction.func3] == 'slti'):
            register_file[instruction.rd] = (twos_comp(register_file[instruction.rs1]) < twos_comp(instruction.imm)) & bitmask32
        elif(funct3_mapping_itype[instruction.func3] == 'sltiu'):
            register_file[instruction.rd] = (register_file[instruction.rs1] < instruction.imm) & bitmask32
        elif(funct3_mapping_itype[instruction.func3] == 'xori'):
            register_file[instruction.rd] = (register_file[instruction.rs1] ^ instruction.imm) & bitmask32
        elif(funct3_mapping_itype[instruction.func3] == 'ori'):
            register_file[instruction.rd] = (register_file[instruction.rs1] | instruction.imm) & bitmask32
        elif(funct3_mapping_itype[instruction.func3] == 'andi'):
            register_file[instruction.rd] = (register_file[(instruction.rs1)] & (instruction.imm)) & bitmask32
        elif(funct3_mapping_itype[instruction.func3] == 'slli'):
            register_file[instruction.rd] = (register_file[instruction.rs1] << instruction.shamt) & bitmask32
        elif(funct3_mapping_itype[instruction.func3] == 'srliOrSrai'):
            if(funct7_mapping_srliOrSrai[instruction.func7] == 'srli'):
                register_file[instruction.rd] = (register_file[instruction.rs1] >> instruction.shamt) & bitmask32
            elif(funct7_mapping_srliOrSrai[instruction.func7] == 'srai'):
                register_file[instruction.rd] = (twos_comp(register_file[instruction.rs1]) >> instruction.shamt) & bitmask32
    elif(instruction.type == 'R'):
        if(funct3_mapping_rType[instruction.func3] == 'addOrSub'):
            if(funct7_mapping_addOrSub[instruction.func7] == 'add'):
                register_file[instruction.rd] = (register_file[instruction.rs1] + register_file[instruction.rs2]) & bitmask32
            elif(funct7_mapping_addOrSub[instruction.func7] == 'sub'):
                register_file[instruction.rd] = (register_file[instruction.rs1] - register_file[instruction.rs2]) & bitmask32
        elif(funct3_mapping_rType[instruction.func3] == 'sll'):
            register_file[instruction.rd] = (register_file[instruction.rs1] << register_file[instruction.rs2]) & bitmask32
        elif(funct3_mapping_rType[instruction.func3] == 'slt'):
            register_file[instruction.rd] = (twos_comp(register_file[instruction.rs1]) < twos_comp(register_file[instruction.rs2])) & bitmask32
        elif(funct3_mapping_rType[instruction.func3] == 'sltu'):
            register_file[instruction.rd] = (register_file[instruction.rs1] < register_file[instruction.rs2]) & bitmask32
        elif(funct3_mapping_rType[instruction.func3] == 'xor'):
            register_file[instruction.rd] = (register_file[(instruction.rs1)] ^ register_file[instruction.rs2]) & bitmask32
        elif(funct3_mapping_rType[instruction.func3] == 'srl'):
            register_file[instruction.rd] = (register_file[instruction.rs1] >> register_file[instruction.rs2]) & bitmask32
        elif(funct3_mapping_rType[instruction.func3] == 'sra'):
            register_file[instruction.rd] = (twos_comp(register_file[instruction.rs1]) >> register_file[instruction.rs2]) & bitmask32
        elif(funct3_mapping_rType[instruction.func3] == 'or'):
            register_file[instruction.rd] = (register_file[instruction.rs1] | register_file[instruction.rs2]) & bitmask32
        elif(funct3_mapping_rType[instruction.func3] == 'and'):
            register_file[instruction.rd] = (register_file[instruction.rs1] & register_file[instruction.rs2]) & bitmask32
        
    elif(instruction.type == 'S'):
        if(funct3_mapping_sType[instruction.func3] == 'sb'):
            memory.write_8((register_file[instruction.rs1] + instruction.s_offset) & bitmask32, register_file[instruction.rs2] & bitmask8)
        elif(funct3_mapping_sType[instruction.func3] == 'sh'):
            memory.write_16((register_file[instruction.rs1] + instruction.s_offset) & bitmask32, register_file[instruction.rs2] & bitmask16)
        elif(funct3_mapping_sType[instruction.func3] == 'sw'):
            memory.write((register_file[instruction.rs1] + instruction.s_offset) & bitmask32 , register_file[instruction.rs2])

    elif(instruction.type == 'L'):
        if(funct3_mapping_sType[instruction.func3] == 'lb'):
            register_file[instruction.rd] = memory.read_8_s((register_file[instruction.rs1] + instruction.s_offset) & bitmask32)
        elif(funct3_mapping_sType[instruction.func3] == 'lh'):
            register_file[instruction.rd] = memory.read_16_s((register_file[instruction.rs1] + instruction.s_offset) & bitmask32)
        elif(funct3_mapping_sType[instruction.func3] == 'lw'):
            register_file[instruction.rd] = memory.read((register_file[instruction.rs1] + instruction.s_offset) & bitmask32)
        elif(funct3_mapping_sType[instruction.func3] == 'lbu'):
            register_file[instruction.rd] = memory.read_8((register_file[instruction.rs1] + instruction.s_offset) & bitmask32) 
        elif(funct3_mapping_sType[instruction.func3] == 'lhu'):
            register_file[instruction.rd] = memory.read_16((register_file[instruction.rs1] + instruction.s_offset) & bitmask32) 
               
    elif(instruction.type == 'B'):
        if(funct3_mapping_bType[instruction.func3] == 'beq'):
            if(register_file[instruction.rs1] == register_file[instruction.rs2]):
                next_pc = (program_counter + instruction.s_offset) & bitmask32
        elif(funct3_mapping_bType[instruction.func3] == 'bne'):
            if(register_file[instruction.rs1] != register_file[instruction.rs2]):
                next_pc = (program_counter + instruction.s_offset) & bitmask32
        elif(funct3_mapping_bType[instruction.func3] == 'blt'):
            if(twos_comp(register_file[instruction.rs1]) < twos_comp(register_file[instruction.rs2])):
                next_pc = (program_counter + instruction.s_offset) & bitmask32
        elif(funct3_mapping_bType[instruction.func3] == 'bge'):
            if(twos_comp(register_file[instruction.rs1]) >= twos_comp(register_file[instruction.rs2])):
                next_pc = (program_counter + instruction.s_offset) & bitmask32
        elif(funct3_mapping_bType[instruction.func3] == 'bltu'):
            if(register_file[instruction.rs1] < register_file[instruction.rs2]):
                next_pc = (program_counter + instruction.s_offset) & bitmask32
        elif(funct3_mapping_bType[instruction.func3] == 'bgeu'):
            if(register_file[instruction.rs1] >= register_file[instruction.rs2]):
                next_pc = (program_counter + instruction.s_offset) & bitmask32

    elif(instruction.type == 'LUI'):
        register_file[instruction.rd] = instruction.imm

    elif(instruction.type == 'AUIPC'):
        register_file[instruction.rd] = (program_counter + instruction.imm) & bitmask32

    elif(instruction.type == 'JAL'):
        register_file[instruction.rd] = (program_counter + 4) & bitmask32
        next_pc = (program_counter + instruction.imm) & bitmask32
    
    elif(instruction.type == 'JALR'):
        register_file[instruction.rd] = (program_counter + 4) & bitmask32
        next_pc = ((register_file[instruction.rs1] + instruction.imm) & ~1) & bitmask32

    register_file[0] = 0 
    # print(program_counter,list(map(twos_comp,register_file)))
    if(next_pc == program_counter):
        print("infinite loop detected")
        exit()
    program_counter = next_pc