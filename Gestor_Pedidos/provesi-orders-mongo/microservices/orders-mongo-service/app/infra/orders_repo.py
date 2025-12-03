from datetime import datetime
from typing import Any, Dict
from bson import ObjectId
from .mongo_client import get_db

COLLECTION = "orders"

async def insert_order(order_data: Dict[str, Any]) -> str:
    db = get_db()
    doc = {
        "erp_order_id": order_data["erp_order_id"],
        "items": [item.model_dump() for item in order_data["items"]],
        "status": "CREATED",
        "created_at": datetime.utcnow(),
    }
    result = await db[COLLECTION].insert_one(doc)
    return str(result.inserted_id)
