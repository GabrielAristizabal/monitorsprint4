from fastapi import APIRouter, HTTPException, Query
from ..domain.models import OrderCreate, OrderOut
from ..infra.orders_repo import insert_order
from app.infra.orders_repo import get_last_10_orders_from_previous_month

from datetime import datetime

router = APIRouter(prefix="/orders", tags=["orders"])

@router.post("", response_model=OrderOut)
async def create_order(order: OrderCreate):
    try:
        order_id = await insert_order(order)
        return OrderOut(id=order_id, erp_order_id=order.erp_order_id, created_at=datetime.utcnow())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/last-10-previous-month")
async def last_10_previous_month(
    month: str = Query(..., description="Mes en formato YYYY-MM (ej: 2025-11)")
):
    try:
        orders = await get_last_10_orders_from_previous_month(month)
        return {
            "status": "success",
            "orders": orders,
            "count": len(orders),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))