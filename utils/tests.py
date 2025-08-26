#########################################################
# Utilidades generación y ejecución de casos de prueba. #
#########################################################

import src.game_builder as gb

from . import math as math
from . import metric as mu
from .network import NetworkGenerator

import numpy as np


#----------------- Constantes ---------------------------------


QUBITS_LIMIT = 16
NETWORK_GENERATOR = NetworkGenerator()


#----------------- Generación de pruebas ----------------------

def get_specific_test_case(n, m):
    """ 
        Obtiene un caso de prueba para un juego de n x m. 
            Retorna la información de la red 'N' generada, 
            los 'n' paquetes, 'm' caminos y las métricas en 
            flujo óptimo 'opt'.
    """
    N = NETWORK_GENERATOR.generate_random_with_paths(m)
    opt = gb.opt(N, n).play()[1]
    return (N, n, m, opt) 

def get_test_case():
    """ Obtiene un caso de prueba aleatorio. """
    while True:
        n = np.random.randint(2, QUBITS_LIMIT + 1)
        m = np.random.randint(2, QUBITS_LIMIT + 1)
        if _valid_game_size(n, m):
            return get_specific_test_case(n, m)

def get_test_cases(n_cases):
    """ Obtiene 'n' casos de prueba aleatorios. """
    return [get_test_case() for _ in range(n_cases)]

def get_matrix_test_cases(n_tests_per_size):
    """ 
        Obtiene una matriz de casos de prueba para distintos valores de 
            'n' y 'm'. Para cada combinación de n x m, hay 'n_tests_per_size' casos.
    """
    test_cases = []
    for n in range(2, QUBITS_LIMIT+1):
        test_cases_n = []
        for m in range(2, QUBITS_LIMIT+1):
            if not _valid_game_size(n, m):
                continue
            test_cases_m = []
            for _ in range(n_tests_per_size):
                test_cases_m.append(get_specific_test_case(n, m))
            test_cases_n.append(test_cases_m)
        test_cases.append(test_cases_n)
    return test_cases

def get_possible_test_latencies():
    """ 
        Obtiene las posibles combinaciones de latencias en el rango de
            a in [1,2] y b in [0,1].
    """
    possible_latencies = []
    for a in range(1,3):
        for b in range(0,2):
            possible_latencies.append((a,b))
    return possible_latencies

def combinations_test_cases_3(n):
    """ 
        Genera casos de prueba para todas las posibles redes de 3 nodos y 2 caminos.
            n: cantidad de paquetes utilizados en la prueba.
    """
    possible_latencies = get_possible_test_latencies()
    test_cases = []
    for a_02, b_02 in possible_latencies:
        edge_02 = (0, 2, {"latency": (a_02,b_02)})
        for a_01, b_01 in possible_latencies:
            edge_01 = (0, 1, {"latency": (a_01,b_01)})
            for a_12, b_12 in possible_latencies:
                edge_12 = (1, 2, {"latency": (a_12,b_12)})
                N = NETWORK_GENERATOR.generate_based_on_definition(3, [edge_02, edge_01, edge_12])
                opt = gb.opt(N, n).play()[1]
                test_cases.append((N, n, 2, opt))
    return test_cases

def combinations_test_cases_4(n):
    """ 
        Genera casos de prueba para todas las posibles redes de 4 nodos y 2 caminos.
            (no se incluyen las de estructura de 3 nodos más un enlace extra).
    """
    possible_latencies = get_possible_test_latencies()
    test_cases = []
    for a_01, b_01 in possible_latencies:
        edge_01 = (0, 1, {"latency": (a_01,b_01)})
        for a_13, b_13 in possible_latencies:
            edge_13 = (1, 3, {"latency": (a_13,b_13)})
            for a_02, b_02 in possible_latencies:
                edge_02 = (0, 2, {"latency": (a_02,b_02)})
                for a_23, b_23 in possible_latencies:
                    edge_23 = (2, 3, {"latency": (a_23,b_23)})
                    N = NETWORK_GENERATOR.generate_based_on_definition(3, [edge_01, edge_13, edge_02, edge_23])
                    opt = gb.opt(N, n).play()[1]
                    test_cases.append((N, n, 2, opt))
    return test_cases

def combinations_test_cases_5(n):
    """ 
        Genera casos de prueba para todas las posibles redes de 5 nodos y 2 caminos.
            (no se incluyen las de estructura de 3 nodos más un enlace extra).
    """
    possible_latencies = get_possible_test_latencies()
    test_cases = []
    for a_01, b_01 in possible_latencies:
        edge_01 = (0, 1, {"latency": (a_01,b_01)})
        for a_14, b_14 in possible_latencies:
            edge_14 = (1, 4, {"latency": (a_14,b_14)})
            for a_02, b_02 in possible_latencies:
                edge_02 = (0, 2, {"latency": (a_02,b_02)})
                for a_23, b_23 in possible_latencies:
                    edge_23 = (2, 3, {"latency": (a_23,b_23)})
                    for a_34, b_34 in possible_latencies:
                        edge_34 = (3, 4, {"latency": (a_34,b_34)})
                        N = NETWORK_GENERATOR.generate_based_on_definition(3, [edge_01, edge_14, edge_02, edge_23, edge_34])
                        opt = gb.opt(N, n).play()[1]
                        test_cases.append((N, n, 2, opt))
    return test_cases


#----------------- Ejecución de pruebas ----------------------


def execute_regular_test(rounds, test_case, protocols):
    """ 
        Ejecuta una prueba normal.
            Ejecución de un 'test_case' por 'rounds' rondas, para cada 
            uno de los 'protocolos', compilando las métricas por ronda.
    """
    execution_metrics = []
    N, n, _, optimal = test_case
    for protocol in protocols:
        _, metrics = gb.game(N, n, rounds, protocol).play()
        game_metrics = mu.get_game_metrics(metrics, optimal)
        execution_metrics.append(game_metrics)
    return execution_metrics

def execute_hyperparameter_test(rounds, test_cases, protocol_providers, hyperparameter_range):
    """ 
        Ejecuta una prueba de hiperparámetros.
            Compila la información media por cada protocolo para 
            cada valor del rando del hiperparámetro.
            rounds: cantidad de rondas a jugar por prueba.
            test_cases: los casos de prueba para cada combinación de (protocolo, valor de hiperparámetro).
            protocol_providers: las funciones que devuelven los protocolos a utilizar para cada valor del hiperparámetro.
            hyperparameter_range: el rango de valores del hiperparámetro a probar.
    """
    execution_metrics = []
    for protocol_provider in protocol_providers:
        protocol_metrics = []
        for hypterparameter in hyperparameter_range:
            tests_metrics = []
            for (N, n, m, optimal) in test_cases:
                protocol = protocol_provider(hypterparameter)
                _, metrics = gb.game(N, n, rounds, protocol).play()
                tests_metrics.append(mu.get_single_test_metrics(metrics, optimal))
            protocol_metrics.append(mu.get_mean_test_metrics(tests_metrics))
        execution_metrics.append(protocol_metrics)
    return execution_metrics

def execute_matrix_test(rounds, test_cases, protocols):
    """ 
        Ejecuta una prueba para generar una matriz de resultados para distintos valores de n x m.
            Compila la información media por cada protocolo para cada valor de n y m.
            rounds: cantidad de rondas a jugar por prueba.
            test_cases: los casos de prueba para cada combinación de n y m.
            protocols: los protocolos a utilizar para cada prueba.
    """
    execution_metrics = []
    for i in range(len(test_cases)):
        execution_metrics_n = []
        for j in range(len(test_cases[i])):
            execution_metrics_m = []
            test_cases_ij = test_cases[i][j]
            for protocol in protocols:
                protocol_metrics = []
                for (N, n, m, optimal) in test_cases_ij:
                    _, metrics = gb.game(N, n, rounds, protocol).play()
                    protocol_metrics.append(mu.get_single_test_metrics(metrics, optimal))
                execution_metrics_m.append(mu.get_mean_test_metrics(protocol_metrics))
            execution_metrics_n.append(execution_metrics_m)
        execution_metrics.append(execution_metrics_n)
    return execution_metrics

def execute_combinations_test(rounds, test_cases, tests_per_case, protocols):
    """ 
        Ejecuta una prueba de todas las posibles combinaciones de redes
            de v nodos y 2 caminos.
            rounds: cantidad de rondas a jugar por prueba.
            test_cases: los casos de prueba.
            tests_per_case: la cantidad de veces que se ejecuta el test por cada caso.
            protocols: los protocolos a utilizar para cada prueba.
    """
    execution_metrics = []
    for N, n, _, optimal in test_cases:
        test_case_metrics = []
        for protocol in protocols:
            protocol_metrics = []
            for _ in range(tests_per_case):
                _, metrics = gb.game(N, n, rounds, protocol).play()
                protocol_metrics.append(mu.get_single_test_metrics(metrics, optimal))
            test_case_metrics.append(mu.get_mean_test_metrics(protocol_metrics))
        execution_metrics.append(test_case_metrics)
    return execution_metrics


#----------------- Auxiliares -------------------------

def _valid_game_size(n, m):
    """ 
        Determina si el tamaño del juego es válido de acuerdo
            a la limitación en el número de qubits.
    """
    return n * math.ceil_log2(m) <= QUBITS_LIMIT
