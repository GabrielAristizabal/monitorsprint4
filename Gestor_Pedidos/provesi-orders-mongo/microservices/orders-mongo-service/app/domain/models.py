from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

class OrderItem(BaseModel):
    sku: str
    quantity: int = Field(gt=0)
    stand_id_estimada: str
    tiempo_estimado_pick: float

class OrderCreate(BaseModel):
    erp_order_id: str
    items: List[OrderItem]

class OrderOut(BaseModel):
    id: str
    erp_order_id: str
    created_at: datetime

class StandDeviation(BaseModel):
    stand_id: str
    tiempo_estimado_promedio: float
    tiempo_real_promedio: float
    desviacion_promedio: float

class RouteReport(BaseModel):
    month: str
    orders_count: int
    stands_con_problema: List[StandDeviation] = []
