########################################
# Protocolos de enrutamiento clásicos. #
########################################

from .routing_protocols import RoutingProtocol

import numpy as np


class ClassicalRoutingProtocol(RoutingProtocol):
    """ 
        Clase que modela los protocolos de enrutamiento clásicos.
    """

    def init(self, N, packets, possible_paths):
        """ Inicializa las estrategias de los paquetes en base al generador de estrategias. """
        for packet in packets:
            packet.strategy = self.strategy_provider(n_paths = len(possible_paths))

    def select_paths(self, _, packets, possible_paths):
        """ 
            Selecciona un camino para cada paquete en base a los índices obtenidos 
                como estrategias puras clásicas en base a las estrategias realmente utilizadas. 
        """
        paths = []
        for packet in packets:
            selected_path_idx = packet.strategy.get_classical_pure_strategy()
            paths.append(possible_paths[selected_path_idx])
        return paths
