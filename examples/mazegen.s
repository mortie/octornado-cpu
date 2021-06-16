#const maze_size = 8
#new_yd = maze_size >> 1
#while (new_yd << 1) >= 1:
#    yi = (new_yd << 1) - 1
#    while yi < (maze_size << 1):
#        coli = 0
#        while coli < maze_size:
#            set(((coli & ((maze_size - new_yd) << 1)) | rand & (new_yd << 1 - 1)) << 1,
#                yi)
#            coli += (new_yd << 1)
#        if new_yd > 0:
#            rowi = 0
#            while rowi < maze_size:
#                set(yi,
#                    ((rowi & (maze_size - new_yd)) | rand & (new_yd - 1)) << 1)
#                rowi += new_yd
#        yi += new_yd << 1
#    new_yd >>= 1

def maze 252
def maze_size 16
def maze_size_double 32
def send_x_and_update 0b01000000
def done_signal 0b10000000
def erase 0b11000000
mov r7 maze
st erase                        # erase maze
mov r0 maze_size                # r0: new_yd << 1
shr r1 r0 0                     # r1: new_yd
loop0_body:
    sub r2 r0 1                 # r2: yi
    loop1_body:
        mov r3 0                # r3: coli
        loop2_body:
            st r2
            mov r4 maze_size_double
            sub r4 r4 r0
            and r4 r3 r4
            rand r5             # r5: rng
            sub r6 r0 1
            and r5 r5 r6
            or r4 r4 r5
            add r4 r4 r4
            mov r5 send_x_and_update
            or r4 r4 r5
            st r4
        loop2_inc:
            add r3 r3 r0
        loop2_cond:
            mov r4 maze_size
            cmp r4 r3
            jgt loop2_body
        cmp r1 0
        jeq loop1_inc
        mov r3 0                # r3: rowi
        loop3_body:
            mov r4 maze_size
            sub r4 r4 r1
            and r4 r3 r4
            rand r5             # r5: rng
            sub r6 r1 1
            and r5 r5 r6
            or r4 r4 r5
            add r4 r4 r4
            st r4
            mov r4 send_x_and_update
            or r4 r4 r2
            st r4
        loop3_inc:
            add r3 r3 r1
        loop3_cond:
            mov r4 maze_size
            cmp r4 r3
            jgt loop3_body
    loop1_inc:
        add r3 r0 r0
        add r2 r2 r3
    loop1_cond:
        mov r3 maze_size_double
        cmp r3 r2
        jgt loop1_body
loop0_inc:
    shr r0 r0 0
    shr r1 r1 0
loop0_cond:
    cmp r0 1
    jge loop0_body
done:
    st done_signal              # indicate finished
    halt