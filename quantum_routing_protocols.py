import pennylane as qml
import quantum_utils as qu
import random
import numpy as np
from routing_protocols import RoutingProtocol
from network_utils import Packet
from scipy.optimize import minimize
import metric_utils as mu

class QuantumRoutingProtocol(RoutingProtocol):

    def play_round(self, N, possible_paths, packets):

        # Se define el circuito
        @qml.qnode(dev)
        def circuit(params):
            # Initial state |00>
            
            # Apply entangling operator J(γ)
            qu(gamma, range(n_paths))
            
            # Player strategies
            for p in params:
                if 
        
            # Measurement in computational basis
            return qml.sample(qml.PauliZ(0)), qml.sample(qml.PauliZ(1))
        
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

    def apply_strategy(self, N):
        pass

    
        

class MWProtocol(QuantumRoutingProtocol):

    def select_path(self, N, possible_paths, packet):
    

def mw(N, possible_paths, circuit):

def mw_circuit(n_paths):
    dev = qml.device("default.qubit", wires=range(n_paths), shots=1000)
    
    gamma = np.pi / 2
    
    