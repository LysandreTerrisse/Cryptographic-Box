# Creates a counter, that is, a list of bits, least significant bit first
# Then, for each bit, we increase the counter by 1 if and only if x is true
def count(bits):
    counter = [0] * (len(bits).bit_length())
    for x in bits:
        carry = x
        for i in range(len(counter)):
            counter[i], carry = counter[i] ^ carry, counter[i] & carry
    return counter

# Compares a counter to an integer
def equal(counter, n):
    equal = 1
    for i in range(len(counter)):
        # We compare the i-th bit of the counter with the i-th bit of n
        equal &= counter[i] ^ (not ((n >> i) & 1))
    return equal
