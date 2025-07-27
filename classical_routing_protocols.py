import random
import numpy as np
from routing_protocols import RoutingProtocol
from network_utils import Packet
from scipy.optimize import minimize
import metric_utils as mu


class BestLatencyProtocol(RoutingProtocol):

    # Inicializa estrategias aleatoriamente.
    def init(self, _, packets, possible_paths):
        for packet in packets:
            packet.strategy = random.choice(possible_paths)

    # Como son estrategias puras, devuelve el camino elegido.
    def select_paths(self, _, packets, __):
        return [packet.strategy for packet in packets]

    # Elige el camino óptimo individual de cada paquete.
    def update_strategies(self, N, packets, possible_paths):
        for packet in packets:
            packet.strategy = self._best_latency_path(N, packet, possible_paths)
    
    def _best_latency_path(self, N, packet, possible_paths):
        def latency_variation(path):
            N.move_flow_unit(packet.path, path)
            new_latency = N.get_path_latency(path)
            N.move_flow_unit(path, packet.path) # rollback
            return new_latency - packet.latency
        return min(possible_paths, key=lambda path: latency_variation(path))


class OptimizableLatencyProtocol:

    def __init__(self, optimizations_per_round):
        self.optimizations_per_round = optimizations_per_round

    # Inicializa estrategias aleatoriamente.
    def init(self, _, packets, possible_paths):
        for packet in packets:
            packet.strategy = np.random.dirichlet(np.ones(len(possible_paths)))

    # Devuelve un  camino de acuerdo a la distribución de probabilidades de la estrategia mixta.
    def select_paths(self, _, packets, possible_paths):
        return [possible_paths[np.random.choice(range(len(possible_paths), p=packet.strategy)] for packet in packets]

    # Optimiza la latencia esperada.
    def update_strategies(self, N, packets, possible_paths):
        for packet in packets:
            packet.strategy = self._optimized_probabilities(N, packet, possible_paths)
    
    def _optimized_probabilities(self, N, packet, possible_paths):
        def expected_latency(probs):
            return sum([p[i] * self._get_path_potential_latency(possible_paths[i]) for i in range(n_paths)])
        
        constraints = {'type': 'eq', 'fun': lambda x : np.sum(x) - 1} 
        bounds = [(0, 1)] * len(possible_paths)
        return minimize(expected_latency, packet.strategy, method='SLSQP', bounds=bounds, 
                        constraints=constraints, options={'maxiter': self.optimizations_per_round}).x

    def _get_path_potential_latency(self, N, packet, path):
        N.move_flow_unit(packet.path, path)
        new_latency = N.get_path_latency(path)
        N.move_flow_unit(path, packet.path) # rollback
        return new_latency

    # Estrategia que minimza el costo esperado de acuerdo a las probabilidades de la estrategia mixta.
    def select_path(self, N, possible_paths, packet):

        # Latencia esperada.
        def expected_latency(p):
            for 
            return sum([p[i] * N.get_path_latency(possible_paths[i]) for i in range(n_paths)])
        