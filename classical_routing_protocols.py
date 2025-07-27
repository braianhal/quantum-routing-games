import random
import numpy as np
from routing_protocols import RoutingProtocol
from network_utils import Packet
from scipy.optimize import minimize
import metric_utils as mu


class ClassicalRoutingProtocol(RoutingProtocol):

    def play_round(self, N, possible_paths, packets):
        # Se itera por paquete.
        for packet in packets:
            packet.latency = 0
            
            # Enruta el paquete de acuerdo al protocolo dado.
            selected_path = self.select_path(N, possible_paths, packet)
            
            # Actualiza el camino actual (reduciendo el flujo del camino previamente elegido).
            if (packet.current_path is not None):
                N.update_path_flow(packet.current_path, -1)
            packet.current_path = selected_path
            # Incrementa el flujo de las aristas del camino elegido.
            N.update_path_flow(selected_path, 1)
            # Actualiza la latencia del paquete.
            package_latency = N.get_path_latency(selected_path)

        # Devuelve la red actualizada y las métricas de la ronda.
        metrics = mu.calculate_protocol_execution_metrics(N, packets)
        return N, metrics

    # Estrategia a jugar.
    def select_path(self, N, possible_paths, packet):
        pass


class RandomPathProtocol(ClassicalRoutingProtocol):
    
    # Estrategia mixta equiprobable entre todos los caminos posibles.
    def select_path(self, N, possible_paths, _):
        return random.choice(possible_paths)



class BestLatencyProtocol(ClassicalRoutingProtocol):
    
    # Estrategia pura que elige el mejor camino posible actual.
    def select_path(self, N, possible_paths, _):
        return min(possible_paths, key=lambda path: N.get_path_latency(path))


class OptimizableLatencyProtocol(ClassicalRoutingProtocol):

    def __init__(self, optimizations_per_round):
        self.optimizations_per_round = optimizations_per_round

    # Estrategia que minimza el costo esperado de acuerdo a las probabilidades de la estrategia mixta.
    def select_path(self, N, possible_paths, packet):
        n_paths = len(possible_paths)
        
        # Inicializa probabilidades aleatoriamente si es la primera vez.
        if ("p" not in packet.params):
            packet.params["p"] = np.random.dirichlet(np.ones(n_paths))

        # Latencia esperada.
        def expected_latency(p):
            return sum([p[i] * N.get_path_latency(possible_paths[i]) for i in range(n_paths)])

        # Minimización de latencia esperada en base a los parámetros.
        p = packet.params["p"]
        constraints = {'type': 'eq', 'fun': lambda x : np.sum(x) - 1} 
        bounds = [(0, 1)] * n_paths
        p = minimize(expected_latency, p, method='SLSQP', bounds=bounds, constraints=constraints, options={'maxiter': self.optimizations_per_round}).x
        packet.params["p"] = p

        # Devuelve un camino aleatorio elegido en base a la distribución de probabilidad.
        return possible_paths[np.random.choice(range(n_paths), p=p)]
        