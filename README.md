# Octornado

Octornado is a work-in-progress CPU design. This repo will contain
an assembler, an emulator, some screenshots, etc.

Here are some assembly code examples:

* An `int strlen(char *)` function: <https://github.com/mortie/octornado-cpu/blob/main/examples/strlen.s>
* An `int fib(int n)` function: <https://github.com/mortie/octornado-cpu/blob/main/examples/fibonacci.s>

ISA: <https://docs.google.com/spreadsheets/d/1MuFLPnch6_CgV2hZuCr0WL27mB1EIJyWn5a9Nx-m7_M/edit?usp=sharing>

## Instructions

Here's the instructions as understood by the assemblers:

* `def <name> <value>`: A pseudo-instruction. Generates no code, but defines `<name>`
  to be used later.
* `byte <value>`: A pseudo-instruction. Generates the literal byte `<value>` in
  the binary.
* `nop`: Do nothing.
* `add <dest> <A> <B>`: `dest = A + B`.
* `mov <dest> <value>`: `dest = A`. Generates either an IMM instruction or an ADD instruction
  in the binary.
* `sub <dest> <A> <B>`: `dest = A - B`.
* `xor <dest> <A> <B>`: `dest = A XOR B`.
* `nand <dest> <A> <B>`: `dest = A NAND B`.
* `or <dest> <A> <B>`: `dest = A OR B`.
* `and <dest> <A> <B>`: `dest = A AND B`.
* `shr <dest> <A> <B>`: `dest = (A + B) << 1`. The shifted-out bit goes to the carry flag.
* `cmp <A> <B>`: Execute `A - B`. Discard the result, but set flags.
* `jmp <value>`: Jump to `<value>`. Generates an actual `JMP` instruction if `<value>`
  is a register, or a `JMPI` instruction if `<value>` is an immediate or label.
* `jeq/jgt/jge/jgts/jges <value>`: Jump if condition. Generates an actual `JMP`
  instruction if `<value>` is a register, or a `JMPI` instruction if `<value>` is
  an immediate or label.
	* `jeq`: Jump if equals (i.e if zero flag is set)
	* `jgt`: Jump if greater than (i.e if carry flag is set and zero flag isn't)
	* `jge`: Jump if greater or equal (i.e if carry flag is set)
	* `jgts`: Jump if greater than, signed (i.e jump if zero flag is set and
	  signed overflow flag == sign flag)
	* `jges`: Jump if greater or equal, signed (i.e jump if signed overflow
	  flag == sign flag)
* `jmp <A> <B>`: Like `jmp <value>`, but jumps to `<A> + <B>`.
* `jeq/jgt/jge/jgts/jges <A> <B>`: Like `jeq/... <value>`, but conditionally
  jumps to `<A> + <B>`
* `ld <dest>`: Load from RAM at address given by `r7` into `<dest>`
* `st <value>`: Store `<value>` to RAM at address given by `r7`. Generates an `ST`
  instruction if `<value>` is a register, or an `STI` instruction if it's an
  immediate or label.
* `st <A> <B>`: Store `<A> + <B>` to RAM at address given by `r7`.
* `addc <dest> <A> <B>`: Like `add`, but take carry in from the carry flag.
* `subc <dest> <A> <B>`: Like `sub`, but take carry in from the carry flag.
* `cmpc <dest> <A> <B>`: Like `cmp`, but take carry in from the carry flag.
* `shrc <dest> <A> <B>`: Like `shr`, but shift in the value in the carry flag
  rather than zero.

Here's what the arguments mean:

* `<dest>` is the destination register. Must be a register between `r0` and `r7`.
* `<A>` is the A argument to the ALU. Must be a register between `r0` and `r7`.
* `<B>` is the B argument to the ALU. Must be either a register between
  `r0` and `r7`, or an immediate or label with value between -8 and 7.
* `<value>` must be either a register between `r0` and `r7`, or an immediate
  or label between 0 and 255.

The legal syntaxes for label/immediate values are:

* `[0-9]+`: Decimal number
* `0x[0-9a-f]+`: Hexadecimal number
* `0b[01]+`: Binary number
* `0o[0-7]+`: Octal number
* `'.'`: ASCII character
* `[a-zA-Z_][a-zA-Z0-9_]*`: Either a label, or a defined value created by `def`
