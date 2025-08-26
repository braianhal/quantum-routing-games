#############################################################
# Utilidades para generar los gráficos de los experimentos. #
#############################################################

from matplotlib.colors import BoundaryNorm, ListedColormap
from matplotlib.patches import Patch
import matplotlib.pyplot as plt
import numpy as np


def series(x, ys, labels, titles, window = 1, optimal = None, show_mins = False, figsize = (12, 4)):   
    """ 
        Muestra N series de tiempo (x, ys) en el mismo gráfico.
            labels y titles: son las etiquetas de cada serie y del gráfico en general.
            window: permite definir la media móvil.
            optimal: muestra una línea punteada con el valor óptimo si existe.
            show_mins: muestra el punto mínimo de cada serie.
            figsize: el tamaño de la figura.
    """
    # Tamaño de figura
    plt.figure(figsize=figsize)

    # Plot de las series.
    for i in range(len(ys)):
        y = ys[i]
        if (window > 1):
            yy = np.convolve(y, np.ones(window)/window, mode='same')
            plot_x = x[window:-window]
            plot_y = yy[window:-window]
        else:
            plot_x = x
            plot_y = y
        plt.plot(plot_x, plot_y, label=labels[i])

        # Plot de los mínimos
        if show_mins:
            min_idx = np.argmin(plot_y)
            plt.scatter(plot_x[min_idx], plot_y[min_idx], 
                        facecolors='none', edgecolors='black', s=80, linewidths=2,
                        zorder=5)
            plt.annotate(titles[0] + "=" + str(round(plot_x[min_idx], 2)), (plot_x[min_idx], plot_y[min_idx]), 
                         xytext=(7, 7), textcoords='offset points')

    # Plot del óptimo
    if (optimal is not None):
        plt.axhline(y=optimal, linestyle='--', color='gray', label='Óptimo') 

    # Plot de labels/títulos.
    plt.xlabel(titles[0])
    plt.ylabel(titles[1])
    plt.legend()
    
    plt.show()

def heatmap(matrix, metric, labels, titles):
    """ 
        Muestra un mapa de calor con los valores de la mariz matrix.
            metric: la métrica particular de matrix a usar para mostrar el mapa de calor.
            labels y titles: son las etiquetas de cada serie y del gráfico en general.
    """
    # Cálculo de la información del mapa de calor.
    n_rows = len(matrix)
    n_cols = max([len(row) for row in matrix])
    heatmap_data = np.full((n_rows, n_cols), np.nan)

    # Generación de colores del mapa de color.
    fig, ax = plt.subplots()
    base_cmap = plt.get_cmap("tab10")
    colors = base_cmap.colors[:len(labels)] 
    cmap = ListedColormap(colors)
    norm = BoundaryNorm(range(len(labels)+1), cmap.N)

    # Cálculo de colores.
    for n in range(n_rows):
        for m in range(len(matrix[n])):
            cell_metrics = matrix[n][m]
            min_idx = np.argmin([cm[metric] for cm in cell_metrics])
            heatmap_data[n][m] = min_idx

    # Plot de los colores del mapa de calor.
    im = ax.imshow(heatmap_data, cmap=cmap, norm=norm)
    cmap.set_bad(color="white")

    # Definición de los tamaños y posicionamiento de la matriz.
    ax.set_xticks(range(n_cols))
    ax.set_yticks(range(n_rows))
    ax.set_xticklabels(range(2, n_cols+2))
    ax.set_yticklabels(range(2, n_rows+2))
    ax.invert_yaxis()

    # Plot de labels/títulos.
    plt.xlabel(titles[0])
    plt.ylabel(titles[1])
    plt.title(titles[2])

    # Plot de leyenda de colores.
    legend_handles = [Patch(facecolor=colors[i], label=labels[i]) for i in range(len(labels))]
    ax.legend(handles=legend_handles, bbox_to_anchor=(1.05, 1), loc="upper left")
    
    plt.show()


def pie(execution_metrics, metric, labels, title):
    """ 
        Muestra un gráfico de torta con las execution_metrics separadas por cada protocolo.
            metric: la métrica particular de matrix a usar para mostrar el mapa de calor.
            labels y title: son las etiquetas de cada conjunto y del gráfico en general.
    """
    # Cálculo de valores.
    results = [0] * len(labels)
    for test_metrics in execution_metrics:
        min_idx = np.argmin([m[metric] for m in test_metrics])
        results[min_idx] += 1

    # Plot del gráfico.
    plt.pie(
        results, 
        labels=labels,         # labels on slices
        autopct="%1.1f%%",     # show percentages
        startangle=90,         # rotate start for better orientation
    )

    # Seteo de título y presentación.
    plt.title(title)
    plt.show()

def plot_3d():
    # Define function q(n,p)
    def q(n, p):
        return n * np.ceil(np.log2(p))

    # Define ranges for n and p
    n_vals = np.arange(2, 17)
    p_vals = np.arange(2, 17)

    # Create meshgrid
    N, P = np.meshgrid(n_vals, p_vals)
    Q = q(N, P)

    # Plot 3D surface
    fig = plt.figure(figsize=(8, 4))
    ax = fig.add_subplot(111, projection='3d')
    ax.plot_surface(N, P, Q, cmap="viridis")

    # Axis labels and title
    ax.set_xlabel("n")
    ax.set_ylabel(r"$|\mathcal{P}|$")
    ax.set_zlabel("q(C)")
    ax.set_title(r"$q(C) = n \cdot \lceil \log_2 |\mathcal{P}| \rceil$")

    plt.show()