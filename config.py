"""
Configuración del microservicio de monitoreo
"""

import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

class Config:
    """Configuración base"""
    
    # Base de datos del gestor de pedidos
    GESTOR_DB_HOST = os.getenv('GESTOR_DB_HOST', 'localhost')
    GESTOR_DB_PORT = int(os.getenv('GESTOR_DB_PORT', 3306))
    GESTOR_DB_USER = os.getenv('GESTOR_DB_USER', 'root')
    GESTOR_DB_PASSWORD = os.getenv('GESTOR_DB_PASSWORD', '')
    GESTOR_DB_NAME = os.getenv('GESTOR_DB_NAME', 'pedidos')
    
    # Base de datos de logs
    LOG_DB_HOST = os.getenv('LOG_DB_HOST', 'localhost')
    LOG_DB_PORT = int(os.getenv('LOG_DB_PORT', 3306))
    LOG_DB_USER = os.getenv('LOG_DB_USER', 'root')
    LOG_DB_PASSWORD = os.getenv('LOG_DB_PASSWORD', '')
    LOG_DB_NAME = os.getenv('LOG_DB_NAME', 'LOGSEGURIDAD')
    
    # API del gestor
    GESTOR_API_URL = os.getenv('GESTOR_API_URL', 'http://localhost:5000')
    
    # Configuración del monitor
    MONITOR_PORT = int(os.getenv('MONITOR_PORT', 5001))
    MONITOR_INTERVAL = int(os.getenv('MONITOR_INTERVAL', 30))
    
    # Configuración de seguridad
    SECRET_KEY = os.getenv('SECRET_KEY', 'change-this-secret-key-in-production')

