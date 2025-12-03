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
