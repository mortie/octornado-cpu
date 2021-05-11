#!/usr/bin/env python3

import assembler as asm
import sys

class CPU:
    def __init__(self):
        self.regs = [0] * 8
        self.ram = [0] * 256
        self.iptr = 0
        self.halted = False
        self.cflag = 0
        self.zflag = 0

    def load_program(self, bs):
        if len(bs) >= 256:
            raise Exception("Program too big")

        for i, b in enumerate(bs):
            self.ram[i] = b

    def step(self):
        hi = self.ram[self.iptr]
        lo = self.ram[self.iptr + 1]
        self.iptr = (self.iptr + 2) % 256

        op = (hi & 0b11111000) >> 3
        rc = (hi & 0b00000111)

        if op >= 0b10000 and op <= 0b10101:
            imm = lo
        else:
            isel = (lo & 0b10000000) >> 7
            csel = (lo & 0b01000000) >> 6
            ra =   (lo & 0b00111000) >> 3
            rb =   (lo & 0b00000111)
            a = self.regs[ra]
            if isel:
                b = rb
            else:
                b = self.regs[rb]

            if csel:
                carry = self.cflag
            else:
                carry = 0

        out = 0
        if op == asm.INS_NOP:
            pass
        elif op == asm.INS_ADD:
            out = a + b + carry
            self.regs[rc] = out % 256
        elif op == asm.INS_SUB:
            out = a - b + carry
            self.regs[rc] = out % 256
        elif op == asm.INS_XOR:
            out = a ^ b + carry
            self.regs[rc] = out % 256
        elif op == asm.INS_NAND:
            out = ~(a | b) + carry
            self.regs[rc] = out % 256
        elif op == asm.INS_OR:
            out = (a | b) + carry
            self.regs[rc] = out % 256
        elif op == asm.INS_AND:
            out = (a & b) + carry
            self.regs[rc] = out % 256
        elif op == asm.INS_SHR:
            out = ((a + b) >> 1) + carry
            self.regs[rc] = out % 256
        elif op == asm.INS_CMP:
            out = a - b + carry
        elif op == asm.INS_JMP:
            out = a + b
            self.iptr = out % 256
        elif op == asm.INS_JC:
            out = a + b
            if self.cflag:
                self.iptr = out % 256
        elif op == asm.INS_JZ:
            out = a + b
            if self.zflag:
                self.iptr = out % 256
        elif op == asm.INS_JNZC:
            out = a + b
            if self.cflag and not self.zflag:
                self.iptr = out % 256
        elif op == asm.INS_LD:
            self.regs[rc] = self.ram[self.regs[7]]
        elif op == asm.INS_ST:
            out = a + b
            self.ram[self.regs[7]] = out % 256
        elif op == asm.INS_JMPI:
            self.iptr = imm
        elif op == asm.INS_JCI:
            if self.cflag:
                self.iptr = imm
        elif op == asm.INS_JZI:
            if self.zflag:
                self.iptr = imm
        elif op == asm.INS_JNZCI:
            if self.cflag and not self.zflag:
                self.iptr = imm
        elif op == asm.INS_IMM:
            self.regs[rc] = imm
        elif op == asm.INS_STI:
            self.ram[self.regs[7]] = imm
        elif op == asm.INS_HALT:
            self.halted = True
        else:
            raise Exception("Illegal instruction: " + hex(op))

        self.cflag = (out & 0b100000000) >> 8
        self.zflag = 1 if (out & 0b11111111) == 0 else 0

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: " + sys.argv[0] + " <infile>")
        exit(1)

    cpu = CPU()
    with open(sys.argv[1], "rb") as f:
        cpu.load_program(f.read())

    while not cpu.halted:
        cpu.step()

    print("Registers after execution:")
    print(cpu.regs)
