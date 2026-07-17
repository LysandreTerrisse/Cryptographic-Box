from mpc import encrypt, decrypt
from boolean_circuits import count
import os
import sys

# Download pypy here (https://pypy.org/download.html) for better performances
# To allow unicode characters in Powershell, type "chcp 65001"
# C:/PyPy/pypy program3_game_of_life.py

# Let n be the number of neighbours
# The game of life outputs 1 if n=3, 1 if the center is active and n=3, 0 otherwise
# Equivalently, f(c, n) = (n=3) XOR (c & (n=2))
def local_rule_game_of_life(a, b, c, d, e, f, g, h, i):
    neighbours = [a, b, c, d, f, g, h, i]
    return count(neighbours, 3) ^ (e & count(neighbours, 2))

def game_of_life(x, t=1):
    for _ in range(t):
        y = [[0]*len(x[0]) for _ in range(len(x))]
        for i in range(1, len(x)-1):
            for j in range(1, len(x[0])-1):
                y[i][j] = local_rule_game_of_life(
                    x[i-1][j-1], x[i-1][j], x[i-1][j+1],
                    x[i][j-1], x[i][j], x[i][j+1],
                    x[i+1][j-1], x[i+1][j], x[i+1][j+1]
                )
        x = y
    return x

os.system("")
def print_pretty_2D(x):
    sys.stdout.write("\033[2J\033[H") # clear screen + move cursor home
    sys.stdout.write("\n".join("".join("█" if e else "." for e in row) for row in x))
    sys.stdout.flush()


# This is the Gosper Glider Gun (https://conwaylife.com/wiki/Gosper_glider_gun)
x = encrypt([
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,1,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0],
    [0,1,1,0,0,0,0,0,0,0,0,1,0,0,0,0,0,1,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,1,1,0,0,0,0,0,0,0,0,1,0,0,0,1,0,1,1,0,0,0,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,1,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
])

"""
# You can uncomment this part in order to load Breeder 1. However, this one is extremely slow and may cause memory errors.
# Breeder 1 can be found here (https://conwaylife.com/wiki/Breeder_1) and here (https://conwaylife.com/patterns/breeder1.cells)
padding_top, padding_right, padding_bottom, padding_left = 10, 100, 10, 10
with open("breeder1.cells", "r") as fd:
    # We skip the first four lines and remove the "\n"
    content = [line.rstrip("\n") for line in fd.readlines()[4:]]
    
    # We transform the content into a rectangle (because not all lines have the same width)
    # We also add padding to the left and to the right
    maximal_length = max(len(line) for line in content)
    content = ["." * padding_left + line + "." * (maximal_length - len(line) + padding_right) for line in content]
    
    # We add padding to the top and the bottom
    empty_line = "." * (padding_left + maximal_length + padding_right)
    content = [empty_line]*padding_top + content + [empty_line]*padding_bottom
    
    # We encrypt the boolean array
    x = encrypt([[e=="O" for e in line] for line in content])
"""

while True:
    x = game_of_life(x)
    print_pretty_2D(decrypt(x))
