from time import time

def get_transition_table(code):
    """Convert the compact machine description into a transition table."""
    table = []
    for state_code in code.split("_"):
        row = []
        for i in range(0, len(state_code), 3):
            next_symbol, direction, next_state = state_code[i:i+3]
            row.append(((int(next_symbol)), (-1 if direction=="L" else 1), ord(next_state) - ord("A")))
        table.append(row)
    return table

def local_rule(table, l, c, r):
    """Each n-state 2-symbol TM can be converted to a cellular automaton of (2n + 2) states.
    If the TM has states {A, B, C} and symbols {0, 1}, then the states of the cells are {0, 0A, 0B, 0C, 1, 1A, 1B, 1C}.
    For us, the value of each cell will be a tuple (state, symbol), where state belongs to the set {A, B, ...} union {not_here}
    We will encode the states {not_here, A, B, ...} as {-1, 0, 1, 2, ...}."""
    (state_l, symbol_l), (state_c, symbol_c), (state_r, symbol_r) = l, c, r
    
    # If the head is at the left
    if state_l != -1:
        # If the head moves towards the center
        if table[state_l][symbol_l][1] == +1:
            # The symbol is the same but the head is here and has the new state
            return (table[state_l][symbol_l][2], symbol_c)
        else:
            return c
    # If the head is at the center
    elif state_c != -1:
        # The head is no longer here and the symbol is the new symbol
        return (-1, table[state_c][symbol_c][0])
    # If the head is at the right
    elif state_r != -1:
        # If the head moves towards the center
        if table[state_r][symbol_r][1] == -1:
            # The symbol is the same but the head is here and has the new state
            return (table[state_r][symbol_r][2], symbol_c)
        else:
            return c
    else:
        return c
    

tape = [(-1, 0) for _ in range(30000)]
tape[30000//2] = (0, 0)

code = "1RB1LB_1LA1RZ"
code = "1RB1RZ_1LB0RC_1LC1LA"
code = "1RB1LB_1LA0LC_1RZ1LD_1RD0RA"
code = "1RB1LC_1RC1RB_1RD0LE_1LA1LD_1RZ0LA"
table = get_transition_table(code)
i = 0
t0 = time()
while all(state < len(table) for (state, _) in tape):
    i += 1
    if i%1000==0:
        print(i)
    tape = [(-1, 0)] + [local_rule(table, tape[j-1], tape[j], tape[j+1]) for j in range(1, len(tape)-1)] + [(-1, 0)]
t1 = time()
print(t1 - t0)
print(i)
