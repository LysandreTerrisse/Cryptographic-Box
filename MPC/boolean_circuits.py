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
        equal &= (counter[i] ^ bool((n >> i) & 1)) ^ 1
    return equal"""The following functions form a boolean circuit to count whether an array of bits has n elements"""

# Takes a counter, that is, a list of bits, least significant bit first
# This function increases the counter by 1 if and only if x is true
def add_bit(counter, x):
    carry = x
    for i, bit in enumerate(counter):
        counter[i], carry = bit ^ carry, bit & carry

# bits is a list of encrypted bits
# Returns whether exactly n of the boolean inputs are True.
def count(bits, n):
    counter_size = len(bits).bit_length()
    counter = [0]*counter_size
    for x in bits:
        add_bit(counter, x)
    
    expected_counter = [bool((n >> i) & 1) for i in range(counter_size)]

    equal = 1
    for a, b in zip(counter, expected_counter):
        equal &= (a ^ b) ^ 1

    return equal
