from mpc import encrypt, decrypt

# Rule 60 is defined as f(x,y,z) = x XOR y
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
    print("".join("█" if e else " " for e in x))


x = encrypt([i==2 for i in range(101)])
while True:
    print_pretty(decrypt(x))
    x = rule_60(x)
