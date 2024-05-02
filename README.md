# The cryptographic box
The goal of this project is to create a program that would enable us to run infinitely dangerous programs safely, by using Fully Homomorphic Encryption schemes with perfect secrecy. The initial goal described in [this post](https://www.lesswrong.com/posts/TK8ptSJGvAqj2HaRr/) was to implement Min Liang's symmetric QFHE scheme from [this paper](https://arxiv.org/abs/1304.5087v4). However, I proved in [this post (not released yet)]() that the scheme was not perfectly secret, and I fixed the mistake in the scheme by making a key update during the CNOT evaluation.

This repository contains some code that I made in order to implement the symmetric QFHE scheme:
- `encrypted_toffoli_gate.py` shows how to implement the Toffoli gate, as it is a universal gate.
- `encrypted_rule_60.py` shows how to implement rule 60 using the symmetric QFHE scheme.
- `encrypted_rule_60_with_fixed_scheme.py` is like the previous program, except that it implements the fix I made.
