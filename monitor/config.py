"""
Configuración del microservicio de monitoreo
"""

import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

class Config:
    """Configuración base"""
    
    # Base de datos del gestor de pedidos (MongoDB - para monitoreo)
    GESTOR_MONGO_URI = os.getenv('GESTOR_MONGO_URI', 'mongodb://localhost:27017')
    GESTOR_MONGO_DB = os.getenv('GESTOR_MONGO_DB', 'provesi_wms')
    
    # Base de datos de logs (MySQL - LOGSEGURIDAD)
    LOG_DB_HOST = os.getenv('LOG_DB_HOST', 'localhost')
    LOG_DB_PORT = int(os.getenv('LOG_DB_PORT', 5432))
    LOG_DB_USER = os.getenv('LOG_DB_USER', 'monitor_user')
    LOG_DB_PASSWORD = os.getenv('LOG_DB_PASSWORD', '')
    LOG_DB_NAME = os.getenv('LOG_DB_NAME', 'logseguridad')
    
    # API del gestor
    GESTOR_API_URL = os.getenv('GESTOR_API_URL', 'http://localhost:5000')
    
    # Configuración del monitor
    MONITOR_PORT = int(os.getenv('MONITOR_PORT', 5001))
    MONITOR_INTERVAL = int(os.getenv('MONITOR_INTERVAL', 30))
    
    # Configuración de seguridad
    SECRET_KEY = os.getenv('SECRET_KEY', 'change-this-secret-key-in-production')
    GESTOR_BLOCK_URL = os.getenv('GESTOR_BLOCK_URL', f"{GESTOR_API_URL}/admin/block")


