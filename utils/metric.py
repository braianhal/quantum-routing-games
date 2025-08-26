############################################################################
# Utilidades para cálculos las métricas de las ejecuciones y experimentos. #
############################################################################

import numpy as np


#----------------- Constantes ---------------------------------


# Nombres de las métricas básicas utilizadas en todos los juegos.
METRICS = [("poa", r"$\kappa$"),
           ("expected_packet_latency", r"$E(l)$"),
           ("packet_latency_max", r"$\max(l_i)$"),
           ("edge_flows_max", r"$\max(f_e)$")]

# Nombres de las medias de METRICS.
MEAN_METRICS = [("mean_" + m_name, m_label) for (m_name, m_label) in METRICS]


#----------------- Métricas de ejecución de los juegos --------


def calculate_protocol_execution_metrics(N, packets = []):
    """ 
        Calcula las métricas de ejecución de una ronda del protocolo 
            en base a la red 'N' y los paquetes 'packets'.
    """
    metrics = {}

    # Costo total.
    metrics["total_cost"] = N.get_total_cost()

    # Flujos de la red.
    edges_flows = N.get_edge_flows()
    metrics["edge_flows_max"] = np.max(edges_flows)

    # Latencia de paquetes.
    if (len(packets) > 0):
        packet_latencies = [p.latency for p in packets]
        metrics["packet_latency_max"] = np.max(packet_latencies)
        metrics["expected_packet_latency"] = N.get_expected_latency()

    return metrics

def compute_poa(current_cost, optimal_cost):
    """ Calcula el precio de anarquía. """
    return current_cost/optimal_cost


#----------------- Métricas de los experimentos --------------


def get_game_metrics(metrics, optimal):
    """ Obtiene el diccionario de métricas del juego. """
    return {"poa": [compute_poa(m["total_cost"], optimal["total_cost"]) for m in metrics],
            "expected_packet_latency": [m["expected_packet_latency"] for m in metrics],
            "packet_latency_max": [m["packet_latency_max"] for m in metrics],
            "edge_flows_max": [m["edge_flows_max"] for m in metrics]}

def get_single_test_metrics(metrics, optimal):
    """ Obtiene el diccionario de métricas del juego para un experimento de una única ejecución. """
    mean_cost = np.mean([m["total_cost"] for m in metrics])
    mean_poa = compute_poa(mean_cost, optimal["total_cost"])
    mean_expected_packet_latency = np.mean([m["expected_packet_latency"] for m in metrics])
    mean_packet_latency_max = np.mean([m["packet_latency_max"] for m in metrics])
    mean_edge_flows_max = np.mean([m["edge_flows_max"] for m in metrics])
    return {"mean_poa": mean_poa,
            "mean_expected_packet_latency": mean_expected_packet_latency,
            "mean_packet_latency_max": mean_packet_latency_max,
            "mean_edge_flows_max": mean_edge_flows_max}

def get_mean_test_metrics(test_metrics):
    """ Obtiene el diccionario de métricas del juego para un experimento que requiere las medias de las métricas. """
    mean_metrics = {}
    for key_metric in ["mean_poa", "mean_expected_packet_latency", "mean_packet_latency_max", "mean_edge_flows_max"]:
        mean_metrics[key_metric] = np.mean([m[key_metric] for m in test_metrics])
    return mean_metrics