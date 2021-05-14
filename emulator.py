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
    elif op == asm.INS_JMP:
        if rc == asm.JC_ALWAYS:
            name = "jmp"
        elif rc == asm.JC_JEQ:
            name = "jeq"
        elif rc == asm.JC_JGT:
            name = "jgt"
        elif rc == asm.JC_JGE:
            name = "jge"
        elif rc == asm.JC_JGTS:
            name = "jgts"
        elif rc == asm.JC_JGES:
            name = "jges"
        else:
            raise Exception("Illegal jump condition: " + hex(rc))
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
        if rc == asm.JC_ALWAYS:
            name = "jmpi"
        elif rc == asm.JC_JEQ:
            name = "jeqi"
        elif rc == asm.JC_JGT:
            name = "jgti"
        elif rc == asm.JC_JGE:
            name = "jgei"
        elif rc == asm.JC_JGTS:
            name = "jgtsi"
        elif rc == asm.JC_JGES:
            name = "jgesi"
        else:
            raise Exception("Illegal jump condition: " + hex(rc))
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
        self.sflag = 0
        self.zflag = 0
        self.oflag = 0

    def load_program(self, bs):
        if len(bs) >= 256:
            raise Exception("Program too big")

        for i, b in enumerate(bs):
            self.ram[i] = b

    def jmp_cond(self, cond):
        if cond == asm.JC_ALWAYS:
            return True
        elif cond == asm.JC_JEQ:
            return self.zflag != 0
        elif cond == asm.JC_JGT:
            return self.cflag != 0 and self.zflag == 0
        elif cond == asm.JC_JGE:
            return self.cflag != 0
        elif cond == asm.JC_JGTS:
            return self.zflag == 0 and self.oflag == self.sflag
        elif cond == asm.JC_JGES:
            return self.oflag == self.sflag
        else:
            raise Exception("Illegal jump condition: " + hex(cond))

    def step(self):
        hi = self.ram[self.iptr]
        lo = self.ram[(self.iptr + 1) % 256]
        iptr = self.iptr
        self.iptr = (self.iptr + 2) % 256

        op = (hi & 0b11111000) >> 3
        rc = (hi & 0b00000111)

        if op >= asm.INS_IMM_START and op <= asm.INS_IMM_END:
            imm = lo
            a = 0
            b = 0
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
            b = 0b11111111 ^ b
            out = a + b + 1
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
            b = 0b11111111 ^ b
            out = a + b + 1
        elif op == asm.INS_JMP:
            out = a + b
            if self.jmp_cond(rc):
                self.iptr = out % 256
        elif op == asm.INS_LD:
            self.regs[rc] = self.ram[self.regs[7]]
        elif op == asm.INS_ST:
            out = a + b
            self.ram[self.regs[7]] = out % 256
        elif op == asm.INS_ADDC:
            out = a + b + self.cflag
            self.regs[rc] = out % 256
        elif op == asm.INS_SUBC:
            b = 0b11111111 ^ b
            out = a + b + self.cflag
            self.regs[rc] = out % 256
        elif op == asm.INS_SHRC:
            out = a + b
            out >>= 1 | ((out & 0b1) << 8) # Put the shifted-out bit in cout
            out |= self.cflag << 7 # Shifted-in number is carry flag
            self.regs[rc] = out % 256
        elif op == asm.INS_CMPC:
            b = 0b11111111 ^ b
            out = a + b + self.cflag
        elif op == asm.INS_JMPI:
            if self.jmp_cond(rc):
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
        self.sflag = (out & 0b10000000) >> 7
        self.zflag = 1 if (out & 0b11111111) == 0 else 0
        overflowed = a & 0b10000000 == b & 0b10000000 and a & 0b10000000 != out & 0b10000000
        self.oflag = 1 if overflowed else 0

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
                    cpu.regs,
                    f"z:{cpu.zflag} c:{cpu.cflag} s:{cpu.sflag} o:{cpu.oflag}")
            input()
            cpu.step()
    else:
        while not cpu.halted:
            cpu.step()

    print("Registers after execution:")
    print(cpu.regs)
