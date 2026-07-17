# The cryptographic box
The goal of this project was to create a program that would enable us to run infinitely dangerous programs safely, by using Fully Homomorphic Encryption (FHE) schemes with perfect secrecy. The initial goal described in [my first post](https://www.lesswrong.com/posts/TK8ptSJGvAqj2HaRr/) was to implement Min Liang's symmetric QFHE scheme from [this paper](https://arxiv.org/abs/1304.5087v4). However, in [my second post](https://www.lesswrong.com/posts/wuESDsLmDYtMgAFeE/), I proved that the scheme was not perfectly secret, and I fixed the mistake in the scheme by making a key update during the evaluations. However, this fix enables us to simulate only affine gates, called Clifford gates.

Then, I realized in my third post that Fully Homomorphic Encryption is not the way to go. Instead, to provide perfect secrecy, we need Secure Multi-Party Computation (MPC). This is the solution to our problem.

This repository contains:
- The code of the second post in the folder `FHE`:
  - `encrypted_toffoli_gate.py` shows how to implement the Toffoli gate using the (unsafe) symmetric QFHE scheme, as it is a universal gate.
  - `encrypted_rule_60.py` shows how to implement rule 60 using the (unsafe) symmetric QFHE scheme.
  - `encrypted_rule_60_with_fixed_scheme.py` is like the previous program, except that it implements the fix I made. I can apply the fix here, as rule 60 uses only the CNOT gate, which is universal.
  - `finding_all_evaluations_of_one_qubit_gates.py` is the program that I used in order to find the fix for the one-qubit gates.
  - `brute_forcing_a_solution_for_cnot_evaluation.py` is the program that I used in order to find the fix for the CNOT gate. It is different than the previous program because it only partially brute-forces the problem (as otherwise it would suffer from combinatorial explosion). Therefore, although it doesn't give every solution, it finds at least one.
  - `Fully_Homomorphic_Encryption.pdf`, which is a beamer that I made for an english presentation at my university.
- The code of the third post in the folder `MPC`
  - `mpc.py` is the file in which I implemented the [MPC scheme made by David Chaum, Claude Crépeau, and Ivan Damgård](https://chaum.com/wp-content/uploads/2021/12/Multiparty_unconditionally_secure_protocols.pdf).
  - `boolean_circuits.py` is a file containing some useful boolean circuits, such as a function `count(table, n)` which tells whether there are exactly `n` variables in `table` that are set to `True`. This can be tedious when implemented as a boolean circuit from just XOR and AND gates.
  - `program1_rule_60.py` uses the MPC scheme to run Rule 60.
  - `program2_rule_110.py` uses the MPC scheme to run Rule 110.
  - `program3_game_of_life.py` uses the MPC scheme to run the Game of Life.
  - `breeder1.cells` is the raw file for a structure in the Game of Life called Breeder 1. This file can also be downloaded [here](https://conwaylife.com/patterns/breeder1.cells). Alternatively, if Breeder 1 is too big, you can comment the code about it and uncomment the part of the code just below in order to run a structure called the [Gosper glider gun](https://conwaylife.com/wiki/Gosper_glider_gun). I recommend using [PyPy](https://pypy.org/download.html) for better performances. 
