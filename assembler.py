#!/usr/bin/env python3

import sys

class AsmError(Exception):
    pass

TAG_INT = 0
TAG_REG = 1
TAG_STRING = 2
TAG_LABEL = 3

def tokenize_line(line):
    idx = 0
    def checkidx():
        if idx >= len(line):
            raise AsmError("Unexpected EOL")

    while idx < len(line):
        if line[idx].isspace():
            idx += 1
            continue

        if line[idx] == '#':
            break

        if line[idx] == '\'':
            idx += 1
            if line[idx] == '\'':
                raise AsmError("Char literal needs contents")

            if line[idx] == '\\':
                idx += 1
                checkidx()
                if line[idx] == 'n':
                    ch = '\n'
                elif line[idx] == 'r':
                    ch = '\r'
                elif line[idx] == 't':
                    ch = '\t'
                elif line[idx] == '0':
                    ch = '\0'
                else:
                    ch = line[idx]
            else:
                ch = line[idx]

            idx += 1
            checkidx()
            if line[idx] != '\'':
                raise AsmError("Missing closing quote in char literal")

            yield (TAG_INT, ord(ch))
            idx += 1
            continue

        start = idx
        idx += 1
        while idx <= len(line) and not line[idx].isspace():
            idx += 1

        part = line[start:idx]
        if part.startswith("0x"):
            yield (TAG_INT, int(part[2:], 16))
        elif part.startswith("0b"):
            yield (TAG_INT, int(part[2:], 2))
        elif part.startswith("0o"):
            yield (TAG_INT, int(part[2:], 8))
        elif part.isnumeric():
            yield (TAG_INT, int(part, 10))
        elif part == "r0":
            yield (TAG_REG, 0)
        elif part == "r1":
            yield (TAG_REG, 1)
        elif part == "r2":
            yield (TAG_REG, 2)
        elif part == "r3":
            yield (TAG_REG, 3)
        elif part == "r4":
            yield (TAG_REG, 4)
        elif part == "r5":
            yield (TAG_REG, 5)
        elif part == "r6":
            yield (TAG_REG, 6)
        elif part == "r7":
            yield (TAG_REG, 7)
        elif part.endswith(":"):
            yield (TAG_LABEL, part[:-1])
        else:
            yield (TAG_STRING, part)

FMT_R = 0
FMT_I = 1
FMT_BYTE = 2

INS_NOP = 0
INS_ADD = 1
INS_SUB = 2
INS_XOR = 3
INS_NAND = 4
INS_OR = 5
INS_AND = 6
INS_SHR = 7
INS_CMP = 8
INS_JMP = 9
INS_JC = 10
INS_JZ = 11
INS_JNZC = 12
INS_LD = 13
INS_ST = 14
INS_JMPI = 16
INS_JCI = 17
INS_JZI = 18
INS_JNZCI = 19
INS_IMM = 20
INS_STI = 21
INS_HALT = 31

INS_IMM_START = INS_JMPI
INS_IMM_END = INS_STI

def parse_line(line, defines, labels, iptr):
    parts = list(tokenize_line(line))

    while len(parts) > 0 and parts[0][0] == TAG_LABEL:
        labels[parts[0][1]] = iptr
        parts = parts[1:]

    if len(parts) == 0:
        return None

    if parts[0][0] != TAG_STRING:
        raise AsmError("Op must be a string")
    op = parts[0][1]

    args = parts[1:]
    for i in range(len(args)):
        if args[i][0] == TAG_STRING and args[i][1] in defines:
            args[i] = defines[args[i][1]]

    def require_args(*ns):
        for n in ns:
            if len(args) == n:
                return
        raise AsmError("Invalid argument count for " + op + ", expected " + str(ns))

    if op == "def":
        require_args(2)
        defines[parts[1]] = args[1]
        return None
    if op == "byte":
        require_args(1)
        return (FMT_BYTE, args[0])
    if op == "nop":
        require_args(0)
        return (FMT_R, INS_NOP, (TAG_REG, 0), (TAG_INT, 0), (TAG_INT, 0), 0)
    if op == "add":
        require_args(3)
        return (FMT_R, INS_ADD, args[0], args[1], args[2], 0)
    if op == "addc":
        require_args(3)
        return (FMT_R, INS_ADD, args[0], args[1], args[2], 1)
    if op == "mov":
        require_args(2)
        if args[1][0] == TAG_INT or args[1][0] == TAG_STRING:
            return (FMT_I, INS_IMM, args[0], args[1])
        else:
            return (FMT_R, INS_ADD, args[0], args[1], (TAG_INT, 0), 0)
        return (FMT_R, INS_ADD, args[0], (TAG_REG, 0), args[1], 0)
    if op == "sub":
        require_args(3)
        return (FMT_R, INS_SUB, args[0], args[1], args[2], 0)
    if op == "subc":
        require_args(3)
        return (FMT_R, INS_SUB, args[0], args[1], args[2], 1)
    if op == "xor":
        require_args(3)
        return (FMT_R, INS_XOR, args[0], args[1], args[2], 0)
    if op == "nand":
        require_args(3)
        return (FMT_R, INS_NAND, args[0], args[1], args[2], 0)
    if op == "or":
        require_args(3)
        return (FMT_R, INS_OR, args[0], args[1], args[2], 0)
    if op == "and":
        require_args(3)
        return (FMT_R, INS_AND, args[0], args[1], args[2], 0)
    if op == "shr":
        require_args(3)
        return (FMT_R, INS_SHR, args[0], args[1], args[2], 0)
    if op == "shrc":
        require_args(3)
        return (FMT_R, INS_SHR, args[0], args[1], args[2], 1)
    if op == "cmp":
        require_args(2)
        return (FMT_R, INS_CMP, (TAG_REG, 0), args[0], args[1], 0)
    if op == "cmpc":
        require_args(2)
        return (FMT_R, INS_CMP, (TAG_REG, 0), args[1], args[2], 1)
    if (
            op == "jmp" or op == "jc" or op == "jge"
            or op == "jz" or op == "jeq" or op == "jnzc" or op == "jgt"):
        require_args(1, 2)
        if (
                len(args) == 1 and
                (args[0][0] == TAG_INT or args[0][0] == TAG_STRING)):
            if op == "jmp":
                ins = INS_JMPI
            elif op == "jc" or op == "jge":
                ins = INS_JCI
            elif op == "jz" or op == "jeq":
                ins = INS_JZI
            elif op == "jnzc" or op == "jgt":
                ins = INS_JNZCI
            return (FMT_I, ins, (TAG_REG, 0), args[0])
        else:
            if op == "jmp":
                ins = INS_JMP
            elif op == "jc" or op == "jge":
                ins = INS_JC
            elif op == "jz" or op == "jeq":
                ins = INS_JZ
            elif op == "jnzc" or op == "jgt":
                ins = INS_JNZC

            if len(args) == 1:
                return (FMT_R, ins, (TAG_REG, 0), args[0], (TAG_INT, 0), 0)
            else:
                return (FMT_R, ins, (TAG_REG, 0), args[0], args[1], 0)
    if op == "ld":
        require_args(1)
        return (FMT_R, INS_LD, args[0], (TAG_REG, 0), (TAG_REG, 0), 0)
    if op == "st":
        require_args(1, 2)
        if len(args) == 1 and (args[0][0] == TAG_INT or args[0][0] == TAG_STRING):
            return (FMT_I, INS_STI, (TAG_REG, 0), args[0])
        elif len(args) == 1:
            return (FMT_R, INS_ST, (TAG_REG, 0), (TAG_REG, 0), args[0], 0)
        else:
            return (FMT_R, INS_ST, (TAG_REG, 0), args[0], args[1], 0)
    if op == "halt":
        require_args(0)
        return (FMT_R, INS_HALT, (TAG_REG, 0), (TAG_REG, 0), (TAG_REG, 0), 0)

    raise AsmError("Unknown op " + op)

def serialize_instr(instr, defines, labels):
    def unlabel(arg):
        if arg[0] == TAG_STRING:
            if arg[1] in labels:
                return (TAG_INT, labels[arg[1]])
            else:
                raise AsmError("Unknown label: " + arg[1])
        else:
            return arg

    if instr[0] == FMT_BYTE:
        fmt, b = instr
        b = unlabel(b)
        if b[0] != TAG_INT:
            raise AsmError("Bytes must be known at compile time")
        return bytes((b[1],))
    if instr[0] == FMT_I:
        fmt, op, rc, imm = instr
        imm = unlabel(imm)
        
        if rc[0] != TAG_REG:
            raise AsmError("Destination must be a register")
        rc = rc[1]

        if imm[0] != TAG_INT:
            raise AsmError("Immediate must me an integer")
        imm = imm[1]

        hi = (op << 3) | rc
        lo = imm
        return bytes((hi, lo))
    if instr[0] == FMT_R:
        fmt, op, rc, ra, rb, csel = instr
        isel = 0
        ra = unlabel(ra)
        rb = unlabel(rb)

        if rc[0] != TAG_REG:
            raise AsmError("Destination must be a register")
        rc = rc[1]

        if ra[0] != TAG_REG:
            raise AsmError("Argument A must be a register")
        ra = ra[1]

        if rb[0] == TAG_INT:
            isel = 1
            if rb[1] < 0 or rb[1] > 7:
                raise AsmError("Argument B must be between 0 and 7")
        rb = rb[1]

        hi = (op << 3) | rc
        lo = (isel << 7) | (csel << 6) | (ra << 3) | rb
        return bytes((hi, lo))

def assemble(inf, outf):
    instrs = []
    defines = {}
    labels = {}
    iptr = 0
    linenum = 1
    for line in inf:
        try:
            instr = parse_line(line, defines, labels, iptr)
        except AsmError as ex:
            raise AsmError("Error on line " + str(linenum) +": " + str(ex)) from None

        if instr != None:
            instrs.append((linenum, instr))
            if instr[0] == FMT_BYTE:
                iptr += 1
            else:
                iptr += 2
        linenum += 1

    for linenum, instr in instrs:
        try:
            bs = serialize_instr(instr, defines, labels)
        except AsmError as ex:
            raise AsmError("Error on line " + str(linenum) + ": " + str(ex)) from None

        outf.write(bs)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: " + sys.argv[0] + " <infile> <outfile>")
        exit(1)
    with open(sys.argv[1], "r") as inf:
        with open(sys.argv[2], "wb") as outf:
            try:
                assemble(inf, outf)
            except AsmError as ex:
                print(str(ex))
                exit(1)
