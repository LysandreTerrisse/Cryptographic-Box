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

def step():
    """Simulate exactly one step of the original TM."""
    # This counts the number of steps and can be removed
    global number_steps
    number_steps += 1
    if number_steps%100==0:
        print(number_steps)
        t1 = time()
        print(t1 - t0)
    # The head is at the origin
    origin = len(tape)//2
    
    # We update the head and the two neighbouring cells
    symbol_l, symbol_c, symbol_r = tape[origin-1], tape[origin], tape[origin+1]
    state_c = tape_state[origin]
    
    # The two following for loop are equivalent to:
    # new_symbol, direction, new_state = table[state_c][symbol_c]
    new_symbol, direction, new_state = 0, 0, 0
    for state, row in enumerate(table):
        state_match_c = equal(state, state_c)
        for symbol, (new_symbol_, direction_, new_state_) in enumerate(row):
            match_c = state_match_c & equal(symbol, symbol_c)
            new_symbol = if_then_else(match_c, new_symbol_, new_symbol)
            direction = if_then_else(match_c, direction_, direction)
            new_state = if_then_else(match_c, new_state_, new_state)
    
    # The cell to the left gets the head if the direction is L (False)
    # Its symbol stays the same (symbol_l)
    # Its state becomes the new state
    tape[origin-1] = symbol_l
    tape_head[origin-1] = direction ^ 1
    tape_state[origin-1] = new_state
    
    # The cell to the middle doesn't have the head anymore
    # Its symbol becomes the new symbol
    tape[origin] = new_symbol
    tape_head[origin] = 0
    tape_state[origin] = 0
    
    # The cell to the right gets the head if the direction is R (True)
    # Its symbol stays the same (symbol_r)
    # Its state becomes the new state
    tape[origin+1] = symbol_r
    tape_head[origin+1] = direction
    tape_state[origin+1] = new_state

def ensure_capacity(j):
    # COMPRESS(j) will consider a sphere of radius 2^(j+1) - 1.
    # A sphere of radius r will have a length of 2*r + 1 = 2 * (2^(j+1) - 1) + 1 = 2^(j+2) - 2 + 1 = 2^(j+2) - 1
    # We therefore need at least this length
    required_length = 2**(j+2) - 1
    if len(tape) < required_length:
        # We add some amount to the left and to the right
        # Note that the origin is still at the center of the tape after the operation
        tape[:0] = [0 for _ in range((required_length - len(tape)) // 2)]
        tape.extend([0 for _ in range(required_length - len(tape))])
        tape_head[:0] = [0 for _ in range((required_length - len(tape_head)) // 2)]
        tape_head.extend([0 for _ in range(required_length - len(tape_head))])
        tape_state[:0] = [0 for _ in range((required_length - len(tape_state)) // 2)]
        tape_state.extend([0 for _ in range(required_length - len(tape_state))])

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

def rotate(begin, end, amount, is_left, is_right):
    # We compute the three possible rotations
    center       = tape[begin:end + 1]
    center_head  = tape_head[begin:end + 1]
    center_state = tape_state[begin:end + 1]
    
    left       = center[amount:] + center[:amount]
    left_head  = center_head[amount:] + center_head[:amount]
    left_state = center_state[amount:] + center_state[:amount]
    
    right       = center[-amount:] + center[:-amount]
    right_head  = center_head[-amount:] + center_head[:-amount]
    right_state = center_state[-amount:] + center_state[:-amount]
    
    # We perform the left rotation if the head is to the right
    # We perform the right rotation if the head is to the left
    # We perform no rotation if the head is to the center
    for i in range(len(center)):
        tape[begin+i] = if_then_else(is_right, left[i], if_then_else(is_left, right[i], center[i]))
        tape_head[begin+i] = if_then_else(is_right, left_head[i], if_then_else(is_left, right_head[i], center_head[i]))
        tape_state[begin+i] = if_then_else(is_right, left_state[i], if_then_else(is_left, right_state[i], center_state[i]))

def compress(j):
    # The origin is at len(tape)//2
    origin = len(tape)//2
    # We find whether the head is to the right or to the left or to the origin.
    is_right = 0
    for i in range(origin + 1, len(tape)):
        is_right |= tape_head[i]
    is_center = tape_head[origin]
    is_left = (is_center ^ 1) & (is_right ^ 1)
    # We consider the cells in a 2^(j+1) - 1 radius around the origin
    # We do a 2^(j-1)-shift towards the direction where the head isn't.
    # In the case where the head is at the origin, we do nothing
    rotate(begin = origin - (2**(j+1) - 1), end = origin + (2**(j+1) - 1), amount = 2**(j-1), is_left=is_left, is_right=is_right)
    # We add a note to the stack that tells the position where the head was
    stack.append((is_left, is_right))

def expand(j):
    # We get the note
    (was_left, was_right) = stack.pop()
    # We do the opposite direction
    origin = len(tape)//2
    rotate(begin = origin - (2**(j+1) - 1), end = origin + (2**(j+1) - 1), amount = 2**(j-1), is_left=was_right, is_right=was_left)


# The tape is separated in three parts:
# - tape_symbol, which tells the symbol of the tape
# - tape_head, which tells whether the head is here
# - tape_state, which tells the state of the tape
tape = encrypt([0 for _ in range(2**7 - 1)])
tape_head = [i==len(tape)//2 for i in range(len(tape))]
tape_state = [0 for _ in range(len(tape))]

stack = []

#code = "1RB1LB_1LA1RC_0RC1LC"
#code = "1RB1RD_1LB0RC_1LC1LA_0RD1LD"
#code = "1RB1LB_1LA0LC_1RE1LD_1RD0RA_0RE1LE"
code = "1RB1LC_1RC1RB_1RD0LE_1LA1LD_1RZ0LA_0RZ1LZ"
table = get_transition_table(code)

number_steps = 0
j = 0
t0 = time()
while all(not(state==len(table)-1 and head_here) for state, head_here in zip(decrypt(tape_state), decrypt(tape_head))): # While the head is not in the last state
    #print("".join([str((v&2) >> 1) for v in tape]))#decrypt(tape)]))
    #print("".join([str(symbol) for symbol in decrypt(tape)]))
    phase(j)
    j += 1
print("".join([str(symbol) for symbol in decrypt(tape)]))
print(number_steps)
