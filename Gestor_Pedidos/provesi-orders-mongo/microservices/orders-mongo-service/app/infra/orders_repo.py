from datetime import datetime
from typing import Any, Dict

from .mongo_client import get_db

COLLECTION = "orders"


async def insert_order(order_data: Dict[str, Any]) -> str:
    """
    order_data puede ser:
    - un Pydantic model (OrderCreate)
    - o un dict normal (si ya lo convertiste antes)
    """
    db = get_db()

    # Si viene como modelo Pydantic, lo convertimos a dict
    if hasattr(order_data, "model_dump"):
        order_dict = order_data.model_dump()
    elif hasattr(order_data, "dict"):
        order_dict = order_data.dict()
    else:
        order_dict = dict(order_data)

    items = order_dict.get("items", [])

    normalized_items = []
    for item in items:
        if hasattr(item, "model_dump"):
            normalized_items.append(item.model_dump())
        elif hasattr(item, "dict"):
            normalized_items.append(item.dict())
        else:
            normalized_items.append(item)  # dict u otro tipo simple

    doc = {
        "erp_order_id": order_dict["erp_order_id"],
        "items": normalized_items,
        "status": "CREATED",
        "created_at": datetime.utcnow(),
    }

    result = await db[COLLECTION].insert_one(doc)
    return str(result.inserted_id)

async def get_last_10_orders_from_previous_month(month: str) -> List[Dict[str, Any]]:
    """
    Devuelve los últimos 10 pedidos del mes ANTERIOR al mes dado (YYYY-MM),
    ordenados por created_at descendente.
    """
    db = get_db()

    year, month_num = map(int, month.split("-"))

    # calcular mes anterior
    if month_num == 1:
        prev_year = year - 1
        prev_month = 12
    else:
        prev_year = year
        prev_month = month_num - 1

    start = datetime(prev_year, prev_month, 1)
    # inicio del mes siguiente al anterior
    if prev_month == 12:
        end = datetime(prev_year + 1, 1, 1)
    else:
        end = datetime(prev_year, prev_month + 1, 1)

    query = {
        "created_at": {
            "$gte": start,
            "$lt": end
        }
    }

    cursor = (
        db[COLLECTION]
        .find(query)
        .sort("created_at", -1)  # últimos
        .limit(10)
    )

    results = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        results.append(doc)

    return results
