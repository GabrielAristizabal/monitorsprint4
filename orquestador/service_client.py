"""
Cliente para comunicarse con los microservicios usando service discovery
"""
import requests
import time
from typing import Optional, Dict, Any
from .service_registry import registry
from .config import Config

class ServiceClient:
    """Cliente para llamar a los microservicios con service discovery"""
    
    def __init__(self):
        self.timeout = Config.REQUEST_TIMEOUT
    
    def _get_service_url(self, service_name: str, fallback_url: Optional[str] = None) -> Optional[str]:
        """Obtiene la URL del servicio desde el registry o usa fallback"""
        url = registry.get_service_url(service_name)
        if not url and fallback_url:
            return fallback_url
        return url
    
    def call_gestor_pedidos(self, endpoint: str, method: str = 'GET', **kwargs) -> Optional[Dict]:
        """
        Llama a un endpoint del gestor de pedidos
        
        Args:
            endpoint: Ruta del endpoint (ej: '/health', '/orders')
            method: Método HTTP ('GET', 'POST', etc.)
            **kwargs: Argumentos adicionales para requests
        """
        url = self._get_service_url('gestor-pedidos', Config.GESTOR_PEDIDOS_URL)
        if not url:
            raise Exception("Servicio gestor-pedidos no disponible")
        
        full_url = f"{url}{endpoint}"
        
        try:
            start_time = time.time()
            response = requests.request(
                method,
                full_url,
                timeout=self.timeout,
                **kwargs
            )
            elapsed = time.time() - start_time
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error llamando a {full_url}: {response.status_code}")
                return None
        except requests.exceptions.Timeout:
            print(f"Timeout llamando a {full_url}")
            return None
        except Exception as e:
            print(f"Error llamando a {full_url}: {e}")
            return None
    
    def call_ruta_optima(self, endpoint: str, method: str = 'GET', **kwargs) -> Optional[Dict]:
        """
        Llama a un endpoint de ruta_optima
        
        Args:
            endpoint: Ruta del endpoint (ej: '/calcular-ruta/')
            method: Método HTTP ('GET', 'POST', etc.)
            **kwargs: Argumentos adicionales para requests
        """
        url = self._get_service_url('ruta-optima', Config.RUTA_OPTIMA_URL)
        if not url:
            raise Exception("Servicio ruta-optima no disponible")
        
        full_url = f"{url}{endpoint}"
        
        try:
            start_time = time.time()
            response = requests.request(
                method,
                full_url,
                timeout=self.timeout,
                **kwargs
            )
            elapsed = time.time() - start_time
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error llamando a {full_url}: {response.status_code}")
                return None
        except requests.exceptions.Timeout:
            print(f"Timeout llamando a {full_url}")
            return None
        except Exception as e:
            print(f"Error llamando a {full_url}: {e}")
            return None

