from random import getrandbits

ZERO, ONE, ALPHA, ONE_PLUS_ALPHA = 0, 1, 2, 3

mul = (
    ZERO, ZERO, ZERO, ZERO,
    ZERO, ONE, ALPHA, ONE_PLUS_ALPHA,
    ZERO, ALPHA, ONE_PLUS_ALPHA, ONE,
    ZERO, ONE_PLUS_ALPHA, ONE, ALPHA
)

mul_by_alpha          = (ZERO, ALPHA, ONE_PLUS_ALPHA, ONE)
mul_by_one_plus_alpha = (ZERO, ONE_PLUS_ALPHA, ONE, ALPHA)

class EncryptedBit:
    __slots__ = ("share_alice", "share_bob", "share_charlie")
    
    def __init__(self, share_alice, share_bob, share_charlie):
        self.share_alice = share_alice
        self.share_bob = share_bob
        self.share_charlie = share_charlie
    
    # xor between p and q
    def __xor__(self, q):
        if isinstance(q, EncryptedBit):
            # Alice, Bob, and Charlie each add their two shares for p and q together. They obtain new shares for the polynomial p + q
            # Note that addition in GF(4) corresponds to bitwize XOR in {0, 1, 2, 3}
            return EncryptedBit(self.share_alice ^ q.share_alice, self.share_bob ^ q.share_bob, self.share_charlie ^ q.share_charlie)
        # If q isn't an EncryptedBit, then the addition is trivial:
        if q:
            return EncryptedBit(self.share_alice ^ q, self.share_bob ^ q, self.share_charlie ^ q)
        else:
            return self
    
    # and between p and q
    def __and__(self, q):
        if isinstance(q, EncryptedBit):
            # Alice, Bob, and Charlie each multiply their two shares for p and q together. They obtain new shares
            # Note that accessing a 2D list by doing T[a][b] is equivalent to accessing a 1D list by doing T[(a << 2) | b]
            share_alice_of_p_times_q   = mul[(self.share_alice << 2) | q.share_alice]
            share_bob_of_p_times_q     = mul[(self.share_bob << 2) | q.share_bob]
            share_charlie_of_p_times_q = mul[(self.share_charlie << 2) | q.share_charlie]
            
            # But the shares correspond to a polynomial of degree 2 rather than one
            # Alice, Bob, and Charlie therefore generate six bits each (or three GF(4) elements each)
            randbits = getrandbits(18)
            
            # Alice generates a polynomial f_A(x) = a * x + b of degree 1
            # She gives f_A(1) to herself, f_A(α) to Bob, and f_A(1 + α) to Charlie
            a, b = randbits & 3, (randbits >> 2) & 3
            share_alice_of_f_A   = a ^ b  # f_A(1) = a * 1 + b = a + b
            share_bob_of_f_A     = mul_by_alpha[a] ^ b
            share_charlie_of_f_A = mul_by_one_plus_alpha[a] ^ b
            
            # She also generates a polynomial g_A(x) of degree 1 of same y-intercept than f_A(x)
            # She gives g_A(1) to herself, g_A(α) to Bob, and g_A(1 + α) to Charlie
            a = (randbits >> 4) & 3
            share_alice_of_g_A   = a ^ b
            share_bob_of_g_A     = mul_by_alpha[a] ^ b
            share_charlie_of_g_A = mul_by_one_plus_alpha[a] ^ b
            
            # Bob also generates a polynomial f_B(x) of degree 1
            # He gives f_B(1) to Alice, f_B(α) to himself, and f_B(1 + α) to Charlie
            a, b = (randbits >> 6) & 3, (randbits >> 8) & 3
            share_alice_of_f_B   = a ^ b
            share_bob_of_f_B     = mul_by_alpha[a] ^ b
            share_charlie_of_f_B = mul_by_one_plus_alpha[a] ^ b
            
            # He also generates a polynomial g_B(x) of degree 1 of same y-intercept than f_B(x)
            # He gives g_B(1) to Alice, g_B(α) to himself, and g_B(1 + α) to Charlie
            a = (randbits >> 10) & 3
            share_alice_of_g_B   = a ^ b
            share_bob_of_g_B     = mul_by_alpha[a] ^ b
            share_charlie_of_g_B = mul_by_one_plus_alpha[a] ^ b
            
            # Charlie also generates a polynomial f_C(x) of degree 1
            # They give f_C(1) to Alice, f_C(α) to Bob, and f_C(1 + α) to themselves
            a, b = (randbits >> 12) & 3, (randbits >> 14) & 3
            share_alice_of_f_C   = a ^ b
            share_bob_of_f_C     = mul_by_alpha[a] ^ b
            share_charlie_of_f_C = mul_by_one_plus_alpha[a] ^ b
            
            # They also generates a polynomial g_C(x) of degree 1 of same y-intercept than f_C(x)
            # They give g_C(1) to Alice, g_C(α) to Bob, and g_C(1 + α) to themselves
            a = (randbits >> 16) & 3
            share_alice_of_g_C   = a ^ b
            share_bob_of_g_C     = mul_by_alpha[a] ^ b
            share_charlie_of_g_C = mul_by_one_plus_alpha[a] ^ b
            
            # They then all add their own shares f_A, f_B, and f_C together in order to obtain the shares of the polynomial f = f_A + f_B + f_C
            share_alice_of_f   = share_alice_of_f_A ^ share_alice_of_f_B ^ share_alice_of_f_C
            share_bob_of_f     = share_bob_of_f_A ^ share_bob_of_f_B ^ share_bob_of_f_C
            share_charlie_of_f = share_charlie_of_f_A ^ share_charlie_of_f_B ^ share_charlie_of_f_C
            
            # They then all add their own shares g_A, g_B, and g_C together in order to obtain the shares of the polynomial g = g_A + g_B + g_C
            # Note that this polynomial has the same y-intercept than f
            share_alice_of_g   = share_alice_of_g_A ^ share_alice_of_g_B ^ share_alice_of_g_C
            share_bob_of_g     = share_bob_of_g_A ^ share_bob_of_g_B ^ share_bob_of_g_C
            share_charlie_of_g = share_charlie_of_g_A ^ share_charlie_of_g_B ^ share_charlie_of_g_C
            
            # Note that no one knows the value of f(0).
            # This value will be useful in order to hide the y-intercept of the polynomial p + q
            # They add the polynomial f and the polynomial p + q together
            # That is, they each add their share of f with their share of p + q
            # let's call this new polynomial "broadcast", since it will be broadcasted
            share_alice_of_broadcast   = share_alice_of_f ^ share_alice_of_p_times_q
            share_bob_of_broadcast     = share_bob_of_f ^ share_bob_of_p_times_q
            share_charlie_of_broadcast = share_charlie_of_f ^ share_charlie_of_p_times_q
            
            # They broadcast their shares of "broadcast" and compute its y-intercept
            # Note that the y-intercept is equal to f(0) + (p(0) * q(0))
            # To compute the y-intercept of a degree-2 polynomial from 3 points, we do as follows:
            # Let h be our polynomial. Alice has h(1), Bob has h(2), and Charlie has h(3)
            # h(1) = a * 1² + b * 1 + c = a + b + c
            # h(α) = a * α² + b * α + c = a(α + 1) + bα + c
            # h(α + 1) = a * (α + 1)² + b(α + 1) + c = aα + b(α + 1) + c
            # Therefore, h(1) + h(α) + h(α + 1) = (a + b + c) + (a(α + 1) + bα + c) + (aα + b(α + 1) + c)
            # = (a + b + c) + (aα + a + bα + c) + (aα + bα + b + c) = c
            # The y-intercept of the function "broadcast" (which we will call v) is therefore equal to the sum of the three shares
            v = share_alice_of_broadcast ^ share_bob_of_broadcast ^ share_charlie_of_broadcast
            
            # Now, they compute the polynomial v - g
            # Note that the y-intercept of this new polynomial is f(0) + (p * q) - g(0) = p * q
            return EncryptedBit(v ^ share_alice_of_g, v ^ share_bob_of_g, v ^ share_charlie_of_g)
        # If q isn't an EncryptedBit, then the multiplication is trivial:
        if q:
            return self
        else:
            return 0
    
    def __or__(self, b):
        return self ^ b ^ (self & b)
    
    def __eq__(self, b):
        return self ^ b ^ 1
    
    def __rxor__(self, b):
        return self ^ b
    
    def __rand__(self, b):
        return self & b
    
    def __ror__(self, b):
        return self | b
    
    def __req__(self, b):
        return self == b

class EncryptedInt:
    __slots__ = ("bits")
    
    def __init__(self, bits):
        self.bits = bits
    
    def bit_length(self):
        return len(self.bits)
    
    def __lshift__(self, n):
        return EncryptedInt(self.bits + [0]*n)
    
    def __rshift__(self, n):
        if n <= 0:
            return self
        if n >= len(self.bits):
            return 0
        return EncryptedInt(self.bits[:-n])
    
    def __and__(self, q):
        p, q = self.bits, MSB_list(q)
        min_len = min(len(p), len(q))
        # We reduce the size of p and q to the same size
        p = p[-min_len:]
        q = q[-min_len:]
        # We do the bitwize AND
        return EncryptedInt([p[i] & q[i] for i in range(min_len)])
    
    def __xor__(self, q):
        p, q = self.bits, MSB_list(q)
        len_p, len_q = len(p), len(q)
        # We increase the size of p and q to the same size
        if len_p < len_q:
            p = [0] * (len_q - len_p) + p
        elif len_q < len_p:
            q = [0] * (len_p - len_q) + q
        # We do the bitwize XOR
        return EncryptedInt([p[i] ^ q[i] for i in range(len(p))])
    
    def __invert__(self):
        return EncryptedInt([b ^ 1 for b in self.bits])
    
    def __or__(self, b):
        return (self ^ b) ^ (self & b)
    
    def __eq__(self, b):
        a, b = self.bits, MSB_list(b)
        len_a, len_b = len(a), len(b)
        # We increase the size of a and b to the same size
        if len_a < len_b:
            a[:0] = [0] * (len_b - len_a)
        elif len_b < len_a:
            b[:0] = [0] * (len_a - len_b)
        res = 1
        for i in range(len(a)):
            res &= a[i] ^ b[i] ^ 1
        return EncryptedInt([res])
    
    def __mul__(self, b):
        if b.bit_length()==1:
            if isinstance(b, EncryptedInt):
                return EncryptedInt([bit & b.bits[0] for bit in self.bits])
            elif b:
                return self
            else:
                return 0
        elif self.bit_length()==1:
            if isinstance(b, EncryptedInt):
                return EncryptedInt([self.bits[0] & bit for bit in b.bits])
            elif b > 1:
                return EncryptedInt([self.bits[0] & bit for bit in MSB_list(b)])
            elif b==1:
                return self
            else:
                return 0
        else:
            raise Exception('Multiplication of two EncryptedInts of size different than 1')

    def __rxor__(self, b):
        return self ^ b

    def __rand__(self, b):
        return self & b

    def __ror__(self, b):
        return self | b
    
    def __rmul__(self, b):
        return self * b

def equal(x, y):
    if isinstance(y, EncryptedInt):
        return y == x
    else:
        return x == y

# Takes an int and returns the MSB list
def MSB_list(x):
    if isinstance(x, EncryptedInt):
        return x.bits
    length = max(1, x.bit_length())
    return [(x>>i)&1 for i in range(length-1, -1, -1)]

def encrypt_bit(x):
    # Case where it is already encrypted
    if isinstance(x, EncryptedBit):
        return x
    # We create a random polynomial whose y-intercept is the secret x
    # We generate shares and distribute them to Alice, Bob, and Charlie
    a = getrandbits(2)
    return EncryptedBit(a ^ x, mul_by_alpha[a] ^ x, mul_by_one_plus_alpha[a] ^ x)
    
# This function outputs elements of the class EncryptedBit (or lists of them).
def encrypt(x):
    # Case where it is a list
    if isinstance(x, list):
        return [encrypt(e) for e in x]
    
    # Case where it is already encrypted
    if isinstance(x, EncryptedInt):
        return x
    
    return EncryptedInt([encrypt_bit(bit) for bit in MSB_list(x)])
    
def decrypt(x):
    # Case where it is a list:
    if isinstance(x, list):
        return [decrypt(e) for e in x]
    
    if isinstance(x, EncryptedBit):
        # We have the shares of a polynomial p(x) = ax + b of degree 1
        # Alice has p(1), Bob has p(α), and Charlie has p(α+1)
        # p(1) = a * 1 + b = a + b
        # p(α) = a * α + b
        # Therefore, p(1) + p(α) = (a + b) + (a * α + b) = a + a * α = a(1 + α), meaning that a = (p(1) + p(α))/(1 + α)
        # Thus, p(0) = b = p(1) - a = p(1) - (p(1) + p(α))/(1 + α) = p(1) + (p(1) + p(α))/(1 + α)
        # From α^3 = 1, we get that α² * α = 1, and therefore α = 1 / α² = 1/(1 + α)
        # Therefore, p(0) = p(1) + (p(1) + p(α))/(1 + α) = p(1) + α(p(1) + p(α)) = p(1) + αp(1) + αp(α) = (1 + α)p(1) + αf(α)
        # We therefore have to return p(0) = (1 + α)p(1) + αf(α)
        return mul_by_one_plus_alpha[x.share_alice] ^ mul_by_alpha[x.share_bob]
    
    if isinstance(x, EncryptedInt):
        res = 0
        for bit in x.bits:
            res = (res << 1) | decrypt(bit)
        return res
    
    # Case where it is already decrypted
    return x
