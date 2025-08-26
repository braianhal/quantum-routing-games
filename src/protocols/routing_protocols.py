#################################################
# Clase base de los protocolos de enrutamiento. #
#################################################

import numpy as np


class RoutingProtocol:
    """ Clase base de los protocolos de enrutamiento. """

    # Pago asociado a una penalización.
    PENALTY_PAYOFF = -2

    def __init__(self, name=None, strategy_provider=None):
        self.name = name
        self.strategy_provider = strategy_provider

    def get_name(self):
        """ Devuelve el nombre del protocolo. """
        return self.name

    def init(self, N, packets, possible_paths):
        """ [Abstracto] Inicializa el protocolo. """
        pass

    def select_paths(self, N, packets, possible_paths):
        """ [Abstracto] Selecciona un camino para cada paquete en base al estado actual del juego. """
        pass

    def update_strategies(self, N, packets, possible_paths):
        """ Actualiza las estrategias de los jugadores/paquetes en base al pago obtenido. """
        for packet in packets:
            packet.strategy.update(N, possible_paths.index(packet.path), self._get_packet_payoff(N, packet))

    def _get_packet_payoff(self, N, packet):
        """ 
            Obtiene el pago asociado a un paquete. 
                Si no hay penalización, esto es: sg(E[l]-l_i).
        """
        if packet.penalty:
            return RoutingProtocol.PENALTY_PAYOFF
        else:
            return np.sign(N.get_expected_latency() - packet.latency)