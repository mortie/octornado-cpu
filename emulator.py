#!/usr/bin/env python3

import assembler as asm

def disassemble(hi, lo):
    op = (hi & 0b11111000) >> 3
    rc = (hi & 0b00000111)

    if op == asm.INS_NOP:
        name = "nop"
    elif op == asm.INS_ADD:
        name = "add"
    elif op == asm.INS_SUB:
        name = "sub"
    elif op == asm.INS_XOR:
        name = "xor"
    elif op == asm.INS_NAND:
        name = "nand"
    elif op == asm.INS_OR:
        name = "or"
    elif op == asm.INS_AND:
        name = "and"
    elif op == asm.INS_SHR:
        name = "shr"
    elif op == asm.INS_CMP:
        name = "cmp"
    elif op == asm.INS_JC:
        name = "jge"
    elif op == asm.INS_JZ:
        name = "jeq"
    elif op == asm.INS_JNZC:
        name = "jgt"
    elif op == asm.INS_LD:
        name = "ld"
    elif op == asm.INS_ST:
        name = "st"
    elif op == asm.INS_ADDC:
        name = "addc"
    elif op == asm.INS_SUBC:
        name = "subc"
    elif op == asm.INS_SHRC:
        name = "shrc"
    elif op == asm.INS_CMPC:
        name = "cmpc"
    elif op == asm.INS_JMPI:
        name = "jmpi"
    elif op == asm.INS_JCI:
        name = "jgei"
    elif op == asm.INS_JZI:
        name = "jeqi"
    elif op == asm.INS_JNZCI:
        name = "jgti"
    elif op == asm.INS_IMM:
        name = "imm"
    elif op == asm.INS_STI:
        name = "sti"
    elif op == asm.INS_HALT:
        name = "halt"
    else:
        raise Exception("Illegal instruction: " + hex(op))

    if op >= asm.INS_IMM_START and op <= asm.INS_IMM_END:
        return f"{name} r{rc} {lo}"
    else:
        isel = (lo & 0b10000000) >> 7
        ra =   (lo & 0b01110000) >> 4
        rb =   (lo & 0b00001111)
        if csel:
            name += "c"
        if isel:
            return f"{name} r{rc} r{ra} {rb}"
        else:
            return f"{name} r{rc} r{ra} r{rb}"

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
        lo = self.ram[(self.iptr + 1) % 256]
        iptr = self.iptr
        self.iptr = (self.iptr + 2) % 256

        op = (hi & 0b11111000) >> 3
        rc = (hi & 0b00000111)

        if op >= asm.INS_IMM_START and op <= asm.INS_IMM_END:
            imm = lo
        else:
            isel = (lo & 0b10000000) >> 7
            ra =   (lo & 0b01110000) >> 4
            rb =   (lo & 0b00001111)
            a = self.regs[ra]
            if isel:
                b = rb
                if b & 0b1000:
                    b |= 0b11111000
            else:
                b = self.regs[rb % 8]

        out = 0
        if op == asm.INS_NOP:
            pass
        elif op == asm.INS_ADD:
            out = a + b
            self.regs[rc] = out % 256
        elif op == asm.INS_SUB:
            out = a + (0b11111111 ^ b) + 1
            self.regs[rc] = out % 256
        elif op == asm.INS_XOR:
            out = a ^ b
            self.regs[rc] = out % 256
        elif op == asm.INS_NAND:
            out = ~(a | b)
            self.regs[rc] = out % 256
        elif op == asm.INS_OR:
            out = (a | b)
            self.regs[rc] = out % 256
        elif op == asm.INS_AND:
            out = (a & b)
            self.regs[rc] = out % 256
        elif op == asm.INS_SHR:
            out = a + b
            out >>= 1 | ((out & 0b1) << 8) # Put the shifted-out bit in cout
            self.regs[rc] = out % 256
        elif op == asm.INS_CMP:
            out = a + (0b11111111 ^ b) + 1
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
            raise Exception("Illegal instruction at " + str(iptr) + ": " + hex(op))

        self.cflag = (out & 0b100000000) >> 8
        self.zflag = 1 if (out & 0b11111111) == 0 else 0

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("infile", help="Input file to execute")
    parser.add_argument("--step", default=False, action="store_true", help="Step through the program")
    args = parser.parse_args()

    cpu = CPU()
    with open(args.infile, "rb") as f:
        cpu.load_program(f.read())

    if args.step:
        while not cpu.halted:
            print(cpu.ram)
            print(
                    f"{cpu.iptr}:",
                    disassemble(cpu.ram[cpu.iptr], cpu.ram[cpu.iptr + 1]),
                    cpu.regs)
            input()
            cpu.step()
    else:
        while not cpu.halted:
            cpu.step()

    print("Registers after execution:")
    print(cpu.regs)
