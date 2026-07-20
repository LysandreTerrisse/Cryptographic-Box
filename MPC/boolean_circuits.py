# Takes a counter, that is, a list of bits, least significant bit first
# This function increases the counter by 1 if and only if x is true
def add_bit(counter, x):
    carry = x
    for i, bit in enumerate(counter):
        counter[i], carry = bit ^ carry, bit & carry

# bits is a list of encrypted bits
# Creates a counter and adds every encrypted bit to it
def count(bits):
    counter_size = len(bits).bit_length()
    counter = [0]*counter_size
    for x in bits:
        add_bit(counter, x)
    return counter

# Compares a counter to an integer
def equal(counter, n):
    equal = 1
    for i in range(len(counter)):
        # We compare the i-th bit of the counter with the i-th bit of n
        equal &= counter[i] ^ (not ((n >> i) & 1))
    return equal
