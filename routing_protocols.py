import metric_utils as mu
import cvxpy as cp
import numpy as np
from network_utils import Packet

class RoutingProtocol:

    def init(self, N, packets, possible_paths):
        pass

    def select_paths(self, N, packets, possible_paths):
        pass

    def update_strategies(self, N, packets, possible_paths):
        pass