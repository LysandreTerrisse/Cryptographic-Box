# The cryptographic box
The goal of this project is to create a program that would enable us to run infinitely dangerous programs safely, by using Fully Homomorphic Encryption schemes with perfect secrecy. The initial goal described in [this post](https://www.lesswrong.com/posts/TK8ptSJGvAqj2HaRr/) was to implement Min Liang's symmetric QFHE scheme from [this paper](https://arxiv.org/abs/1304.5087v4). However, since I proved in [this post (not released yet)]() that the scheme was not perfectly secret, the new goal is to use the asymmetric QFHE scheme from [this paper](https://arxiv.org/abs/1410.2435), still made by Min Liang.

This repository contains some code that I made in order to implement the symmetric QFHE scheme. One of them shows how to implement the Toffoli gate, as it is a universal gate. Another program shows how to implement rule 60 using the symmetric QFHE scheme.

As I haven't implemented the asymmetric QFHE scheme yet, I cannot provide any code for it yet.
