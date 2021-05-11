mov r7 stack_start
st retaddr
mov r1 data
jmp strlen
retaddr:
	halt

strlen:
	mov r0 0
	mov r2 r7
	mov r7 r1

strlen_loop:
	ld r1
	cmp r1 0
	jeq strlen_exit
	add r0 r0 1
	add r7 r7 1
	jmp strlen_loop

strlen_exit:
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
