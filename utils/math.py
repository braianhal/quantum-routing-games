###########################
# Utilidades matemáticas. #
###########################

import math
import numpy as np


def normalized_probs(probs):
    """ Normaliza las probabilidad del array 'probs'. """
    probs = np.array([clamp(p, 0, 1) for p in probs])
    return probs / sum(probs)

def clamp(number, a, b):
    """ Limita el valor de 'number' entre 'a' y 'b'. """
    return max(min(number, b), a)

def ceil_log2(x):
    """ Calcula el techo del logaritmo en base 2 de 'x'. """
    return math.ceil(math.log2(x))

def int_to_bitlist(x, n):
    """ Transforma 'x' a un bitstring de longitud 'n'. """
    return [int(b) for b in format(x, f'0{n}b')]

def bitlist_to_int(bitlist):
    """ Operación inversa a 'int_to_bitlist'. """
    return int("".join(str(b) for b in bitlist), 2)