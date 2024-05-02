import numpy as np
from numpy import cos, sin, exp, dot, kron, pi
from numpy.linalg import multi_dot, inv, matrix_power
from random import randint
import functools as ft

X = [[0, 1], [1, 0]]
Z = [[1, 0], [0, -1]]
CNOT = [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0]]

def R_y(theta):
    return np.array([[cos(theta/2), -sin(theta/2)], [sin(theta/2), cos(theta/2)]])
    
def R_z(theta):
    return np.array([[exp(-1j*theta/2), 0], [0, exp(1j*theta/2)]])

def U(alpha, beta, gamma, delta):
    return exp(1j*alpha) * multi_dot([R_z(beta), R_y(gamma), R_z(delta)])

def multikron(t):
    return ft.reduce(np.kron, t)

#This function takes an index i, and applies a CNOT gate whose control qubit is i-1 and whose target qubit is i
def cnot(i):
    global sigma
    #We compute CNOT'
    CNOT_prime = dot(CNOT, kron((-1)**(a[i-1]*b[i]) * matrix_power(Z, b[i]), matrix_power(X, a[i-1])))
    #We update the ciphertext
    M = multikron([np.identity(2**(i-1)), CNOT_prime, np.identity(2**(n-i-1))])
    sigma = multi_dot([M, sigma, inv(M)])

#This function takes an index i, and applies a U(alpha, beta, gamma, delta) gate on the qubit i
def u(i, alpha, beta, gamma, delta):
    global sigma
    #We compute U'(alpha, beta, gamma, delta)
    U_prime = U(alpha, (-1)**a[i]*beta, (-1)**(a[i]+b[i])*gamma, (-1)**a[i]*delta)
    #We update the ciphertext
    M = multikron([np.identity(2**i), U_prime, np.identity(2**(n-i-1))])
    sigma = multi_dot([M, sigma, inv(M)])

#This is our initial sequence of bits of length n
sequence = [1, 1, 0]
n = len(sequence)
print("Before applying the Toffoli gate:", "".join(map(str, sequence)))
#We convert this sequence of bits into binary
i = sum(j * 2**i for i,j in enumerate(reversed(sequence)))
#We transform it into a standard unit vector of the form e_i, and then we transform this vector into a density matrix rho
#I directly generate the density matrix without generating the standard unit vector
#Indeed, the standard unit vector is just a vector of zeros except for a 1 at the index i
#And the density matrix rho is a square matrix of zeros whose diagonal is the standard unit vector
#Therefore, the density matrix rho contains a single 1, which is located at the intersection between the row of index i and the column of index i
rho = np.zeros([2**n, 2**n])
rho[i][i] = 1
#We generate the secret keys a and b
a = [randint(0, 1) for _ in range(n)]
b = [randint(0, 1) for _ in range(n)]
#We encrypt rho into sigma
M = multikron([dot(matrix_power(X, a[i]), matrix_power(Z, b[i])) for i in range(n)])
sigma = multi_dot([M, rho, inv(M)])



#Now that the sequence is encrypted, we can apply any program on it. For instance, I perform the Toffoli gate on it, as it is a universal quantum logic gate that can easily built using the circuit from this website https://www.semanticscholar.org/paper/On-the-CNOT-cost-of-TOFFOLI-gates-Shende-Markov/c7011bd2c3eb2dbd4e8879ffb9803dc221c17c09

def h(i):
    u(i, pi/2, 0, pi/2, pi)

def t(i):
    u(i, 0, 0, 0, pi/4)

def tinv(i):
    u(i, 0, 0, 0, -pi/4)

def toffoli(i):
    h(i)
    cnot(i)
    tinv(i)
    cnot(i-1)
    cnot(i)
    cnot(i-1)
    cnot(i)
    t(i)
    cnot(i)
    tinv(i)
    cnot(i-1)
    cnot(i)
    cnot(i-1)
    cnot(i)
    t(i-1)
    t(i)
    cnot(i-1)
    h(i)
    t(i-2)
    tinv(i-1)
    cnot(i-1)

toffoli(2)



#We decrypt sigma into rho
rho = multi_dot([M, sigma, inv(M)])
#We convert rho into a standard unit vector of the form e_j, and then we deduce j
#Again, I do not generate the standard unit vector
j = [j for j in range(2**n) if rho[j][j]==1][0]
#We convert the index into binary
sequence = [(j >> k) & 1 for k in range(n-1,-1,-1)]
print("After applying the Toffoli gate:", "".join(map(str, sequence)))
