##############################################################
# Estrategias utilizadas por los protocolos de enrutamiento. #
##############################################################

import utils.math as math

import numpy as np
import pennylane as qml


class Strategy:
    """ Clase base para las estrategias. """

    def update(self, N, selected_path_idx, payoff):
        """ 
            [Abstracto] 
            Actualiza la estrategia en base al estado actual de la red,
            el camino elegido y el pago obtenido de la ronda anterior. 
        """
        pass

    def get_params(self):
        """ Retorna los parámetros de la estrategia. """
        return self.params

    def get_classical_pure_strategy(self):
        """ 
            Obtiene la estrategia clásica pura (índice de camino elegido) en
            base a la aplicación de la estrategia actual.
            Sólo aplica si el protocolo es clásico.
        """
        pass

    def apply_to_quantum_circuit(self, base_qubit):
        """ Aplica la estrategia al circuito cuántico del protocolo. """
        pass

    def _apply_quantum_int_codification(self, base_qubit, number):
        """ 
            Codifica el número 'number' como un bitstring y lo aplica como operaciones
                I (0) y X (1) en el circuito cuántico del protocolo.
        """
        qubit = 0
        for bit in math.int_to_bitlist(number, self.n_qubits):
            if bit == 1:
                qml.PauliX(wires = base_qubit + qubit)
            qubit += 1


class PureStrategy(Strategy):

    def __init__(self, n_qubits, n_paths):
        self.n_qubits = n_qubits
        self.params = np.random.choice(range(n_paths))

    def update(self, N, _, payoff):
        """ 
            Actualiza la estrategia en base al pago obtenido.
                Si fue negativo, se elige alguno de los caminos con mínima 
                latencia de la red. En otro caso se mantiene el camino elegido.
        """
        if payoff < 0:
            self.params = self._get_min_latency_path_idx(N)

    def _get_min_latency_path_idx(self, N):
        """ Obtiene alguno de los caminos de mínima latencia de la red. """
        return np.random.choice(N.get_min_latency_path_idxs())

    def get_classical_pure_strategy(self):
        """ Función trivial, esta estrategia ya es una estrategia pura. """
        return self.params

    def apply_to_quantum_circuit(self, base_qubit):
        """ 
            Aplica el índice del camino codificado como puertas I y X 
                en el circuito cuántico del protocolo. 
        """
        selected_path_idx = self.params
        self._apply_quantum_int_codification(base_qubit, selected_path_idx)


class MixedStrategy(Strategy):
    """ Clase que modela las estrategias mixtas. """

    def __init__(self, alpha, n_qubits, n_paths):
        self.alpha = alpha
        self.n_qubits = n_qubits
        self.params = np.random.dirichlet(np.ones(n_paths))

    def update(self, _, selected_path_idx, payoff):
        """ 
            Actualiza la estrategia en base al camino elegido y su pago.
                Refuerza la probabilidad de obtener ese camino si su pago fue positivo,
                lo deja igual si fue 0, y la decrementa si fue negativo.
                Hace lo opuesto con el resto de los caminos.
        """
        n_params = len(self.params)
        for p in range(n_params):
            if p == selected_path_idx:
                # Refuerzo del camino elegido.
                variation = payoff * (self.alpha / 2)
            else:
                # Refuerzo opuesto del resto de los caminos.
                variation = -payoff * (self.alpha / (2 * (n_params-1)))
            self.params[p] += variation
        # Normaliza las probabilidades del vector.
        self.params = math.normalized_probs(self.params)

    def get_classical_pure_strategy(self):
        """ 
            Devuelve una estrategia clásica pura obtenida como muestra de la 
                distribución de probabilidad de la estrategia mixta.
        """
        return np.random.choice(range(len(self.params)), p=self.params)

    def apply_to_quantum_circuit(self, base_qubit):
        """ 
            Obtiene una estrategia pura como muestra de la distribución de probabilidad
                de la estrategia mixta y la aplica como operaciones I y X en el circuito
                del protocolo.
        """
        selected_path_idx = np.random.choice(range(len(self.params)), p = self.params)
        self._apply_quantum_int_codification(base_qubit, selected_path_idx)


class RotationsBasedStrategy(Strategy):
    """ Clase que modela las estrategias basadas en rotaciones de qubits. """

    def __init__(self, alpha, sigma, n_qubits, n_params_per_qubit):
        self.alpha = alpha
        self.sigma = sigma
        self.params = [[np.random.uniform(0, 2 * np.pi) for _ in range(n_params_per_qubit)] for _ in range(n_qubits)]
        self.perturbations = [[self._sample_perturbation() for _ in range(n_params_per_qubit)] for _ in range(n_qubits)]

    def update(self, _, __, payoff):
        """ 
            Actualiza los parámetros de la estrategia.
                Para cada qubit refuerza la perturbación anterior si su pago fue positivo, la mantiene igual si fue 0
                o la revierte si fue negativo. Luego aplica una nueva perturbación aleatoria. 
        """
        for q in range(len(self.params)):
            for p in range(len(self.params[q])):
                # Reforzar/castigar dirección de perturbación anterior.
                self.params[q][p] = self._get_updated_param(self.params[q][p], self.perturbations[q][p], payoff)
                # Configurar perturbación siguiente.
                self.perturbations[q][p] = self._sample_perturbation()
                self.params[q][p] = self._get_updated_param(self.params[q][p], self.perturbations[q][p])

    def _get_updated_param(self, param, perturbation, payoff = 1):
        """ 
            Devuelve el parámetro con la perturbación aplicada. 
                El resultado se limita entre [0;2pi).
        """
        return (param + perturbation * payoff * self.alpha) % (2 * np.pi)
    
    def _sample_perturbation(self):
        """ Obtiene una perturbación aleatoria basada en la distribución normal. """
        return np.random.normal(0, self.sigma)

    def apply_to_quantum_circuit(self, base_qubit):
        """ 
            Aplica la estrategia al circuito cuántico dependiendo del número de parámetros por qubit:
                - 1: la aplica como puertas RX.
                - 2: la aplica como puertas U2.
                - 3: la aplica como puertas U3.
        """
        qubit = 0
        for params in self.params:
            match params:
                case (theta, phi, alpha):
                    qml.U3(theta, phi, alpha, wires = base_qubit + qubit)
                case (theta, phi):
                    qml.U2(theta, phi, wires = base_qubit + qubit)
                case theta:
                    qml.RX(theta, wires = base_qubit + qubit)
            qubit += 1