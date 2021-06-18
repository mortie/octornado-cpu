#!/usr/bin/env python3

import struct
import sys
import gzip

NBT_END = 0
NBT_BYTE = 1
NBT_SHORT = 2
NBT_INT = 3
NBT_LONG = 4
NBT_FLOAT = 5
NBT_DOUBLE = 6
NBT_BYTE_ARRAY = 7
NBT_STRING = 8
NBT_LIST = 9
NBT_COMPOUND = 10

class NBT:
    def __init__(self, f):
        self.f = f

    def write_end(self):
        self.write_byte(NBT_END)

    def write_byte(self, val):
        self.f.write(struct.pack("b", val))

    def write_short(self, val):
        self.f.write(struct.pack(">h", val))

    def write_int(self, val):
        self.f.write(struct.pack(">i", val))

    def write_string(self, s):
        bs = s.encode("utf-8")
        self.write_short(len(bs))
        self.f.write(bs)

    def start_named_tag(self, tag, name):
        self.write_byte(tag)
        self.write_string(name)

    def start_byte_array(self, length):
        self.write_int(length)

BLOCK_ZERO = (0, 0)
BLOCK_ONE = (75, 3)

def nbt_range_xyz(width, height, length):
    for y in range(0, height):
        for z in range(0, length):
            for x in range(0, width):
                yield (x, y, z)

def write_rom(f, bs):
    nbt = NBT(f)
    nbt.start_named_tag(NBT_COMPOUND, "Schematic")

    width = 68
    height = 16
    length = 19

    nbt.start_named_tag(NBT_SHORT, "Width")
    nbt.write_short(width)
    nbt.start_named_tag(NBT_SHORT, "Height")
    nbt.write_short(height)
    nbt.start_named_tag(NBT_SHORT, "Length")
    nbt.write_short(length)
    nbt.start_named_tag(NBT_STRING, "Materials")
    nbt.write_string("Alpha")

    for name, p in (("Blocks", 0), ("Data", 1)):
        nbt.start_named_tag(NBT_BYTE_ARRAY, name)
        nbt.start_byte_array(width * height * length)
        for x, y, z in nbt_range_xyz(width, height, length):
            if z % 6 != 0:
                nbt.write_byte(0)
            else:
                col = z // 6
                offset = 0
                if col > 0:
                    offset = 4
                if (col == 0 and x < 64 or col > 0 and x >= 4) \
                   and x % 2 == 1 and y % 2 == 1:
                        byteidx = (x - offset) // 2 + col * 32
                        bitidx = y // 2
                        if len(bs) <= byteidx:
                            nbt.write_byte(0)
                            continue
                        bit = bs[byteidx] & (1 << bitidx)
                        if bit:
                            nbt.write_byte(BLOCK_ONE[p])
                        else:
                            nbt.write_byte(BLOCK_ZERO[p])
                else:
                    nbt.write_byte(0)
    nbt.write_end()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: " + sys.argv[0] + " <infile> <outfile>")
        exit(1)
    with open(sys.argv[1], "rb") as inf:
        with gzip.open(sys.argv[2], "wb") as outf:
            write_rom(outf, inf.read())
