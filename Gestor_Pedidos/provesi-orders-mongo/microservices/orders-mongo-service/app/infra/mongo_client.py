import os
from motor.motor_asyncio import AsyncIOMotorClient

# Leer variables de entorno
MONGO_URI = os.getenv(
    "MONGO_URI",
    "mongodb://ruta_user:RutaPasswordSeguro1!@172.31.64.75:3306/ruta_optima?authSource=ruta_optima",
)
MONGO_DB = os.getenv("MONGO_DB", "ruta_optima")

print("⚙️ USANDO MONGO_URI:", MONGO_URI)
print("⚙️ USANDO MONGO_DB:", MONGO_DB)

_client = AsyncIOMotorClient(MONGO_URI)
_db = _client[MONGO_DB]


def get_db():
    return _db
