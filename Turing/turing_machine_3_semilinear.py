from mpc import encrypt, decrypt, equal
from time import time

def get_transition_table(code):
    """Convert the compact machine description into a transition table."""
    table = []
    for state_code in code.split("_"):
        row = []
        for i in range(0, len(state_code), 3):
            new_symbol, direction, new_state = state_code[i:i+3]
            new_symbol, direction, new_state = int(new_symbol), direction=="R", ord(new_state) - ord("A")
            row.append((new_symbol, direction, new_state))
        table.append(row)
    return table

def if_then_else(b, seq1, seq2):
    return (b * seq1) ^ ((b ^ 1) * seq2)

def local_rule(table, l, c, r):
    """Each n-state 2-symbol TM can be converted to a cellular automaton of (2n + 2) states.
    If the TM has states {A, B, C} and symbols {0, 1}, then the states of the cells are {0, 0A, 0B, 0C, 1, 1A, 1B, 1C}.
    For us, the value of each cell will be a tuple (symbol, head_here, state_of_head)
    The first indicates the symbol (int)
    The second indicates whether the head is here (boolean)
    The third indicates the state of the head (int)"""
    
    head_l, symbol_l, state_l = l & 1, (l >> 1) & 1, l >> 2
    head_c, symbol_c, state_c = c & 1, (c >> 1) & 1, c >> 2
    head_r, symbol_r, state_r = r & 1, (r >> 1) & 1, r >> 2

    direction_l = 0
    new_state_l = 0
    new_symbol_c = 0
    direction_r = 0
    new_state_r = 0
    
    # The two following for loop are equivalent to:
    # _, direction_l, new_state_l = table[state_l][symbol_l]
    # new_symbol_c, _, _ = table[state_c][symbol_c]
    # _, direction_r, new_state_r = table[state_r][symbol_r]
    for state, row in enumerate(table):
        state_match_l = equal(state, state_l)
        state_match_c = equal(state, state_c)
        state_match_r = equal(state, state_r)

        for symbol, (new_symbol, direction, new_state) in enumerate(row):
            match_l = state_match_l & equal(symbol, symbol_l)
            match_c = state_match_c & equal(symbol, symbol_c)
            match_r = state_match_r & equal(symbol, symbol_r)

            direction_l = if_then_else(match_l, direction, direction_l)
            new_state_l = if_then_else(match_l, new_state, new_state_l)

            new_symbol_c = if_then_else(match_c, new_symbol, new_symbol_c)

            direction_r = if_then_else(match_r, direction, direction_r)
            new_state_r = if_then_else(match_r, new_state, new_state_r)

    # The new symbol is:
    # - the new symbol of the center (new_symbol_c) if the head is at the center (head_c)
    # - the symbol of the center (symbol_c) otherwise
    new_symbol = if_then_else(head_c, new_symbol_c, symbol_c)
    
    # The new head_here is true if and only if one of the clauses is met (OR and XOR work):
    # - The head is at the left and goes to the right (head_l & direction_l)
    # - The head is at the right and goes to the left (head_r & (direction_r ^ 1))
    new_head = (head_l & direction_l) ^ (head_r & (direction_r ^ 1))
    
    # The new state of the head is:
    # - the new state of the left cell (new_state_l) if the head is at the left (head_l)
    # - the new state of the right cell (new_state_r) otherwise
    new_state = if_then_else(head_l, new_state_l, new_state_r)
    
    return new_head ^ (new_symbol << 1) ^ (new_state << 2)


def step():
    """Simulate exactly one step of the original TM."""
    # This counts the number of steps and can be removed
    global number_steps
    number_steps += 1
    if number_steps%100==0:
        print(number_steps)
    # The head is at the origin
    origin = len(tape)//2
    # We update the head and the two neighbouring cells
    state = tape[origin] >> 2
    a, b, c, d, e = tape[origin-2], tape[origin-1], tape[origin], tape[origin+1], tape[origin+2]
    tape[origin-1] = local_rule(table, a, b, c)
    tape[origin] = local_rule(table, b, c, d)
    tape[origin+1] = local_rule(table, c, d, e)

def ensure_capacity(j):
    # COMPRESS(j) will consider a sphere of radius 2^(j+1) - 1.
    # A sphere of radius r will have a length of 2*r + 1 = 2 * (2^(j+1) - 1) + 1 = 2^(j+2) - 2 + 1 = 2^(j+2) - 1
    # We therefore need at least this length
    required_length = 2**(j+2) - 1
    if len(tape) < required_length:
        # We add some amount to the left and to the right
        # Note that the origin is still at the center of the tape after the operation
        tape[:0] = [0] * ((required_length - len(tape)) // 2)
        tape.extend([0] * (required_length - len(tape)))

def phase(j):
    ensure_capacity(j)
    if j==0:
        step()
    else:
        compress(j)
        phase(j-1)
        compress(j)
        phase(j-1)
        expand(j)
        expand(j)

def rotate(begin, end, amount, is_left, is_right, is_center):
    length = end - begin + 1
    # We compute the three possible rotations
    left = [tape[begin + (i + amount) % length] for i in range(length)]
    right = [tape[begin + (i - amount) % length] for i in range(length)]
    center = tape[begin:end + 1]
    # We mask the (in)correct ones
    # We perform the left rotation if the head is to the right
    # We perform the right rotation if the head is to the left
    # We perform no rotation if the head is to the center
    tape[begin:end + 1] = [if_then_else(is_right, left[i], if_then_else(is_left, right[i], center[i])) for i in range(length)]

def compress(j):
    # The origin is at len(tape)//2
    origin = len(tape)//2
    # We find whether the head is to the right or to the left or to the origin.
    is_right = 0
    for i in range(origin + 1, len(tape)):
        is_right |= tape[i] & 1
    is_center = tape[origin] & 1
    is_left = (is_center ^ 1) & (is_right ^ 1)
    # We consider the cells in a 2^(j+1) - 1 radius around the origin
    # We do a 2^(j-1)-shift towards the direction where the head isn't.
    # In the case where the head is at the origin, we do nothing
    rotate(begin = origin - (2**(j+1) - 1), end = origin + (2**(j+1) - 1), amount = 2**(j-1), is_left=is_left, is_right=is_right, is_center=is_center)
    # We add a note to the stack that tells the position where the head was
    stack.append((is_left, is_right, is_center))

def expand(j):
    # We get the note
    (was_left, was_right, was_center) = stack.pop()
    # We do the opposite direction
    origin = len(tape)//2
    rotate(begin = origin - (2**(j+1) - 1), end = origin + (2**(j+1) - 1), amount = 2**(j-1), is_left=was_right, is_right=was_left, is_center=was_center)

tape = [0 for _ in range(2**7 - 1)]#range(30000)]
tape[len(tape)//2] = 1 # We set the LSB to 1 to tell that the head is here
tape = encrypt(tape)

stack = []

#code = "1RB1LB_1LA1RC_0RC1LC"
#code = "1RB1RD_1LB0RC_1LC1LA_0RD1LD"
code = "1RB1LB_1LA0LC_1RE1LD_1RD0RA_0RE1LE"
code = "1RB1LC_1RC1RB_1RD0LE_1LA1LD_1RZ0LA_0RZ1LZ"
table = get_transition_table(code)

number_steps = 0
j = 0
t0 = time()
while all(not((v>>2)==len(table)-1 and (v&1)) for v in decrypt(tape)): # While the head is not in the last state
    #print("".join([str((v&2) >> 1) for v in tape]))#decrypt(tape)]))
    phase(j)
    j += 1
print("".join([str((v&2) >> 1) for v in decrypt(tape)]))
t1 = time()
print(t1 - t0)
print(number_steps)
