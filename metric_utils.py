import numpy as np

def calculate_protocol_execution_metrics(N, packets = []):
    metrics = {}

    # Costo total.
    metrics["total_cost"] = N.get_total_cost()

    # Flujos de la red.
    edges_flows = N.get_edge_flows()
    metrics["edge_flows_avg"] = np.mean(edges_flows)
    metrics["edge_flows_stdev"] = np.std(edges_flows)
    metrics["edge_flows_max"] = np.max(edges_flows)
    metrics["edge_flows_min"] = np.min(edges_flows)

    # Latencia de paquetes.
    if (len(packets) > 0):
        packet_latencies = [p.latency for p in packets]
        metrics["packet_latency_avg"] = np.mean(packet_latencies)
        metrics["packet_latency_stdev"] = np.std(packet_latencies)
        metrics["packet_latency_max"] = np.max(packet_latencies)
        metrics["packet_latency_min"] = np.min(packet_latencies)

    return metrics