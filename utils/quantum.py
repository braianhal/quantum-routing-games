#########################################
# Utilidades para algoritmos cuánticos. #
#########################################

import numpy as np
import pennylane as qml
import random


def J(gamma, wires):
    """ 
        Aplica el operador de entrelazamiento J sobre los qubits 'wires'
        utilizando un nivel de entrelazamiento 'gamma'.
    """
    n = len(wires)

    # Aplica cambio de base RX iniciales.
    for q in wires:
        qml.RX(np.pi/2, wires=q)

    # Aplica cascada de CNOTs para entrelazar.
    for i in range(n-1, 0, -1):
        qml.CNOT(wires=[wires[i], wires[i-1]])

    # Aplica puerta RZ con la rotación gamma.
    qml.RZ(gamma, wires=0)

    # Aplica cascada de CNOTs inversas.
    for i in range(n-1):
        qml.CNOT(wires=[wires[i+1], wires[i]])

    # Aplica cambio de base RX finales.
    for q in wires:
        qml.RX(-np.pi/2, wires=q)