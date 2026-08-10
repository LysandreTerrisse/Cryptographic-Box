from time import time

def get_transition_table(code):
    """Convert the compact machine description into a transition table."""
    table = []
    for state_code in code.split("_"):
        row = []
        for i in range(0, len(state_code), 3):
            new_symbol, direction, new_state = state_code[i:i+3]
            row.append((int(new_symbol), direction=="R", ord(new_state) - ord("A")))
        table.append(row)
    return table

def mask(b, nb_bits=32):
    """Takes a bit b and duplicates it nb_bits times"""
    res = 0
    for i in range(nb_bits):
        res |= b << i
    return res

def if_then_else(b, seq1, seq2):
    """Takes a boolean and two sequences"""
    mask_b = mask(b)
    return (seq1 & mask_b) ^ (seq2 & ~mask_b)

def local_rule(table, l, c, r):
    """Each n-state 2-symbol TM can be converted to a cellular automaton of (2n + 2) states.
    If the TM has states {A, B, C} and symbols {0, 1}, then the states of the cells are {0, 0A, 0B, 0C, 1, 1A, 1B, 1C}.
    For us, the value of each cell will be encoded as a sequence v of bits.
    The first LSB (that is, v & 1) will indicate whether the head is here.
    The next LSB (that is, (v >> 1) & 1) will encode the symbol of the tape (here binary).
    The next bits (v >> 2) will encode the state of the TM.
    """
    head_l, symbol_l, state_l = l & 1, (l >> 1) & 1 , l >> 2
    head_c, symbol_c, state_c = c & 1, (c >> 1) & 1, c >> 2
    head_r, symbol_r, state_r = r & 1, (r >> 1) & 1, r >> 2

    new_symbol_l, direction_l, new_state_l = table[state_l][symbol_l]
    new_symbol_c, direction_c, new_state_c = table[state_c][symbol_c]
    new_symbol_r, direction_r, new_state_r = table[state_r][symbol_r]

    res_from_left = 1 | (symbol_c << 1) | (new_state_l << 2)
    res_from_center = new_symbol_c << 1
    res_from_right = 1 | (symbol_c << 1) | (new_state_r << 2)

    res = c
    res = if_then_else(head_r & ~direction_r, res_from_right, res)
    res = if_then_else(head_c, res_from_center, res)
    res = if_then_else(head_l & direction_l, res_from_left, res)

    return res

def step():
    """Simulate exactly one step of the original TM."""
    # This counts the number of steps and can be removed
    global number_steps
    number_steps += 1
    if number_steps % 1000 == 0:
        print(number_steps, len(tape))
    # The head is at the origin
    origin = len(tape)//2
    # We update the head and the two neighbouring cells
    state = tape[origin] >> 2
    if state < len(table):
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

def rotate(begin, end, amount, direction):
    assert 0 <= begin < end < len(tape)
    length = end - begin + 1
    amount %= length
    if direction:  # right
        tape[begin:end + 1] = tape[begin:end + 1][-amount:] + tape[begin:end + 1][:-amount]
    else:          # left
        tape[begin:end + 1] = tape[begin:end + 1][amount:] + tape[begin:end + 1][:amount]

def compress(j):
    # The origin is at len(tape)//2
    origin = len(tape)//2
    # We find whether the head is to the right or to the left
    is_right = 0
    for i in range(origin + 1, len(tape)):
        is_right |= tape[i] & 1
    # In the special case where the head is at the origin, we do nothing
    if tape[len(tape)//2] & 1:
        stack.append(None)
    else:
        # We consider the cells in a 2^(j+1) - 1 radius around the origin
        # We do a 2^(j-1)-shift towards the direction where the head isn't.
        rotate(begin = origin - (2**(j+1) - 1), end = origin + (2**(j+1) - 1), amount = 2**(j-1), direction = is_right ^ 1)
        stack.append(is_right ^ 1)

def expand(j):
    # We get the note
    direction = stack.pop()
    # In the special case where the head is at the origin, we do nothing
    if direction!=None:
        # We do the opposite direction
        origin = len(tape)//2
        rotate(begin = origin - (2**(j+1) - 1), end = origin + (2**(j+1) - 1), amount = 2**(j-1), direction = direction ^ 1)

tape = [0 for _ in range(2**7 - 1)]#range(30000)]
tape[len(tape)//2] = 1 # We set the LSB to 1 to tell that the head is here

stack = []

code = "1RB1LB_1LA1RZ"
code = "1RB1RZ_1LB0RC_1LC1LA"
code = "1RB1LB_1LA0LC_1RZ1LD_1RD0RA"
#code = "1RB1LC_1RC1RB_1RD0LE_1LA1LD_1RZ0LA"
table = get_transition_table(code)

number_steps = 0
j = 0
t0 = time()
while all((v>>2) < len(table) for v in tape): # While no state is an halting state
    #print("".join([str((v&2) >> 1) for v in tape]))
    phase(j)
    j += 1
print("".join([str((v&2) >> 1) for v in tape]))
t1 = time()
print(t1 - t0)
print(number_steps)
