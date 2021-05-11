# Initialization code to set up the stack and run 'strlen(data)'
	mov r7 stack_start
	st retaddr
	mov r1 data
	jmp strlen
retaddr:
	halt

strlen:
	mov r2 r7
	sub r7 r1 1

strlen_loop:
	add r7 r7 1
	ld r0
	cmp r0 0
	jgt strlen_loop

	sub r0 r7 r1
	mov r7 r2
	ld r1
	jmp r1

data:
	byte 'H'
	byte 'e'
	byte 'l'
	byte 'l'
	byte 'o'
	byte ' '
	byte 'w'
	byte 'o'
	byte 'r'
	byte 'l'
	byte 'd'
	byte '\0'

stack_start:
