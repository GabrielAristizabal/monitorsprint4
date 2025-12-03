from typing import List
from ..domain.models import RouteReport, StandDeviation

# Esta implementación es de ejemplo. En un entorno real, se haría un aggregation sobre Mongo.
async def get_last_10_routes_with_stand_deviation(month: str) -> RouteReport:
    stands = [
        StandDeviation(
            stand_id="A1",
            tiempo_estimado_promedio=10.0,
            tiempo_real_promedio=14.0,
            desviacion_promedio=4.0,
        ),
        StandDeviation(
            stand_id="B3",
            tiempo_estimado_promedio=8.0,
            tiempo_real_promedio=12.5,
            desviacion_promedio=4.5,
        ),
    ]
    return RouteReport(month=month, orders_count=10, stands_con_problema=stands)
