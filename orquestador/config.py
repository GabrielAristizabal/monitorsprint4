"""
Configuración del orquestador
"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuración del orquestador"""
    
    # Puerto del orquestador
    ORCHESTRATOR_PORT = int(os.getenv('ORCHESTRATOR_PORT', 8080))
    
    # URLs de los microservicios (fallback si no hay service discovery)
    GESTOR_PEDIDOS_URL = os.getenv('GESTOR_PEDIDOS_URL', 'http://localhost:5000')
    RUTA_OPTIMA_URL = os.getenv('RUTA_OPTIMA_URL', 'http://localhost:8000')
    
    # Configuración de service registry
    REGISTRY_PORT = int(os.getenv('REGISTRY_PORT', 8081))
    SERVICE_TTL = int(os.getenv('SERVICE_TTL', 30))  # Tiempo de vida del servicio en segundos
    
    # Timeouts para llamadas a microservicios
    REQUEST_TIMEOUT = float(os.getenv('REQUEST_TIMEOUT', 0.5))  # 500ms para cumplir < 1 segundo total

