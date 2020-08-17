"""CPU functionality."""

import sys
from numbers import Number


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""

        # Memory
        self.ram = [None] * 256
        # Registers
        self.reg = [None] * 8
        # Program Counter
        self.pc = 0
        # Stack Pointer
        self.reg[7] = 0xF4
        # Flags Register
        self.fl = 0b00000000

    def load(self, program):
        """Load a program into memory."""

        address = 0

        try:
            with open(program) as file:
                for line in file:
                    comment_split = line.split('#')
                    possible_num = comment_split[0]

                    if possible_num == '':
                        continue

                    if possible_num[0] == '1' or possible_num[0] == '0':
                        num = possible_num[:8]
                        self.ram[address] = int(num, 2)
                        address += 1

        except:
            print("Program not found.")

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "CMP":
            # FL bits: 0b00000LGE
            if self.reg[reg_a] == self.reg[reg_b]:
                self.fl = 0b00000001
            elif self.reg[reg_a] < self.reg[reg_b]:
                self.fl = 0b00000100
            elif self.reg[reg_a] > self.reg[reg_b]:
                self.fl = 0b00000010
            else:
                self.fl = 0b00000000

        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %s | %02X %02X %02X |" % (
            self.pc,
            bin(self.fl),
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='\n')

        # for i in range(7):
        #     print(" %02X" % self.reg[i], end='')

    def ram_read(self, addr):
        return self.ram[addr]

    def ram_write(self, val, addr):
        self.ram[addr] = val

    def run(self):
        """Run the CPU."""

        running = True

        while running:
            IR = self.ram[self.pc]
            try:
                self.trace()
            except:
                print('Trace failed.')

            # HLT
            if IR == int('00000001', 2):
                running = False
                self.pc = 0

            # LDI
            elif IR == int('10000010', 2):
                index = self.ram[self.pc + 1]
                value = self.ram[self.pc + 2]
                self.reg[index] = value
                self.pc += 3

            # PRN
            elif IR == int('01000111', 2):
                index = self.ram[self.pc + 1]
                value = self.reg[index]
                print(value)
                self.pc += 2

            # MUL
            elif IR == int('10100010', 2):
                indexA = self.ram[self.pc + 1]
                indexB = self.ram[self.pc + 2]
                self.reg[indexA] = self.reg[indexA] * self.reg[indexB]
                self.pc += 3

            # PUSH
            elif IR == int('01000101', 2):
                self.reg[7] -= 1
                register_number = self.ram[self.pc + 1]
                number_to_push = self.reg[register_number]
                stack_pntr = self.reg[7]
                self.ram[stack_pntr] = number_to_push
                self.pc += 2

            # POP
            elif IR == int('01000110', 2):
                stack_pntr = self.reg[7]
                popped_value = self.ram[stack_pntr]
                register_number = self.ram[self.pc + 1]
                self.reg[register_number] = popped_value
                self.reg[7] += 1
                self.pc += 2

            # CALL
            elif IR == int('01010000', 2):
                next_instruction = self.pc + 2
                self.reg[7] -= 1
                stack_pntr = self.reg[7]
                self.ram[stack_pntr] = next_instruction
                reg_idx = self.ram[self.pc + 1]
                self.pc = self.reg[reg_idx]

            # RET
            elif IR == int('00010001', 2):
                stack_pntr = self.reg[7]
                return_addr = self.ram[stack_pntr]
                self.reg[7] += 1
                self.pc = return_addr

            # CMP
            elif IR == int('10100111', 2):
                reg_a = self.ram[self.pc + 1]
                reg_b = self.ram[self.pc + 2]
                self.alu("CMP", reg_a, reg_b)
                self.pc += 3

            # JMP
            elif IR == int('01010100', 2):
                reg = self.ram[self.pc + 1]
                self.pc = self.reg[reg]

            # JEQ
            elif IR == int('01010101', 2):
                if self.fl & 0b00000001:
                    reg = self.ram[self.pc + 1]
                    self.pc = self.reg[reg]
                else:
                    self.pc += 2

            # JNE
            elif IR == int('01010101', 2):
                if self.fl & 0b00000001 == False:
                    print('not equal')
                    reg = self.ram[self.pc + 1]
                    self.pc = self.reg[reg]
                else:
                    self.pc += 2

            else:
                print('Woah now.')
                self.pc += 1
