from mpc import encrypt, decrypt

# Download pypy here (https://pypy.org/download.html) for better performances

# Rule 60's Algebraic Normal Form (ANF) l XOR c
# It therefore doesn't use AND gates
def local_rule_60(l, c, r):
    return l ^ c

def rule_60(x, t=1):
    for _ in range(t):
        y = [0]*len(x)
        for i in range(1, len(x)-1):
            y[i] = local_rule_60(x[i-1], x[i], x[i+1])
        x = y
    return x

def print_pretty(x):
    print("".join("O" if e else " " for e in x))

x = encrypt([i==1 for i in range(128 + 2)])
while True:
    print_pretty(decrypt(x))
    x = rule_60(x)
