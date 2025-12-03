from .base import RouteAlgorithm

class ShortestPathAlgorithm(RouteAlgorithm):
    async def compute_route(self, request):
        # TODO: Implementar llamado al microservicio del grafo de bodega
        # y cálculo de la ruta óptima.
        return {"route": [], "total_estimated_time": 0.0}
