from random import getrandbits

# Alice, Bob and Charlie have points.
# They store their points in lists.
# Their lists always have the same lengths.
# The shares for Alice, Bob, and Charlie correspond to the same polynomial iff they are stored at the same index in their lists.
alice = []
bob = []
charlie = []

ZERO, ONE, ALPHA, ONE_PLUS_ALPHA = 0, 1, 2, 3

mul_GF = (
    (ZERO, ZERO, ZERO, ZERO),
    (ZERO, ONE, ALPHA, ONE_PLUS_ALPHA),
    (ZERO, ALPHA, ONE_PLUS_ALPHA, ONE),
    (ZERO, ONE_PLUS_ALPHA, ONE, ALPHA)
)

# This is the class for indexes.
class Index:
    __slots__ = ("i",) # for optimization
    
    def __init__(self, i):
        self.i = i # index
    
    # xor between p and q
    def __xor__(self, q):
        # If q isn't an Index, then it is a constant, and thus the addition is trivial:
        if not isinstance(q, Index):
            alice.append(alice[self.i] ^ q)
            bob.append(bob[self.i] ^ q)
            charlie.append(charlie[self.i] ^ q)
            return Index(len(alice)-1)
        
        # Alice, Bob, and Charlie each add their two shares for p and q together. They obtain new shares for the polynomial p + q
        # Note that addition in GF(4) corresponds to bitwize XOR in {0, 1, 2, 3}
        alice.append(alice[self.i] ^ alice[q.i])
        bob.append(bob[self.i] ^ bob[q.i])
        charlie.append(charlie[self.i] ^ charlie[q.i])
        
        # We output the index where Alice, Bob, and Charlie stored the new shares (it is the same index for the three)
        return Index(len(alice)-1)
    
    # and between p and q
    def __and__(self, q):
        # If q isn't an Index, then it is a constant, and thus the multiplication is trivial:
        if not isinstance(q, Index):
            alice.append(mul_GF[alice[self.i]][q])
            bob.append(mul_GF[bob[self.i]][q])
            charlie.append(mul_GF[charlie[self.i]][q])
            return Index(len(alice)-1)
        
        # Alice, Bob, and Charlie each multiply their two shares for p and q together. They obtain new shares
        share_alice_of_p_times_q   = mul_GF[alice[self.i]][alice[q.i]]
        share_bob_of_p_times_q     = mul_GF[bob[self.i]][bob[q.i]]
        share_charlie_of_p_times_q = mul_GF[charlie[self.i]][charlie[q.i]]
        
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
        alice.append(v ^ share_alice_of_g)
        bob.append(v ^ share_bob_of_g)
        charlie.append(v ^ share_charlie_of_g)
        
        # We output the index where Alice, Bob, and Charlie stored the new shares (it is the same index for the three)
        return Index(len(alice)-1)
    
    def __or__(self, b):
        return (self ^ b) ^ (self & b)
    
    def __rxor__(self, b):
        return self ^ b
    
    def __rand__(self, b):
        return self & b
    
    def __ror__(self, b):
        return self | b

# This function outputs elements of the class Index (or lists of them).
def encrypt(x, base=2):
    # Case where it is a list
    if isinstance(x, list):
        return [encrypt(e, base) for e in x]
    
    # Case where it is already encrypted
    if isinstance(x, Index):
        return x
    
    # We create a random polynomial whose y-intercept is the secret x
    a, b = getrandbits(2), x
    
    # We generate three shares and distribute them to Alice, Bob, and Charlie
    alice.append(mul_GF[a][ONE] ^ b)
    bob.append(mul_GF[a][ALPHA] ^ b)
    charlie.append(mul_GF[a][ONE_PLUS_ALPHA] ^ b)
    
    # We output the index where Alice, Bob, and Charlie stored their shares (it is the same index for the three)
    return Index(len(alice)-1)
    
def decrypt(index):
    # Case where it is a list:
    if isinstance(index, list):
        return [decrypt(e) for e in index]
    
    # Case where it is already decrypted
    if not isinstance(index, Index):
        return index

    # We have the shares of a polynomial p(x) = ax + b of degree 1
    # Alice has p(1), Bob has p(α), and Charlie has p(α+1)
    # p(1) = a * 1 + b = a + b
    # p(α) = a * α + b
    # Therefore, p(1) + p(α) = (a + b) + (a * α + b) = a + a * α = a(1 + α), meaning that a = (p(1) + p(α))/(1 + α)
    # Thus, p(0) = b = p(1) - a = p(1) - (p(1) + p(α))/(1 + α) = p(1) + (p(1) + p(α))/(1 + α)
    # From α^3 = 1, we get that α² * α = 1, and therefore α = 1 / α² = 1/(1 + α)
    # Therefore, p(0) = p(1) + (p(1) + p(α))/(1 + α) = p(1) + α(p(1) + p(α)) = p(1) + αp(1) + αp(α) = (1 + α)p(1) + αf(α)
    # We therefore have to return p(0) = (1 + α)p(1) + αf(α)
    return mul_GF[ONE_PLUS_ALPHA][alice[index.i]] ^ mul_GF[ALPHA][bob[index.i]]
