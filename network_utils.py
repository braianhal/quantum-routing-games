import networkx as nx
import random
import matplotlib.pyplot as plt

# Red (subclase de digrafo).
class Network(nx.DiGraph):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.possible_paths = []

    # Obtiene los nodos de la red agrupados en capas de acuerdo
    # al tamaño del camino mínimo de los nodos precendentes.
    def get_precedence_layers(self):
        layers = {}
        for n in self.nodes():
            predecesors = len(nx.shortest_path(self, source=0, target=n))
            if predecesors in layers:
                layers[predecesors].append(n)
            else:
                layers[predecesors] = [n]
        return layers

    # Devuelve la latencia de la arista dada.
    def get_edge_latency(self, u, v):
        edge = self[u][v]
        a,b = edge['latency']
        x = edge['flow']
        return a + b*x

    # Devuelve el costo de la arista dada flujo * latencia).
    def get_edge_cost(self, u, v):
        return self.get_edge_latency(u, v) * self[u][v]["flow"]

    # Devuelve el costo de un camino (suma de costos de sus aristas).
    def get_path_cost(self, path):
        return sum([self.get_edge_cost(path[i], path[i+1]) for i in range(len(path)-1)])

    # Devuelve la latencia de un camino (suma de latencias de sus aristas).
    def get_path_latency(self, path):
        return sum([self.get_edge_latency(path[i], path[i+1]) for i in range(len(path)-1)])

    # Devuelve el costo total de la red.
    def get_total_cost(self):
        return sum(self.get_edge_cost(u, v) for u, v in self.edges())

    # Devuelve los caminos posibles desde el nodo source al target.
    def get_all_possible_paths(self):
        if len(self.possible_paths) == 0:
            self.possible_paths = list(nx.all_simple_paths(self, source=0, target=len(self.nodes())-1))
        return self.possible_paths

    # Vuelve a cero el flujo de la red.
    def reset_flow(self):
        for _, _, d in self.edges(data = True):
            d['flow'] = 0

    # Devuelve una lista con los flujos de todas las aristas.
    def get_edge_flows(self):
        return [d["flow"] for _,_,d in self.edges(data = True)]

    # Actualiza el flujo del camino elegido de acuerdo al factor dado.
    def update_path_flow(self, path, factor):
        for n in range(len(path)-1):
            u, v = path[n], path[n+1]
            self[u][v]["flow"] += factor

# Clase para generar redes aleatorias.
class NetworkGenerator:

    # Genera una red aleatoria del tamaño dado.
    def generate_random(self, n_nodes):
        N = Network()
        
        nodes = range(n_nodes)
        N.add_nodes_from(range(n_nodes))

        for n in nodes[:-1]:
            N.add_edge(n, random.choice(nodes[n+1:]))
        for n in nodes[1:]:
            N.add_edge(random.choice(nodes[:n]), n)
    
        for u, v in N.edges():
            N[u][v]["latency"] = (random.randint(0,10), random.randint(0,10))
        
        return N

# Clase para dibujar las redes.
class NetworkDrawer:

    # Obtiene un par (x,y) para graficar los nodos en función de su capa.
    # de precedencia.
    def _get_node_position(self, n, layers, layers_x_pos):
        layer = -1
        nodes_in_layer = []
        for l, nodes in layers.items():
            if n in nodes:
                layer = l
                nodes_in_layer = nodes
        x = layers_x_pos.index(layer)
        y = nodes_in_layer.index(n) - len(nodes_in_layer)/2
        return (x,y)

    # Dibuja la red mostrando en las aristas el atributo dado.
    def draw(self, N, attribute_to_draw):    
        layers = N.get_precedence_layers()
        layers_x_pos = sorted(layers.keys())
        pos = { n: self._get_node_position(n, layers, layers_x_pos) for n in N.nodes() }
        
        special_nodes = {0, len(N.nodes())-1}
        node_colors = [ 'orange' if node in special_nodes else 'skyblue' for node in N.nodes() ]

        nx.draw(N, pos, with_labels=True, node_color=node_colors, node_size=1500, arrows=True)

        edge_labels = { 
            (u,v): d[attribute_to_draw] for u, v, d in N.edges(data=True)
        }
        nx.draw_networkx_edge_labels(N, pos, edge_labels=edge_labels, font_size=10)
        
        plt.title("Red")
        plt.show()

class Packet:

    def __init__(self):
        self.latency = 0
        self.current_path = None
        self.params = {}
