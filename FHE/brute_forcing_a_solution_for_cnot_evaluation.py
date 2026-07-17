#Normally, to brute-force the solution, we would have to find f1, f2, g1, g2 such that CNOT(X^a1·Z^b1 ⊗ X^a2·Z^b2) = (X^f1(a1, a2, b1, b2)·Z^g1(a1, a2, b1, b2) ⊗ X^hf2(a1, a2, b1, b2)·Z^g2(a1, a2, b1, b2))CNOT
#However, we cannot brute-force the solution by checking every quadruple of functions that take four parameters each.
#Therefore, we brute-force the solution by checking only quadruples of functions that take two parameters each.
#That is, we look at the cases where we update a independently of b, and where we update b independently of a.
#We may miss some solutions, but in that specific case, we get exactly one solution, which is enough.
#So, we try to find f1, f2, g1, g2 such that CNOT(X^a1·Z^b1 ⊗ X^a2·Z^b2) = (X^f1(a1, a2)·Z^g1(b1, b2) ⊗ X^f2(a1, a2)·Z^g2(b1, b2))CNOT
import numpy as np
from numpy import dot, kron
from numpy.linalg import inv, matrix_power
import itertools

X = np.array([[0, 1], [1, 0]])
Z = np.array([[1, 0], [0, -1]])
CNOT = np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0]])

def allBinaryFunctions():
    return [(lambda x, y, array=arr: array[2*x + y]) for arr in itertools.product([0, 1], repeat=4)]

for f1, f2, g1, g2 in itertools.product(allBinaryFunctions(), repeat=4):
    corresponds = True
    for a1, a2, b1, b2 in itertools.product([0, 1], repeat=4):
        corresponds &= np.allclose(
            CNOT @ kron(matrix_power(X, a1) @ matrix_power(Z, b1), matrix_power(X, a2) @ matrix_power(Z, b2)),
            kron(matrix_power(X, f1(a1, a2)) @ matrix_power(Z, g1(b1, b2)), matrix_power(X, f2(a1, a2)) @ matrix_power(Z, g2(b1, b2))) @ CNOT
        )
        if not corresponds:
            break
    
    if corresponds:
        print("Found")
        print("f1 :", f1(0, 0), f1(0, 1), f1(1, 0), f1(1, 1))
        print("f2 :", f2(0, 0), f2(0, 1), f2(1, 0), f2(1, 1))
        print("g1 :", g1(0, 0), g1(0, 1), g1(1, 0), g1(1, 1))
        print("g2 :", g2(0, 0), g2(0, 1), g2(1, 0), g2(1, 1))
