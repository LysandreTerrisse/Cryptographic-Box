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

tape = [0]*30000

code = "1RB1LB_1LA1RZ"
code = "1RB1RZ_1LB0RC_1LC1LA"
code = "1RB1LB_1LA0LC_1RZ1LD_1RD0RA"
code = "1RB1LC_1RC1RB_1RD0LE_1LA1LD_1RZ0LA"
table = get_transition_table(code)
pos = len(tape)//2
state = 0
i = 0
t0 = time()
while state < len(table) and 0 <= pos < len(tape):
    i += 1
    symbol = tape[pos]
    tape[pos], direction, state = table[state][symbol]
    pos += direction
t1 = time()
print(t1 - t0)
print(i)

