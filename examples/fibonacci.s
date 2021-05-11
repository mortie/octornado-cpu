# Initialization code to set up the stack and run 'fib(10)'
	mov r7 stack_start
	st retaddr
	mov r1 10
	jmp fib
retaddr:
	halt

fib:
	cmp r1 2
	jge fib_main
	cmp r1 0
	jeq fib_zero
	mov r0 1
	jmp fib_exit

fib_zero:
	mov r1 0
	jmp fib_exit

fib_main:
	sub r1 r1 2
	mov r0 0
	mov r2 0
	mov r3 1

fib_loop:
	add r0 r2 r3
	mov r2 r3
	mov r3 r0
	sub r1 r1 1
	jge fib_loop

fib_exit:
	ld r1
	jmp r1

stack_start:
