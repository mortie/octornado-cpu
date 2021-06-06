### Hello World

	def screen 254

	# r0: String pointer
	# r1: Character byte

	mov r0 data
loop:
	mov r7 r0
	ld r1
	cmp r1 0
	jeq exit
	mov r7 screen
	st r1
	add r0 r0 1
	jmp loop

exit:
	halt

data:
	byte 'H'
	byte 'E'
	byte 'L'
	byte 'L'
	byte 'O'
	byte ' '
	byte 'W'
	byte 'O'
	byte 'R'
	byte 'L'
	byte 'D'
	byte '\0'
