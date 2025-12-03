import os
from pydantic import BaseModel

class Settings(BaseModel):
    mongo_uri: str = os.getenv("MONGO_URI", "mongodb://ruta_user:RutaPasswordSeguro1!@172.31.64.75:3306/ruta_optima?authSource=ruta_optima")
    mongo_db: str = os.getenv("MONGO_DB", "ruta_optima")

settings = Settings()
