#We want to find f, g, h, i such that CNOT(X^a1·Z^b1 ⊗ X^a2·Z^b2) = (X^f(a1, a2)·Z^g(b1, b2) ⊗ X^h(a1, a2)·Z^i(b1, b2))CNOT
import numpy as np
from numpy import dot, kron
from numpy.linalg import inv, matrix_power
import itertools

X = [[0, 1], [1, 0]]
Z = [[1, 0], [0, -1]]
CNOT = [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0]]

def allBinaryFunctions():
    return [(lambda x, y, array=arr: array[2*x + y]) for arr in itertools.product([0, 1], repeat=4)]

for f, g, h, i in itertools.product(allBinaryFunctions(), repeat=4):
    corresponds = True
    for a, b in itertools.product(itertools.product([0, 1], repeat=2), repeat=2):
        wanted = CNOT @ kron(matrix_power(X, a[0]) @ matrix_power(Z, b[0]), matrix_power(X, a[1]) @ matrix_power(Z, b[1]))
        result = kron(matrix_power(X, f(a[0], a[1])) @ matrix_power(Z, g(b[0], b[1])), matrix_power(X, h(a[0], a[1])) @ matrix_power(Z, i(b[0], b[1]))) @ CNOT
        corresponds &= np.round(wanted, decimals=2).tolist() == np.round(result, decimals=2).tolist()
        if not corresponds:
            break
    
    if corresponds:
        print("Found")
        print("f :", f(0, 0), f(0, 1), f(1, 0), f(1, 1))
        print("g :", g(0, 0), g(0, 1), g(1, 0), g(1, 1))
        print("h :", h(0, 0), h(0, 1), h(1, 0), h(1, 1))
        print("i :", i(0, 0), i(0, 1), i(1, 0), i(1, 1))
