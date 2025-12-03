from ..routes_algorithms.shortest_path import ShortestPathAlgorithm
from ..routes_algorithms.base import RouteAlgorithm

def get_algorithm(name: str = "shortest_path") -> RouteAlgorithm:
    # En una versión futura se podría leer de config/BD
    return ShortestPathAlgorithm()
