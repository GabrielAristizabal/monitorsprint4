from motor.motor_asyncio import AsyncIOMotorClient
from ..core.config import settings

_client = AsyncIOMotorClient(settings.mongo_uri)
_db = _client[settings.mongo_db]

def get_db():
    return _db
