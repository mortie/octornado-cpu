#!/usr/bin/env python3

import sys

class AsmError(Exception):
    pass

TAG_INT = 0
TAG_REG = 1
TAG_LABEL = 2

def parse_arg(arg, defines):
    if arg[0].isnumeric():
        if arg.startswith("0x"):
            return (TAG_INT, int(arg[2:], 16))
        elif arg.startswith("0b"):
            return (TAG_INT, int(arg[2:], 2))
        elif arg.startswith("0o"):
            return (TAG_INT, int(arg[2:], 8))
        else:
            return (TAG_INT, int(arg, 10))
    elif arg == "r0":
        return (TAG_REG, 0)
    elif arg == "r1":
        return (TAG_REG, 1)
    elif arg == "r2":
        return (TAG_REG, 2)
    elif arg == "r3":
        return (TAG_REG, 3)
    elif arg == "r4":
        return (TAG_REG, 4)
    elif arg == "r5":
        return (TAG_REG, 5)
    elif arg == "r6":
        return (TAG_REG, 6)
    elif arg == "r7":
        return (TAG_REG, 7)
    elif arg in defines:
        return (TAG_INT, defines[arg])
    else:
        return (TAG_LABEL, arg)

FMT_R = 0
FMT_I = 1

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

def parse_line(line, defines, labels, iptr):
    parts = line.strip().split()

    while True:
        if len(parts) == 0:
            return None

        if parts[0].endswith(":"):
            labels[parts[1][:-1]] = iptr
            parts = parts[1:]
        else:
            break

    op = parts[0].lower()
    args = [parse_arg(part, defines) for part in parts[1:]]

    def require_args(*ns):
        for n in ns:
            if len(args) == n:
                return
        raise AsmError("Invalid argument count for " + op + ", expected " + str(ns))

    if op == "def":
        require_args(2)
        defines[parts[1]] = args[1]
        return None

    if op == "nop":
        require_args(0)
        return (FMT_R, INS_NOP, (TAG_REG, 0), (TAG_INT, 0), (TAG_INT, 0), 0)
    elif op == "add":
        require_args(3)
        return (FMT_R, INS_ADD, args[0], args[1], args[2], 0)
    elif op == "addc":
        require_args(3)
        return (FMT_R, INS_ADD, args[0], args[1], args[2], 1)
    elif op == "mov":
        require_args(2)
        if args[1][0] == TAG_INT or args[1][0] == TAG_LABEL:
            return (FMT_I, INS_IMM, args[0], args[1])
        else:
            return (FMT_R, INS_ADD, args[0], args[1], (TAG_INT, 0), 0)
        return (FMT_R, INS_ADD, args[0], (TAG_REG, 0), args[1], 0)
    elif op == "sub":
        require_args(3)
        return (FMT_R, INS_SUB, args[0], args[1], args[2], 0)
    elif op == "subc":
        require_args(3)
        return (FMT_R, INS_SUB, args[0], args[1], args[2], 1)
    elif op == "xor":
        require_args(3)
        return (FMT_R, INS_XOR, args[0], args[1], args[2], 0)
    elif op == "nand":
        require_args(3)
        return (FMT_R, INS_NAND, args[0], args[1], args[2], 0)
    elif op == "or":
        require_args(3)
        return (FMT_R, INS_OR, args[0], args[1], args[2], 0)
    elif op == "and":
        require_args(3)
        return (FMT_R, INS_AND, args[0], args[1], args[2], 0)
    elif op == "shr":
        require_args(3)
        return (FMT_R, INS_SHR, args[0], args[1], args[2], 0)
    elif op == "shrc":
        require_args(3)
        return (FMT_R, INS_SHR, args[0], args[1], args[2], 1)
    elif op == "cmp":
        require_args(2)
        return (FMT_R, INS_CMP, (TAG_REG, 0), args[1], args[2], 0)
    elif op == "cmpc":
        require_args(2)
        return (FMT_R, INS_CMP, (TAG_REG, 0), args[1], args[2], 1)
    elif (
            op == "jmp" or op == "jc" or op == "jz" or op == "jnzc" or
            op == "jgt" or op == "jge"):
        require_args(1, 2)
        if (
                len(args) == 1 and
                (args[0][0] == TAG_INT or args[0][1] == TAG_LABEL)):
            if op == "jmp":
                ins = INS_JMPI
            elif op == "jc" or op == "jge":
                ins = INS_JCI
            elif op == "jz":
                ins = INS_JZI
            elif op == "jnzc" or op == "jgt":
                ins = INS_JNZCI
            return (FMT_I, ins, (TAG_INT, 0), args[0])
        else:
            if op == "jmp":
                ins = INS_JMP
            elif op == "jc" or op == "jge":
                ins = INS_JC
            elif op == "jz":
                ins = INS_JZ
            elif op == "jnzc" or op == "jgt":
                ins = INS_JNZC

            if len(args) == 1:
                return (FMT_R, ins, (TAG_REG, 0), (TAG_REG, 0), args[0], 0)
            else:
                return (FMT_R, ins, (TAG_REG, 0), args[0], args[1], 0)
    elif op == "ld":
        require_args(1)
        return (FMT_R, INS_LD, args[0], (TAG_REG, 0), (TAG_REG, 0), 0)
    elif op == "st":
        require_args(1, 2)
        if len(args) == 1 and (args[0][0] == TAG_INT or args[0][0] == TAG_LABEL):
            return (FMT_I, INS_STI, args[0])
        elif len(args) == 1:
            return (FMT_R, INS_ST, (TAG_REG, 0), (TAG_REG, 0), args[0], 0)
        else:
            return (FMT_R, INS_ST, (TAG_REG, 0), args[0], args[1], 0)
    elif op == "halt":
        require_args(0)
        return (FMT_R, INS_HALT, (TAG_REG, 0), (TAG_REG, 0), (TAG_REG, 0), 0)
    else:
        raise AsmError("Unknown op " + op)

def serialize_instr(instr, defines, labels):
    def unlabel(arg):
        if arg[0] == TAG_LABEL:
            if arg[1] in labels:
                return (TAG_INT, labels[arg[1]])
            else:
                raise AsmError("Unknown label: " + arg[0])
        else:
            return arg

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
    elif instr[0] == FMT_R:
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
            iptr += 1
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
