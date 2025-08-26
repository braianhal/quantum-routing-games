#####################################################
# Clases principales de los juegos de enrutamiento. #
#####################################################

import utils.metric as mu
from utils.network import Packet

import cvxpy as cp
import numpy as np


class RoutingGame:
    """ 
        Clase que modela el juego de enrutamiento.
    """

    def __init__(self, N, packets_to_send, rounds=1, protocol=None):
        self.N = N
        self.possible_paths = self.N.get_all_possible_paths()
        self.packets = [Packet() for _ in range(packets_to_send)]
        self.rounds = rounds
        self.protocol = protocol

    def play(self):
        """ 
            Ejecuta el juego de enrutamiento con los parámetros del constructor.
        """
        
        # A. Reinicialización de la red.
        self.N.reset_flow()

        # B. Inicialización del protocolo.
        self.protocol.init(self.N, self.packets, self.possible_paths)
        
        # C. Ejecución de las rondas (actualización de red y métricas).
        metrics = []
        for _ in range(self.rounds):
            round_metrics = self._play_round()
            metrics.append(round_metrics)

        # D. Retorno de la red actualizada y las métricas.
        return self.N, metrics

    def _play_round(self):
        """ 
            Ejecuta una ronda del juego de enrutamiento.
        """
        
        # C.1. Cálculo de caminos efectivamente elegidos.
        selected_paths = self.protocol.select_paths(self.N, self.packets, self.possible_paths)

        # C.2. Actualización del flujo de la red y latencia de paquetes.
        for packet, selected_path in zip(self.packets, selected_paths):
            self.N.move_flow_unit(packet.path, selected_path)
            packet.path = selected_path
            packet.latency = self.N.get_path_latency(selected_path)

        # C.3. Actualización de estrategias.
        self.protocol.update_strategies(self.N, self.packets, self.possible_paths)

        # C.4. Cálculo de métricas.
        return mu.calculate_protocol_execution_metrics(self.N, self.packets)


class OptimalFlowRoutingGame(RoutingGame):
    """ 
        Clase que modela un juego de enrutamiento que calcula manualmente el flujo óptimo.
    """

    def play(self):
        """ 
            Ejecuta el algoritmo de optimización que permite calcular el flujo óptimo.
        """
        
        # A. Reinicialización de la red.
        self.N.reset_flow()
        
        # B. Definir las variables a minimizar y sus constraints.
        path_vars = [cp.Variable(integer=True) for _ in self.possible_paths]
        constraints = [cp.sum(path_vars) == len(self.packets)]
        for var in path_vars:
            constraints.append(var >= 0)
    
        # C. Optimizar variables en base a minimizar el costo total.
        total_cost_expr = 0
        for u,v,d in self.N.edges(data = True):
            edge_flow = 0
            for i, path in enumerate(self.possible_paths):
                for j in range(len(path)-1):
                    if (path[j] == u and path[j+1] == v):
                        edge_flow += path_vars[i]
                        break
            a,b = d['latency']
            total_cost_expr += (a * edge_flow + b * edge_flow**2)
        problem = cp.Problem(cp.Minimize(total_cost_expr), constraints)
        problem.solve(solver=cp.ECOS_BB)
    
        # D. Actualizar red con el flujo óptimo.
        for i, path in enumerate(self.possible_paths):
            path_flow = np.round(path_vars[i].value)
            for j in range(len(path)-1):
                self.N[path[j]][path[j+1]]["flow"] += path_flow

        # E. Retorno de la red actualizada y las métricas.
        metrics = mu.calculate_protocol_execution_metrics(self.N)
        return self.N, metrics
