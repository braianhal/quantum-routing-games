###########################
# Utilidades para listas. #
###########################


def group(lst, group_size):
    """ 
        Devuelve una lista de listas, con los valores de 'lst' agrupados de a 
        'group_size' elementos.
    """
    return [lst[i:i+group_size] for i in range(0, len(lst), group_size)]
