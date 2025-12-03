from datetime import datetime
from typing import Any, Dict

from .mongo_client import get_db

COLLECTION = "orders"


async def insert_order(order_data: Dict[str, Any]) -> str:
    db = get_db()

    items = order_data.get("items", [])

    # Si algún item es modelo Pydantic lo convertimos, si es dict lo dejamos igual
    normalized_items = []
    for item in items:
        if hasattr(item, "model_dump"):
            normalized_items.append(item.model_dump())
        elif hasattr(item, "dict"):
            normalized_items.append(item.dict())
        else:
            normalized_items.append(item)  # dict u otro tipo simple

    doc = {
        "erp_order_id": order_data["erp_order_id"],
        "items": normalized_items,
        "status": "CREATED",
        "created_at": datetime.utcnow(),
    }

    result = await db[COLLECTION].insert_one(doc)
    return str(result.inserted_id)
