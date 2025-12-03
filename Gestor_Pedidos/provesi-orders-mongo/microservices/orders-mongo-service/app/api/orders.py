from fastapi import APIRouter, HTTPException
from ..domain.models import OrderCreate, OrderOut
from ..infra.orders_repo import insert_order
from datetime import datetime

router = APIRouter(prefix="/orders", tags=["orders"])

@router.post("", response_model=OrderOut)
async def create_order(order: OrderCreate):
    try:
        order_id = await insert_order(order.model_dump())
        return OrderOut(id=order_id, erp_order_id=order.erp_order_id, created_at=datetime.utcnow())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
