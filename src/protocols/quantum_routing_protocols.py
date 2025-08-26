#########################################
# Protocolos de enrutamiento cuánticos. #
#########################################

from .routing_protocols import RoutingProtocol

import utils.lists as lu
import utils.math as math
from utils.network import Packet
import utils.quantum as qu

import numpy as np
import pennylane as qml


class QuantumRoutingProtocol(RoutingProtocol):
    """ 
        Clase que modela los protocolos de enrutamiento cuánticos.
    """

    def __init__(self, 
                 name = None,
                 strategy_provider = None,
                 gamma = None, 
                 has_disentanglement = None):
        super().__init__(name, strategy_provider)
        self.gamma = gamma
        self.has_disentanglement = has_disentanglement

    def init(self, _, packets, possible_paths):
        """ 
            Inicializa el protocolo, esto inclute:
                - inicializar el circuito cuántico del protocolo.
                - inicializar las estrategias de los paquetes en base al generador de estrategias. 
        """
        self.n_possible_paths = len(possible_paths)
        self.n_qubits_per_packet = math.ceil_log2(self.n_possible_paths)
        self.qubits = range(len(packets) * self.n_qubits_per_packet)
        self.dev = qml.device("default.qubit", wires=len(self.qubits), shots=1)
        self.qnode = qml.QNode(self._circuit, self.dev)
        for packet in packets:
            packet.strategy = self.strategy_provider(n_paths = self.n_possible_paths, n_qubits = self.n_qubits_per_packet)

    def _circuit(self, strategies):
        """ Circuito cuántico del protocolo. """
        
        # Puerta de entrelazamiento J.
        qu.J(self.gamma, self.qubits)

        qml.Barrier(wires = self.qubits)

        # Estrategias codificadas.
        qubit = 0
        for strategy in strategies:
            strategy.apply_to_quantum_circuit(qubit)
            qubit += self.n_qubits_per_packet

        qml.Barrier(wires = self.qubits)

        # Puerta de desentrelazamiento J daga (si es necesaria).
        if self.has_disentanglement:
            qu.J(-self.gamma, self.qubits)

        qml.Barrier(wires = self.qubits)

        # Devuelve el resultado de 1 shot.
        return qml.sample(wires=self.qubits)

    def select_paths(self, _, packets, possible_paths):
        """ 
            Selecciona los caminos efectivamente elegidos por cada paquete 
                en base al output del circuito cuántico.
                Asigna una penalización al paquete si no obtuvo un camino válido
                tras la medición del circuito.
        """
        output = self.qnode([packet.strategy for packet in packets])
        paths = []
        for packet, o in zip(packets, lu.group(output, self.n_qubits_per_packet)):
            path_idx, penalty = self._circuit_output_to_path(o)
            paths.append(possible_paths[path_idx])
            packet.penalty = penalty
        return paths

    def _circuit_output_to_path(self, output):
        """ 
            Convierte el output del circuito en un índice de camino 
                Retorna una penalización al paquete si el índice de camino no es válido
                y le asigna uno válido aleatoriamente.
        """
        path_idx = math.bitlist_to_int(output)
        penalty = False
        if path_idx >= self.n_possible_paths:
            path_idx = np.random.choice(range(self.n_possible_paths))
            penalty = True
        return (path_idx, penalty)

    def draw(self, N, n_packets, strategies):
        """ Dibuja el circuito del protocolo usando los parámetros dados. """
        self.init(N, [Packet() for _ in range(n_packets)], N.get_all_possible_paths())
        print(qml.draw_mpl(self.qnode)(strategies))
