##########################
# Utilidades para redes. #
##########################

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import random


#----------------- Red ---------------------------------


class Network(nx.DiGraph):
    """ 
        Clase extensión de un grafo dirigido que almacena la información 
            de las redes para los juegos.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.possible_paths = []

    def get_precedence_layers(self):
        """ 
            Obtiene los nodos de la red agrupados en capas de acuerdo
                al tamaño del camino mínimo de los nodos precendentes.
        """
        layers = {}
        for n in self.nodes():
            predecesors = len(nx.shortest_path(self, source=0, target=n))
            if predecesors in layers:
                layers[predecesors].append(n)
            else:
                layers[predecesors] = [n]
        return layers

    def get_all_possible_paths(self):
        """ Devuelve los caminos posibles desde el nodo origen al destino. """
        if len(self.possible_paths) == 0:
            self.possible_paths = list(nx.all_simple_paths(self, source=0, target=len(self.nodes())-1))
        return self.possible_paths

    def get_edge_flows(self):
        """ Devuelve una lista con los flujos de todas las aristas. """
        return [d["flow"] for _,_,d in self.edges(data = True)]

    def get_path_flow(self, path):
        """ Devuelve el flujo de un camino (suma del flujo de sus aristas). """
        return min([self[path[i]][path[i+1]]['flow'] for i in range(len(path)-1)])
    
    def update_path_flow(self, path, factor):
        """ Actualiza el flujo del camino elegido de acuerdo al factor dado. """
        for n in range(len(path)-1):
            u, v = path[n], path[n+1]
            self[u][v]["flow"] += factor

    def move_flow_unit(self, old_path, new_path):
        """ 
            Mueve una unidad de flujo de un camino a otro. 
                Si el primer camino no existe, solo agrega el flujo en el segundo.
        """
        if (old_path is not None):
            self.update_path_flow(old_path, -1)
        self.update_path_flow(new_path, 1)

    def reset_flow(self):
        """ Vuelve a cero el flujo de la red. """
        for _, _, d in self.edges(data = True):
            d['flow'] = 0
    
    def get_edge_latency(self, u, v):
        """ Devuelve la latencia de la arista dada. """
        edge = self[u][v]
        a,b = edge['latency']
        x = edge['flow']
        return a + b*x

    def get_path_latency(self, path):
        """ Devuelve la latencia de un camino (suma de latencias de sus aristas). """
        return sum([self.get_edge_latency(path[i], path[i+1]) for i in range(len(path)-1)])

    def get_expected_latency(self):
        """ Devuelve la latencia esperada de la red (E[l]). """
        total_latency = total_flow = 0
        for path in self.possible_paths:
            path_flow = self.get_path_flow(path)
            total_latency += self.get_path_latency(path) * path_flow
            total_flow += path_flow
        return total_latency / total_flow

    def get_min_latency_path_idxs(self):
        """ Obtiene los caminos con mínima latencia de la red. """
        min_latency = np.inf
        min_latency_path_idxs = []
        for i in range(len(self.possible_paths)):
            path = self.possible_paths[i]
            path_latency = self.get_path_latency(path)
            if (path_latency == min_latency):
                min_latency_path_idxs.append(i)
            elif (path_latency < min_latency):
                min_latency_path_idxs.append(i)
                min_latency = path_latency
        return min_latency_path_idxs
    
    def get_edge_cost(self, u, v):
        """ Devuelve el costo de la arista dada (flujo * latencia). """
        return self.get_edge_latency(u, v) * self[u][v]["flow"]
    
    def get_total_cost(self):
        """ Devuelve el costo total de la red. """
        return sum(self.get_edge_cost(u, v) for u, v in self.edges())
    

#----------------- Generación de redes -------------------------


class NetworkGenerator:
    """ 
        Clase que permite la generación de redes.
    """
    
    def generate_random(self, n_nodes):
        """ Genera una red aleatoria con la cantidad de nodos dada. """
        N = Network()

        # Nodos.
        nodes = range(n_nodes)
        N.add_nodes_from(range(n_nodes))

        # Aristas aleatorias.
        for n in nodes[:-1]:
            N.add_edge(n, random.choice(nodes[n+1:]))
        for n in nodes[1:]:
            N.add_edge(random.choice(nodes[:n]), n)

        # Funciones de latencia aleatorias.
        for u, v in N.edges():
            N[u][v]["latency"] = (random.randint(1,5), 
                                  random.randint(0,5))
        
        return N

    def generate_random_with_paths(self, n_paths):
        """ Genera una red aleatoria con la cantidad de caminos dada. """
        paths = 0
        possible_nodes = range(int(np.floor(n_paths/2))+1, n_paths*3)
        # Itera generando redes aleatorias hasta conseguir la deseada.
        while paths != n_paths:
            N = self.generate_random(random.choice(possible_nodes))
            paths = len(N.get_all_possible_paths())
        return N

    def generate_based_on_definition(self, n_nodes, edges_info):
        """ Genera una red basada en la definición de sus nodos y aristas. """
        N = Network()
        N.add_nodes_from(range(n_nodes))
        N.add_edges_from(edges_info)
        return N
    

#----------------- Gráfico de redes -------------------------


class NetworkDrawer:
    """ 
        Clase que permite graficar redes.
    """

    # 
    def draw(self, N, attribute_to_draw):    
        """ 
            Dibuja la red mostrando en las aristas el atributo dado.
        """
        # Cálculo de posiciones.
        layers = N.get_precedence_layers()
        layers_x_pos = sorted(layers.keys())
        pos = { n: self._get_node_position(n, layers, layers_x_pos) for n in N.nodes() }

        # Colores especiales para nodos origen y destino.
        special_nodes = {0, len(N.nodes())-1}
        node_colors = [ 'orange' if node in special_nodes else 'skyblue' for node in N.nodes() ]

        # Dibujo de la red.
        nx.draw(N, pos, with_labels=True, node_color=node_colors, node_size=1500, arrows=True)

        # Gráfico de las etiquetas en las aristas.
        edge_labels = { 
            (u,v): d[attribute_to_draw] for u, v, d in N.edges(data=True)
        }
        nx.draw_networkx_edge_labels(N, pos, edge_labels=edge_labels, font_size=10)

        # Título.
        plt.title("Red")
        
        plt.show()
    
    def _get_node_position(self, n, layers, layers_x_pos):
        """ 
            Obtiene un par (x,y) para graficar el nodo en función de su capa.
        """
        layer = -1
        nodes_in_layer = []
        for l, nodes in layers.items():
            if n in nodes:
                layer = l
                nodes_in_layer = nodes
        x = layers_x_pos.index(layer)
        y = nodes_in_layer.index(n) - len(nodes_in_layer)/2
        return (x,y)


#----------------- Paquetes -------------------------


class Packet:
    """ 
        Clase que almacena la información de un paquete circulando por una red.
    """

    def __init__(self):
        self.latency = 0
        self.path = None
        self.strategy = None
        self.penalty = False
