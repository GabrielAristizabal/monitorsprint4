from fastapi import APIRouter, Query
from ..infra.routes_repo import get_last_10_routes_with_stand_deviation
from ..domain.models import RouteReport

router = APIRouter(prefix="/reports", tags=["reports"])

@router.get("/optimized-routes/last-10", response_model=RouteReport)
async def last_10_routes(month: str = Query(..., description="Mes en formato YYYY-MM, por ejemplo 2025-11")):
    report = await get_last_10_routes_with_stand_deviation(month)
    return report
