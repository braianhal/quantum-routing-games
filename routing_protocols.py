import metric_utils as mu
import cvxpy as cp
import numpy as np
from network_utils import Packet

class RoutingProtocol:

    def run(self, N, packets_to_send, rounds=1):
        # Reinicia el estado de la red.
        N.reset_flow()

        # Inicializa los paquetes.
        packets = [Packet() for _ in range(packets_to_send)]
        
        # Calcula los caminos posibles.
        possible_paths = N.get_all_possible_paths()
        
        # Ejecuta de a una ronda por vez actualizando la red y acumulando las métricas.
        metrics = []
        for _ in range(rounds):
            N, round_metrics = self.play_round(N, possible_paths, packets)
            metrics.append(round_metrics)

        # Retorna la red y las métricas.
        return N, metrics

    # Abstracto.
    def play_round(self, N, possible_paths, packets):
        pass

class OptimalFlowProtocol(RoutingProtocol):

    def play_round(self, N, possible_paths, packets):
        # Definir caminos posibles y sus variables de optimización asociadas
        path_vars = [cp.Variable(integer=True) for _ in possible_paths]
    
        # Definir constraints para que la demanda total sea satisfecha
        # y para que las variables sean necesariamente >= 0
        constraints = [cp.sum(path_vars) == len(packets)]
        for var in path_vars:
            constraints.append(var >= 0)
    
        # Optimizar variables en base a minimizar el costo total
        total_cost_expr = 0
        for u,v,d in N.edges(data = True):
            edge_flow = 0
            for i, path in enumerate(possible_paths):
                for j in range(len(path)-1):
                    if (path[j] == u and path[j+1] == v):
                        edge_flow += path_vars[i]
                        break
            a,b = d['latency']
            total_cost_expr += (a * edge_flow + b * edge_flow**2)
        problem = cp.Problem(cp.Minimize(total_cost_expr), constraints)
        problem.solve(solver=cp.ECOS_BB)
    
        # Calcular flujo óptimo
        for i, path in enumerate(possible_paths):
            path_flow = np.round(path_vars[i].value)
            for j in range(len(path)-1):
                N[path[j]][path[j+1]]["flow"] += path_flow

        # Retornar la red con el flujo óptimo y las métricas asociadas
        metrics = mu.calculate_protocol_execution_metrics(N)
        return N, metrics