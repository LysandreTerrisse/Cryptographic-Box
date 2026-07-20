from random import getrandbits

ZERO, ONE, ALPHA, ONE_PLUS_ALPHA = 0, 1, 2, 3

mul = (
    (ZERO, ZERO, ZERO, ZERO),
    (ZERO, ONE, ALPHA, ONE_PLUS_ALPHA),
    (ZERO, ALPHA, ONE_PLUS_ALPHA, ONE),
    (ZERO, ONE_PLUS_ALPHA, ONE, ALPHA)
)

mul_by_alpha          = (ZERO, ALPHA, ONE_PLUS_ALPHA, ONE)
mul_by_alpha_plus_one = (ZERO, ONE_PLUS_ALPHA, ONE, ALPHA)

class EncryptedBit:
    __slots__ = ("share_alice", "share_bob", "share_charlie") # for optimization
    
    def __init__(self, share_alice, share_bob, share_charlie):
        self.share_alice = share_alice
        self.share_bob = share_bob
        self.share_charlie = share_charlie
    
    # xor between p and q
    def __xor__(self, q):
        # If q isn't an EncryptedBit, then it is a constant, and thus the addition is trivial:
        if not isinstance(q, EncryptedBit):
            return EncryptedBit(self.share_alice ^ q, self.share_bob ^ q, self.share_charlie ^ q)
        
        # Alice, Bob, and Charlie each add their two shares for p and q together. They obtain new shares for the polynomial p + q
        # Note that addition in GF(4) corresponds to bitwize XOR in {0, 1, 2, 3}
        return EncryptedBit(self.share_alice ^ q.share_alice, self.share_bob ^ q.share_bob, self.share_charlie ^ q.share_charlie)
    
    # and between p and q
    def __and__(self, q):
        # If q isn't an EncryptedBit, then it is a constant, and thus the multiplication is trivial:
        if not isinstance(q, EncryptedBit):
            return EncryptedBit(mul[self.share_alice][q], mul[self.share_bob][q], mul[self.share_charlie][q])
        
        # Alice, Bob, and Charlie each multiply their two shares for p and q together. They obtain new shares
        share_alice_of_p_times_q   = mul[self.share_alice][q.share_alice]
        share_bob_of_p_times_q     = mul[self.share_bob][q.share_bob]
        share_charlie_of_p_times_q = mul[self.share_charlie][q.share_charlie]
        
        # But the shares correspond to a polynomial of degree 2 rather than one
        # Alice, Bob, and Charlie therefore generate six bits each (or three GF(4) elements)
        randbits = getrandbits(18)
        
        # Alice generates a polynomial f_A(x) = a * x + b of degree 1
        # She gives f_A(1) to herself, f_A(α) to Bob, and f_A(1 + α) to Charlie
        a, b = randbits & 3, (randbits >> 2) & 3
        share_alice_of_f_A   = a ^ b  # f_A(1) = a * 1 + b = a + b
        share_bob_of_f_A     = mul_by_alpha[a] ^ b
        share_charlie_of_f_A = mul_by_alpha_plus_one[a] ^ b
        
        # She also generates a polynomial g_A(x) of degree 1 of same y-intercept than f_A(x)
        # She gives g_A(1) to herself, g_A(α) to Bob, and g_A(1 + α) to Charlie
        a = (randbits >> 4) & 3
        share_alice_of_g_A   = a ^ b
        share_bob_of_g_A     = mul_by_alpha[a] ^ b
        share_charlie_of_g_A = mul_by_alpha_plus_one[a] ^ b
        
        # Bob also generates a polynomial f_B(x) of degree 1
        # He gives f_B(1) to Alice, f_B(α) to himself, and f_B(1 + α) to Charlie
        a, b = (randbits >> 6) & 3, (randbits >> 8) & 3
        share_alice_of_f_B   = a ^ b
        share_bob_of_f_B     = mul_by_alpha[a] ^ b
        share_charlie_of_f_B = mul_by_alpha_plus_one[a] ^ b
        
        # He also generates a polynomial g_B(x) of degree 1 of same y-intercept than f_B(x)
        # He gives g_B(1) to Alice, g_B(α) to himself, and g_B(1 + α) to Charlie
        a = (randbits >> 10) & 3
        share_alice_of_g_B   = a ^ b
        share_bob_of_g_B     = mul_by_alpha[a] ^ b
        share_charlie_of_g_B = mul_by_alpha_plus_one[a] ^ b
        
        # Charlie also generates a polynomial f_C(x) of degree 1
        # They give f_C(1) to Alice, f_C(α) to Bob, and f_C(1 + α) to themselves
        a, b = (randbits >> 12) & 3, (randbits >> 14) & 3
        share_alice_of_f_C   = a ^ b
        share_bob_of_f_C     = mul_by_alpha[a] ^ b
        share_charlie_of_f_C = mul_by_alpha_plus_one[a] ^ b
        
        # They also generates a polynomial g_C(x) of degree 1 of same y-intercept than f_C(x)
        # They give g_C(1) to Alice, g_C(α) to Bob, and g_C(1 + α) to themselves
        a = (randbits >> 16) & 3
        share_alice_of_g_C   = a ^ b
        share_bob_of_g_C     = mul_by_alpha[a] ^ b
        share_charlie_of_g_C = mul_by_alpha_plus_one[a] ^ b
        
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
    
    def __or__(self, b):
        return (self ^ b) ^ (self & b)
    
    def __rxor__(self, b):
        return self ^ b
    
    def __rand__(self, b):
        return self & b
    
    def __ror__(self, b):
        return self | b

# This function outputs elements of the class EncryptedBit (or lists of them).
def encrypt(x, base=2):
    # Case where it is a list
    if isinstance(x, list):
        return [encrypt(e, base) for e in x]
    
    # Case where it is already encrypted
    if isinstance(x, EncryptedBit):
        return x
    
    # We create a random polynomial whose y-intercept is the secret x
    a, b = getrandbits(2), x
    
    # We generate shares and distribute them to Alice, Bob, and Charlie
    return EncryptedBit(mul[a][ONE] ^ b, mul[a][ALPHA] ^ b, mul[a][ONE_PLUS_ALPHA] ^ b)
    
def decrypt(x):
    # Case where it is a list:
    if isinstance(x, list):
        return [decrypt(e) for e in x]
    
    # Case where it is already decrypted
    if not isinstance(x, EncryptedBit):
        return x

    # We have the shares of a polynomial p(x) = ax + b of degree 1
    # Alice has p(1), Bob has p(α), and Charlie has p(α+1)
    # p(1) = a * 1 + b = a + b
    # p(α) = a * α + b
    # Therefore, p(1) + p(α) = (a + b) + (a * α + b) = a + a * α = a(1 + α), meaning that a = (p(1) + p(α))/(1 + α)
    # Thus, p(0) = b = p(1) - a = p(1) - (p(1) + p(α))/(1 + α) = p(1) + (p(1) + p(α))/(1 + α)
    # From α^3 = 1, we get that α² * α = 1, and therefore α = 1 / α² = 1/(1 + α)
    # Therefore, p(0) = p(1) + (p(1) + p(α))/(1 + α) = p(1) + α(p(1) + p(α)) = p(1) + αp(1) + αp(α) = (1 + α)p(1) + αf(α)
    # We therefore have to return p(0) = (1 + α)p(1) + αf(α)
    return mul[ONE_PLUS_ALPHA][x.share_alice] ^ mul[ALPHA][x.share_bob]from random import getrandbits

ZERO, ONE, ALPHA, ONE_PLUS_ALPHA = 0, 1, 2, 3

mul_GF = (
    (ZERO, ZERO, ZERO, ZERO),
    (ZERO, ONE, ALPHA, ONE_PLUS_ALPHA),
    (ZERO, ALPHA, ONE_PLUS_ALPHA, ONE),
    (ZERO, ONE_PLUS_ALPHA, ONE, ALPHA)
)

class EncryptedBit:
    __slots__ = ("share_alice", "share_bob", "share_charlie") # for optimization
    
    def __init__(self, share_alice, share_bob, share_charlie):
        self.share_alice = share_alice
        self.share_bob = share_bob
        self.share_charlie = share_charlie
    
    # xor between p and q
    def __xor__(self, q):
        # If q isn't an EncryptedBit, then it is a constant, and thus the addition is trivial:
        if not isinstance(q, EncryptedBit):
            return EncryptedBit(self.share_alice ^ q, self.share_bob ^ q, self.share_charlie ^ q)
        
        # Alice, Bob, and Charlie each add their two shares for p and q together. They obtain new shares for the polynomial p + q
        # Note that addition in GF(4) corresponds to bitwize XOR in {0, 1, 2, 3}
        return EncryptedBit(self.share_alice ^ q.share_alice, self.share_bob ^ q.share_bob, self.share_charlie ^ q.share_charlie)
    
    # and between p and q
    def __and__(self, q):
        # If q isn't an EncryptedBit, then it is a constant, and thus the multiplication is trivial:
        if not isinstance(q, EncryptedBit):
            return EncryptedBit(mul_GF[self.share_alice][q], mul_GF[self.share_bob][q], mul_GF[self.share_charlie][q])
        
        # Alice, Bob, and Charlie each multiply their two shares for p and q together. They obtain new shares
        share_alice_of_p_times_q   = mul_GF[self.share_alice][q.share_alice]
        share_bob_of_p_times_q     = mul_GF[self.share_bob][q.share_bob]
        share_charlie_of_p_times_q = mul_GF[self.share_charlie][q.share_charlie]
        
        # But the shares correspond to a polynomial of degree 2 rather than one
        # Alice, Bob, and Charlie therefore generate six bits each (or three GF(4) elements)
        randbits = getrandbits(18)
        
        # Alice generates a polynomial f_A(x) = a * x + b of degree 1
        # She gives f_A(1) to herself, f_A(α) to Bob, and f_A(1 + α) to Charlie
        a, b = randbits & 3, (randbits >> 2) & 3
        share_alice_of_f_A   = a ^ b  # f_A(1) = a * 1 + b = a + b
        share_bob_of_f_A     = mul_GF[a][ALPHA] ^ b
        share_charlie_of_f_A = mul_GF[a][ONE_PLUS_ALPHA] ^ b
        
        # She also generates a polynomial g_A(x) of degree 1 of same y-intercept than f_A(x)
        # She gives g_A(1) to herself, g_A(α) to Bob, and g_A(1 + α) to Charlie
        a = (randbits >> 4) & 3
        share_alice_of_g_A   = a ^ b
        share_bob_of_g_A     = mul_GF[a][ALPHA] ^ b
        share_charlie_of_g_A = mul_GF[a][ONE_PLUS_ALPHA] ^ b
        
        # Bob also generates a polynomial f_B(x) of degree 1
        # He gives f_B(1) to Alice, f_B(α) to himself, and f_B(1 + α) to Charlie
        a, b = (randbits >> 6) & 3, (randbits >> 8) & 3
        share_alice_of_f_B   = a ^ b
        share_bob_of_f_B     = mul_GF[a][ALPHA] ^ b
        share_charlie_of_f_B = mul_GF[a][ONE_PLUS_ALPHA] ^ b
        
        # He also generates a polynomial g_B(x) of degree 1 of same y-intercept than f_B(x)
        # He gives g_B(1) to Alice, g_B(α) to himself, and g_B(1 + α) to Charlie
        a = (randbits >> 10) & 3
        share_alice_of_g_B   = a ^ b
        share_bob_of_g_B     = mul_GF[a][ALPHA] ^ b
        share_charlie_of_g_B = mul_GF[a][ONE_PLUS_ALPHA] ^ b
        
        # Charlie also generates a polynomial f_C(x) of degree 1
        # They give f_C(1) to Alice, f_C(α) to Bob, and f_C(1 + α) to themselves
        a, b = (randbits >> 12) & 3, (randbits >> 14) & 3
        share_alice_of_f_C   = a ^ b
        share_bob_of_f_C     = mul_GF[a][ALPHA] ^ b
        share_charlie_of_f_C = mul_GF[a][ONE_PLUS_ALPHA] ^ b
        
        # They also generates a polynomial g_C(x) of degree 1 of same y-intercept than f_C(x)
        # They give g_C(1) to Alice, g_C(α) to Bob, and g_C(1 + α) to themselves
        a = (randbits >> 16) & 3
        share_alice_of_g_C   = a ^ b
        share_bob_of_g_C     = mul_GF[a][ALPHA] ^ b
        share_charlie_of_g_C = mul_GF[a][ONE_PLUS_ALPHA] ^ b
        
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
        share_alice_of_broadcast = share_alice_of_f ^ share_alice_of_p_times_q
        share_bob_of_broadcast = share_bob_of_f ^ share_bob_of_p_times_q
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
    
    def __or__(self, b):
        return (self ^ b) ^ (self & b)
    
    def __rxor__(self, b):
        return self ^ b
    
    def __rand__(self, b):
        return self & b
    
    def __ror__(self, b):
        return self | b

# This function outputs elements of the class EncryptedBit (or lists of them).
def encrypt(x, base=2):
    # Case where it is a list
    if isinstance(x, list):
        return [encrypt(e, base) for e in x]
    
    # Case where it is already encrypted
    if isinstance(x, EncryptedBit):
        return x
    
    # We create a random polynomial whose y-intercept is the secret x
    a, b = getrandbits(2), x
    
    # We generate shares and distribute them to Alice, Bob, and Charlie
    return EncryptedBit(mul_GF[a][ONE] ^ b, mul_GF[a][ALPHA] ^ b, mul_GF[a][ONE_PLUS_ALPHA] ^ b)
    
def decrypt(x):
    # Case where it is a list:
    if isinstance(x, list):
        return [decrypt(e) for e in x]
    
    # Case where it is already decrypted
    if not isinstance(x, EncryptedBit):
        return x

    # We have the shares of a polynomial p(x) = ax + b of degree 1
    # Alice has p(1), Bob has p(α), and Charlie has p(α+1)
    # p(1) = a * 1 + b = a + b
    # p(α) = a * α + b
    # Therefore, p(1) + p(α) = (a + b) + (a * α + b) = a + a * α = a(1 + α), meaning that a = (p(1) + p(α))/(1 + α)
    # Thus, p(0) = b = p(1) - a = p(1) - (p(1) + p(α))/(1 + α) = p(1) + (p(1) + p(α))/(1 + α)
    # From α^3 = 1, we get that α² * α = 1, and therefore α = 1 / α² = 1/(1 + α)
    # Therefore, p(0) = p(1) + (p(1) + p(α))/(1 + α) = p(1) + α(p(1) + p(α)) = p(1) + αp(1) + αp(α) = (1 + α)p(1) + αf(α)
    # We therefore have to return p(0) = (1 + α)p(1) + αf(α)
    return mul_GF[ONE_PLUS_ALPHA][x.share_alice] ^ mul_GF[ALPHA][x.share_bob]from random import getrandbits

ZERO, ONE, ALPHA, ONE_PLUS_ALPHA = 0, 1, 2, 3

mul_GF = (
    (ZERO, ZERO, ZERO, ZERO),
    (ZERO, ONE, ALPHA, ONE_PLUS_ALPHA),
    (ZERO, ALPHA, ONE_PLUS_ALPHA, ONE),
    (ZERO, ONE_PLUS_ALPHA, ONE, ALPHA)
)

class EncryptedBit:
    __slots__ = ("share_alice", "share_bob", "share_charlie") # for optimization
    
    def __init__(self, share_alice, share_bob, share_charlie):
        self.share_alice = share_alice
        self.share_bob = share_bob
        self.share_charlie = share_charlie
    
    # xor between p and q
    def __xor__(self, q):
        # If q isn't an EncryptedBit, then it is a constant, and thus the addition is trivial:
        if not isinstance(q, EncryptedBit):
            return EncryptedBit(self.share_alice ^ q, self.share_bob ^ q, self.share_charlie ^ q)
        
        # Alice, Bob, and Charlie each add their two shares for p and q together. They obtain new shares for the polynomial p + q
        # Note that addition in GF(4) corresponds to bitwize XOR in {0, 1, 2, 3}
        return EncryptedBit(self.share_alice ^ q.share_alice, self.share_bob ^ q.share_bob, self.share_charlie ^ q.share_charlie)
    
    # and between p and q
    def __and__(self, q):
        # If q isn't an EncryptedBit, then it is a constant, and thus the multiplication is trivial:
        if not isinstance(q, EncryptedBit):
            return EncryptedBit(mul_GF[self.share_alice][q], mul_GF[self.share_bob][q], mul_GF[self.share_charlie][q])
        
        # Alice, Bob, and Charlie each multiply their two shares for p and q together. They obtain new shares
        share_alice_of_p_times_q   = mul_GF[self.share_alice][q.share_alice]
        share_bob_of_p_times_q     = mul_GF[self.share_bob][q.share_bob]
        share_charlie_of_p_times_q = mul_GF[self.share_charlie][q.share_charlie]
        
        # But the shares correspond to a polynomial of degree 2 rather than one
        
        # Alice therefore generates a polynomial f_A(x) = a * x + b of degree 1
        # She gives f_A(1) to herself, f_A(α) to Bob, and f_A(1 + α) to Charlie
        # Note that to obtain an element of GF(4) randomly, we only need to generate a 2-bit number
        a, b1 = getrandbits(2), getrandbits(2)
        share_alice_of_f_A   = a ^ b1  # f_A(1) = a * 1 + b1 = a + b1
        share_bob_of_f_A     = mul_GF[a][ALPHA] ^ b1
        share_charlie_of_f_A = mul_GF[a][ONE_PLUS_ALPHA] ^ b1
        
        # Bob also generates a polynomial f_B(x) of degree 1
        # He gives f_B(1) to Alice, f_B(α) to himself, and f_B(1 + α) to Charlie
        a, b2 = getrandbits(2), getrandbits(2)
        share_alice_of_f_B   = a ^ b2
        share_bob_of_f_B     = mul_GF[a][ALPHA] ^ b2
        share_charlie_of_f_B = mul_GF[a][ONE_PLUS_ALPHA] ^ b2
        
        # Charlie also generates a polynomial f_C(x) of degree 1
        # They give f_C(1) to Alice, f_C(α) to Bob, and f_C(1 + α) to themselves
        a, b3 = getrandbits(2), getrandbits(2)
        share_alice_of_f_C   = a ^ b3
        share_bob_of_f_C     = mul_GF[a][ALPHA] ^ b3
        share_charlie_of_f_C = mul_GF[a][ONE_PLUS_ALPHA] ^ b3
        
        # They then all add their own shares together in order to obtain the shares of the polynomial f = f_A + f_B + f_C
        share_alice_of_f   = share_alice_of_f_A ^ share_alice_of_f_B ^ share_alice_of_f_C
        share_bob_of_f     = share_bob_of_f_A ^ share_bob_of_f_B ^ share_bob_of_f_C
        share_charlie_of_f = share_charlie_of_f_A ^ share_charlie_of_f_B ^ share_charlie_of_f_C
        
        # Note that no one know the value of f(0).
        # This value will be useful in order to hide the y-intercept of the polynomial p + q
        # They add the polynomial f and the polynomial p + q together
        # That is, they each add their share of f with their share of p + q
        # let's call this new polynomial "broadcast", since it will be broadcasted
        share_alice_of_broadcast = share_alice_of_f ^ share_alice_of_p_times_q
        share_bob_of_broadcast = share_bob_of_f ^ share_bob_of_p_times_q
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
        
        # Now, Alice generates a polynomial g_A(x) of degree 1 of same y-intercept than f_A(x)
        # She gives g_A(1) to herself, g_A(α) to Bob, and g_A(1 + α) to Charlie
        a = getrandbits(2)
        share_alice_of_g_A   = a ^ b1
        share_bob_of_g_A     = mul_GF[a][ALPHA] ^ b1
        share_charlie_of_g_A = mul_GF[a][ONE_PLUS_ALPHA] ^ b1
        
        # Bob also generates a polynomial g_B(x) of degree 1 of same y-intercept than f_B(x)
        # He gives g_B(1) to Alice, g_B(α) to himself, and g_B(1 + α) to Charlie
        a = getrandbits(2)
        share_alice_of_g_B   = a ^ b2
        share_bob_of_g_B     = mul_GF[a][ALPHA] ^ b2
        share_charlie_of_g_B = mul_GF[a][ONE_PLUS_ALPHA] ^ b2
        
        # Charlie also generates a polynomial g_C(x) of degree 1 of same y-intercept than f_C(x)
        # They give g_C(1) to Alice, g_C(α) to Bob, and g_C(1 + α) to themselves
        a = getrandbits(2)
        share_alice_of_g_C   = a ^ b3
        share_bob_of_g_C     = mul_GF[a][ALPHA] ^ b3
        share_charlie_of_g_C = mul_GF[a][ONE_PLUS_ALPHA] ^ b3
        
        # They then all add their own shares together in order to obtain the shares of the polynomial g = g_A + g_B + g_C
        # Note that this polynomial has the same y-intercept than f
        share_alice_of_g   = share_alice_of_g_A ^ share_alice_of_g_B ^ share_alice_of_g_C
        share_bob_of_g     = share_bob_of_g_A ^ share_bob_of_g_B ^ share_bob_of_g_C
        share_charlie_of_g = share_charlie_of_g_A ^ share_charlie_of_g_B ^ share_charlie_of_g_C
        
        # Now, they compute the polynomial v - g
        # Note that the y-intercept of this new polynomial is f(0) + (p * q) - g(0) = p * q
        return EncryptedBit(v ^ share_alice_of_g, v ^ share_bob_of_g, v ^ share_charlie_of_g)
    
    def __or__(self, b):
        return (self ^ b) ^ (self & b)
    
    def __rxor__(self, b):
        return self ^ b
    
    def __rand__(self, b):
        return self & b
    
    def __ror__(self, b):
        return self | b

# This function outputs elements of the class EncryptedBit (or lists of them).
def encrypt(x, base=2):
    # Case where it is a list
    if isinstance(x, list):
        return [encrypt(e, base) for e in x]
    
    # Case where it is already encrypted
    if isinstance(x, EncryptedBit):
        return x
    
    # We create a random polynomial whose y-intercept is the secret x
    a, b = getrandbits(2), x
    
    # We generate shares and distribute them to Alice, Bob, and Charlie
    return EncryptedBit(mul_GF[a][ONE] ^ b, mul_GF[a][ALPHA] ^ b, mul_GF[a][ONE_PLUS_ALPHA] ^ b)
    
def decrypt(x):
    # Case where it is a list:
    if isinstance(x, list):
        return [decrypt(e) for e in x]
    
    # Case where it is already decrypted
    if not isinstance(x, EncryptedBit):
        return x

    # We have the shares of a polynomial p(x) = ax + b of degree 1
    # Alice has p(1), Bob has p(α), and Charlie has p(α+1)
    # p(1) = a * 1 + b = a + b
    # p(α) = a * α + b
    # Therefore, p(1) + p(α) = (a + b) + (a * α + b) = a + a * α = a(1 + α), meaning that a = (p(1) + p(α))/(1 + α)
    # Thus, p(0) = b = p(1) - a = p(1) - (p(1) + p(α))/(1 + α) = p(1) + (p(1) + p(α))/(1 + α)
    # From α^3 = 1, we get that α² * α = 1, and therefore α = 1 / α² = 1/(1 + α)
    # Therefore, p(0) = p(1) + (p(1) + p(α))/(1 + α) = p(1) + α(p(1) + p(α)) = p(1) + αp(1) + αp(α) = (1 + α)p(1) + αf(α)
    # We therefore have to return p(0) = (1 + α)p(1) + αf(α)
    return mul_GF[ONE_PLUS_ALPHA][x.share_alice] ^ mul_GF[ALPHA][x.share_bob]
