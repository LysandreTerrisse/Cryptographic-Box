from mpc import encrypt, decrypt

# Download pypy here (https://pypy.org/download.html) for better performances

# Rule 110's Algebraic Normal Form (ANF) is c XOR r XOR cr XOR lcr
# It can be found at https://atlas.wolfram.com/01/01/110/01_01_1_110.html
def local_rule_110(l, c, r):
    return c ^ r ^ (c & r) ^ (l & c & r)

def rule_110(x, t=1):
    for _ in range(t):
        y = [0]*len(x)
        for i in range(1, len(x)-1):
            y[i] = local_rule_110(x[i-1], x[i], x[i+1])
        x = y
    return x

def print_pretty(x):
    print("".join("O" if e else " " for e in x))

x = encrypt([i==128 for i in range(128 + 2)])
while True:
    print_pretty(decrypt(x))
    x = rule_110(x)
