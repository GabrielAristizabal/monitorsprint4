# core/mongo.py
import os
from pymongo import MongoClient

# Ejemplo de MONGO_URI:
# mongodb://ruta_user:ruta_password@10.0.1.23:27017/ruta_optima?authSource=admin
MONGO_URI = os.getenv(
    "MONGO_URI",
    "mongodb://localhost:27017/ruta_optima"  # valor por defecto para desarrollo local
)

client = MongoClient(MONGO_URI)

# Si la URI trae el nombre de la DB (…/ruta_optima), esta llamada usa esa DB
db = client.get_default_database()

# Colección donde guardaremos el resultado de cada cálculo de ruta
rutas_collection = db["rutas"]
