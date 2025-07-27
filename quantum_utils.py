import pennylane as q
import random

def J(gamma, wires):
    n = len(wires)
    for i in range(n - 1):
        qml.IsingXX(gamma, wires=[wires[i], wires[i+1]])
    qml.IsingXX(gamma, wires=[wires[-1], wires[0]])

def mixed_operator(p, A, B):
    if (random.uniform(0,1) <= p):
        qml.apply(A, 