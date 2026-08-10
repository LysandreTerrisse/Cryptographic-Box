from time import time

def get_transition_table(code):
    """Convert the compact machine description into a transition table."""
    table = []
    for state_code in code.split("_"):
        row = []
        for i in range(0, len(state_code), 3):
            next_symbol, direction, next_state = state_code[i:i+3]
            row.append((int(next_symbol), direction=="R", ord(next_state) - ord("A")))
        table.append(row)
    return table

# Takes a bit b and duplicates it nb_bits times
def mask(b, nb_bits=32):
    res = 0
    for i in range(nb_bits):
        res |= b << i
    return res

# Takes a boolean and two sequences
def if_then_else(b, seq1, seq2):
    mask_b = mask(b)
    return (seq1 & mask_b) ^ (seq2 & ~mask_b)

def local_rule(table, l, c, r):
    """Each n-state 2-symbol TM can be converted to a cellular automaton of (2n + 2) states.
    If the TM has states {A, B, C} and symbols {0, 1}, then the states of the cells are {0, 0A, 0B, 0C, 1, 1A, 1B, 1C}.
    For us, the value of each cell will be encoded as a sequence v of bits.
    The first LSB (that is, v & 1) will indicate whether the head is here.
    The next LSB (that is, v & 2) will encode the symbol of the tape (here binary).
    The next bits will encode the state of the TM.
    """
    head_here_l, symbol_l, state_l = l & 1, (l & 2) >> 1, l >> 2
    head_here_c, symbol_c, state_c = c & 1, (c & 2) >> 1, c >> 2
    head_here_r, symbol_r, state_r = r & 1, (r & 2) >> 1, r >> 2
    
    # If the head is at the left
    return if_then_else(head_here_l,
        # If the head is headed to the right, then the head is here, the symbol is the same, and the state is the new state
        if_then_else(
            table[state_l][symbol_l][1],
            1 | (symbol_c << 1) | (table[state_l][symbol_l][2] << 2),
            c
        ),
    # If the head is at the center
    if_then_else(head_here_c,
        table[state_c][symbol_c][0] << 1,
    # If the head is at the right
    if_then_else(head_here_r,
        # If the head is headed to the left, then the head is here, the symbol is the same, and the state is the new state
        if_then_else(
            table[state_r][symbol_r][1],
            c,
            1 | (symbol_c << 1) | (table[state_r][symbol_r][2] << 2)
        ),
        c
    )))
    

tape = [0 for _ in range(30000)]#range(80)]#
tape[len(tape)//2] = 1 # We set the LSB to 1 to tell that the head is here

code = "1RB1LB_1LA1RZ"
code = "1RB1RZ_1LB0RC_1LC1LA"
code = "1RB1LB_1LA0LC_1RZ1LD_1RD0RA"
#code = "1RB1LC_1RC1RB_1RD0LE_1LA1LD_1RZ0LA"
table = get_transition_table(code)
i = 0
t0 = time()
while all((v>>2) < len(table) for v in tape): # While no state is an halting state
    #print("".join([str((v&2) >> 1) for v in tape]))
    i += 1
    if i%1000==0:
        print(i)
    y = [0]*len(tape)
    for j in range(1, len(tape)-1):
        y[j] = local_rule(table, tape[j-1], tape[j], tape[j+1])
    tape = y
t1 = time()
print(t1 - t0)
print(i)
