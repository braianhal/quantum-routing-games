#####################################################################################
# Funciones que permiten construir los juegos junto con sus parámetros y protocolos #
#####################################################################################

from .protocols.classical_routing_protocols import ClassicalRoutingProtocol
from .protocols.quantum_routing_protocols import QuantumRoutingProtocol
from .protocols.strategies import PureStrategy, MixedStrategy, RotationsBasedStrategy
from .routing_games import RoutingGame, OptimalFlowRoutingGame

import numpy as np


#----------------- Juego ---------------------------------


def opt(N, n):
    """ Construye un juego que calcula el flujo óptimo. """
    return OptimalFlowRoutingGame(N, n)

def game(N, n, r, P):
    """ Construye un juego genérico. """
    return RoutingGame(N, n, r, P)


#----------------- Protocolos ---------------------------------


def cp():
    """ Construye el protocolo clásico puro (CP). """
    return ClassicalRoutingProtocol(
        name = "CP", 
        strategy_provider = _psp())

def cm(alpha = 0.35):
    """ Construye el protocolo clásico mixto (CM). """
    return ClassicalRoutingProtocol(
        name = "CM", 
        strategy_provider = _msp(alpha))

def mwp(gamma = np.pi/16):
    """ Construye el protocolo cuántico MW puro (MWP). """
    return QuantumRoutingProtocol(
        name = "MWP", 
        strategy_provider = _psp(),
        gamma = gamma, 
        has_disentanglement = False)

def mwm(gamma = np.pi/16, alpha = 0.35):
    """ Construye el protocolo cuántico MW mixto (MWM). """
    return QuantumRoutingProtocol(
        name = "MWM", 
        strategy_provider = _msp(alpha),
        gamma = gamma, 
        has_disentanglement = False)

def ewl(gamma = (7/16)*np.pi, alpha = 0.8, sigma = 1, n_params_per_qubit = 1):
    """ Construye el protocolo cuántico EWL. """
    return QuantumRoutingProtocol(
        name = "EWL", 
        strategy_provider = _rbsp(alpha, sigma, n_params_per_qubit),
        gamma = gamma, 
        has_disentanglement = True)


#----------------- Estrategias ---------------------------------


def _psp():
    """ Construye un generador de estrategias puras. """
    return lambda n_paths = None, n_qubits = None : PureStrategy(n_qubits, n_paths)

def _msp(alpha):
    """ Construye un generador de estrategias mixtas. """
    return lambda n_paths = None, n_qubits = None : MixedStrategy(alpha, n_qubits, n_paths)

def _rbsp(alpha, sigma, n_params_per_qubit):
    """ Construye un generador de estrategias cuánticas basadas en rotaciones. """
    return lambda n_paths = None, n_qubits = None : RotationsBasedStrategy(alpha, sigma, n_qubits, n_params_per_qubit)
