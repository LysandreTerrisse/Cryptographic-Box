# The cryptographic box
The goal of this project is to create a program that would enable us to run infinitely dangerous programs safely, by using Fully Homomorphic Encryption schemes with perfect secrecy. The initial goal described in [this post](https://www.lesswrong.com/posts/TK8ptSJGvAqj2HaRr/) was to implement Min Liang's symmetric QFHE scheme from [this paper](https://arxiv.org/abs/1304.5087v4). However, I proved in [this post (not released yet)]() that the scheme was not perfectly secret, and I fixed the mistake in the scheme by making a key update during the evaluations. However, this fix enables us to simulate only Clifford gates.

This repository contains some code that I made in order to implement the symmetric QFHE scheme:
- `encrypted_toffoli_gate.py` shows how to implement the Toffoli gate using the (unsafe) symmetric QFHE scheme, as it is a universal gate.
- `encrypted_rule_60.py` shows how to implement rule 60 using the (unsafe) symmetric QFHE scheme.
- `encrypted_rule_60_with_fixed_scheme.py` is like the previous program, except that it implements the fix I made. I can apply the fix here, as rule 60 uses only the CNOT gate, which is universal.
- `finding_all_evaluations_of_one_qubit_gates.py` is the program that I used in order to find the fix for the one-qubit gates.
- `brute_forcing_a_solution_for_cnot_evaluation.py` is the program that I used in order to find the fix for the CNOT gate. It is different than the previous program because it only partially brute-forces the problem (as otherwise it would suffer from combinatorial explosion). Therefore, although it doesn't give every solution, it finds at least one.

I haven't implemented the fix for the Toffoli gate, as it isn't a Clifford gate and that therefore the scheme cannot work for this program.
