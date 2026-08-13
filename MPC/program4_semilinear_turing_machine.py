from mpc import encrypt, decrypt
from time import time

def get_transition_table(code):
    """Convert the compact machine description into a transition table."""
    nb_states = code.count("_") + 1
    nb_symbols = len(code.split("_")[0])//3
    # The states will be encoded in MSB, such as [0, 0, 0], [0, 0, 1], ..., [1, 1, 1].
    # Same for the symbols.
    states = [[(state >> i) & 1 for i in range((nb_states-1).bit_length() - 1, -1, -1)] for state in range(nb_states)]
    symbols = [[(symbol >> i) & 1 for i in range((nb_symbols-1).bit_length() - 1, -1, -1)] for symbol in range(nb_symbols)]
    # The table will give for each state and symbol a new symbol, a direction, and a new state.
    table = []
    for state_code in code.split("_"):
        row = []
        for i in range(0, len(state_code), 3):
            new_symbol, direction, new_state = state_code[i:i+3]
            new_symbol, direction, new_state = int(new_symbol), direction=="R", ord(new_state) - ord("A")
            new_symbol, new_state = symbols[new_symbol], states[new_state]
            row.append((new_symbol, direction, new_state))
        table.append(row)
    return states, symbols, table

def to_int(x):
    """Takes a MSB list and returns an int"""
    if isinstance(x, list):
        res = 0
        for bit in x:
            res = (res << 1) | bit
        return res
    return x

def equal(a, b):
    """Takes two sequences (list) of same length"""
    res = a[0] ^ b[0] ^ 1
    for i in range(1, len(a)):
        res &= a[i] ^ b[i] ^ 1
    return res

def step():
    """Simulate exactly one step of the original TM."""
    # This counts the number of steps and can be removed
    global number_steps, current_state
    number_steps += 1
    if number_steps%100==0:
        print(number_steps)
        t1 = time()
        print(t1 - t0)
    # The head is at the origin
    origin = len(tape)//2
    current_symbol = tape[origin]
    
    # We compute where the state matches and where the symbol matches
    state_matches = [equal(state, current_state) for state in states]
    symbol_matches = [equal(symbol, current_symbol) for symbol in symbols]
    
    # The two following for loops are equivalent to:
    # new_symbol, direction, new_state = table[to_int(current_state)][to_int(current_symbol)]
    new_symbol, direction, new_state = [0]*len(symbols[0]), 0, [0]*len(states[0])
    for i, state in enumerate(states):
        for j, symbol in enumerate(symbols):
            match = state_matches[i] & symbol_matches[j]
            new_symbol_, direction_, new_state_ = table[i][j]
            # The direction is easy to compute since it is a single bit
            direction ^= match & direction_
            # For the new symbol and the new state, we need to make a loop
            for k in range(len(new_symbol)):
                new_symbol[k] ^= match & new_symbol_[k]
            for k in range(len(new_state)):
                new_state[k] ^= match & new_state_[k]
    
    # We update the current state, the current symbol, and the head markers
    current_state, tape[origin] = new_state, new_symbol
    head_markers[origin-1] = direction ^ 1
    head_markers[origin] = 0
    head_markers[origin+1] = direction

def ensure_capacity(j):
    # COMPRESS(j) will consider a sphere of radius 2^(j+1) - 1.
    # A sphere of radius r will have a length of 2*r + 1 = 2 * (2^(j+1) - 1) + 1 = 2^(j+2) - 2 + 1 = 2^(j+2) - 1 = (1 << (j + 2)) - 1
    # We therefore need at least this length
    required_length = (1 << (j + 2)) - 1
    if len(tape) < required_length:
        # We add some amount to the left and to the right
        # Note that the origin is still at the center of the tape after the operation
        tape[:0] = [symbols[0]] * ((required_length - len(tape)) // 2)
        tape.extend([symbols[0]] * (required_length - len(tape)))
        # We do the same for the head markers
        head_markers[:0] = [0] * ((required_length - len(head_markers)) // 2)
        head_markers.extend([0] * (required_length - len(head_markers)))

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
    # We compute the three possible rotations, both for the tape and the head markers
    center       = tape[begin:end + 1]
    left       = center[amount:] + center[:amount]
    right       = center[-amount:] + center[:-amount]
    
    center_head_markers  = head_markers[begin:end + 1]
    left_head_markers  = center_head_markers[amount:] + center_head_markers[:amount]
    right_head_markers  = center_head_markers[-amount:] + center_head_markers[:-amount]
    
    symbol_size = len(symbols[0])
    
    # We perform the left rotation if the head is to the right
    # We perform the right rotation if the head is to the left
    # We perform no rotation if the head is to the center
    for i in range(len(center)):
        # These temporary variables are in order to prevent a lot of list accesses and additions
        begin_plus_i = begin + i
        left_i, center_i, right_i = left[i], center[i], right[i]
        
        # Equivalently, head_markers[begin+i] = if_then_else(is_right, left_head_markers[i], if_then_else(is_left, right_head_markers[i], center_head_markers[i]))
        head_markers[begin_plus_i] = (is_right & (left_head_markers[i] ^ center_head_markers[i])) ^ (is_left & (right_head_markers[i] ^ center_head_markers[i])) ^ center_head_markers[i]
        
        # Equivalently, tape[begin+i] = if_then_else(is_right, left[i], if_then_else(is_left, right[i], center[i]))
        tape[begin_plus_i] = [0] * symbol_size
        for j in range(symbol_size):
            tape[begin_plus_i][j] = (is_right & (left_i[j] ^ center_i[j])) ^ (is_left & (right_i[j] ^ center_i[j])) ^ center_i[j]

def compress(j):
    # We consider the cells in a 2**(j+1) - 1 = (1 << (j + 1)) - 1 radius around the origin
    # The origin is at len(tape)//2
    origin = len(tape)//2
    radius = ((1 << (j + 1)) - 1)
    # We find whether the head is to the right or to the left or to the origin.
    is_right = head_markers[origin + 1]
    for i in range(origin + 2, origin + radius):
        is_right ^= head_markers[i]
    is_left = head_markers[origin] ^ is_right ^ 1
    # We do a 2**(j-1)-shift = (1 << (j - 1)) towards the direction where the head isn't.
    # In the case where the head is at the origin, we do nothing
    rotate(begin = origin - radius, end = origin + radius, amount = 1 << (j - 1), is_left=is_left, is_right=is_right)
    # We add a note to the stack that tells the position where the head was
    stack.append((is_left, is_right))

def expand(j):
    # We get the note
    (was_left, was_right) = stack.pop()
    # We do the opposite direction
    origin = len(tape)//2
    rotate(begin = origin - ((1 << (j + 1)) - 1), end = origin + ((1 << (j + 1)) - 1), amount = 1 << (j - 1), is_left=was_right, is_right=was_left)

#code = "1RB1LB_1LA1RC_0RC1LC" # BB(2)
#code = "1RB1RD_1LB0RC_1LC1LA_0RD1LD" # BB(3)
#code = "1RB1LB_1LA0LC_1RE1LD_1RD0RA_0RE1LE" # BB(4)
code = "1RB1LC_1RC1RB_1RD0LE_1LA1LD_1RF0LA_0RF1LF" # BB(5)
#code = "1RB2LB1RC_2LA2RB1LB_0RC1RC2RC" # BB(2, 3)
states, symbols, table = get_transition_table(code)


tape = encrypt([symbols[0]])
# The head marker tells for each cell whether the head is here
head_markers = [i==len(tape)//2 for i in range(len(tape))]
current_state = states[0]
stack = []
number_steps = 0

"""
import cProfile
r = range(13)
cProfile.run("for j in r: phase(j)")
exit()
"""

j = 0
t0 = time()
while not(to_int(decrypt(current_state))==len(table)-1):
    phase(j)
    j += 1
print("".join([str(to_int(symbol)) for symbol in decrypt(tape)]))
print(number_steps)
