import numpy as np
from numpy import exp, pi, sqrt
from numpy.linalg import inv, matrix_power
import itertools

def allBinaryFunctions():
    return [(lambda x, y, array=arr: array[2*x + y]) for arr in itertools.product([0, 1], repeat=4)]

def equal_up_to_scalar(A, B):
    tmp = A[(B != 0)] / B[(B != 0)]
    return np.allclose(tmp, tmp[0]) and np.array_equal((A != 0), (B != 0))

I = np.array([[1, 0], [0, 1]])
X = np.array([[0, 1], [1, 0]])
Y = np.array([[0, -1j], [1j, 0]])
Z = np.array([[1, 0], [0, -1]])
H = np.array([[1/sqrt(2), 1/sqrt(2)], [1/sqrt(2), -1/sqrt(2)]])
S = np.array([[1, 0], [0, 1j]])
T = np.array([[1, 0], [0, exp(1j*pi/4)]])

for name, G in zip(["X", "Y", "Z", "H", "S", "T"], [X, Y, Z, H, S, T]):
    for f, g in itertools.product(allBinaryFunctions(), repeat=2):
        t = []
        for a, b in itertools.product([0, 1], repeat=2):
            G_prime = inv(matrix_power(X, f(a, b)) @ matrix_power(Z, g(a, b))) @ G @ inv(matrix_power(X, a) @ matrix_power(Z, b))
            t.append(G_prime)
        
        if all(equal_up_to_scalar(G_prime, t[0]) for G_prime in t):
            print("Found a solution for", name)
            print("f:", f(0, 0), f(0, 1), f(1, 0), f(1, 1))
            print("g:", g(0, 0), g(0, 1), g(1, 0), g(1, 1))
            print("G': (any scalar multiplication allowed)\n", t[0])
            #We do not need to print t[1], t[2] and t[3] because they are equal to t[0] up to a scalar
            #We can add a break in order to print only a single solution up to a scalar
            #The other solutions may not be equal up to a scalar to this one
